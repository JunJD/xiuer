"""
Webhook 路由测试
测试webhook接收和数据处理功能
"""

import pytest
from fastapi import status


class TestWebhook:
    @pytest.mark.asyncio(loop_scope="function")
    async def test_webhook_test_endpoint(self, test_client):
        """测试webhook测试端点"""
        response = await test_client.post("/api/webhook/test")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["status"] == "ok"
        assert result["message"] == "webhook端点正常工作"

    @pytest.mark.asyncio(loop_scope="function")
    async def test_webhook_invalid_data(self, test_client):
        """测试webhook无效数据"""
        webhook_data = {
            "invalid_field": "invalid_value"
        }
        
        response = await test_client.post(
            "/api/webhook/xhs-result",
            json=webhook_data
        )
        
        # 应该返回422验证错误
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 