"""
Webhook API 端点
专门处理来自GitHub Actions的webhook回调和数据处理
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import json
import hmac
import hashlib

from app.database import get_async_session
from app.schemas.webhook import (
    WebhookRequest,
    WebhookResponse,
    WebhookStatus
)
from app.schemas.notes import (
    XhsNoteData,
    ProcessResult
)
from app.services.xhs_async_service import XhsDataService
from app.models.task import CrawlTask, TaskStatus
from app.core.logger import app_logger as logger
from sqlalchemy import select
from datetime import datetime
import uuid

router = APIRouter()


async def update_task_status(db: AsyncSession, task_id: str, status: TaskStatus, 
                           result: ProcessResult = None, error_message: str = None):
    """
    更新爬取任务状态
    """
    try:
        if not task_id:
            return
            
        # 查找任务
        result_task = await db.execute(select(CrawlTask).where(CrawlTask.id == uuid.UUID(task_id)))
        task = result_task.scalar_one_or_none()
        
        if not task:
            logger.warning(f"未找到任务ID: {task_id}")
            return
        
        # 更新任务状态
        task.status = status
        
        if status == TaskStatus.RUNNING:
            task.started_at = datetime.utcnow()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            task.finished_at = datetime.utcnow()
            
        # 更新结果统计
        if result:
            task.total_crawled = result.total_processed
            task.new_notes = result.new_count
            task.changed_notes = result.changed_count
            task.important_notes = result.important_count
            
        # 更新错误信息
        if error_message:
            task.error_message = error_message
            
        await db.commit()
        logger.info(f"更新任务状态: {task_id} -> {status.value}")
        
    except Exception as e:
        logger.error(f"更新任务状态失败: {str(e)}")


def transform_note_data(raw_data: dict) -> dict:
    """
    转换原始笔记数据为符合XhsNoteData schema的格式
    将嵌套结构转换为扁平化结构
    """
    transformed = {}
    
    # 复制基础字段
    for key in ['note_id', 'note_url', 'note_type', 'title', 'desc', 'tags', 
                'upload_time', 'ip_location', 'video_cover', 
                'image_list', 'xsec_token']:
        if key in raw_data:
            transformed[key] = raw_data[key]
    
    # 处理author嵌套字段
    if 'author' in raw_data and isinstance(raw_data['author'], dict):
        author = raw_data['author']
        transformed['author_user_id'] = author.get('user_id')
        transformed['author_nickname'] = author.get('nickname')
        transformed['author_avatar'] = author.get('avatar')
    
    # 处理interact_info嵌套字段
    if 'interact_info' in raw_data and isinstance(raw_data['interact_info'], dict):
        interact = raw_data['interact_info']
        transformed['liked_count'] = interact.get('liked_count', 0)
        transformed['collected_count'] = interact.get('collected_count', 0)
        transformed['comment_count'] = interact.get('comment_count', 0)
        transformed['share_count'] = interact.get('share_count', 0)
    else:
        # 如果没有嵌套结构，尝试直接从根级别获取
        transformed['liked_count'] = raw_data.get('liked_count', 0)
        transformed['collected_count'] = raw_data.get('collected_count', 0)
        transformed['comment_count'] = raw_data.get('comment_count', 0)
        transformed['share_count'] = raw_data.get('share_count', 0)
    
    return transformed

async def process_webhook_data_background(data: Any, db: AsyncSession, task_id: str = None):
    """
    后台处理webhook数据 - 简化版
    """
    try:
        xhs_service = XhsDataService(db)
        result = None
        
        # 处理数据
        if isinstance(data, dict):
            # 检查是否是包含notes数组的数据格式
            if "notes" in data and isinstance(data["notes"], list):
                notes_data = []
                for item in data["notes"]:
                    if isinstance(item, dict) and "note_id" in item:
                        # 转换数据格式
                        transformed_item = transform_note_data(item)
                        notes_data.append(XhsNoteData(**transformed_item))
                
                if notes_data:
                    result = await xhs_service.process_notes_batch(notes_data)
                    logger.info(f"处理笔记批量数据完成: 新增{result.new_count}个笔记，变更{result.changed_count}个笔记")
                else:
                    logger.warning(f"notes数组为空或格式不正确")
            # 检查是否是单个笔记
            elif "note_id" in data:
                # 转换数据格式
                transformed_data = transform_note_data(data)
                note_data = XhsNoteData(**transformed_data)
                is_new, is_changed, is_important = await xhs_service.process_single_note(note_data)
                logger.info(f"处理单个笔记完成: {note_data.note_id}")
                # 为单个笔记创建处理结果
                result = ProcessResult(
                    total_processed=1,
                    new_count=1 if is_new else 0,
                    changed_count=1 if is_changed else 0,
                    important_count=1 if is_important else 0,
                    errors=[]
                )
            else:
                logger.warning(f"未知的数据格式: {data}")
                
        elif isinstance(data, list):
            # 处理笔记列表
            notes_data = []
            for item in data:
                if isinstance(item, dict) and "note_id" in item:
                    # 转换数据格式
                    transformed_item = transform_note_data(item)
                    notes_data.append(XhsNoteData(**transformed_item))
            
            if notes_data:
                result = await xhs_service.process_notes_batch(notes_data)
                logger.info(f"处理笔记批量数据完成: 新增{result.new_count}个笔记，变更{result.changed_count}个笔记")
        
        # 更新任务状态
        if task_id and result:
            await update_task_status(db, task_id, TaskStatus.COMPLETED, result)
        
    except Exception as e:
        logger.error(f"后台处理webhook数据失败: {str(e)}")
        if task_id:
            await update_task_status(db, task_id, TaskStatus.FAILED, None, str(e))


@router.post("/xhs-result", response_model=WebhookResponse)
async def receive_xhs_webhook(
    webhook_data: WebhookRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session)
):
    """
    接收小红书爬虫结果的webhook端点
    """
    try:
        logger.info(f"收到webhook数据: 状态={webhook_data.status}, 消息={webhook_data.message}")
        
        # 根据不同状态处理数据
        if webhook_data.status == WebhookStatus.STARTED:
            # 更新任务为运行状态
            if webhook_data.task_id:
                background_tasks.add_task(update_task_status, db, webhook_data.task_id, TaskStatus.RUNNING)
            return WebhookResponse(
                status="received",
                message="任务开始通知已接收"
            )
        
        elif webhook_data.status == WebhookStatus.PROGRESS:
            # 进度更新，可以记录到日志或更新任务状态
            logger.info(f"任务进度更新: {webhook_data.progress}% - {webhook_data.message}")
            return WebhookResponse(
                status="received",
                message="进度更新已接收"
            )
        
        elif webhook_data.status == WebhookStatus.SUCCESS:
            # 成功完成，处理返回的数据
            if webhook_data.data:
                background_tasks.add_task(
                    process_webhook_data_background,
                    webhook_data.data,
                    db,
                    webhook_data.task_id  # 传递task_id
                )
                logger.info(f"SUCCESS状态收到数据，后台处理中")
            
            return WebhookResponse(
                status="received",
                message="成功数据已接收，后台处理中"
            )
        
        elif webhook_data.status == WebhookStatus.COMPLETED:
            # 任务完成（可能含部分错误），如果有数据也要处理
            logger.info(f"任务完成: {webhook_data.message}")
            
            if webhook_data.data:
                background_tasks.add_task(
                    process_webhook_data_background,
                    webhook_data.data,
                    db,
                    webhook_data.task_id  # 传递task_id
                )
                logger.info(f"COMPLETED状态收到数据，后台处理中")
                return WebhookResponse(
                    status="received",
                    message="完成数据已接收，后台处理中"
                )
            else:
                # 没有数据，只更新任务为完成状态
                if webhook_data.task_id:
                    background_tasks.add_task(update_task_status, db, webhook_data.task_id, TaskStatus.COMPLETED)
                return WebhookResponse(
                    status="received", 
                    message="完成通知已接收（无数据）"
                )
        
        elif webhook_data.status in [WebhookStatus.ERROR, WebhookStatus.FAILED]:
            # 错误处理
            logger.error(f"任务执行失败: {webhook_data.message}")
            # 更新任务为失败状态
            if webhook_data.task_id:
                background_tasks.add_task(update_task_status, db, webhook_data.task_id, TaskStatus.FAILED, None, webhook_data.message)
            return WebhookResponse(
                status="received",
                message="错误信息已接收"
            )
        
        else:
            logger.warning(f"未知的webhook状态: {webhook_data.status}")
            return WebhookResponse(
                status="received",
                message="未知状态已接收"
            )
            
    except Exception as e:
        logger.error(f"处理webhook失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理webhook失败: {str(e)}")


@router.post("/test")
async def test_webhook():
    """测试webhook端点"""
    return {"message": "Webhook测试成功", "timestamp": datetime.utcnow()}


def verify_webhook_signature(request: Request, secret: str) -> bool:
    """验证webhook签名"""
    try:
        signature = request.headers.get("X-Hub-Signature-256")
        if not signature:
            return False
        
        body = request.body()
        expected_signature = hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        expected_signature = f"sha256={expected_signature}"
        
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False 