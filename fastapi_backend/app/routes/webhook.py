"""
Webhook API 端点
专门处理来自GitHub Actions的webhook回调和数据处理
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import json
import hmac
import hashlib

from app.database import get_async_session
from app.schemas.webhook import (
    WebhookRequest,
    WebhookResponse,
    WebhookStatus,
    XhsSearchResult,
    XhsNoteData,
    XhsUserResult,
    BatchProcessResult
)
from app.services.xhs_async_service import XhsDataService
from app.core.logger import app_logger as logger

router = APIRouter()


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
                    db
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
                    db
                )
                logger.info(f"COMPLETED状态收到数据，后台处理中")
                return WebhookResponse(
                    status="received",
                    message="完成数据已接收，后台处理中"
                )
            else:
                return WebhookResponse(
                    status="received", 
                    message="完成通知已接收（无数据）"
                )
        
        elif webhook_data.status in [WebhookStatus.ERROR, WebhookStatus.FAILED]:
            # 错误处理
            logger.error(f"任务执行失败: {webhook_data.message}")
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


async def process_webhook_data_background(data: Dict[Any, Any], db: AsyncSession):
    """
    后台处理webhook数据
    """
    try:
        xhs_service = XhsDataService(db)
        
        # 判断数据类型并处理
        if isinstance(data, dict):
            # 检查是否是搜索结果
            if "query" in data and "notes" in data:
                # 转换为搜索结果对象
                search_result = XhsSearchResult(**data)
                result = await xhs_service.process_search_result(search_result)
                logger.info(f"处理搜索结果完成: 新增{result.new_notes}个笔记，变更{result.changed_notes}个笔记")
                
            # 检查是否是单个笔记
            elif "note_id" in data:
                note_data = XhsNoteData(**data)
                result = await xhs_service.process_single_note(note_data)
                logger.info(f"处理单个笔记完成: {result.note_id}")
                
            # 检查是否是用户结果
            elif "user_url" in data and "notes" in data:
                user_result = XhsUserResult(**data)
                # 处理用户的笔记数据
                notes = []
                for note_info in user_result.notes:
                    if "note_id" in note_info:
                        try:
                            note_data = XhsNoteData(**note_info)
                            notes.append(note_data)
                        except Exception as e:
                            logger.warning(f"转换笔记数据失败: {str(e)}")
                
                if notes:
                    # 创建假的搜索结果来处理
                    fake_search = XhsSearchResult(
                        query=f"用户:{user_result.user_url}",
                        total_found=len(notes),
                        notes=notes
                    )
                    result = await xhs_service.process_search_result(fake_search)
                    logger.info(f"处理用户笔记完成: 新增{result.new_notes}个笔记")
            
            else:
                logger.warning(f"未知的数据格式: {data}")
                
    except Exception as e:
        logger.error(f"后台处理webhook数据失败: {str(e)}")
        # 这里可以添加更多的错误处理，比如重试机制


@router.post("/test")
async def test_webhook():
    """
    测试webhook端点
    """
    return {"status": "ok", "message": "webhook端点正常工作"}


# 可选：webhook签名验证
def verify_webhook_signature(request: Request, secret: str) -> bool:
    """
    验证webhook签名（可选的安全措施）
    """
    try:
        signature_header = request.headers.get("X-Hub-Signature-256")
        if not signature_header:
            return False
        
        body = request.body()
        expected_signature = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(
            signature_header,
            f"sha256={expected_signature}"
        )
    except Exception:
        return False 