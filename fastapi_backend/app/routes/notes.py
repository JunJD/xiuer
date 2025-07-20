"""
笔记查询 API 端点
专门处理笔记和评论的查询功能
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timezone, timedelta

from app.database import get_async_session
from app.schemas.notes import (
    NoteStatsResponse,
    XhsNoteResponse,
    NotesListResponse,
)
from app.services.xhs_async_service import XhsDataService
from app.core.logger import app_logger as logger

router = APIRouter()


@router.get("/stats", response_model=NoteStatsResponse)
async def get_notes_stats(db: AsyncSession = Depends(get_async_session)):
    """
    获取笔记统计信息
    """
    try:
        xhs_service = XhsDataService(db)
        stats = await xhs_service.get_notes_stats()
        
        return NoteStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.get("/", response_model=NotesListResponse)
async def search_notes(
    keyword: str = None,
    is_new: bool = None,
    is_changed: bool = None,
    is_important: bool = None,
    author_user_id: str = None,
    today_only: bool = False,
    page: int = 1,
    size: int = 50,
    # 新增的筛选和排序参数
    filters: str = None,
    sort: str = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    搜索和筛选笔记 - 支持分页、筛选和排序
    """
    try:
        # 处理today_only参数
        date_from = None
        if today_only:
            # 获取中国时区的当前时间（通过UTC+8小时），然后取其零点，生成一个 naive datetime
            now_in_cst = datetime.utcnow() + timedelta(hours=8)
            today_start = now_in_cst.replace(hour=0, minute=0, second=0, microsecond=0)
            date_from = today_start
            print(f"date_from3: {date_from}")
        
        # 计算偏移量
        offset = (page - 1) * size
        
        xhs_service = XhsDataService(db)
        
        # 获取总数
        total = await xhs_service.count_notes(
            keyword=keyword,
            is_new=is_new,
            is_changed=is_changed,
            is_important=is_important,
            author_user_id=author_user_id,
            date_from=date_from,
            filters=filters,
        )
        
        # 获取笔记列表
        notes = await xhs_service.search_notes(
            keyword=keyword,
            is_new=is_new,
            is_changed=is_changed,
            is_important=is_important,
            author_user_id=author_user_id,
            date_from=date_from,
            limit=size,
            offset=offset,
            filters=filters,
            sort=sort,
        )
        
        # 转换为响应模式
        result = []
        for note in notes:
            note_response = XhsNoteResponse(
                id=str(note.id),
                note_id=note.note_id,
                note_url=note.note_url,
                note_type=note.note_type,
                title=note.title,
                desc=note.desc,
                author_nickname=note.author_nickname,
                liked_count=note.liked_count,
                comment_count=note.comment_count,
                current_tags=note.current_tags,
                is_new=note.is_new,
                is_changed=note.is_changed,
                is_important=note.is_important,
                first_crawl_time=note.first_crawl_time,
                last_crawl_time=note.last_crawl_time,
                image_list=note.image_list,
                author_avatar=note.author_avatar
            )
            result.append(note_response)
        
        return NotesListResponse(
            notes=result,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"搜索笔记失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/{note_id}")
async def get_note_detail(
    note_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取单个笔记详情
    """
    try:
        xhs_service = XhsDataService(db)
        note = await xhs_service.get_note_by_id(note_id)
        
        if not note:
            raise HTTPException(status_code=404, detail="笔记不存在")
            
        return XhsNoteResponse(
            id=str(note.id),
            note_id=note.note_id,
            note_url=note.note_url,
            note_type=note.note_type,
            title=note.title,
            desc=note.desc,
            author_nickname=note.author_nickname,
            liked_count=note.liked_count,
            comment_count=note.comment_count,
            current_tags=note.current_tags,
            is_new=note.is_new,
            is_changed=note.is_changed,
            is_important=note.is_important,
            first_crawl_time=note.first_crawl_time,
            last_crawl_time=note.last_crawl_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取笔记详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取详情失败: {str(e)}") 