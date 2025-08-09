from plugins_func.register import register_function, ToolType, ActionResponse, Action
from config.logger import setup_logging

logger = setup_logging()

start_english_practise_desc = {
    "type": "function",
    "function": {
        "name": "start_english_practise",
        "description": "开始英语练习会话",
        "parameters": {
            "type": "object",
            "properties": {
                "AgentId": {
                    "type": "string",
                    "description": "Agent ID"
                },
                "params": {
                    "type": "string",
                    "description": "对话内容"
                }
            },
            "required": ["AgentId", "params"]
        }
    }
}

# @register_function("start_english_practise", start_english_practise_desc, ToolType.WAIT)
# def start_english_practise(MacAddress: str, AgentId: str, params: str):
#     """
#     开始英语练习的处理器函数
#     """
#     # 打印日志
#     logger.debug(f"启动英语练习 - 设备Mac: {MacAddress}, 代理ID: {AgentId}, 参数: {params}")
    
#     # 这里可以添加英语练习的具体逻辑
#     response_text = f"英语练习已启动。设备Mac: {MacAddress}, 代理ID: {AgentId}, 参数: {params}"
#     return ActionResponse(Action.REQLLM, response_text, None)


@register_function("start_english_practise", start_english_practise_desc, ToolType.SYSTEM_CTL)
def start_english_practise(conn, AgentId: str='456', params: str='789'):
    """
    开始英语练习的处理器函数
    """
    macAddress = conn.device_id
    # 打印日志
    logger.info(f"启动英语练习 - 设备Mac: {macAddress}, 代理ID: {AgentId}, 参数: {params}")
    
    # 这里可以添加英语练习的具体逻辑
    response_text = f"启动英语练习 - 设备Mac: {macAddress}, 代理ID: {AgentId}, 参数: {params}"
    return ActionResponse(Action.REQLLM, response_text, None)