from collections import Counter

def unique(original_list):
    counter = Counter(original_list)
    return list(counter.keys())