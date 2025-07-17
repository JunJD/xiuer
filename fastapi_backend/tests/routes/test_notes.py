"""
Notes 路由测试
测试笔记查询功能
"""

import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch
from app.models.note import XhsNote
from sqlalchemy import insert


class TestNotes:
    @pytest.mark.asyncio(loop_scope="function")
    async def test_get_notes_stats(self, test_client, db_session):
        """测试获取笔记统计信息"""
        response = await test_client.get("/api/notes/stats")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        
        # 检查返回的统计字段
        assert "total_notes" in result
        assert "new_notes" in result
        assert "changed_notes" in result
        assert "important_notes" in result
        assert "today_crawled" in result
        
        # 验证数据类型
        assert isinstance(result["total_notes"], int)
        assert isinstance(result["new_notes"], int)
        assert isinstance(result["changed_notes"], int)
        assert isinstance(result["important_notes"], int)
        assert isinstance(result["today_crawled"], int)

    @pytest.mark.asyncio(loop_scope="function")
    async def test_search_notes_empty_database(self, test_client, db_session):
        """测试在空数据库中搜索笔记"""
        response = await test_client.get("/api/notes/")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio(loop_scope="function")
    async def test_search_notes_with_keyword(self, test_client, db_session):
        """测试使用关键词搜索笔记"""
        # 创建测试笔记数据
        test_notes = [
            {
                "note_id": "test_note_1",
                "note_url": "https://test.com/1",
                "note_type": "normal",
                "title": "Python编程教程",
                "desc": "学习Python的基础知识",
                "author_nickname": "测试用户1",
                "liked_count": 100,
                "comment_count": 20,
                "is_new": True,
                "is_changed": False,
                "is_important": False
            },
            {
                "note_id": "test_note_2",
                "note_url": "https://test.com/2",
                "note_type": "normal",
                "title": "JavaScript入门",
                "desc": "前端开发基础",
                "author_nickname": "测试用户2",
                "liked_count": 200,
                "comment_count": 30,
                "is_new": False,
                "is_changed": True,
                "is_important": True
            }
        ]
        
        # 插入测试数据
        for note_data in test_notes:
            await db_session.execute(insert(XhsNote).values(**note_data))
        await db_session.commit()
        
        # 搜索包含"Python"的笔记
        response = await test_client.get("/api/notes/?keyword=Python")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 1
        assert result[0]["title"] == "Python编程教程"

    @pytest.mark.asyncio(loop_scope="function")
    async def test_search_notes_with_filters(self, test_client, db_session):
        """测试使用过滤条件搜索笔记"""
        # 创建测试笔记数据
        test_notes = [
            {
                "note_id": "test_note_1",
                "note_url": "https://test.com/1",
                "note_type": "normal",
                "title": "新笔记",
                "desc": "这是一个新笔记",
                "author_nickname": "测试用户1",
                "liked_count": 100,
                "comment_count": 20,
                "is_new": True,
                "is_changed": False,
                "is_important": False
            },
            {
                "note_id": "test_note_2",
                "note_url": "https://test.com/2",
                "note_type": "normal",
                "title": "重要笔记",
                "desc": "这是一个重要笔记",
                "author_nickname": "测试用户2",
                "liked_count": 200,
                "comment_count": 30,
                "is_new": False,
                "is_changed": True,
                "is_important": True
            }
        ]
        
        # 插入测试数据
        for note_data in test_notes:
            await db_session.execute(insert(XhsNote).values(**note_data))
        await db_session.commit()
        
        # 搜索新笔记
        response = await test_client.get("/api/notes/?is_new=true")
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 1
        assert result[0]["is_new"] == True
        
        # 搜索重要笔记
        response = await test_client.get("/api/notes/?is_important=true")
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 1
        assert result[0]["is_important"] == True

    @pytest.mark.asyncio(loop_scope="function")
    async def test_search_notes_with_pagination(self, test_client, db_session):
        """测试分页功能"""
        # 创建多个测试笔记
        test_notes = []
        for i in range(10):
            test_notes.append({
                "note_id": f"test_note_{i}",
                "note_url": f"https://test.com/{i}",
                "note_type": "normal",
                "title": f"测试笔记 {i}",
                "desc": f"这是第{i}个测试笔记",
                "author_nickname": f"测试用户{i}",
                "liked_count": i * 10,
                "comment_count": i * 2,
                "is_new": i % 2 == 0,
                "is_changed": False,
                "is_important": False
            })
        
        # 插入测试数据
        for note_data in test_notes:
            await db_session.execute(insert(XhsNote).values(**note_data))
        await db_session.commit()
        
        # 测试分页
        response = await test_client.get("/api/notes/?limit=5&offset=0")
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 5
        
        # 测试第二页
        response = await test_client.get("/api/notes/?limit=5&offset=5")
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert len(result) == 5

    @pytest.mark.asyncio(loop_scope="function")
    async def test_get_note_detail_existing(self, test_client, db_session):
        """测试获取存在的笔记详情"""
        # 创建测试笔记
        test_note = {
            "note_id": "test_note_detail",
            "note_url": "https://test.com/detail",
            "note_type": "normal",
            "title": "详情测试笔记",
            "desc": "这是用于测试详情的笔记",
            "author_nickname": "详情测试用户",
            "liked_count": 500,
            "comment_count": 100,
            "is_new": True,
            "is_changed": False,
            "is_important": True
        }
        
        await db_session.execute(insert(XhsNote).values(**test_note))
        await db_session.commit()
        
        # 获取笔记详情
        response = await test_client.get("/api/notes/test_note_detail")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["note_id"] == "test_note_detail"
        assert result["title"] == "详情测试笔记"
        assert result["liked_count"] == 500

    @pytest.mark.asyncio(loop_scope="function")
    async def test_get_note_detail_not_found(self, test_client, db_session):
        """测试获取不存在的笔记详情"""
        response = await test_client.get("/api/notes/nonexistent_note")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        result = response.json()
        assert "detail" in result
        assert result["detail"] == "笔记不存在" 