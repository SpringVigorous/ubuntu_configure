import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from station_routine import *


import os

import sys

from pathlib import Path

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import pickle_load,logger_helper,UpdateTimeType
import math
import matplotlib.transforms as mtransforms
from matplotlib.text import Text

def get_text_dimensions(text, fontsize=12, fontfamily="sans-serif"):
    """
    计算文本在指定字号和字体下的显示尺寸（宽度和高度）
    
    参数:
        text: 文本内容（字符串）
        fontsize: 字号（默认12，单位：磅）
        fontfamily: 字体（默认"sans-serif"，支持系统安装的字体）
    
    返回:
        width: 文本宽度（单位：英寸）
        height: 文本高度（单位：英寸）
    """
    # 创建临时图形和坐标轴（不显示）
    fig, ax = plt.subplots(figsize=(10, 10))  # 临时图形，尺寸不影响结果
    
    # 创建文本对象（设置为不可见，避免显示）
    text_obj = ax.text(
        0, 0, text,
        fontsize=fontsize,
        fontfamily=fontfamily,
        visible=False  # 不显示文本，仅用于计算尺寸
    )
    
    # 绘制图形以确保文本尺寸已计算（关键步骤）
    fig.canvas.draw()
    
    # 获取文本的边界框（单位：像素）
    # bbox包含(x0, y0, width, height)，其中width和height为文本像素尺寸
    bbox = text_obj.get_window_extent()
    
    # 获取图形的DPI（每英寸像素数），用于转换为英寸
    dpi = fig.dpi
    
    # 转换为英寸（像素 ÷ DPI = 英寸）
    width = bbox.width / dpi
    height = bbox.height / dpi
    
    # 关闭临时图形，释放资源
    plt.close(fig)
    
    return width, height
def calculate_node_ratio(ax, fig, node_size):
    """
    计算方形节点占子图区域和整个图形区域的长宽比例（考虑图形边界）
    
    参数:
        ax: matplotlib的axes对象
        fig: matplotlib的figure对象
        node_size: 节点大小值（nx.draw_networkx_nodes的node_size参数）
    
    返回:
        subplot_width_ratio: 节点宽度占子图宽度的比例
        subplot_height_ratio: 节点高度占子图高度的比例
        figure_width_ratio: 节点宽度占整个图形宽度的比例
        figure_height_ratio: 节点高度占整个图形高度的比例
    """
    # 1. 计算方形节点的物理尺寸（英寸）
    side_length_points = math.sqrt(node_size)  # 边长（磅）
    side_length_inch = side_length_points / fig.dpi  # 转换为英寸（1英寸=72磅）
    
    # 2. 获取图形总物理尺寸（含边距，英寸）
    fig_width, fig_height = fig.get_size_inches()  # 图形总宽、总高
    
    # 3. 获取图形边界参数（子图与图形边缘的间距比例）
    subplot_params = fig.subplotpars
    left = subplot_params.left    # 子图左边缘占图形宽度的比例
    right = subplot_params.right  # 子图右边缘占图形宽度的比例
    bottom = subplot_params.bottom  # 子图下边缘占图形高度的比例
    top = subplot_params.top        # 子图上边缘占图形高度的比例
    
    # 4. 计算子图的物理尺寸（英寸）
    subplot_width = fig_width * (right - left)  # 子图宽度 = 图形总宽 × 子图宽度占比
    subplot_height = fig_height * (top - bottom)  # 子图高度 = 图形总高 × 子图高度占比
    
    # 5. 计算节点占子图区域的比例
    subplot_width_ratio = side_length_inch / subplot_width
    subplot_height_ratio = side_length_inch / subplot_height
    
    # 6. 计算节点占整个图形区域（含边距）的比例
    figure_width_ratio = side_length_inch / fig_width
    figure_height_ratio = side_length_inch / fig_height
    
    # return (subplot_width_ratio, subplot_height_ratio,
    #         figure_width_ratio, figure_height_ratio)

    
    return (subplot_width_ratio, subplot_height_ratio)
# ---------------------------
# 可视化工具（已修复节点颜色不匹配问题）
# ---------------------------
class TrainRouteVisualizer:
        

    """列车路线可视化工具（修复节点颜色与数量匹配问题）"""
    def __init__(self, figsize=(14, 10)):
        self.logger=logger_helper("绘制车次路线")
        self.init_size(*figsize)
        # self.fig, self.ax = plt.subplots(figsize=figsize)
        # 关闭Matplotlib的交互式模式（关键修复）
        plt.ioff()  # 禁用交互式模式，确保窗口显示时阻塞程序
        self.G = nx.DiGraph()  # 有向图
        self.node_colors = []  # 节点颜色列表（需与节点数量严格一致）
        self.node_labels = {}  # 节点标签
        self.edge_labels = {}  # 边标签
        self.pos = {}  # 节点位置
        
        
        self.header_G = nx.DiGraph()
        self.header_pos = {}
        self.header_labels = {}
        
        # 样式配置
        self.station_color = "#4CAF50"  # 普通站点（绿色）
        self.transfer_color = "#FF9800"  # 换乘站（橙色）
        self.diff_transfer_color = "#FFFF00"  # 异站换乘站（黄色）
        self.direct_edge_color = "#2196F3"  # 路线边（蓝色）
        self.font_size = 10
        self.node_size=1500
        self.font_family="SimHei"
    
    @property
    def node_scale(self):
        return calculate_node_ratio(self.ax,self.fig,self.node_size)
    
    def init_size(self,cx,cy):
        self.fig, self.ax =plt.subplots(figsize=(cx,cy),dpi=100) 
        

    def _get_node_id(self, station_name: str, route_idx: int, seg_idx: int) -> str:
        """生成唯一节点ID（确保每个节点唯一）"""
        return f"{station_name}_r{route_idx}_s{seg_idx}"

    def add_route(self, route: Route, route_idx: int, y_offset: float = 0):
        """添加一条路线到图中（修复颜色添加逻辑）"""
        segments = route.segments
        num_segments = len(segments)
        w_scale,_=self.node_scale
        w_scale_half=w_scale/2

        x_step =1.0 / (num_segments + 1)  # x轴步长（均匀分布节点）
        header_scale=w_scale*2
        
        header_node_id = f"route_{route_idx}"
        if header_node_id not in self.header_G:  # 添加路线索引节点
            self.header_G.add_node(header_node_id)
            self.header_labels[header_node_id] = f"方案{route_idx:02}：\n耗时:{route.get_total_duration()}\n等待：{route.wait_total_time()}"
            self.header_pos[header_node_id] = (0, y_offset)
        
        for seg_idx in range(num_segments):
            
            is_first= seg_idx == 0
            is_last= seg_idx == num_segments - 1
            
            
            segment = segments[seg_idx]
            # 生成当前段的起点和终点节点ID（唯一标识）
            start_node_id = self._get_node_id(segment.start_station, route_idx, seg_idx)
            end_node_id = self._get_node_id(segment.end_station, route_idx, seg_idx + 1)
            
            # 1. 添加起点节点（如果不存在）
            if start_node_id not in self.G:
                self.G.add_node(start_node_id)
                self.node_labels[start_node_id] = segment.start_station
                
                
                
                self.node_colors.append(self.station_color)  # 仅新节点添加颜色
                off_x= w_scale_half if ((not is_first) and segments[seg_idx-1].end_station!=segment.start_station ) else (0 if not is_first else header_scale)
                
                self.pos[start_node_id] = (seg_idx * x_step+off_x, y_offset)  # 位置
            
            # 2. 添加终点节点（如果不存在）
            if end_node_id not in self.G:
                self.G.add_node(end_node_id)
                self.node_labels[end_node_id] = segment.end_station
                self.node_colors.append(self.station_color)  # 仅新节点添加颜色
                off_x= w_scale_half if not is_last and segments[seg_idx+1].start_station!=segment.end_station else 0
                
                self.pos[end_node_id] = ((seg_idx + 1) * x_step-off_x, y_offset)  # 位置
            
            # 3. 添加边（车次+时间）
            edge_label = f"{segment.train.train_name}\n{segment.departure_time_str}→{segment.arrival_time_str}"
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
        routes=list(sorted(routes,key=lambda x:x.get_total_duration(),reverse=True))
        
        """绘制所有路线（确保节点数量与颜色数量一致）"""
        total_routes = len(routes)
        self.logger.update_time(UpdateTimeType.ALL)
        self.logger.update_target(detail=f"共{total_routes}条路线")
        
        self.init_size(10,int(total_routes*.8))
        if total_routes == 0:
            print("没有找到可用路线")
            return
        # header_width,_=get_text_dimensions("耗时：21:06:07\n等待：01:02:03",self.font_size,self.font_family) 
        # self.header_scale,_=calculate_node_ratio(self.ax,self.fig,(header_width*self.fig.dpi)**2)   
          
            
        # 计算y轴偏移（区分不同路线，避免重叠）
        y_offsets = np.linspace(-0.5 * (total_routes), 0.5 * (total_routes ), total_routes)
        
        # 添加所有路线
        for i, route in enumerate(routes):
            self.add_route(route, i, y_offsets[i])
        
        # 验证节点数量与颜色数量是否一致（调试用）
        assert len(self.G.nodes) == len(self.node_colors), \
            f"节点数量({len(self.G.nodes)})与颜色数量({len(self.node_colors)})不匹配"
        
        
        all_pos=list(self.pos.values())
        all_pos.extend(self.pos.values())
        x_values = [pos[0] for pos in all_pos]
        y_values = [pos[1] for pos in all_pos]
        min_x,max_x=min(x_values),max(x_values)
        min_y,max_y=min(y_values),max(y_values)
        
        x_pad=(max_x-min_x)*0.1
        y_pad=(max_y-min_y)*0.1
        
        self.ax.set_xlim(min_x-x_pad-.1, max_x+x_pad)
        self.ax.set_ylim(min_y-y_pad, max_y+y_pad)
        
        
        # 绘制节点
        nx.draw_networkx_nodes(
            self.G, self.pos, 
            node_size=self.node_size, 
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
            font_family=self.font_family  # 支持中文
        )
        
        # 绘制耗时时长
        nx.draw_networkx_labels(
            self.header_G, self.header_pos, 
            self.header_labels, 
            font_size=self.font_size, 
            font_family=self.font_family,  # 支持中文
            font_color="red"
        )
        # 绘制边标签（车次和时间）
        nx.draw_networkx_edge_labels(
            self.G, self.pos, 
            self.edge_labels, 
            font_size=self.font_size+2 ,
            font_family=self.font_family,
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.7)  # 标签背景
        )
        
        # 设置标题和样式
        self.ax.set_title(title,
                          fontsize=15,
                          fontfamily=self.font_family, 
                          pad=2,  # 标题与子图顶部的距离（默认6，减小为2）
                        y=0.98)  # 标题垂直位置（接近1表示靠近图形顶部）
        self.ax.axis("off")  # 关闭坐标轴
        plt.tight_layout()
        # plt.show()

        # 保存图形到本地
        if not pic_path:
            
            start_station=[route.start_station for route in routes]
            end_station=[route.end_station for route in routes]
            from collections import Counter
            start_station=Counter(start_station).most_common(1)[0][0]
            end_station=Counter(end_station).most_common(1)[0][0]
            route=routes[0]
            pic_path = StationConfig().result_pic_path(start_station,end_station)
        plt.savefig(pic_path)
        plt.close()
        
        self.logger.info("完成",f"保存图片:{pic_path}",update_time_type=UpdateTimeType.ALL)

if __name__ == "__main__":
    
    routes=pickle_load(r"F:\worm_practice\train_ticket\result\上海-西峡_routes.pkl")
    start_station = "上海"
    end_station = "西峡"
    # 可视化路线
    visualizer = TrainRouteVisualizer(figsize=(16, 10))
    visualizer.draw(routes, title=f"{start_station}到{end_station}的列车路线方案\n共{len(routes)}个选择")