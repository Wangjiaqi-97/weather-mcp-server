#!/usr/bin/env python3
"""天气查询 MCP 服务器"""

import json
import sys

import requests
import os
from datetime import datetime
from typing import Dict, Any
from hello_agents.protocols import MCPServer

# 创建 MCP 服务器
weather_server = MCPServer(name="weather-server", description="真实天气查询服务")

CITY_MAP = {
    "北京": "Beijing", "上海": "Shanghai", "广州": "Guangzhou",
    "深圳": "Shenzhen", "杭州": "Hangzhou", "成都": "Chengdu",
    "重庆": "Chongqing", "武汉": "Wuhan", "西安": "Xi'an",
    "南京": "Nanjing", "天津": "Tianjin", "苏州": "Suzhou"
}


def get_weather_data(city: str) -> Dict[str, Any]:
    """从 wttr.in 获取天气数据"""
    city_en = CITY_MAP.get(city, city)
    url = f"https://wttr.in/{city_en}?format=j1"

    # 增加请求头，伪装成正常的浏览器访问，防止被 API 屏蔽
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    # === 修改这里的校验逻辑 ===
    # 提取内部的真实数据字典
    inner_data = data.get("data", {})

    # 检查内层字典是否包含 current_condition
    if "current_condition" not in inner_data or len(inner_data["current_condition"]) == 0:
        import sys
        print(f"⚠️ wttr.in 异常响应: {data}", file=sys.stderr)
        raise ValueError(f"天气服务未返回 {city} 的实时数据，可能触发了限流。")

    # === 下面的提取逻辑也要跟着改，使用 inner_data ===
    current = inner_data["current_condition"][0]

    return {
        "city": city,
        "temperature": float(current["temp_C"]),
        "feels_like": float(current["FeelsLikeC"]),
        "humidity": int(current["humidity"]),
        "condition": current["weatherDesc"][0]["value"],
        "wind_speed": round(float(current["windspeedKmph"]) / 3.6, 1),
        "visibility": float(current["visibility"]),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# 定义工具函数
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
        "name": "Weather MCP Server",
        "version": "1.0.0",
        "tools": ["get_weather", "list_supported_cities", "get_server_info"]
    }
    return json.dumps(info, ensure_ascii=False, indent=2)


# 注册工具到服务器
weather_server.add_tool(get_weather)
weather_server.add_tool(list_supported_cities)
weather_server.add_tool(get_server_info)


if __name__ == "__main__":
    # Smithery requires HTTP transport on PORT environment variable
    port = int(os.getenv("PORT", 8081))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"🌤️  Starting Weather MCP Server...")
    print(f"📡 Transport: HTTP")
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔗 Endpoint: http://{host}:{port}/mcp")
    print(f"✨ Ready to serve weather data!")
    #
    # Run with HTTP transport (required by Smithery)
    weather_server.run(transport="sse", host=host, port=port)

