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
from app.core.logger import app_logger as logger

router = APIRouter()


@router.post("/trigger-crawl", response_model=TaskTriggerResponse) 
async def trigger_crawl_task(
    task_request: CrawlTaskRequest,
    db: AsyncSession = Depends(get_async_session)
    # NOTE: 不需要用户认证，因为可能被外部系统调用
):
    """
    触发爬取任务
    """
    try:
        # 创建任务记录 - 使用系统用户ID或创建匿名任务
        # 查找或创建系统用户
        from sqlalchemy import select
        system_user_email = "system@webhook.local"
        
        result = await db.execute(select(User).where(User.email == system_user_email))
        system_user = result.scalar_one_or_none()
        
        if not system_user:
            # 创建系统用户（简化版本，避免循环导入）
            import uuid
            system_user = User(
                id=uuid.uuid4(),
                email=system_user_email,
                hashed_password="$argon2id$v=19$m=65536,t=3,p=4$dummy$dummyhash",  # 固定的假密码
                is_active=True,
                is_superuser=False,
                is_verified=True
            )
            db.add(system_user)
            await db.commit()
            await db.refresh(system_user)
        
        task = CrawlTask(
            task_name=task_request.task_name,
            keyword=task_request.keyword,
            target_count=task_request.target_count,
            sort_type=task_request.sort_type,
            cookies=task_request.cookies,
            status=TaskStatus.PENDING,
            owner_id=system_user.id
        )
        
        db.add(task)
        await db.commit()
        # 不要刷新关系，只获取任务ID
        task_id = task.id
        
        # 准备GitHub Actions参数 - 根据workflow的repository_dispatch要求
        # 参考workflow中的client_payload参数要求
        github_payload = {
            "event_type": "search-xhs",  # 匹配workflow中的types: [search-xhs, crawl-task]
            "client_payload": {
                # GitHub Actions workflow期望的直接参数
                "query": task_request.keyword,
                "num": task_request.target_count,
                "sort_type": task_request.sort_type,
                "cookies": task_request.cookies or "",
                "webhook_url": task_request.webhook_url,
                "get_comments": False,  # 默认不获取评论
                "no_delay": False,      # 默认启用延迟
                "task_id": str(task_id),  # 重要：添加task_id以便webhook回调时更新对应任务
            }
        }
        
        # 发送请求到GitHub API
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise HTTPException(status_code=500, detail="GitHub token 未配置")
        
        repo_owner = os.getenv("GITHUB_REPO_OWNER", "JunJD")
        repo_name = os.getenv("GITHUB_REPO_NAME", "xiuer-spider")
        
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
                task_id=str(task_id),
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