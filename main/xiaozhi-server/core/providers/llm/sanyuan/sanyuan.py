import json
import requests
from config.logger import setup_logging, create_connection_logger
from core.providers.llm.base import LLMProviderBase
from core.utils.util import check_model_key

TAG = __name__
logger = setup_logging()

# 测试日志
logger.bind(tag=TAG).info("SanyuanLLM provider initialized")
logger.bind(tag=TAG).debug("This is a debug message")
logger.bind(tag=TAG).warning("This is a warning message")
logger.bind(tag=TAG).error("This is an error message")

# 检查日志级别
logger.bind(tag=TAG).info(f"Current log level: {logger._core.min_level}")

# 使用create_connection_logger测试# 测试连接logger
connection_logger = create_connection_logger("test_module")
connection_logger.bind(tag=TAG).info("Test connection logger")


# 简单的测试函数，用于验证模块是否被加载
def test_module_loading():
    logger.bind(tag=TAG).info("Test function called - module is loaded")
    return "Module loaded successfully"


# 如果直接运行此模块，执行测试
if __name__ == "__main__":
    logger.bind(tag=TAG).info("Running sanyuan.py directly")
    test_module_loading()

class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        logger.bind(tag=TAG).info("Initializing LLMProvider with config: {}".format(json.dumps(config, ensure_ascii=False)))
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://tool.wanwuweiai.com/api/chat/completions").rstrip("/")
        #self.model_name = config.get("model_name", "default")
        
        logger.bind(tag=TAG).info(f"Base URL: {self.base_url}")
        
        # 设置默认参数
        param_defaults = {
            "max_tokens": (500, int),
            "temperature": (0.7, lambda x: round(float(x), 1)),
            "top_p": (1.0, lambda x: round(float(x), 1)),
        }

        for param, (default, converter) in param_defaults.items():
            value = config.get(param)
            try:
                setattr(
                    self,
                    param,
                    converter(value) if value not in (None, "") else default,
                )
            except (ValueError, TypeError):
                setattr(self, param, default)

        model_key_msg = check_model_key("SanyuanLLM", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)

    def response(self, session_id, dialogue, conn, **kwargs):
        logger.bind(tag=TAG).info(f"response method called with session_id: {session_id}")
        #logger.bind(tag=TAG).info(f"dialogue: {json.dumps(dialogue, ensure_ascii=False)}, conn: {json.dumps(conn, ensure_ascii=False)}")
        try:
            logger.bind(tag=TAG).info(f"dialogue: {json.dumps(dialogue, ensure_ascii=False)}")
            # 过滤对话，只保留最新的user角色消息
            filtered_dialogue = []
            # 逆序查找最后一条用户消息
            for msg in reversed(dialogue):
                if msg.get("role") == "user":
                    filtered_dialogue.append(msg)
                    logger.bind(tag=TAG).info(f"Found latest user message: {json.dumps(msg, ensure_ascii=False)}")
                    break  # 只取最新的一条用户消息
            if not filtered_dialogue:
                logger.bind(tag=TAG).warning("No user messages found in dialogue")
            
            # 构建请求参数
            device_id = conn.device_id;
            logger.bind(tag=TAG).info(f"device_id: {device_id}")
            logger.bind(tag=TAG).info(f"conn object type: {type(conn)}")

            request_json = {
                "messages": filtered_dialogue,
                "stream": True,
                "thinking": {
                    "type": "disabled"
                },
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p),
                "device_id": device_id,
            }

            # 打印请求日志
            logger.bind(tag=TAG).info(f"SanyuanLLM request: {json.dumps(request_json, ensure_ascii=False)}")
            logger.bind(tag=TAG).info(f"Request URL: {self.base_url}")

            headers = {
                "Content-Type": "application/json",
                "device_id": device_id,
            }
            # 打印header
            logger.bind(tag=TAG).info(f"SanyuanLLM request header: {json.dumps(headers, ensure_ascii=False)}")

            # 如果提供了api_key，则添加到请求头
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # 发起流式请求
            try:
                with requests.post(
                    self.base_url,
                    headers=headers,
                    json=request_json,
                    stream=True,
                ) as r:
                    for line in r.iter_lines():
                        logger.bind(tag=TAG).info(f"Received line: {line}")
                        if not line:
                            logger.bind(tag=TAG).info("Empty line received, skipping")
                            continue
                        try:
                            if line.startswith(b"data: "):
                                logger.bind(tag=TAG).info("Line starts with 'data: ', removing prefix")
                                line = line[6:]
                            if line == b"[DONE]":
                                logger.bind(tag=TAG).info("Received [DONE] signal, breaking loop")
                                break

                            chunk = json.loads(line)
                            logger.bind(tag=TAG).info(f"Parsed chunk: {json.dumps(chunk, ensure_ascii=False)}")
                        except json.JSONDecodeError as e:
                            logger.bind(tag=TAG).error(f"JSON decode error: {str(e)}")
                            continue
                        if "choices" in chunk and chunk["choices"]:
                            choice = chunk["choices"][0]
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")
                            logger.bind(tag=TAG).info(f"sanyuan response: {content}")
                            if content:        # 有内容就先 yield
                                yield content

                            if choice.get("finish_reason"):   # 内容发完再判断结束
                                logger.bind(tag=TAG).info(f"finish_reason: {choice['finish_reason']}, stream ended")
                                break
            except requests.exceptions.RequestException as e:
                logger.bind(tag=TAG).error(f"Request failed: {e}")
                yield "【三元服务请求异常】"

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in response generation: {e}")
            import traceback
            logger.bind(tag=TAG).error(f"Traceback: {traceback.format_exc()}")
            yield "【三元服务响应异常】"

    def response_with_functions(self, session_id, dialogue, conn, functions=None, **kwargs):
        try:
            # 过滤对话，只保留最新的user角色消息
            filtered_dialogue = []
            # 逆序查找最后一条用户消息
            for msg in reversed(dialogue):
                if msg.get("role") == "user":
                    filtered_dialogue.append(msg)
                    break  # 只取最新的一条用户消息
            
            # 打印请求日志
            logger.bind(tag=TAG).info(f"kwargs: {json.dumps(kwargs, ensure_ascii=False)}")

            # 构建请求参数
            device_id = conn.device_id
            logger.bind(tag=TAG).info(f"device_id: {device_id}")

            request_json = {
                "messages": filtered_dialogue,
                "stream": True,
                "thinking": {
                    "type": "disabled"
                },
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "device_id": device_id,
            }

            # 打印请求日志
            logger.bind(tag=TAG).info(f"SanyuanLLM function call request: {json.dumps(request_json, ensure_ascii=False)}")

            # 添加函数信息
            if functions:
                request_json["tools"] = functions
                request_json["tool_choice"] = "auto"

            headers = {
                "Content-Type": "application/json",
                "device_id": device_id,
            }

            # 如果提供了api_key，则添加到请求头
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # 发起流式请求
            with requests.post(
                self.base_url,
                headers=headers,
                json=request_json,
                stream=True,
            ) as r:
                last_tool_calls = None
                for line in r.iter_lines():
                    if line:
                        try:
                            # 记录接收到的原始行
                            logger.bind(tag=TAG).info(f"Received line in function call: {line}")
                            # 移除前缀 "data: "
                            if line.startswith(b"data: "):
                                line = line[6:]
                                logger.bind(tag=TAG).info(f"Processed line in function call: {line}")
                            # 检查是否为结束信号
                            if line == b"[DONE]":
                                logger.bind(tag=TAG).info("Received [DONE] signal in function call, stopping stream")
                                break
                            # 解析JSON
                            chunk = json.loads(line)
                            logger.bind(tag=TAG).info(f"Parsed chunk in function call: {chunk}")
                            # 提取内容和工具调用
                            content = ""
                            tool_calls = None
                            should_break = False
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                choice = chunk["choices"][0]
                                delta = choice.get("delta", {})
                                content = delta.get("content", "")
                                tool_calls = delta.get("tool_calls")
                                # 检查是否有finish_reason
                                if choice.get("finish_reason") == "stop":
                                    logger.bind(tag=TAG).info("Received finish_reason: stop in function call, stopping stream")
                                    should_break = True
                                # 保存最新的工具调用
                                if tool_calls is not None:
                                    last_tool_calls = tool_calls
                            else:
                                logger.bind(tag=TAG).info("No choices in chunk in function call")
                            if should_break:
                                break
                            # 打印响应日志
                            logger.bind(tag=TAG).info(f"SanyuanLLM function call response chunk: content='{content}', tool_calls={tool_calls}")
                            # 处理内容和工具调用
                            if tool_calls is not None:
                                yield content, tool_calls
                            elif content:
                                yield content, None
                        except json.JSONDecodeError as e:
                            logger.bind(tag=TAG).error(f"Error decoding JSON: {e}, line: {line}")
                        except Exception as e:
                            logger.bind(tag=TAG).error(f"Unexpected error processing line: {e}")
                # 如果最后有工具调用但没有内容，发送空内容和工具调用
                if last_tool_calls is not None:
                    yield "", last_tool_calls

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in function call streaming: {e}")
            yield "【三元服务响应异常】", None