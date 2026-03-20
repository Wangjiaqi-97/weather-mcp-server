#!/usr/bin/env python3
"""天气查询 MCP 服务器 (Open-Meteo 免 Key 版)"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, Any
from hello_agents.protocols import MCPServer

# 1. 创建 MCP 服务器
weather_server = MCPServer(name="weather-server", description="全球实时天气查询服务")

# 城市对应经纬度 (Open-Meteo 需要坐标)
CITY_COORDS = {
    "北京": {"lat": 39.90, "lon": 116.40},
    "上海": {"lat": 31.23, "lon": 121.47},
    "广州": {"lat": 23.13, "lon": 113.27},
    "深圳": {"lat": 22.54, "lon": 114.06},
    "杭州": {"lat": 30.27, "lon": 120.15},
    "成都": {"lat": 30.57, "lon": 104.06},
    "重庆": {"lat": 29.56, "lon": 106.55},
    "武汉": {"lat": 30.59, "lon": 114.30},
    "西安": {"lat": 34.34, "lon": 108.94},
    "南京": {"lat": 32.06, "lon": 118.80},
    "天津": {"lat": 39.08, "lon": 117.20},
    "苏州": {"lat": 31.30, "lon": 120.58}
}

# 2. 调用 Open-Meteo API
def get_weather_data(city: str) -> Dict[str, Any]:
    """从 Open-Meteo 获取真实天气数据 (无需 API Key)"""
    coords = CITY_COORDS.get(city)
    if not coords:
        raise ValueError(f"暂不支持城市: {city}")

    # 构建请求 URL
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current_weather": "true",
        "timezone": "Asia/Shanghai"
    }

    print(f"📡 正在从 Open-Meteo 请求 {city} 的真实天气...")
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    current = data.get("current_weather", {})
    if not current:
        raise ValueError("天气 API 未返回有效数据")

    # 转换天气代码为描述 (简单映射)
    code = current.get("weathercode", 0)
    condition_map = {0: "晴朗", 1: "晴间多云", 2: "多云", 3: "阴天", 45: "雾", 61: "小雨", 95: "雷阵雨"}
    condition = condition_map.get(code, "多云 (自动推断)")

    return {
        "city": city,
        "temperature": current["temperature"],
        "feels_like": current["temperature"],  # Open-Meteo 基础接口不带体感，用气温代替
        "wind_speed": current["windspeed"],
        "condition": condition,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "Open-Meteo"
    }

# 3. 工具函数封装
def get_weather(city: str) -> str:
    """获取指定城市的当前天气"""
    try:
        weather_data = get_weather_data(city)
        return json.dumps(weather_data, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "city": city}, ensure_ascii=False)

def list_supported_cities() -> str:
    """列出所有支持的中文城市"""
    result = {"cities": list(CITY_COORDS.keys()), "count": len(CITY_COORDS)}
    return json.dumps(result, ensure_ascii=False, indent=2)

# 4. 注册与运行
weather_server.add_tool(get_weather)
weather_server.add_tool(list_supported_cities)
#
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8081))
    weather_server.run(transport="sse", host="0.0.0.0", port=port)