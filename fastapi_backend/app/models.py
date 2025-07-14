from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, JSON, Boolean, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime
import enum


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    items = relationship("Item", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("UserLog", back_populates="user", cascade="all, delete-orphan")
    crawl_tasks = relationship("CrawlTask", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

    user = relationship("User", back_populates="items")


class UserLog(Base):
    __tablename__ = "user_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    action = Column(String(100), nullable=False)  # 例如: "login", "logout", "create_item"
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # 支持IPv6
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="logs")


# 笔记标签枚举
class NoteTag(enum.Enum):
    NEW = "new"  # 新笔记
    CHANGED = "changed"  # 数据有变更
    IMPORTANT = "important"  # 重要（评论中包含业务相关内容）


# 爬取任务状态枚举
class TaskStatus(enum.Enum):
    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


# 小红书笔记表
class XhsNote(Base):
    __tablename__ = "xhs_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    note_id = Column(String(100), nullable=False, unique=True, index=True)  # 笔记ID
    note_url = Column(String(500), nullable=True)  # 笔记URL
    note_type = Column(String(20), nullable=True)  # 笔记类型：图集/视频
    
    # 作者基本信息（简化版）
    author_user_id = Column(String(100), nullable=True, index=True)  # 作者用户ID
    author_nickname = Column(String(100), nullable=True)  # 作者昵称
    
    # 笔记内容
    title = Column(String(500), nullable=True)  # 标题
    desc = Column(Text, nullable=True)  # 描述内容
    tags = Column(JSON, nullable=True)  # 标签列表
    upload_time = Column(DateTime, nullable=True)  # 上传时间
    ip_location = Column(String(100), nullable=True)  # IP归属地
    
    # 互动数据（用于检测变更）
    liked_count = Column(Integer, default=0)  # 点赞数量
    collected_count = Column(Integer, default=0)  # 收藏数量
    comment_count = Column(Integer, default=0)  # 评论数量
    share_count = Column(Integer, default=0)  # 分享数量
    
    # 媒体内容
    video_cover = Column(String(500), nullable=True)  # 视频封面URL
    video_addr = Column(String(500), nullable=True)  # 视频地址URL
    image_list = Column(JSON, nullable=True)  # 图片地址URL列表
    author_avatar = Column(String(500), nullable=True)  # 作者头像URL
    
    # 标签和追踪字段
    current_tags = Column(JSON, nullable=True)  # 当前标签列表 [NoteTag.NEW, NoteTag.IMPORTANT]
    is_new = Column(Boolean, default=True)  # 是否为新笔记
    is_changed = Column(Boolean, default=False)  # 是否有变更
    is_important = Column(Boolean, default=False)  # 是否重要
    change_reason = Column(String(200), nullable=True)  # 变更原因（如：评论数增加）
    important_comment_ids = Column(JSON, nullable=True)  # 重要评论ID列表
    
    # 数据追踪
    first_crawl_time = Column(DateTime, default=datetime.utcnow, nullable=False)  # 首次爬取时间
    last_crawl_time = Column(DateTime, default=datetime.utcnow, nullable=False)  # 最后爬取时间
    crawl_count = Column(Integer, default=1)  # 爬取次数
    
    # 历史数据快照（用于对比变更）
    previous_stats = Column(JSON, nullable=True)  # 上次的统计数据
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系映射
    comments = relationship("XhsComment", back_populates="note", cascade="all, delete-orphan")
    tag_logs = relationship("NoteTagLog", back_populates="note", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_note_crawl_time', 'last_crawl_time'),
        Index('idx_note_tags', 'is_new', 'is_changed', 'is_important'),
        Index('idx_author_id', 'author_user_id'),
    )


# 小红书评论表（简化版）
class XhsComment(Base):
    __tablename__ = "xhs_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    comment_id = Column(String(100), nullable=False, unique=True, index=True)  # 评论ID
    note_id = Column(String(100), ForeignKey("xhs_notes.note_id"), nullable=False, index=True)  # 笔记ID
    
    # 评论者基本信息
    commenter_user_id = Column(String(100), nullable=True)  # 评论用户ID
    commenter_nickname = Column(String(100), nullable=True)  # 评论用户昵称
    
    # 评论内容
    content = Column(Text, nullable=True)  # 评论内容
    like_count = Column(Integer, default=0)  # 点赞数量
    upload_time = Column(DateTime, nullable=True)  # 评论时间
    ip_location = Column(String(100), nullable=True)  # IP归属地
    
    # 层级关系
    parent_comment_id = Column(String(100), nullable=True, index=True)  # 父评论ID
    root_comment_id = Column(String(100), nullable=True, index=True)  # 根评论ID
    
    # 业务相关标记
    contains_business_keywords = Column(Boolean, default=False)  # 是否包含业务关键词
    business_keywords_found = Column(JSON, nullable=True)  # 发现的业务关键词列表
    importance_score = Column(Integer, default=0)  # 重要性评分（0-10）
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系映射
    note = relationship("XhsNote", back_populates="comments")


# 笔记标签变更日志表
class NoteTagLog(Base):
    __tablename__ = "note_tag_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    note_id = Column(String(100), ForeignKey("xhs_notes.note_id"), nullable=False, index=True)
    
    # 标签变更信息
    old_tags = Column(JSON, nullable=True)  # 旧标签
    new_tags = Column(JSON, nullable=True)  # 新标签
    change_type = Column(String(50), nullable=False)  # 变更类型：added, removed, updated
    change_reason = Column(String(200), nullable=True)  # 变更原因
    
    # 变更数据
    old_stats = Column(JSON, nullable=True)  # 旧的统计数据
    new_stats = Column(JSON, nullable=True)  # 新的统计数据
    related_comment_ids = Column(JSON, nullable=True)  # 相关评论ID（如果是因为评论变更）
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系映射
    note = relationship("XhsNote", back_populates="tag_logs")


# 爬取任务表（简化版）
class CrawlTask(Base):
    __tablename__ = "crawl_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_name = Column(String(200), nullable=False)  # 任务名称
    keyword = Column(String(200), nullable=False, index=True)  # 搜索关键词
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)  # 任务状态
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)  # 任务创建者
    
    # 爬取配置
    target_count = Column(Integer, default=200)  # 目标爬取数量
    sort_type = Column(Integer, default=1)  # 排序方式：1最新
    cookies = Column(Text, nullable=True)  # 使用的cookies
    
    # 执行结果
    total_crawled = Column(Integer, default=0)  # 总爬取数量
    new_notes = Column(Integer, default=0)  # 新笔记数量
    changed_notes = Column(Integer, default=0)  # 变更笔记数量
    important_notes = Column(Integer, default=0)  # 重要笔记数量
    error_message = Column(Text, nullable=True)  # 错误信息
    
    # 时间字段
    scheduled_time = Column(DateTime, nullable=True)  # 计划执行时间（每日定时）
    started_at = Column(DateTime, nullable=True)  # 开始执行时间
    finished_at = Column(DateTime, nullable=True)  # 完成时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系映射
    owner = relationship("User", overlaps="crawl_tasks")


# 业务关键词配置表
class BusinessKeyword(Base):
    __tablename__ = "business_keywords"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    keyword = Column(String(100), nullable=False, index=True)  # 业务关键词
    category = Column(String(50), nullable=True)  # 分类
    weight = Column(Integer, default=1)  # 权重（1-10）
    is_active = Column(Boolean, default=True)  # 是否启用
    description = Column(String(200), nullable=True)  # 描述
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
