from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple


class Station:
    """站点信息类，包含站点名称、到站时间和发车时间"""
    def __init__(self, name: str, arrival_time: Optional[str], departure_time: Optional[str]):
        """
        初始化站点信息
        :param name: 站点名称
        :param arrival_time: 到站时间，格式"HH:MM"，首站为None
        :param departure_time: 发车时间，格式"HH:MM"，终点站为None
        """
        self.name = name
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        
    def __repr__(self) -> str:
        return f"{self.name} (到达: {self.arrival_time or '起点'}, 发车: {self.departure_time or '终点'})"


class Train:
    """列车信息类，包含车次和途经站点列表"""
    def __init__(self, train_no: str, stations: List[Station]):
        """
        初始化列车信息
        :param train_no: 车次编号
        :param stations: 途经站点列表
        """
        self.train_no = train_no
        self.stations = stations
        
    def get_station_index(self, station_name: str) -> int:
        """获取站点在列车路线中的索引位置"""
        for idx, station in enumerate(self.stations):
            if station.name == station_name:
                return idx
        return -1
        
    def has_station(self, station_name: str) -> bool:
        """判断列车是否经过指定站点"""
        return self.get_station_index(station_name) != -1
        
    def __repr__(self) -> str:
        return f"车次 {self.train_no}: {[s.name for s in self.stations]}"


class RouteSegment:
    """路线段类，表示某一车次从某站到某站的行程"""
    def __init__(self, train: Train, start_station: str, end_station: str):
        """
        初始化路线段
        :param train: 列车信息
        :param start_station: 出发站
        :param end_station: 到达站
        """
        self.train = train
        self.start_station = start_station
        self.end_station = end_station
        
        start_idx = train.get_station_index(start_station)
        end_idx = train.get_station_index(end_station)
        
        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            raise ValueError(f"列车 {train.train_no} 无法从 {start_station} 到达 {end_station}")
            
        self.departure_time = train.stations[start_idx].departure_time
        self.arrival_time = train.stations[end_idx].arrival_time
        
    def __repr__(self) -> str:
        return f"{self.train.train_no}: {self.start_station} {self.departure_time} -> {self.end_station} {self.arrival_time}"


class Route:
    """完整路线类，由一个或多个路线段组成"""
    def __init__(self, segments: List[RouteSegment]):
        """
        初始化完整路线
        :param segments: 路线段列表
        """
        self.segments = segments
        self.start_station = segments[0].start_station
        self.end_station = segments[-1].end_station
        
    def get_total_duration(self) -> timedelta:
        """计算总行程时间"""
        start_time = datetime.strptime(self.segments[0].departure_time, "%H:%M")
        end_time = datetime.strptime(self.segments[-1].arrival_time, "%H:%M")
        
        # 处理跨天情况
        if end_time < start_time:
            end_time += timedelta(days=1)
            
        return end_time - start_time
        
    def get_transfer_info(self) -> List[Tuple[str, str, str]]:
        """获取换乘信息：(换乘站, 到达时间, 出发时间)"""
        transfers = []
        for i in range(len(self.segments) - 1):
            arrival_segment = self.segments[i]
            departure_segment = self.segments[i+1]
            transfers.append((
                arrival_segment.end_station,
                arrival_segment.arrival_time,
                departure_segment.departure_time
            ))
        return transfers
        
    def __repr__(self) -> str:
        transfer_count = len(self.segments) - 1
        result = (f"路线: {self.start_station} -> {self.end_station} "
                 f"(换乘 {transfer_count} 次, 总耗时: {self.get_total_duration()})\n")
        
        for i, seg in enumerate(self.segments):
            result += f"  第{i+1}段: {seg}\n"
            
        return result


class TrainRouteFinder:
    """列车路线查找器"""
    def __init__(self, trains: List[Train], city_stations: Dict[str, List[str]] = None):
        """
        初始化路线查找器
        :param trains: 列车列表
        :param city_stations: 城市与所属站点的映射，用于判断同城不同站
        """
        self.trains = trains
        # 默认城市站点映射，可根据实际情况扩展
        self.city_stations = city_stations or {
            "北京": ["北京站", "北京西站", "北京南站", "北京北站"],
            "上海": ["上海站", "上海虹桥站", "上海南站"],
            "广州": ["广州站", "广州南站", "广州东站"],
            "武汉": ["武汉站", "武昌站", "汉口站"]
        }
        
    def _parse_time(self, time_str: str) -> datetime:
        """将时间字符串转换为datetime对象"""
        return datetime.strptime(time_str, "%H:%M")
        
    def _is_same_city(self, station1: str, station2: str) -> bool:
        """判断两个站点是否属于同一城市"""
        for city, stations in self.city_stations.items():
            if station1 in stations and station2 in stations:
                return True
        return False
        
    def _is_valid_transfer(self, arrival_time: str, departure_time: str, 
                          arrival_station: str, departure_station: str) -> bool:
        """
        判断换乘是否有效
        :param arrival_time: 到达换乘站时间
        :param departure_time: 从换乘站出发时间
        :param arrival_station: 到达的换乘站
        :param departure_station: 出发的换乘站
        :return: 是否有效
        """
        # 解析时间
        arr_time = self._parse_time(arrival_time)
        dep_time = self._parse_time(departure_time)
        
        # 处理跨天情况
        if dep_time < arr_time:
            dep_time += timedelta(days=1)
            
        # 计算时间差（分钟）
        time_diff = (dep_time - arr_time).total_seconds() / 60
        
        # 同一站点换乘
        if arrival_station == departure_station:
            return 20 < time_diff < 120  # 20分钟到2小时之间
            
        # 同一城市不同站点换乘
        elif self._is_same_city(arrival_station, departure_station):
            return 60 < time_diff < 120  # 1小时到2小时之间
            
        # 不同城市，无法换乘
        return False
    
    def find_direct_routes(self, start_station: str, end_station: str) -> List[Route]:
        """查找直达路线"""
        direct_routes = []
        
        for train in self.trains:
            start_idx = train.get_station_index(start_station)
            end_idx = train.get_station_index(end_station)
            
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                try:
                    segment = RouteSegment(train, start_station, end_station)
                    direct_routes.append(Route([segment]))
                except ValueError:
                    continue
                    
        return direct_routes
    
    def find_transfer_routes(self, start_station: str, end_station: str, max_transfers: int = 2) -> List[Route]:
        """
        查找换乘路线
        :param start_station: 出发站
        :param end_station: 目的站
        :param max_transfers: 最大换乘次数
        :return: 路线列表
        """
        # 先获取直达路线
        all_routes = self.find_direct_routes(start_station, end_station)
        
        # 用于存储当前可到达的站点和到达该站点的路线
        reachable = {
            start_station: [([], None)]  # (路线段列表, 到达时间)
        }
        
        # 迭代查找换乘路线
        for _ in range(max_transfers + 1):
            new_reachable = {}
            
            # 遍历当前可到达的所有站点
            for station, routes in reachable.items():
                # 对每个到达该站点的路线
                for segments, arr_time in routes:
                    # 查找从该站点出发的所有列车
                    for train in self.trains:
                        # 检查列车是否经过当前站点
                        station_idx = train.get_station_index(station)
                        if station_idx == -1:
                            continue
                            
                        # 遍历该站点之后的所有站点
                        for next_idx in range(station_idx + 1, len(train.stations)):
                            next_station = train.stations[next_idx].name
                            # 到达终点站则添加完整路线
                            if next_station == end_station:
                                try:
                                    new_segment = RouteSegment(train, station, next_station)
                                    # 检查换乘时间是否有效（如果不是第一条路线）
                                    if segments:
                                        last_segment = segments[-1]
                                        if not self._is_valid_transfer(
                                            last_segment.arrival_time,
                                            new_segment.departure_time,
                                            last_segment.end_station,
                                            new_segment.start_station
                                        ):
                                            continue
                                    
                                    new_segments = segments + [new_segment]
                                    new_route = Route(new_segments)
                                    all_routes.append(new_route)
                                except ValueError:
                                    continue
                            
                            # 不是终点站则添加到可达站点
                            else:
                                try:
                                    new_segment = RouteSegment(train, station, next_station)
                                    # 检查换乘时间是否有效（如果不是第一条路线）
                                    if segments:
                                        last_segment = segments[-1]
                                        if not self._is_valid_transfer(
                                            last_segment.arrival_time,
                                            new_segment.departure_time,
                                            last_segment.end_station,
                                            new_segment.start_station
                                        ):
                                            continue
                                    
                                    # 添加到新的可达站点记录
                                    new_segments = segments + [new_segment]
                                    arrival_time = new_segment.arrival_time
                                    
                                    if next_station not in new_reachable:
                                        new_reachable[next_station] = []
                                    new_reachable[next_station].append((new_segments, arrival_time))
                                except ValueError:
                                    continue
            
            # 更新可达站点
            reachable = new_reachable
            if not reachable:
                break
        
        # 去重并按总耗时排序
        unique_routes = []
        seen = set()
        for route in all_routes:
            route_key = tuple((seg.train.train_no, seg.start_station, seg.end_station) for seg in route.segments)
            if route_key not in seen:
                seen.add(route_key)
                unique_routes.append(route)
        
        return sorted(unique_routes, key=lambda x: x.get_total_duration())


# 示例用法
def example_usage():
    # 创建站点
    beijing_west = Station("北京西站", None, "08:00")
    shijiazhuang = Station("石家庄站", "09:30", "09:35")
    zhengzhou = Station("郑州站", "12:00", "12:05")
    wuhan = Station("武汉站", "15:30", "15:35")
    changsha = Station("长沙站", "18:00", "18:05")
    guangzhou = Station("广州站", "22:00", None)
    
    # 创建列车1：北京西 -> 广州
    train1 = Train("G101", [beijing_west, shijiazhuang, zhengzhou, wuhan, changsha, guangzhou])
    
    # 创建列车2：北京西 -> 郑州
    beijing_west2 = Station("北京西站", None, "07:00")
    shijiazhuang2 = Station("石家庄站", "08:30", "08:35")
    zhengzhou2 = Station("郑州站", "11:00", None)
    train2 = Train("G103", [beijing_west2, shijiazhuang2, zhengzhou2])
    
    # 创建列车3：郑州 -> 广州
    zhengzhou3 = Station("郑州站", None, "12:30")
    wuhan3 = Station("武汉站", "15:00", "15:05")
    changsha3 = Station("长沙站", "17:30", "17:35")
    guangzhou3 = Station("广州站", "21:30", None)
    train3 = Train("G105", [zhengzhou3, wuhan3, changsha3, guangzhou3])
    
    # 创建列车4：武汉 -> 广州
    wuhan4 = Station("武汉站", None, "16:00")
    changsha4 = Station("长沙站", "18:30", "18:35")
    guangzhou4 = Station("广州站", "22:30", None)
    train4 = Train("G107", [wuhan4, changsha4, guangzhou4])
    
    # 创建路线查找器
    finder = TrainRouteFinder([train1, train2, train3, train4])
    
    # 查找从北京西站到广州站的所有路线（最多换乘2次）
    routes = finder.find_transfer_routes("北京西站", "广州站", max_transfers=2)
    
    # 打印结果
    print(f"找到 {len(routes)} 条从北京西站到广州站的路线：\n")
    for i, route in enumerate(routes, 1):
        print(f"路线 {i}:")
        print(route)
        if i < len(routes):
            print("-" * 80)


if __name__ == "__main__":
    example_usage()
    