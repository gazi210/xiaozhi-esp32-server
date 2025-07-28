from plugins_func.register import register_function, ToolType, ActionResponse, Action

start_english_practise_desc = {
    "type": "function",
    "function": {
        "name": "start_english_practise",
        "description": "开始英语练习会话",
        "parameters": {
            "type": "object",
            "properties": {
                "MacAddress": {
                    "type": "string",
                    "description": "设备的Mac地址"
                },
                "AgentId": {
                    "type": "string",
                    "description": "Agent ID"
                },
                "params": {
                    "type": "string",
                    "description": "对话内容"
                }
            },
            "required": ["MacAddress", "AgentId", "params"]
        }
    }
}

@register_function("start_english_practise", start_english_practise_desc, ToolType.WAIT)
def start_english_practise(MacAddress: str, AgentId: str, params: str):
    """
    开始英语练习的处理器函数
    """
    # 这里可以添加英语练习的具体逻辑
    response_text = f"英语练习已启动。设备Mac: {MacAddress}, 代理ID: {AgentId}, 参数: {params}"
    return ActionResponse(Action.REQLLM, response_text, None)