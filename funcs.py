def case_insensitive_find(s, sub, start=None, end=None):
    """不区分大小写的查找"""
    s_lower = s.lower()
    sub_lower = sub.lower()
    return s_lower.find(sub_lower, start, end)
