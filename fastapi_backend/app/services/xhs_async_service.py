"""
小红书数据异步服务
处理小红书笔记和评论数据的业务逻辑
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.future import select
import json

from app.models.note import XhsNote, NoteTag, NoteTagLog
from app.models.comment import XhsComment
from app.models.keyword import BusinessKeyword
from app.models.task import CrawlTask
from app.schemas.notes import XhsNoteData, ProcessResult
from app.schemas.comments import XhsCommentData
from app.core.logger import app_logger as logger
from app.utils import parse_filters, parse_sort, apply_filters_to_query, apply_sorting_to_query

# 定义 CST 时区，用于将输入的 naive datetime 转换为 aware datetime
CST = timezone(timedelta(hours=8))


class XhsDataService:
    """小红书数据处理服务 - 异步版本"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @staticmethod
    def _utc_now() -> datetime:
        return datetime.utcnow()
        
    async def process_notes_batch(self, notes_data: List[XhsNoteData]) -> ProcessResult:
        """处理笔记批量数据"""
        try:
            logger.info(f"开始处理笔记批量数据，共{len(notes_data)}个笔记")
            
            new_count = 0
            changed_count = 0
            important_count = 0
            errors = []
            
            for note_data in notes_data:
                try:
                    is_new, is_changed, is_important = await self.process_single_note(note_data)
                    
                    if is_new:
                        new_count += 1
                    if is_changed:
                        changed_count += 1
                    if is_important:
                        important_count += 1
                        
                except Exception as e:
                    error_msg = f"处理笔记 {note_data.note_id} 失败: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # 提交数据库变更
            await self.db.commit()
            
            return ProcessResult(
                total_processed=len(notes_data),
                new_count=new_count,
                changed_count=changed_count,
                important_count=important_count,
                errors=errors
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"处理笔记批量数据失败: {str(e)}")
            raise
    
    async def process_single_note(self, note_data: XhsNoteData) -> Tuple[bool, bool, bool]:
        """处理单个笔记数据，返回(is_new, is_changed, is_important)"""
        try:
            # 先查找现有笔记（不过滤时间，确保能找到已存在的记录）
            result = await self.db.execute(
                select(XhsNote).filter(XhsNote.note_id == note_data.note_id)
            )
            existing_note = result.scalars().first()
            
            # 获取今天00:00的时间用于对比逻辑
            now = self._utc_now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            is_new = existing_note is None
            is_changed = False
            is_important = False
            
            if is_new:
                # 创建新笔记
                note = self._create_new_note_object(note_data)
                # 检查是否重要
                is_important = await self._check_note_importance(note_data)
                note.is_important = is_important
                    
                self.db.add(note)
                logger.info(f"创建新笔记: {note_data.note_id}")
                
            else:
                # 检查是否今天已经爬取过
                already_crawled_today = existing_note.last_crawl_time >= today_start
                
                if already_crawled_today:
                    # 今天已经爬取过，只更新数据，不重新检测变化
                    is_changed = self._update_existing_note_simple(existing_note, note_data)
                    logger.info(f"今日重复爬取笔记: {note_data.note_id}")
                else:
                    # 今天首次爬取，进行变化检测
                    is_changed = self._update_existing_note_object(existing_note, note_data)
                    if is_changed:
                        logger.info(f"更新笔记: {note_data.note_id}")
                
                # 重新检查重要性
                is_important = await self._check_note_importance(note_data)
                if is_important != existing_note.is_important:
                    existing_note.is_important = is_important
            
            return is_new, is_changed, is_important
            
        except Exception as e:
            logger.error(f"处理笔记 {note_data.note_id} 失败: {str(e)}")
            raise
    
    def _create_new_note_object(self, note_data: XhsNoteData) -> XhsNote:
        """创建新笔记对象"""
        # 创建笔记对象
        note = XhsNote(
            note_id=note_data.note_id,
            note_url=note_data.note_url,
            note_type=note_data.note_type,
            author_user_id=note_data.author_user_id,
            author_nickname=note_data.author_nickname,
            title=note_data.title,
            desc=note_data.desc,
            tags=note_data.tags,
            upload_time=note_data.upload_time,
            ip_location=note_data.ip_location,
            liked_count=note_data.liked_count,
            collected_count=note_data.collected_count,
            comment_count=note_data.comment_count,
            share_count=note_data.share_count,
            video_cover=note_data.video_cover,
            video_addr=note_data.video_addr,
            image_list=note_data.image_list,
            is_new=True,
            is_changed=False,
            current_tags=[NoteTag.NEW.value],
            first_crawl_time=datetime.utcnow(),
            last_crawl_time=datetime.utcnow(),
            crawl_count=1
        )
        
        return note
    
    def _update_existing_note_object(self, existing_note: XhsNote, note_data: XhsNoteData) -> bool:
        """更新现有笔记对象，返回是否有变更"""
        is_changed = False
        
        # 只检查评论数量变化
        is_changed = existing_note.comment_count != note_data.comment_count
        
        # 更新所有互动数据（即使没有变化也要更新到最新值）
        existing_note.liked_count = note_data.liked_count
        existing_note.collected_count = note_data.collected_count
        existing_note.comment_count = note_data.comment_count
        existing_note.share_count = note_data.share_count
        
        # 更新其他可能变化的字段
        # if existing_note.title != note_data.title:
        #     existing_note.title = note_data.title
        #     is_changed = True
            
        # if existing_note.desc != note_data.desc:
        #     existing_note.desc = note_data.desc
        #     is_changed = True
        
        if is_changed:
            existing_note.is_changed = True
            existing_note.is_new = False
            existing_note.last_crawl_time = datetime.utcnow()
            existing_note.crawl_count += 1
            
            # 更新标签
            if NoteTag.CHANGED.value not in existing_note.current_tags:
                existing_note.current_tags.append(NoteTag.CHANGED.value)
        else:
            # 没有变化的情况下也要更新状态
            existing_note.is_changed = False
            existing_note.is_new = False
            existing_note.last_crawl_time = datetime.utcnow()
            existing_note.crawl_count += 1
        
        return is_changed
    
    def _update_existing_note_simple(self, existing_note: XhsNote, note_data: XhsNoteData) -> bool:
        """简单更新现有笔记对象（不检测变化，用于同日重复爬取）"""
        # 更新所有互动数据到最新值
        existing_note.liked_count = note_data.liked_count
        existing_note.collected_count = note_data.collected_count
        existing_note.comment_count = note_data.comment_count
        existing_note.share_count = note_data.share_count
        
        # 更新其他可能变化的字段
        existing_note.title = note_data.title
        existing_note.desc = note_data.desc
        
        # 更新爬取时间和计数，但保持现有的变化状态
        existing_note.last_crawl_time = datetime.utcnow()
        existing_note.crawl_count += 1
        existing_note.is_new = False  # 确保不是新笔记
        
        # 返回 False，表示这次没有新的变化检测
        return existing_note.is_changed
    
    async def _check_note_importance(self, note_data: XhsNoteData) -> bool:
        """检查笔记是否重要（简化版）"""
        try:
            # 获取关键词
            result = await self.db.execute(
                select(BusinessKeyword).filter(BusinessKeyword.is_active == True)
            )
            keywords = result.scalars().all()
            
            # 检查标题和描述中是否包含关键词
            text_to_check = f"{note_data.title or ''} {note_data.desc or ''}"
            
            for keyword in keywords:
                if keyword.keyword.lower() in text_to_check.lower():
                    return True
            
            # 根据互动数据判断
            if (note_data.liked_count > 1000 or 
                note_data.comment_count > 100 or
                note_data.collected_count > 500):
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"检查笔记重要性失败: {str(e)}")
            return False
    
    async def get_notes_stats(self) -> Dict[str, int]:
        """获取笔记统计信息"""
        try:
            today = datetime.utcnow().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            # 执行统计查询
            total_result = await self.db.execute(select(func.count(XhsNote.id)))
            total_notes = total_result.scalar() or 0
            
            new_result = await self.db.execute(
                select(func.count(XhsNote.id)).filter(XhsNote.is_new == True)
            )
            new_notes = new_result.scalar() or 0
            
            changed_result = await self.db.execute(
                select(func.count(XhsNote.id)).filter(XhsNote.is_changed == True)
            )
            changed_notes = changed_result.scalar() or 0
            
            important_result = await self.db.execute(
                select(func.count(XhsNote.id)).filter(XhsNote.is_important == True)
            )
            important_notes = important_result.scalar() or 0
            
            today_result = await self.db.execute(
                select(func.count(XhsNote.id)).filter(XhsNote.first_crawl_time >= today_start)
            )
            today_crawled = today_result.scalar() or 0
            
            return {
                "total_notes": total_notes,
                "new_notes": new_notes,
                "changed_notes": changed_notes,
                "important_notes": important_notes,
                "today_crawled": today_crawled
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {
                "total_notes": 0,
                "new_notes": 0,
                "changed_notes": 0,
                "important_notes": 0,
                "today_crawled": 0
            }
    
    async def search_notes(self, 
                          keyword: Optional[str] = None,
                          is_new: Optional[bool] = None,
                          is_changed: Optional[bool] = None,
                          is_important: Optional[bool] = None,
                          author_user_id: Optional[str] = None,
                          date_from: Optional[datetime] = None,
                          date_to: Optional[datetime] = None,
                          limit: int = 50,
                          offset: int = 0,
                          filters: Optional[str] = None,
                          sort: Optional[str] = None) -> List[XhsNote]:
        """搜索笔记 - 支持高级筛选和排序"""
        try:
            query = select(XhsNote)
            
            # 应用基础筛选条件
            query = self._apply_basic_filters(query, keyword, is_new, is_changed, is_important, author_user_id, date_from, date_to)
            
            # 应用高级筛选
            if filters:
                filter_list = parse_filters(filters)
                query = apply_filters_to_query(query, filter_list, XhsNote)
            
            # 应用排序
            if sort:
                sort_list = parse_sort(sort)
                query = apply_sorting_to_query(query, sort_list, XhsNote)
            else:
                # 默认排序
                query = query.order_by(desc(XhsNote.last_crawl_time))
            
            # 分页
            query = query.offset(offset).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"搜索笔记失败: {str(e)}")
            return []

    async def count_notes(self,
                         keyword: Optional[str] = None,
                         is_new: Optional[bool] = None,
                         is_changed: Optional[bool] = None,
                         is_important: Optional[bool] = None,
                         author_user_id: Optional[str] = None,
                         date_from: Optional[datetime] = None,
                         date_to: Optional[datetime] = None,
                         filters: Optional[str] = None) -> int:
        """计算符合条件的笔记总数 - 支持高级筛选"""
        try:
            query = select(func.count(XhsNote.id))
            
            # 应用基础筛选条件
            query = self._apply_basic_filters(query, keyword, is_new, is_changed, is_important, author_user_id, date_from, date_to)
            
            # 应用高级筛选
            if filters:
                filter_list = parse_filters(filters)
                query = apply_filters_to_query(query, filter_list, XhsNote)
            
            result = await self.db.execute(query)
            return result.scalar() or 0
            
        except Exception as e:
            logger.error(f"计算笔记总数失败: {str(e)}")
            return 0
    
    def _apply_basic_filters(self, query, keyword=None, is_new=None, is_changed=None, is_important=None, author_user_id=None, date_from=None, date_to=None, include_deleted: bool = False):
        """应用基础筛选条件的通用方法"""
        # 默认过滤掉软删除的笔记
        if not include_deleted:
            query = query.filter(XhsNote.is_deleted == False)

        # 添加过滤条件 - 与原有逻辑保持一致
        if keyword:
            query = query.filter(
                or_(
                    XhsNote.title.ilike(f"%{keyword}%"),
                    XhsNote.desc.ilike(f"%{keyword}%")
                )
            )
        
        # 将 is_new, is_changed, is_important 的筛选条件收集起来，作为并集（OR）处理
        boolean_filters = []
        if is_new is not None:
            boolean_filters.append(XhsNote.is_new == is_new)
        
        if is_changed is not None:
            boolean_filters.append(XhsNote.is_changed == is_changed)

        if boolean_filters:
            query = query.filter(or_(*boolean_filters))

        if author_user_id:
            query = query.filter(XhsNote.author_user_id == author_user_id)
        
        if date_from:
            # 1. 将输入的 naive datetime 视为中国时区 (CST)
            aware_date_from = date_from.replace(tzinfo=CST)
            # 2. 转换为 aware UTC datetime
            utc_date_from = aware_date_from.astimezone(timezone.utc)
            # 3. 移除 tzinfo，使其成为 naive UTC datetime，以匹配数据库列类型
            naive_utc_date_from = utc_date_from.replace(tzinfo=None)
            query = query.filter(XhsNote.last_crawl_time >= naive_utc_date_from)
        
        if date_to:
            # 1. 将输入的 naive datetime 视为中国时区 (CST)
            aware_date_to = date_to.replace(tzinfo=CST)
            # 2. 转换为 aware UTC datetime
            utc_date_to = aware_date_to.astimezone(timezone.utc)
            # 3. 移除 tzinfo，使其成为 naive UTC datetime，以匹配数据库列类型
            naive_utc_date_to = utc_date_to.replace(tzinfo=None)
            query = query.filter(XhsNote.last_crawl_time <= naive_utc_date_to)
        
        return query
    
    async def get_note_by_id(self, note_id: str) -> Optional[XhsNote]:
        """根据note_id获取笔记"""
        try:
            result = await self.db.execute(
                select(XhsNote).filter(XhsNote.note_id == note_id, XhsNote.is_deleted == False)
            )
            return result.scalars().first()
            
        except Exception as e:
            logger.error(f"获取笔记详情失败: {str(e)}")
            return None

    async def soft_delete_note(self, note_id: str) -> bool:
        """软删除一个笔记"""
        try:
            result = await self.db.execute(
                select(XhsNote).filter(XhsNote.note_id == note_id)
            )
            note_to_delete = result.scalars().first()
            
            if not note_to_delete:
                return False
            
            note_to_delete.is_deleted = True
            await self.db.commit()
            logger.info(f"笔记 {note_id} 已被软删除。")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"软删除笔记 {note_id} 失败: {str(e)}")
            raise 