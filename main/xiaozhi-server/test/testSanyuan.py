import json
import requests


def test_sanyuan_api():
    """测试三元API接口 https://tool.wanwuweiai.com/api/chat/completions"""
    # 使用指定的URL
    url = "https://tool.wanwuweiai.com/api/chat/completions"

    # 构造请求参数
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "你谁啊"
            }
        ],
        "stream": False,
        "thinking": {
            "type": "disabled"
        }
    }

    # 注意：有些API可能需要API密钥认证
    api_key = "your_api_key_here"  # 请替换为实际的API密钥

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # 如果提供了API密钥，则添加到请求头
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        print(f"发送请求到: {url}")
        print(f"请求方式: POST")
        print(f"请求头: {json.dumps(headers, ensure_ascii=False, indent=2)}")
        print(f"请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        # 发送POST请求
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
            allow_redirects=True
        )

        print(f"最终请求URL: {response.url}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {json.dumps(dict(response.headers), ensure_ascii=False, indent=2)}")

        if response.status_code == 200:
            try:
                result = response.json()
                print(f"响应成功! 结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return result
            except json.JSONDecodeError:
                print(f"响应不是有效的JSON格式: {response.text}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"请求发生异常: {e}")

    return None


if __name__ == "__main__":
    test_sanyuan_api()