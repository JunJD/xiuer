"""
小红书数据处理服务 - 异步版本
负责处理从webhook接收到的小红书数据，包括笔记、评论等
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.future import select
from datetime import datetime, timedelta
import json

from app.models import (
    XhsNote, 
    XhsComment, 
    NoteTagLog, 
    BusinessKeyword,
    NoteTag,
    CrawlTask,
    TaskStatus
)
from app.schemas.webhook import (
    XhsNoteData, 
    XhsCommentData, 
    XhsSearchResult,
    NoteProcessResult,
    BatchProcessResult
)
from app.core.logger import logger


class XhsDataService:
    """小红书数据处理服务 - 异步版本"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def process_search_result(self, search_result: XhsSearchResult) -> BatchProcessResult:
        """处理搜索结果数据"""
        try:
            logger.info(f"开始处理搜索结果: {search_result.query}, 共{len(search_result.notes)}个笔记")
            
            results = []
            errors = []
            new_count = 0
            changed_count = 0
            important_count = 0
            
            for note_data in search_result.notes:
                try:
                    result = await self.process_single_note(note_data)
                    results.append(result)
                    
                    if result.is_new:
                        new_count += 1
                    if result.is_changed:
                        changed_count += 1
                    if result.is_important:
                        important_count += 1
                        
                except Exception as e:
                    error_msg = f"处理笔记 {note_data.note_id} 失败: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # 提交数据库变更
            await self.db.commit()
            
            return BatchProcessResult(
                total_processed=len(results),
                new_notes=new_count,
                changed_notes=changed_count,
                important_notes=important_count,
                errors=errors,
                details=results
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"处理搜索结果失败: {str(e)}")
            raise
    
    async def process_single_note(self, note_data: XhsNoteData) -> NoteProcessResult:
        """处理单个笔记数据"""
        try:
            # 查找现有笔记
            result = await self.db.execute(
                select(XhsNote).filter(XhsNote.note_id == note_data.note_id)
            )
            existing_note = result.scalars().first()
            
            is_new = existing_note is None
            is_changed = False
            is_important = False
            change_reason = None
            important_keywords = []
            
            if is_new:
                # 创建新笔记
                note = self._create_new_note_object(note_data)
                # 检查是否重要
                is_important, important_keywords = await self._check_note_importance(note_data)
                note.is_important = is_important
                if important_keywords:
                    note.important_comment_ids = important_keywords
                    
                self.db.add(note)
                logger.info(f"创建新笔记: {note_data.note_id}")
                
            else:
                # 更新现有笔记
                is_changed, change_reason = self._update_existing_note_object(existing_note, note_data)
                if is_changed:
                    logger.info(f"更新笔记: {note_data.note_id}, 变更原因: {change_reason}")
                
                # 重新检查重要性
                is_important, important_keywords = await self._check_note_importance(note_data)
                if is_important != existing_note.is_important:
                    existing_note.is_important = is_important
                    if important_keywords:
                        existing_note.important_comment_ids = important_keywords
            
            return NoteProcessResult(
                note_id=note_data.note_id,
                is_new=is_new,
                is_changed=is_changed,
                is_important=is_important,
                change_reason=change_reason,
                important_keywords=important_keywords
            )
            
        except Exception as e:
            logger.error(f"处理笔记 {note_data.note_id} 失败: {str(e)}")
            raise
    
    def _create_new_note_object(self, note_data: XhsNoteData) -> XhsNote:
        """创建新笔记对象"""
        # 提取作者信息
        author_user_id = None
        author_nickname = None
        if note_data.author:
            author_user_id = note_data.author.user_id
            author_nickname = note_data.author.nickname
        
        # 提取互动信息
        liked_count = 0
        collected_count = 0
        comment_count = 0
        share_count = 0
        if note_data.interact_info:
            liked_count = note_data.interact_info.liked_count
            collected_count = note_data.interact_info.collected_count
            comment_count = note_data.interact_info.comment_count
            share_count = note_data.interact_info.share_count
        
        # 创建笔记对象
        note = XhsNote(
            note_id=note_data.note_id,
            note_url=note_data.note_url,
            note_type=note_data.note_type,
            author_user_id=author_user_id,
            author_nickname=author_nickname,
            title=note_data.title,
            desc=note_data.desc,
            tags=note_data.tags,
            upload_time=note_data.upload_time,
            ip_location=note_data.ip_location,
            liked_count=liked_count,
            collected_count=collected_count,
            comment_count=comment_count,
            share_count=share_count,
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
    
    def _update_existing_note_object(self, existing_note: XhsNote, note_data: XhsNoteData) -> Tuple[bool, Optional[str]]:
        """更新现有笔记对象，返回是否有变更和变更原因"""
        changes = []
        
        # 保存旧的统计数据
        old_stats = {
            "liked_count": existing_note.liked_count,
            "collected_count": existing_note.collected_count,
            "comment_count": existing_note.comment_count,
            "share_count": existing_note.share_count
        }
        
        # 检查互动数据变化
        if note_data.interact_info:
            new_liked = note_data.interact_info.liked_count
            new_collected = note_data.interact_info.collected_count
            new_comment = note_data.interact_info.comment_count
            new_share = note_data.interact_info.share_count
            
            if new_liked != existing_note.liked_count:
                changes.append(f"点赞数: {existing_note.liked_count} → {new_liked}")
                existing_note.liked_count = new_liked
                
            if new_collected != existing_note.collected_count:
                changes.append(f"收藏数: {existing_note.collected_count} → {new_collected}")
                existing_note.collected_count = new_collected
                
            if new_comment != existing_note.comment_count:
                changes.append(f"评论数: {existing_note.comment_count} → {new_comment}")
                existing_note.comment_count = new_comment
                
            if new_share != existing_note.share_count:
                changes.append(f"分享数: {existing_note.share_count} → {new_share}")
                existing_note.share_count = new_share
        
        # 更新基础信息
        existing_note.last_crawl_time = datetime.utcnow()
        existing_note.crawl_count += 1
        existing_note.is_new = False  # 不再是新笔记
        
        if changes:
            existing_note.is_changed = True
            existing_note.previous_stats = old_stats
            change_reason = "; ".join(changes)
            existing_note.change_reason = change_reason
            
            # 更新标签
            current_tags = existing_note.current_tags or []
            if NoteTag.CHANGED.value not in current_tags:
                current_tags.append(NoteTag.CHANGED.value)
            existing_note.current_tags = current_tags
            
            return True, change_reason
        
        return False, None
    
    async def _check_note_importance(self, note_data: XhsNoteData) -> Tuple[bool, List[str]]:
        """检查笔记是否重要（基于业务关键词）"""
        try:
            # 获取所有激活的业务关键词
            result = await self.db.execute(
                select(BusinessKeyword).filter(BusinessKeyword.is_active == True)
            )
            keywords = result.scalars().all()
            
            if not keywords:
                return False, []
            
            found_keywords = []
            text_to_check = []
            
            # 收集要检查的文本
            if note_data.title:
                text_to_check.append(note_data.title)
            if note_data.desc:
                text_to_check.append(note_data.desc)
            if note_data.tags:
                text_to_check.extend(note_data.tags)
            
            full_text = " ".join(text_to_check).lower()
            
            # 检查每个关键词
            for keyword in keywords:
                if keyword.keyword.lower() in full_text:
                    found_keywords.append(keyword.keyword)
            
            is_important = len(found_keywords) > 0
            return is_important, found_keywords
            
        except Exception as e:
            logger.error(f"检查笔记重要性失败: {str(e)}")
            return False, []
    
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
                          offset: int = 0) -> List[XhsNote]:
        """搜索笔记"""
        try:
            query = select(XhsNote)
            
            # 添加过滤条件
            if keyword:
                query = query.filter(
                    or_(
                        XhsNote.title.ilike(f"%{keyword}%"),
                        XhsNote.desc.ilike(f"%{keyword}%")
                    )
                )
            
            if is_new is not None:
                query = query.filter(XhsNote.is_new == is_new)
            
            if is_changed is not None:
                query = query.filter(XhsNote.is_changed == is_changed)
            
            if is_important is not None:
                query = query.filter(XhsNote.is_important == is_important)
            
            if author_user_id:
                query = query.filter(XhsNote.author_user_id == author_user_id)
            
            if date_from:
                query = query.filter(XhsNote.first_crawl_time >= date_from)
            
            if date_to:
                query = query.filter(XhsNote.first_crawl_time <= date_to)
            
            # 排序和分页
            query = query.order_by(desc(XhsNote.last_crawl_time))
            query = query.offset(offset).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"搜索笔记失败: {str(e)}")
            return []
    
    async def get_note_by_id(self, note_id: str) -> Optional[XhsNote]:
        """根据note_id获取笔记"""
        try:
            result = await self.db.execute(
                select(XhsNote).filter(XhsNote.note_id == note_id)
            )
            return result.scalars().first()
            
        except Exception as e:
            logger.error(f"获取笔记详情失败: {str(e)}")
            return None 