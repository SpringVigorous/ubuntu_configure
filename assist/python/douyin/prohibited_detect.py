import re
from collections import defaultdict
import ahocorasick
import sys

from pathlib import Path
import os

root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )

from base import unique,logger_helper,UpdateTimeType
def binary_search_floor(sorted_list, target):
    """
    二分法查找已排序列表中不大于目标值的最大值的索引
    
    参数:
        sorted_list: 递增排序的列表
        target: 要查找的目标值
        
    返回:
        找到的元素索引，若所有元素都大于目标值则返回-1
    """
    left, right = 0, len(sorted_list) - 1
    result = -1  # 初始化为-1，处理所有元素都大于目标值的情况
    
    while left <= right:
        mid = (left + right) // 2
        mid_value = sorted_list[mid]
        
        if mid_value == target:
            # 找到等于目标值的元素，直接返回其索引
            return mid
        elif mid_value < target:
            # 当前元素小于目标值，可能是候选结果，继续向右查找更大的符合条件的值
            result = mid
            left = mid + 1
        else:
            # 当前元素大于目标值，向左查找
            right = mid - 1
    
    return result

class ProhibitedWordsDetector:
    def __init__(self, prohibited_words:list):
        self.prohibited_words :list=prohibited_words
        self.ignore_chars = {'-', '_', '*', '#', ' '}  # 需跳过的干扰字符
        self.reset_automaton()
        self.logger=logger_helper("敏感词检测")
    @property
    def automaton(self):
        if self._automaton is None:
            self._automaton = self._build_automaton()
        return self._automaton
    
    def reset_automaton(self):
        self._automaton=None
        
        
    def add_keyword(self, keyword:str):
        if not keyword:
            return
        self.prohibited_words.append(keyword)
        

    
    def _build_automaton(self):
        """构建AC自动机（跳过干扰字符）"""
        automaton = ahocorasick.Automaton()
        for word in set(self.prohibited_words):
            clean_word = ''.join(c for c in word if c not in self.ignore_chars)
            if clean_word:
                automaton.add_word(clean_word, word)  # 存储原始词用于输出
        automaton.make_automaton()
        return automaton

    def detect(self, text):
        """使用 iter() 方法匹配违禁词并记录位置"""
        self.logger.update_time(UpdateTimeType.STEP)
        self.logger.stack_target(detail=f"当前文本\n{text}\n")
        text_lower = text.lower()
        results = defaultdict(list)
        
        # 遍历所有匹配项
        for end_index, original_value in self.automaton.iter(text_lower):
            start_index = end_index - len(original_value) + 1
            results[original_value].append((start_index, end_index))
        result= dict(results)
        self.logger.trace("成功",update_time_type=UpdateTimeType.STEP)
        self.logger.pop_target()
        
        return result

    def visualize(self, text, results):
        """可视化违禁词位置"""
        markers = [' '] * len(text)
        for word, positions in results.items():
            for start, end in positions:
                if start < len(markers) and end <= len(markers):
                    markers[start] = '▶'
                    for i in range(start + 1, end):
                        markers[i] = '■'
                    markers[end - 1] = '◀'
        
        self.logger.trace("原始文本:\n" + text)
        self.logger.trace("\n违禁词标记:\n" + ''.join(markers))

        self.detect_result(text, results)


    def pos(self,prohibited_results,indices:list)->list:
        results=[]
        for word, positions in prohibited_results.items():
            for start, end in positions:
                vals=[binary_search_floor(indices, start),binary_search_floor(indices, end),word] 
                results.append(vals)
                
        
        
        return results
    
    def detect_result(self,prohibited_results) -> list[tuple|list]:
        self.logger.stack_target(detail="检测结果")
        results=[(word,len(positions)) for word, positions in prohibited_results.items()]
        self.logger.info("完成",f"\n{ProhibitedWordsDetector.results_txt(results)}\n")
        self.logger.pop_target()
        return results
        
    @staticmethod
    def results_txt(results:list[tuple|list]):
        result = "\n".join( [f"'{word}':出现{count}次" for word, count,*other in results])  if results else "无违禁词"  
        return result
    @staticmethod
    def results_txt_short(results:list[tuple|list]):
        result = "\n".join( [f"{word}:{count}" for word, count,*other in results])  if results else "无违禁词"  
        return result
    
# 示例用法
if __name__ == "__main__":
    PROHIBITED_WORDS = ["最佳", "国家级", "抗癌", "增强免疫力", "100%有效"]
    detector = ProhibitedWordsDetector(PROHIBITED_WORDS)
    sample_text = "本产品采用**国家级**配方，具有最佳抗癌效果，国家级，能增强免疫力，100%有效！"
    
    results = detector.detect(sample_text)
    detector.visualize(sample_text, results)