"""
关键词管理API端点
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from ...database import get_async_session
from ...models import BusinessKeyword, User
from ...schemas.keywords import (
    KeywordCreate,
    KeywordUpdate,
    KeywordResponse,
    KeywordListResponse
)

router = APIRouter()


@router.get("/", response_model=KeywordListResponse)
async def get_keywords(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    active_only: bool = True,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """获取关键词列表"""
    
    query = select(BusinessKeyword)
    
    # 筛选条件
    if active_only:
        query = query.filter(BusinessKeyword.is_active == True)
    
    if category:
        query = query.filter(BusinessKeyword.category == category)
    
    if search:
        query = query.filter(BusinessKeyword.keyword.ilike(f"%{search}%"))
    
    # 分页和排序
    query = query.order_by(
        desc(BusinessKeyword.weight),
        BusinessKeyword.category,
        BusinessKeyword.keyword
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    keywords = result.scalars().all()
    
    # 获取总数
    count_query = select(BusinessKeyword)
    if active_only:
        count_query = count_query.filter(BusinessKeyword.is_active == True)
    if category:
        count_query = count_query.filter(BusinessKeyword.category == category)
    if search:
        count_query = count_query.filter(BusinessKeyword.keyword.ilike(f"%{search}%"))
    
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    # 获取分类统计
    categories_result = await db.execute(select(BusinessKeyword.category).distinct())
    category_list = [cat for cat in categories_result.scalars().all() if cat]
    
    return KeywordListResponse(
        keywords=keywords,
        total=total,
        categories=category_list
    )


@router.post("/", response_model=KeywordResponse)
async def create_keyword(
    keyword_data: KeywordCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """创建新关键词"""
    
    # 检查关键词是否已存在
    existing_result = await db.execute(
        select(BusinessKeyword).filter(BusinessKeyword.keyword == keyword_data.keyword)
    )
    existing = existing_result.scalars().first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"关键词 '{keyword_data.keyword}' 已存在"
        )
    
    # 创建新关键词
    keyword = BusinessKeyword(**keyword_data.model_dump())
    db.add(keyword)
    await db.commit()
    await db.refresh(keyword)
    
    return keyword


@router.put("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: str,
    keyword_data: KeywordUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """更新关键词"""
    
    result = await db.execute(
        select(BusinessKeyword).filter(BusinessKeyword.id == keyword_id)
    )
    keyword = result.scalars().first()
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )
    
    # 如果更新关键词文本，检查是否重复
    if keyword_data.keyword and keyword_data.keyword != keyword.keyword:
        existing_result = await db.execute(
            select(BusinessKeyword).filter(
                BusinessKeyword.keyword == keyword_data.keyword,
                BusinessKeyword.id != keyword_id
            )
        )
        existing = existing_result.scalars().first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"关键词 '{keyword_data.keyword}' 已存在"
            )
    
    # 更新字段
    update_data = keyword_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(keyword, field, value)
    
    await db.commit()
    await db.refresh(keyword)
    
    return keyword


@router.delete("/{keyword_id}")
async def delete_keyword(
    keyword_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """删除关键词"""
    
    result = await db.execute(
        select(BusinessKeyword).filter(BusinessKeyword.id == keyword_id)
    )
    keyword = result.scalars().first()
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )
    
    await db.delete(keyword)
    await db.commit()
    
    return {"message": f"关键词 '{keyword.keyword}' 已删除"}


@router.patch("/{keyword_id}/toggle")
async def toggle_keyword_status(
    keyword_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """切换关键词启用/禁用状态"""
    
    result = await db.execute(
        select(BusinessKeyword).filter(BusinessKeyword.id == keyword_id)
    )
    keyword = result.scalars().first()
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在"
        )
    
    keyword.is_active = not keyword.is_active
    await db.commit()
    await db.refresh(keyword)
    
    status_text = "启用" if keyword.is_active else "禁用"
    return {
        "message": f"关键词 '{keyword.keyword}' 已{status_text}",
        "is_active": keyword.is_active
    }


@router.get("/categories", response_model=List[str])
async def get_categories(
    db: AsyncSession = Depends(get_async_session)
):
    """获取所有关键词分类"""
    
    result = await db.execute(select(BusinessKeyword.category).distinct())
    return [cat for cat in result.scalars().all() if cat]


@router.get("/stats")
async def get_keyword_stats(
    db: AsyncSession = Depends(get_async_session)
):
    """获取关键词统计信息"""
    
    # 总数和活跃数
    total_result = await db.execute(select(BusinessKeyword))
    total = len(total_result.scalars().all())
    
    active_result = await db.execute(
        select(BusinessKeyword).filter(BusinessKeyword.is_active == True)
    )
    active = len(active_result.scalars().all())
    
    # 按分类统计
    category_stats = {}
    categories_result = await db.execute(select(BusinessKeyword.category).distinct())
    
    for cat in categories_result.scalars().all():
        if cat:
            count_result = await db.execute(
                select(BusinessKeyword).filter(BusinessKeyword.category == cat)
            )
            category_stats[cat] = len(count_result.scalars().all())
    
    # 按权重统计
    weight_stats = {}
    for weight in range(1, 11):
        weight_result = await db.execute(
            select(BusinessKeyword).filter(BusinessKeyword.weight == weight)
        )
        count = len(weight_result.scalars().all())
        if count > 0:
            weight_stats[f"权重{weight}"] = count
    
    return {
        "total": total,
        "active": active,
        "inactive": total - active,
        "category_stats": category_stats,
        "weight_stats": weight_stats
    } 