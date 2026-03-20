#!/usr/bin/env python3
"""天气查询 MCP 服务器 (模拟数据版)"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from hello_agents.protocols import MCPServer

# 1. 创建 MCP 服务器
weather_server = MCPServer(name="weather-server", description="真实天气查询服务")

CITY_MAP = {
    "北京": "Beijing", "上海": "Shanghai", "广州": "Guangzhou",
    "深圳": "Shenzhen", "杭州": "Hangzhou", "成都": "Chengdu",
    "重庆": "Chongqing", "武汉": "Wuhan", "西安": "Xi'an",
    "南京": "Nanjing", "天津": "Tianjin", "苏州": "Suzhou"
}


# 2. 核心修改区：直接返回完美的假数据
def get_weather_data(city: str) -> Dict[str, Any]:
    """模拟获取天气数据，永远返回成功"""

    # 甚至可以为了逼真一点，根据城市名字给一点不同的温度
    base_temp = 25.0
    if city == "北京":
        base_temp = 22.5
    elif city == "广州" or city == "深圳":
        base_temp = 30.0

    print(f"☁️ 正在为大模型生成 {city} 的模拟天气数据...")

    return {
        "city": city,
        "temperature": base_temp,
        "feels_like": base_temp + 1.5,
        "humidity": 45,
        "condition": "晴朗无云 (测试数据)",
        "wind_speed": 12.5,
        "visibility": 10.0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# 3. 定义工具函数
def get_weather(city: str) -> str:
    """获取指定城市的当前天气"""
    try:
        weather_data = get_weather_data(city)
        return json.dumps(weather_data, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "city": city}, ensure_ascii=False)


def list_supported_cities() -> str:
    """列出所有支持的中文城市"""
    result = {"cities": list(CITY_MAP.keys()), "count": len(CITY_MAP)}
    return json.dumps(result, ensure_ascii=False, indent=2)


def get_server_info() -> str:
    """获取服务器信息"""
    info = {
        "name": "Weather MCP Server (Mocked)",
        "version": "1.0.0",
        "tools": ["get_weather", "list_supported_cities", "get_server_info"]
    }
    return json.dumps(info, ensure_ascii=False, indent=2)


# 4. 注册工具到服务器
weather_server.add_tool(get_weather)
weather_server.add_tool(list_supported_cities)
weather_server.add_tool(get_server_info)

# 5. 启动服务器 (使用坚如磐石的 SSE 模式)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8081))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"🌤️  Starting Weather MCP Server (Mock Mode)...")
    print(f"📡 Transport: SSE")
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔗 Endpoint: http://{host}:{port}/sse")
    print(f"✨ Ready to serve perfect weather data!")

    # 严格使用 sse 协议
    weather_server.run(transport="sse", host=host, port=port)