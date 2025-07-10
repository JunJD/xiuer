"""
任务管理 API 端点
专门处理爬取任务的触发和管理
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, List
import json
import os
import requests

from app.database import get_async_session
from app.schemas.webhook import (
    CrawlTaskRequest,
    TaskTriggerResponse,
)
from app.schemas.tasks import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskStatsResponse,
    TaskActionResponse,
    TaskQueryParams,
    TaskStatusEnum
)
from app.models import CrawlTask, TaskStatus, User
from sqlalchemy import select, func, and_, case, literal_column
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
        
        # 准备GitHub Actions参数 - 根据workflow_dispatch的inputs要求
        github_payload = {
            "ref": "main",  # 指定分支
            "inputs": {
                "query": task_request.keyword,
                "num": str(task_request.target_count),  # 需要转成字符串
                "sort_type": str(task_request.sort_type),  # 需要转成字符串
                "cookies": task_request.cookies or "",
                "webhook_url": task_request.webhook_url or "",
                "get_comments": "false",  # 默认不获取评论
                "no_delay": "false",      # 默认启用延迟
                "task_id": str(task_id)   # 转成字符串
            }
        }
        
        # 发送请求到GitHub API
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise HTTPException(status_code=500, detail="GitHub token 未配置")
        
        repo_owner = os.getenv("GITHUB_REPO_OWNER", "JunJD")
        repo_name = os.getenv("GITHUB_REPO_NAME", "xiuer-spider")
        workflow_id = os.getenv("GITHUB_WORKFLOW_ID", "170912099")  # 使用实际的数字 ID
        
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/dispatches"

        print(f"url===>: {url}")
        print(f"github_payload===>: {github_payload}")
        print(f"headers===>: {headers}")
        
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


@router.get("/", response_model=TaskListResponse)
async def get_tasks(
    page: int = 1,
    size: int = 10,
    filters: Optional[List[str]] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取任务列表
    """
    try:
        # 构建查询条件
        conditions = []
        if status:
            try:
                status_enum = TaskStatus(status)
                conditions.append(CrawlTask.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的状态值: {status}")
        
        if keyword:
            conditions.append(CrawlTask.keyword.contains(keyword))
        
        # 分页计算
        offset = (page - 1) * size
        print(f"filters: {filters}")
        # 查询总数
        count_query = select(func.count(CrawlTask.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 查询任务列表
        query = select(CrawlTask).order_by(CrawlTask.created_at.desc())
        if conditions:
            query = query.where(and_(*conditions))
        query = query.offset(offset).limit(size)
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        # 转换为响应模型
        task_responses = [TaskResponse.from_orm(task) for task in tasks]

        return TaskListResponse(
            tasks=task_responses,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务失败: {str(e)}")


@router.get("/stats", response_model=TaskStatsResponse, name="get_task_stats")
async def get_task_stats(
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取任务统计信息
    """
    try:
        # 查询总数
        total_query = select(func.count(CrawlTask.id).label("total"))
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0
        
        # 查询各状态任务数量
        pending_query = select(func.count(CrawlTask.id).label("pending")).where(CrawlTask.status == TaskStatus.PENDING)
        pending_result = await db.execute(pending_query)
        pending = pending_result.scalar() or 0
        
        running_query = select(func.count(CrawlTask.id).label("running")).where(CrawlTask.status == TaskStatus.RUNNING)
        running_result = await db.execute(running_query)
        running = running_result.scalar() or 0
        
        completed_query = select(func.count(CrawlTask.id).label("completed")).where(CrawlTask.status == TaskStatus.COMPLETED)
        completed_result = await db.execute(completed_query)
        completed = completed_result.scalar() or 0
        
        failed_query = select(func.count(CrawlTask.id).label("failed")).where(CrawlTask.status == TaskStatus.FAILED)
        failed_result = await db.execute(failed_query)
        failed = failed_result.scalar() or 0
        
        return TaskStatsResponse(
            total_tasks=total,
            pending_tasks=pending,
            running_tasks=running,
            completed_tasks=completed,
            failed_tasks=failed
        )
        
    except Exception as e:
        logger.error(f"获取任务统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务统计失败: {str(e)}")


@router.get("/detail/{task_id}", response_model=TaskResponse)
async def get_task_detail(
    task_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取任务详情
    """
    try:
        # 验证 task_id 是否为有效的 UUID 格式
        import uuid
        try:
            uuid_obj = uuid.UUID(task_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的任务ID格式: {task_id}")
        
        # 查询任务
        query = select(CrawlTask).where(CrawlTask.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return TaskResponse(
            id=str(task.id),
            task_name=task.task_name,
            keyword=task.keyword,
            target_count=task.target_count,
            sort_type=task.sort_type,
            cookies=task.cookies,
            status=TaskStatusEnum(task.status.value),
            owner_id=str(task.owner_id),
            total_crawled=task.total_crawled,
            new_notes=task.new_notes,
            changed_notes=task.changed_notes,
            important_notes=task.important_notes,
            error_message=task.error_message,
            scheduled_time=task.scheduled_time,
            started_at=task.started_at,
            finished_at=task.finished_at,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        
    except Exception as e:
        logger.error(f"获取任务详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务详情失败: {str(e)}")


@router.delete("/{task_id}", response_model=TaskActionResponse)
async def cancel_task(
    task_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    取消任务
    """
    try:
        # 验证 task_id 是否为有效的 UUID 格式
        import uuid
        try:
            uuid_obj = uuid.UUID(task_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的任务ID格式: {task_id}")
        
        # 查询任务
        query = select(CrawlTask).where(CrawlTask.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 检查任务状态
        if task.status == TaskStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="任务已完成，无法取消")
        
        if task.status == TaskStatus.FAILED:
            raise HTTPException(status_code=400, detail="任务已失败，无法取消")
        
        # 更新任务状态
        task.status = TaskStatus.FAILED
        task.error_message = "任务被用户取消"
        task.finished_at = datetime.utcnow()
        await db.commit()
        
        return TaskActionResponse(
            success=True,
            message=f"任务 {task.task_name} 已取消",
            task_id=str(task.id)
        )
        
    except Exception as e:
        logger.error(f"取消任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")


@router.post("/", response_model=TaskActionResponse)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    创建新任务
    """
    try:
        # 创建系统用户或使用现有用户（简化处理）
        from sqlalchemy import select
        system_user_email = "system@webhook.local"
        
        result = await db.execute(select(User).where(User.email == system_user_email))
        system_user = result.scalar_one_or_none()
        
        if not system_user:
            import uuid
            system_user = User(
                id=uuid.uuid4(),
                email=system_user_email,
                hashed_password="$argon2id$v=19$m=65536,t=3,p=4$dummy$dummyhash",
                is_active=True,
                is_superuser=False,
                is_verified=True
            )
            db.add(system_user)
            await db.commit()
            await db.refresh(system_user)
        
        # 创建任务
        task = CrawlTask(
            task_name=task_data.task_name,
            keyword=task_data.keyword,
            target_count=task_data.target_count,
            sort_type=task_data.sort_type,
            cookies=task_data.cookies,
            status=TaskStatus.PENDING,
            owner_id=system_user.id
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        return TaskActionResponse(
            success=True,
            message=f"任务 {task.task_name} 创建成功",
            task_id=str(task.id)
        )
        
    except Exception as e:
        logger.error(f"创建任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}") 