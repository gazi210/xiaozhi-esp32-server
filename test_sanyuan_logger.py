import sys
import os
import logging

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'main', 'xiaozhi-server'))

# 尝试直接配置loguru日志
try:
    from loguru import logger
    logger.remove()  # 移除默认处理器
    logger.add(sys.stdout, level="INFO")  # 添加标准输出处理器
    print("Loguru配置成功")
    logger.info("这是直接配置的info日志")
    logger.debug("这是直接配置的debug日志")
    logger.warning("这是直接配置的warning日志")
    logger.error("这是直接配置的error日志")
except ImportError:
    print("Loguru未安装")

# 尝试导入项目中的logger
try:
    from config.logger import setup_logging
    logger = setup_logging()
    print("项目日志配置成功")
    logger.info("这是项目配置的info日志")
    logger.debug("这是项目配置的debug日志")
    logger.warning("这是项目配置的warning日志")
    logger.error("这是项目配置的error日志")
except Exception as e:
    print(f"项目日志配置失败: {e}")

print("测试完成，请检查日志输出")