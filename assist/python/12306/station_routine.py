from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from train_station import TrainStationManager
import os

import sys

from pathlib import Path


root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import exception_decorator,logger_helper,UpdateTimeType,get_consecutive_elements_info
from station_config import StationConfig



station_manager:TrainStationManager = TrainStationManager()
def _is_same_city( station1: str, station2: str) -> bool:
        return station_manager.is_same_city(station1, station2)
    
    
def _parse_time(time_str: str) -> datetime:
    if time_str is None: 
        return None
    time_str=str(time_str)
    count=time_str.count(':')
    try:
        return datetime.strptime(time_str, "%H:%M" if count==1 else "%H:%M:%S")
    except :
        pass
    
    
def time_format(dt:datetime)->str:
    
    return dt.strftime("%H:%M")
# ---------------------------
# 数据模型定义（与之前一致）
# ---------------------------
class Station:
    def __init__(self, name: str, arrival_time: Optional[str], departure_time: Optional[str]):
        self.name = name            
            
        self.arrival_time = _parse_time(arrival_time)
        self.departure_time = _parse_time(departure_time)
        
        if not self.arrival_time:
            self.arrival_time=self.departure_time
        if not self.departure_time:
            self.departure_time=self.arrival_time
        
    @property
    def diff_day(self):
         return RouteSegment.diff_day_by_times(self.arrival_time, self.departure_time)
    def __repr__(self) -> str:
        return f"{self.name} (到达: {self.arrival_time or '起点'}, 发车: {self.departure_time or '终点'})"


class Train:
    def __init__(self, train_no: str, stations: List[Station]):
        self.train_no = train_no
        self.stations = stations
        
    def get_station_index(self, station_name: str) -> int:
        for idx, station in enumerate(self.stations):
            #模糊查找
            if _is_same_city(station.name, station_name):
                return idx
        return -1
    def get_station_by_index(self,index:int)->Station:
        if index>-1 and index <len(self.stations):        
            return self.stations[index]
    def has_station(self, station_name: str) -> bool:
        return self.get_station_index(station_name) != -1
        
    def __repr__(self) -> str:
        return f"车次 {self.train_no}: {[s.name for s in self.stations]}"


class RouteSegment:
    def __init__(self, train: Train, start_station: str, end_station: str):
        self.train = train

        start_idx = train.get_station_index(start_station)
        end_idx = train.get_station_index(end_station)
        
        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            raise ValueError(f"列车 {train.train_no} 无法从 {start_station} 到达 {end_station}")
        
        #模糊查找站点名称
        departure_station=train.stations[start_idx]
        arrival_station=train.stations[end_idx]
        self.start_station = departure_station.name
        self.end_station = arrival_station.name
            
        self.departure_time = departure_station.departure_time
        self.arrival_time =arrival_station.arrival_time
        
    @property
    def diff_day(self)->int:
        
        start_idx = self.train.get_station_index(self.start_station)
        end_idx = self.train.get_station_index(self.end_station)
        
        
        cur_stations=self.train.stations[start_idx:end_idx+1]
        
        days=[station.diff_day for station in cur_stations]
        for i in range(1,len(cur_stations)):
            cur_start_station=cur_stations[i-1]
            cur_end_station=cur_stations[i]
            
            days.append(RouteSegment.diff_day_by_times(cur_start_station.arrival_time,cur_end_station.departure_time))
        
        return sum(days)
        
    @staticmethod
    def diff_day_by_times(start_time:datetime,end_time:datetime)->int:
        try:
            return 1 if  end_time < start_time else 0
        except:
            return 0
        
    @staticmethod
    def diff_times(start_time:datetime,end_time:datetime)->timedelta:
        from copy import deepcopy
        end_time_copy=deepcopy(end_time)
        day=RouteSegment.diff_day_by_times(start_time,end_time)
        if day>0:
            end_time_copy+=timedelta(days=day)
        
        return end_time_copy-start_time
    
    @property
    def departure_time_str(self):
        return time_format(self.departure_time)
    
    @property
    def arrival_time_str(self):
        return time_format(self.arrival_time)
    
    
    def __repr__(self) -> str:
        return f"{self.train.train_no}: {self.start_station} {self.departure_time_str} -> {self.end_station} {self.arrival_time_str}"





class Route:
    def __init__(self, segments: List[RouteSegment]):
        self.segments = segments
        self.start_station = segments[0].start_station
        self.end_station = segments[-1].end_station
        
    def arrage(self):
        seg_names= [seg.train.train_no for seg in self.segments]
        lst=get_consecutive_elements_info(seg_names)
        if all( len(item[1])==1 for item in lst):
            return
        result=[]
        for _,index in lst:
            seg:RouteSegment=self.segments[index[0]]
            if len(index)==1:
                result.append(seg)
            else:
                dest_seg=self.segments[index[-1]]
                result.append(RouteSegment(seg.train,seg.start_station,dest_seg.end_station))

        self.segments=result


    def wait_time(self,index:int)->timedelta:
        seg_count=len(self.segments)
        if seg_count==0 or index+1>=seg_count:
            return timedelta()
        

        if index>-1:
            return RouteSegment.diff_times(self.segments[index].arrival_time ,self.segments[index+1].departure_time)
        else:
            result=timedelta()
            for i in range(len(self.segments)-1):
                result+=self.wait_time(i)
            return result
        
    def wait_total_time(self)->timedelta:
        return self.wait_time(-1)
    def get_total_duration(self) -> timedelta:
        start_time =self.segments[0].departure_time
        end_time = self.segments[-1].arrival_time
        
        lst=[seg.diff_day for seg in self.segments]
        for i in range(1,len(self.segments)):
            pre_time=self.segments[i-1].arrival_time
            next_time=self.segments[i].departure_time
            
            
            lst.append(RouteSegment.diff_day_by_times(pre_time,next_time))
            
        days=sum(lst)
        if days>0:
            end_time+=timedelta(days=days)
        
        return end_time - start_time
        
    def get_transfer_info(self) -> List[Tuple[str, str, str]]:
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
        
        stations=[[segment.start_station,segment.end_station] for segment in self.segments]
        
        station_str=" -> ".join(stations[0]) 
        pre_station=stations[0][-1]
        
        from io import StringIO
        buffer = StringIO()
        buffer.write(" -> ".join(stations[0]))  # 写入缓冲区，无临时变量
        for i in range(1,len(stations)):
            cur_item=stations[i]
            this_station=cur_item[0]
            if pre_station!=this_station:
                buffer.write(f"/{this_station}")
                
            buffer.write(f" -> {cur_item[-1]}")
            
        
        
        route_station_str = buffer.getvalue()  # 获取最终字符串
        result = (f"路线: {route_station_str},耗时: {self.get_total_duration()}"
                 f"(换乘 {transfer_count} 次,总等待{self.wait_total_time()})\n")
        
        segments=self.segments
        for i, seg in enumerate(segments):
            wait_time_str= f" {'同站等待' if segments[i].end_station==segments[i+1].start_station else '异站换乘' }：{self.wait_time(i)}" if transfer_count>0 and i<transfer_count else ""
                
            result += f"  第{i+1}段: {seg}{wait_time_str}\n"
            
        return result


# ---------------------------
# 路线查找器（与之前一致）
# ---------------------------
class TrainRouteFinder:
    def __init__(self, trains: List[Train]):
        self.trains = trains


    def _is_valid_transfer(self, arrival_time: datetime, departure_time: datetime, 
                          arrival_station: str, departure_station: str) -> bool:
        arr_time = arrival_time
        dep_time = departure_time
        
        if dep_time < arr_time:
            dep_time += timedelta(days=1)
            
        time_diff = (dep_time - arr_time).total_seconds() / 60
        
        if arrival_station == departure_station:
            return 1 < time_diff < 480
            
        elif _is_same_city(arrival_station, departure_station):
            return 30 < time_diff < 480
            
        return False
    
    def find_direct_routes(self, start_station: str, end_station: str) -> List[Route]:
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
        
        logger=logger_helper("查找路线",f"{start_station}->{end_station}")
        
        all_routes = self.find_direct_routes(start_station, end_station)
        logger.info("成功",f"找到 {len(all_routes)} 条直达路线" if len(all_routes)>0 else "没有直达路线",update_time_type=UpdateTimeType.STAGE)
        reachable = {
            start_station: [([], None)]
        }
        
        for _ in range(max_transfers + 1):
            new_reachable = {}
            
            for station, routes in reachable.items():
                for segments, arr_time in routes:
                    for train in self.trains:
                        station_idx = train.get_station_index(station)
                        if station_idx == -1:
                            continue
                            
                        for next_idx in range(station_idx + 1, len(train.stations)):
                            next_station = train.stations[next_idx].name
                            if _is_same_city(next_station,end_station):
                                try:
                                    new_segment = RouteSegment(train, station, next_station)
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
                                    new_route.arrage()
                                    all_routes.append(new_route)
                                except ValueError:
                                    continue
                            
                            else:
                                try:
                                    new_segment = RouteSegment(train, station, next_station)
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
                                    arrival_time = new_segment.arrival_time
                                    
                                    if next_station not in new_reachable:
                                        new_reachable[next_station] = []
                                    new_reachable[next_station].append((new_segments, arrival_time))
                                except ValueError:
                                    continue
            
            reachable = new_reachable
            if not reachable:
                break
        
        all_routes=TrainRouteFinder.filter_routes(all_routes)
        logger.info("成功",f"一共{len(all_routes)}条线路",update_time_type=UpdateTimeType.STAGE)
        return all_routes


    @staticmethod
    def start_time_valid(start_time:datetime):
         return start_time <= _parse_time("23:00") and start_time >= _parse_time("08:00")
    
    @staticmethod
    def filter_routes(all_routes:list[Route]):
        routes = []
        seen = set()
        logger=logger_helper("过滤路线")
        for route in sorted(all_routes, key=lambda x: x.get_total_duration()):
            first_seg_start_time= route.segments[0].departure_time
            #过滤掉出发点时间不在8:00-23:00之间的路线
            
            flags=[]
            
            if not TrainRouteFinder.start_time_valid(first_seg_start_time):
                flags.append("出发时间不在8:00-23:00之间")           
            if route.get_total_duration()> timedelta(days=1):
                flags.append("时长超过1天的路线")
                
            if flags:
                logger.stack_target(detail=f"过滤掉{'，且'.join(flags)}")
                logger.info("成功",f"\n{route}")
                logger.pop_target()
                continue
            
            route_key = tuple((seg.train.train_no, seg.start_station, seg.end_station) for seg in route.segments)
            if route_key not in seen:
                seen.add(route_key)
                routes.append(route)
        return routes
        # return sorted(routes, key=lambda x: x.get_total_duration())
    
    #按照车次分类
    @staticmethod
    def classify_routes(all_routes)->dict:
        routes={}       
        for route in all_routes:
            route_key = tuple(seg.train.train_no for seg in route.segments)
            if route_key not in routes:
                routes[route_key] = [route]
            else:
                routes[route_key].append(route)
        
        return routes
        
        
    
    
# ---------------------------
# 可视化工具（已修复节点颜色不匹配问题）
# ---------------------------
class TrainRouteVisualizer:
    """列车路线可视化工具（修复节点颜色与数量匹配问题）"""
    def __init__(self, figsize=(14, 10)):
        self.init_size(*figsize)
        # self.fig, self.ax = plt.subplots(figsize=figsize)
        # 关闭Matplotlib的交互式模式（关键修复）
        plt.ioff()  # 禁用交互式模式，确保窗口显示时阻塞程序
        self.G = nx.DiGraph()  # 有向图
        self.node_colors = []  # 节点颜色列表（需与节点数量严格一致）
        self.node_labels = {}  # 节点标签
        self.edge_labels = {}  # 边标签
        self.pos = {}  # 节点位置
        
        # 样式配置
        self.station_color = "#4CAF50"  # 普通站点（绿色）
        self.transfer_color = "#FF9800"  # 换乘站（橙色）
        self.direct_edge_color = "#2196F3"  # 路线边（蓝色）
        self.font_size = 10
    
    def init_size(self,cx,cy):
        self.fig, self.ax =plt.subplots(figsize=(cx,cy)) 
        

    def _get_node_id(self, station_name: str, route_idx: int, seg_idx: int) -> str:
        """生成唯一节点ID（确保每个节点唯一）"""
        return f"{station_name}_r{route_idx}_s{seg_idx}"

    def add_route(self, route: Route, route_idx: int, y_offset: float = 0):
        """添加一条路线到图中（修复颜色添加逻辑）"""
        segments = route.segments
        num_segments = len(segments)
        x_step = 1.0 / (num_segments + 1)  # x轴步长（均匀分布节点）
        
        for seg_idx in range(num_segments):
            segment = segments[seg_idx]
            # 生成当前段的起点和终点节点ID（唯一标识）
            start_node_id = self._get_node_id(segment.start_station, route_idx, seg_idx)
            end_node_id = self._get_node_id(segment.end_station, route_idx, seg_idx + 1)
            
            # 1. 添加起点节点（如果不存在）
            if start_node_id not in self.G:
                self.G.add_node(start_node_id)
                self.node_labels[start_node_id] = segment.start_station
                self.node_colors.append(self.station_color)  # 仅新节点添加颜色
                self.pos[start_node_id] = (seg_idx * x_step, y_offset)  # 位置
            
            # 2. 添加终点节点（如果不存在）
            if end_node_id not in self.G:
                self.G.add_node(end_node_id)
                self.node_labels[end_node_id] = segment.end_station
                self.node_colors.append(self.station_color)  # 仅新节点添加颜色
                self.pos[end_node_id] = ((seg_idx + 1) * x_step, y_offset)  # 位置
            
            # 3. 添加边（车次+时间）
            edge_label = f"{segment.train.train_no}\n{segment.departure_time}→{segment.arrival_time}"
            self.G.add_edge(start_node_id, end_node_id)
            self.edge_labels[(start_node_id, end_node_id)] = edge_label
            
            # 4. 标记换乘站（如果不是最后一段）
            if seg_idx < num_segments - 1:
                # 终点节点是下一段的起点，标记为换乘站
                # self.node_labels[end_node_id] += "\n[换乘]"
                # 找到该节点在颜色列表中的索引并修改颜色
                node_list = list(self.G.nodes)
                node_index = node_list.index(end_node_id)
                self.node_colors[node_index] = self.transfer_color

    def draw(self, routes: List[Route], title: str = "列车路线方案",pic_path:str=None):
        """绘制所有路线（确保节点数量与颜色数量一致）"""
        total_routes = len(routes)
        self.init_size(10,int(total_routes/4))
        if total_routes == 0:
            print("没有找到可用路线")
            return
            
        # 计算y轴偏移（区分不同路线，避免重叠）
        y_offsets = np.linspace(-0.5 * (total_routes - 1), 0.5 * (total_routes - 1), total_routes)
        
        # 添加所有路线
        for i, route in enumerate(routes):
            self.add_route(route, i, y_offsets[i])
        
        # 验证节点数量与颜色数量是否一致（调试用）
        assert len(self.G.nodes) == len(self.node_colors), \
            f"节点数量({len(self.G.nodes)})与颜色数量({len(self.node_colors)})不匹配"
        
        # 绘制节点
        nx.draw_networkx_nodes(
            self.G, self.pos, 
            node_size=1500, 
            node_color=self.node_colors,  # 颜色列表与节点数量一致
            node_shape="s",  # 方形节点
            edgecolors="black"  # 节点边框
        )
        
        # 绘制边
        nx.draw_networkx_edges(
            self.G, self.pos, 
            arrowstyle="->", 
            arrowsize=20, 
            edge_color=self.direct_edge_color, 
            width=2
        )
        
        # 绘制节点标签（站点名称）
        nx.draw_networkx_labels(
            self.G, self.pos, 
            self.node_labels, 
            font_size=self.font_size, 
            font_family="SimHei"  # 支持中文
        )
        
        # 绘制边标签（车次和时间）
        nx.draw_networkx_edge_labels(
            self.G, self.pos, 
            self.edge_labels, 
            font_size=self.font_size - 2,
            font_family="SimHei",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.7)  # 标签背景
        )
        
        # 设置标题和样式
        self.ax.set_title(title, fontsize=15, fontfamily="SimHei")
        self.ax.axis("off")  # 关闭坐标轴
        plt.tight_layout()
        # plt.show()

        # 保存图形到本地
        save_path = pic_path 
        if not save_path:
            route=routes[0]
            save_path = StationConfig().result_pic_path(station_manager.get_station_city( route.start_station),station_manager.get_station_city(route.end_station))
        plt.savefig(save_path)
        plt.close()

# ---------------------------
# 示例数据与运行（与之前一致）
# ---------------------------
def create_sample_data() -> List[Train]:
    """创建完整的示例数据"""
    # 1. 上海到广州的直达列车 G100
    shanghai_hongqiao1 = Station("上海虹桥", None, "07:00")
    hangzhou_east1 = Station("杭州东", "07:45", "07:48")
    nanjing_south1 = Station("南京南", "08:50", "08:53")
    hefei_south1 = Station("合肥南", "09:40", "09:43")
    wuhan1 = Station("武汉", "11:30", "11:35")
    changsha_south1 = Station("长沙南", "13:00", "13:03")
    guangzhou_south1 = Station("广州南", "16:00", None)
    train1 = Train("G100", [
        shanghai_hongqiao1, hangzhou_east1, nanjing_south1,
        hefei_south1, wuhan1, changsha_south1, guangzhou_south1
    ])
    
    # 2. 上海到武汉的列车 G101
    shanghai_hongqiao2 = Station("上海虹桥", None, "08:30")
    hangzhou_east2 = Station("杭州东", "09:15", "09:18")
    nanjing_south2 = Station("南京南", "10:20", "10:23")
    hefei_south2 = Station("合肥南", "11:10", "11:13")
    wuhan2 = Station("武汉", "13:00", None)
    train2 = Train("G101", [
        shanghai_hongqiao2, hangzhou_east2, nanjing_south2,
        hefei_south2, wuhan2
    ])
    
    # 3. 武汉到广州的列车 G102
    wuhan3 = Station("武汉", None, "14:00")  # 与G101到达武汉间隔60分钟（符合换乘）
    changsha_south3 = Station("长沙南", "15:30", "15:33")
    guangzhou_south3 = Station("广州南", "18:30", None)
    train3 = Train("G102", [wuhan3, changsha_south3, guangzhou_south3])
    
    # 4. 上海到郑州的列车 G103
    shanghai_hongqiao4 = Station("上海虹桥", None, "09:00")
    nanjing_south4 = Station("南京", "10:00", "10:03")
    xuzhou_east4 = Station("徐州东", "11:15", "11:18")
    zhengzhou_east4 = Station("郑州东", "12:30", None)
    train4 = Train("G103", [
        shanghai_hongqiao4, nanjing_south4, xuzhou_east4, zhengzhou_east4
    ])
    
    # 5. 郑州到广州的列车 G104
    zhengzhou_east5 = Station("郑州", None, "14:00")  # 与G103到达间隔90分钟（符合换乘）
    wuhan5 = Station("武汉", "15:30", "15:33")
    changsha_south5 = Station("长沙南", "17:00", "17:03")
    guangzhou_south5 = Station("广州南", "20:00", None)
    train5 = Train("G104", [
        zhengzhou_east5, wuhan5, changsha_south5, guangzhou_south5
    ])
    
    # 6. 上海到长沙的列车 G105
    shanghai_hongqiao6 = Station("上海", None, "06:30")
    hangzhou_east6 = Station("杭州东", "07:15", "07:18")
    nanjing_south6 = Station("南京南", "08:20", "08:23")
    changsha_south6 = Station("长沙南", "12:30", None)
    train6 = Train("G105", [
        shanghai_hongqiao6, hangzhou_east6, nanjing_south6, changsha_south6
    ])
    
    # 7. 长沙到广州的列车 G106
    changsha_south7 = Station("长沙南", None, "13:30")  # 与G105到达间隔60分钟（符合换乘）
    guangzhou_south7 = Station("广州南", "16:30", None)
    train7 = Train("G106", [changsha_south7, guangzhou_south7])
    
    return [train1, train2, train3, train4, train5, train6, train7]


def handle_routine():
    # 1. 上海到广州的直达列车 G100

    train1 = Train("C3077", [
        Station("上海南","None","17:52:00"),
        Station("苏州南","18:18:00","18:20:00"),
        Station("湖州南浔","18:35:00","18:41:00"),
        Station("湖州东","18:51:00","19:07:00"),
        Station("杭州西","19:36:00","19:43:00"),
        Station("浦江","20:13:00","20:21:00"),
        Station("义乌","20:30:00","20:32:00"),
        Station("横店","20:49:00","20:49:00"),

        ])
        
        # 2. 上海到武汉的列车 G101

    train2 = Train("K308", [
        Station("温州","none","18:50:00"),
        Station("青田","19:49:00","19:52:00"),
        Station("丽水","21:18:00","21:21:00"),
        Station("缙云","21:53:00","21:56:00"),
        Station("永康南","22:23:00","22:26:00"),
        Station("武义","22:47:00","22:51:00"),
        Station("金华南","23:18:00","23:38:00"),
        Station("义乌","00:07:00","00:12:00"),
        Station("诸暨","00:38:00","00:42:00"),
        Station("杭州","02:09:00","02:27:00"),
        Station("宣城","04:50:00","04:54:00"),
        Station("芜湖","05:52:00","05:57:00"),
        Station("合肥","07:25:00","07:49:00"),
        Station("六安","08:52:00","08:55:00"),
        Station("固始","10:32:00","10:49:00"),
        Station("商城","11:06:00","11:09:00"),
        Station("潢川","11:35:00","11:40:00"),
        Station("息县","12:10:00","12:14:00"),
        Station("罗山","12:35:00","12:48:00"),
        Station("信阳","13:24:00","13:32:00"),
        Station("桐柏","14:37:00","14:41:00"),
        Station("南阳","16:15:00","16:48:00"),
        Station("内乡","17:36:00","17:41:00"),
        Station("西峡","18:09:00","18:13:00"),
        Station("丹凤","19:46:00","19:51:00"),
        Station("商洛北","20:27:00","20:29:00"),
        Station("西安","22:25:00","22:35:00"),
        Station("咸阳","22:52:00","23:01:00"),
        Station("宝鸡","00:50:00","01:18:00"),
        Station("天水","03:01:00","03:07:00"),
        Station("甘谷","03:53:00","04:03:00"),
        Station("武山","04:30:00","04:34:00"),
        Station("陇西","05:00:00","05:04:00"),
        Station("定西","06:00:00","06:04:00"),
        Station("兰州","07:57:00","07:57:00"),
        Station("义乌","00:07:00","00:12:00"),
        Station("诸暨","00:38:00","00:42:00"),
        Station("杭州","02:09:00","02:27:00"),
        Station("宣城","04:50:00","04:54:00"),
        Station("芜湖","05:52:00","05:57:00"),
        Station("合肥","07:25:00","07:49:00"),
        Station("六安","08:52:00","08:55:00"),
        Station("固始","10:32:00","10:49:00"),
        Station("商城","11:06:00","11:09:00"),
        Station("潢川","11:35:00","11:40:00"),
        Station("息县","12:10:00","12:14:00"),
        Station("罗山","12:35:00","12:48:00"),
        Station("信阳","13:24:00","13:32:00"),
        Station("桐柏","14:37:00","14:41:00"),
        Station("南阳","16:15:00","16:48:00"),
        Station("内乡","17:36:00","17:41:00"),
        Station("西峡","18:09:00","18:13:00"),
        Station("丹凤","19:46:00","19:51:00"),
        Station("商洛北","20:27:00","20:29:00"),
        Station("西安","22:25:00","22:35:00"),
        Station("咸阳","22:52:00","23:01:00"),
        Station("宝鸡","00:50:00","01:18:00"),
        Station("天水","03:01:00","03:07:00"),
        Station("甘谷","03:53:00","04:03:00"),
        Station("武山","04:30:00","04:34:00"),
        Station("陇西","05:00:00","05:04:00"),
        Station("定西","06:00:00","06:04:00"),
        Station("兰州","07:57:00","07:57:00"),

        ])
    segs=[RouteSegment(train1, "上海南","义乌"),
          RouteSegment(train2, "义乌","西峡"),
          ]
    
    route=Route(segs)
    total_time=route.get_total_duration()
    print(total_time)
    
    


if __name__ == "__main__":
    
    for time_str in ["06:00","23:01:00","16:00","08:00"]:
        print(TrainRouteFinder.start_time_valid(_parse_time(time_str)))

    exit()
    
    handle_routine()
    exit()
    
    # 创建示例数据
    trains = create_sample_data()
    
    # 创建路线查找器
    finder = TrainRouteFinder(trains)
    
    # 查找从上海虹桥站到广州南站的路线（最多换乘2次）
    start_station = "上海"
    end_station = "广州"
    routes = finder.find_transfer_routes(start_station, end_station, max_transfers=2)
    
    # 打印路线信息
    print(f"从 {start_station} 到 {end_station} 共找到 {len(routes)} 条路线：\n")
    for i, route in enumerate(routes, 1):
        print(f"路线 {i}:")
        print(route)
        if i < len(routes):
            print("-" * 80)
    
    # 可视化路线
    visualizer = TrainRouteVisualizer(figsize=(16, 10))
    visualizer.draw(routes, title=f"{start_station}到{end_station}的列车路线方案")