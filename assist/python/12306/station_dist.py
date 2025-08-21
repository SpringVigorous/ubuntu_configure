
from geopy.distance import geodesic

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.extra.rate_limiter import RateLimiter
import time

def get_coordinates(location_name: str) -> tuple:
    # 1. 配置合理的超时时间（建议 10 秒）和 User-Agent
    geolocator = Nominatim(
        user_agent="my_geocoder_app/1.0",  # 自定义标识，避免被封禁
        timeout=10  # 延长超时时间
    )
    
    # 2. 使用 RateLimiter 控制请求频率（每秒最多 1 次）
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    try:
        location = geocode(location_name)
        if location:
            return location
            return (location.latitude, location.longitude)
        else:
            print(f"未找到地点：{location_name}")
            return (None, None)
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"请求失败：{e}，尝试重新连接...")
        time.sleep(5)  # 等待 5 秒后重试
        return get_coordinates(location_name)  # 递归重试
    except Exception as e:
        print(f"其他错误：{e}")
        return (None, None)

# # 示例
# if __name__ == "__main__":
#     places = ["上海虹桥站", "广州南站"]
#     for place in places:
#         lat, lng = get_coordinates(place)
#         if lat and lng:
#             print(f"{place} 经纬度：({lat:.6f}, {lng:.6f})")


# 地理编码
# geolocator = Nominatim(user_agent="geoapi")
location1 = get_coordinates("上海虹桥站")
location2 = get_coordinates("广州南站")

# 计算距离（默认单位：千米）
distance = geodesic(
    (location1.latitude, location1.longitude),
    (location2.latitude, location2.longitude)
).km
print(f"直线距离：{distance:.2f} 公里")