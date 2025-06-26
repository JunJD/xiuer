"""
任务管理 API 端点
专门处理爬取任务的触发和管理
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
import json
import os
import requests

from app.database import get_async_session
from app.schemas.webhook import (
    CrawlTaskRequest,
    TaskTriggerResponse,
)
from app.models import CrawlTask, TaskStatus, User
from app.core.logger import logger

router = APIRouter()


@router.post("/trigger-crawl", response_model=TaskTriggerResponse) 
async def trigger_crawl_task(
    task_request: CrawlTaskRequest,
    db: AsyncSession = Depends(get_async_session)
    # current_user: Optional[User] = None  # TODO: 添加用户认证
):
    """
    触发爬取任务
    """
    try:
        # 创建任务记录
        task = CrawlTask(
            task_name=task_request.task_name,
            keyword=task_request.keyword,
            target_count=task_request.target_count,
            sort_type=task_request.sort_type,
            cookies=task_request.cookies,
            status=TaskStatus.PENDING,
            owner_id=None  # TODO: 从认证用户获取
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        # 准备GitHub Actions参数
        github_payload = {
            "event_type": "run-xhs-spider",
            "client_payload": {
                "webhook_url": task_request.webhook_url,
                "task_type": "search",
                "task_params": task_request.model_dump_json()
            }
        }
        
        # 发送请求到GitHub API
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise HTTPException(status_code=500, detail="GitHub token 未配置")
        
        repo_owner = os.getenv("GITHUB_REPO_OWNER", "JunJD")
        repo_name = os.getenv("GITHUB_REPO_NAME", "xiuer")
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dispatches"
        
        response = requests.post(url, json=github_payload, headers=headers)
        
        if response.status_code == 204:
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            await db.commit()
            
            return TaskTriggerResponse(
                success=True,
                message="爬取任务已成功触发",
                task_id=str(task.id),
                github_run_url=f"https://github.com/{repo_owner}/{repo_name}/actions"
            )
        else:
            # 更新任务状态为失败
            task.status = TaskStatus.FAILED
            task.error_message = f"GitHub API调用失败: {response.status_code} - {response.text}"
            await db.commit()
            
            raise HTTPException(
                status_code=500, 
                detail=f"触发GitHub Actions失败: {response.status_code}"
            )
            
    except Exception as e:
        logger.error(f"触发爬取任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"触发任务失败: {str(e)}")


@router.get("/")
async def get_tasks(
    limit: int = 50,
    offset: int = 0,
    status: str = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取任务列表
    """
    try:
        # 这里可以添加任务列表查询逻辑
        return {"message": "任务列表功能待实现"}
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务失败: {str(e)}")


@router.get("/{task_id}")
async def get_task_detail(
    task_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取任务详情
    """
    try:
        # 这里可以添加任务详情查询逻辑
        return {"message": f"任务 {task_id} 详情功能待实现"}
        
    except Exception as e:
        logger.error(f"获取任务详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务详情失败: {str(e)}")


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    取消任务
    """
    try:
        # 这里可以添加任务取消逻辑
        return {"message": f"任务 {task_id} 取消功能待实现"}
        
    except Exception as e:
        logger.error(f"取消任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}") 