"""
Tasks 路由测试
测试任务管理功能
"""

import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock
from app.models import CrawlTask, TaskStatus


class TestTasks:
    @pytest.mark.asyncio(loop_scope="function")
    async def test_get_tasks_list(self, test_client, db_session):
        """测试获取任务列表"""
        response = await test_client.get("/api/tasks/")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        # 目前返回待实现消息
        assert "message" in result
        assert "任务列表功能待实现" in result["message"]

    @pytest.mark.asyncio(loop_scope="function")
    async def test_get_task_detail(self, test_client, db_session):
        """测试获取任务详情"""
        task_id = "test_task_123"
        response = await test_client.get(f"/api/tasks/{task_id}")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        # 目前返回待实现消息
        assert "message" in result
        assert task_id in result["message"]

    @pytest.mark.asyncio(loop_scope="function")
    async def test_cancel_task(self, test_client, db_session):
        """测试取消任务"""
        task_id = "test_task_456"
        response = await test_client.delete(f"/api/tasks/{task_id}")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        # 目前返回待实现消息
        assert "message" in result
        assert task_id in result["message"]

    @pytest.mark.asyncio(loop_scope="function")
    @patch('app.routes.tasks.requests.post')
    @patch('app.routes.tasks.os.getenv')
    async def test_trigger_crawl_task_success(self, mock_getenv, mock_post, test_client, db_session):
        """测试成功触发爬取任务"""
        # Mock环境变量
        mock_getenv.side_effect = lambda key, default=None: {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPO_OWNER": "test_owner",
            "GITHUB_REPO_NAME": "test_repo"
        }.get(key, default)
        
        # Mock成功的GitHub API响应
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        # 任务请求数据
        task_data = {
            "task_name": "测试任务",
            "keyword": "测试关键词",
            "target_count": 10,
            "sort_type": 1,
            "webhook_url": "https://test.com/webhook",
            "cookies": "test_cookies"
        }
        
        response = await test_client.post("/api/tasks/trigger-crawl", json=task_data)
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["success"] == True
        assert "成功触发" in result["message"]
        assert "task_id" in result
        assert "github_run_url" in result
        
        # 验证GitHub API调用
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "https://api.github.com/repos/test_owner/test_repo/dispatches" in call_args[0]

    @pytest.mark.asyncio(loop_scope="function")
    @patch('app.routes.tasks.os.getenv')
    async def test_trigger_crawl_task_no_github_token(self, mock_getenv, test_client, db_session):
        """测试没有GitHub token时触发任务失败"""
        # Mock没有GitHub token
        mock_getenv.return_value = None
        
        task_data = {
            "task_name": "测试任务",
            "keyword": "测试关键词",
            "target_count": 10,
            "sort_type": 1,
            "webhook_url": "https://test.com/webhook"
        }
        
        response = await test_client.post("/api/tasks/trigger-crawl", json=task_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        result = response.json()
        assert "detail" in result
        assert "GitHub token 未配置" in result["detail"]

    @pytest.mark.asyncio(loop_scope="function")
    @patch('app.routes.tasks.requests.post')
    @patch('app.routes.tasks.os.getenv')
    async def test_trigger_crawl_task_github_api_error(self, mock_getenv, mock_post, test_client, db_session):
        """测试GitHub API调用失败"""
        # Mock环境变量
        mock_getenv.side_effect = lambda key, default=None: {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPO_OWNER": "test_owner",
            "GITHUB_REPO_NAME": "test_repo"
        }.get(key, default)
        
        # Mock失败的GitHub API响应
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        task_data = {
            "task_name": "测试任务",
            "keyword": "测试关键词",
            "target_count": 10,
            "sort_type": 1,
            "webhook_url": "https://test.com/webhook"
        }
        
        response = await test_client.post("/api/tasks/trigger-crawl", json=task_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        result = response.json()
        assert "detail" in result
        assert "触发GitHub Actions失败" in result["detail"]

    @pytest.mark.asyncio(loop_scope="function")
    async def test_trigger_crawl_task_invalid_data(self, test_client, db_session):
        """测试无效的任务数据"""
        # 缺少必要字段的数据
        invalid_task_data = {
            "task_name": "测试任务"
            # 缺少其他必要字段
        }
        
        response = await test_client.post("/api/tasks/trigger-crawl", json=invalid_task_data)
        
        # 应该返回422验证错误
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio(loop_scope="function")
    @patch('app.routes.tasks.requests.post')
    @patch('app.routes.tasks.os.getenv')
    async def test_trigger_crawl_task_without_cookies(self, mock_getenv, mock_post, test_client, db_session):
        """测试不包含cookies的任务触发"""
        # Mock环境变量
        mock_getenv.side_effect = lambda key, default=None: {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_REPO_OWNER": "test_owner",
            "GITHUB_REPO_NAME": "test_repo"
        }.get(key, default)
        
        # Mock成功的GitHub API响应
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        # 不包含cookies的任务数据
        task_data = {
            "task_name": "无cookies测试任务",
            "keyword": "测试关键词",
            "target_count": 5,
            "sort_type": 2,
            "webhook_url": "https://test.com/webhook"
        }
        
        response = await test_client.post("/api/tasks/trigger-crawl", json=task_data)
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["success"] == True
        
        # 验证GitHub API调用，确保没有cookies字段
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "cookies" not in payload["client_payload"] 