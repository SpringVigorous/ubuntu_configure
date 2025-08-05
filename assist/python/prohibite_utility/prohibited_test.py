import ahocorasick
import re

def hybrid_match(text, keywords, regex_patterns):
    """
    混合匹配方案：
    1. 用Aho-Corasick定位关键词出现的文本区间
    2. 对含关键词的区间应用正则表达式精确匹配
    """
    # 阶段1：构建Aho-Corasick自动机，定位关键词区间
    automaton = ahocorasick.Automaton()
    for word in keywords:
        automaton.add_word(word, word)
    automaton.make_automaton()

    # 记录关键词出现的所有区间（避免重复扫描全文）
    intervals = []
    for end_idx, word in automaton.iter(text):
        start_idx = end_idx - len(word) + 1
        intervals.append((start_idx, end_idx))
    
    # 合并重叠/相邻的区间（减少正则扫描范围）
    intervals.sort(key=lambda x: x[0])
    merged_intervals = []
    for start, end in intervals:
        if not merged_intervals or start > merged_intervals[-1][1] + 1:
            merged_intervals.append([start, end])
        else:
            merged_intervals[-1][1] = max(merged_intervals[-1][1], end)
    
    # 阶段2：对每个区间应用正则表达式匹配
    results = []
    compiled_regexes = [re.compile(pattern) for pattern in regex_patterns]
    
    for start, end in merged_intervals:
        # 扩展区间（避免切割单词），扩展50字符作为缓冲区
        context_start = max(0, start - 50)
        context_end = min(len(text), end + 50)
        context_text = text[context_start:context_end + 1]
        
        # 在该区间内执行所有正则匹配
        for regex in compiled_regexes:
            for match in regex.finditer(context_text):
                # 将匹配位置还原到原始文本坐标
                abs_start = context_start + match.start()
                abs_end = context_start + match.end() - 1
                results.append({
                    "text": match.group(),
                    "start": abs_start,
                    "end": abs_end,
                    "pattern": regex.pattern
                })
    return results

# 示例使用
if __name__ == "__main__":
    text = "请联系support@example.com获取帮助，或访问http://company.net。敏感词：枪、毒品。"
    keywords = ["support", "帮助", "敏感词", "毒品"]  # Aho-Corasick关键词
    regex_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱正则[1,5](@ref)
        r'https?://[^\s/$.?#]+\.[^\s]*'  # URL简化正则[4,5](@ref)
    ]

    matches = hybrid_match(text, keywords, regex_patterns)
    for match in matches:
        print(f"匹配到 '{match['text']}'(位置:{match['start']}-{match['end']})，模式: {match['pattern']}")