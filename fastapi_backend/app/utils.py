"""
工具函数模块
包含通用的实用函数
"""

import json
import secrets
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import asc, desc, and_, or_, func
from sqlalchemy.orm import Query
from sqlalchemy.sql import Select


def simple_generate_unique_route_id(route) -> str:
    """
    简单生成唯一路由ID
    """
    return f"{route.tags[0]}-{route.name}" if route.tags else route.name


def parse_filters(filters_json: str) -> List[Dict[str, Any]]:
    """
    解析前端传来的筛选参数 JSON 字符串
    
    格式：[{"id":"is_changed","value":"true","variant":"boolean","operator":"eq","filterId":"6ueimOD9"}]
    """
    try:
        filters = json.loads(filters_json)
        if not isinstance(filters, list):
            return []
        return filters
    except (json.JSONDecodeError, TypeError):
        return []


def parse_sort(sort_json: str) -> List[Dict[str, Any]]:
    """
    解析前端传来的排序参数 JSON 字符串
    
    格式：[{"id":"is_changed","desc":true}]
    """
    try:
        sort_list = json.loads(sort_json)
        if not isinstance(sort_list, list):
            return []
        return sort_list
    except (json.JSONDecodeError, TypeError):
        return []


def apply_filters_to_query(query: Union[Query, Select], filters: List[Dict[str, Any]], model_class) -> Union[Query, Select]:
    """
    将筛选条件应用到 SQLAlchemy 查询中
    
    Args:
        query: SQLAlchemy 查询对象
        filters: 筛选条件列表
        model_class: 数据模型类
        
    Returns:
        应用了筛选条件的查询对象
    """
    if not filters:
        return query
        
    conditions = []
    
    for filter_item in filters:
        field_name = filter_item.get("id")
        value = filter_item.get("value")
        operator = filter_item.get("operator", "eq")
        variant = filter_item.get("variant", "text")
        
        if not field_name or not hasattr(model_class, field_name):
            continue
            
        field = getattr(model_class, field_name)
        
        # 根据操作符构建条件
        if operator == "eq":
            if variant == "boolean":
                conditions.append(field == (value == "true" if isinstance(value, str) else bool(value)))
            else:
                conditions.append(field == value)
        elif operator == "ne":
            if variant == "boolean":
                conditions.append(field != (value == "true" if isinstance(value, str) else bool(value)))
            else:
                conditions.append(field != value)
        elif operator == "iLike":
            if isinstance(value, str):
                conditions.append(field.ilike(f"%{value}%"))
        elif operator == "notILike":
            if isinstance(value, str):
                conditions.append(~field.ilike(f"%{value}%"))
        elif operator == "gt":
            conditions.append(field > value)
        elif operator == "gte":
            conditions.append(field >= value)
        elif operator == "lt":
            conditions.append(field < value)
        elif operator == "lte":
            conditions.append(field <= value)
        elif operator == "isEmpty":
            conditions.append(or_(field.is_(None), field == ""))
        elif operator == "isNotEmpty":
            conditions.append(and_(field.is_not(None), field != ""))
        elif operator == "inArray":
            if isinstance(value, list):
                conditions.append(field.in_(value))
        elif operator == "notInArray":
            if isinstance(value, list):
                conditions.append(~field.in_(value))
    
    if conditions:
        query = query.filter(and_(*conditions))
    
    return query


def apply_sorting_to_query(query: Union[Query, Select], sort_list: List[Dict[str, Any]], model_class) -> Union[Query, Select]:
    """
    将排序条件应用到 SQLAlchemy 查询中
    
    Args:
        query: SQLAlchemy 查询对象  
        sort_list: 排序条件列表
        model_class: 数据模型类
        
    Returns:
        应用了排序条件的查询对象
    """
    if not sort_list:
        return query
        
    order_clauses = []
    
    for sort_item in sort_list:
        field_name = sort_item.get("id")
        is_desc = sort_item.get("desc", False)
        
        if not field_name or not hasattr(model_class, field_name):
            continue
            
        field = getattr(model_class, field_name)
        
        if is_desc:
            order_clauses.append(desc(field))
        else:
            order_clauses.append(asc(field))
    
    if order_clauses:
        query = query.order_by(*order_clauses)
    
    return query
