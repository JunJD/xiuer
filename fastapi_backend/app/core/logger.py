"""
Logger 配置
"""

import logging
import sys
from typing import Any

# 配置基础日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("fastapi_app")

class Logger:
    """Logger wrapper"""
    
    @staticmethod
    def info(message: str, *args: Any) -> None:
        logger.info(message, *args)
    
    @staticmethod
    def error(message: str, *args: Any) -> None:
        logger.error(message, *args)
    
    @staticmethod
    def warning(message: str, *args: Any) -> None:
        logger.warning(message, *args)
    
    @staticmethod
    def debug(message: str, *args: Any) -> None:
        logger.debug(message, *args)

# 导出logger实例
logger = Logger() 