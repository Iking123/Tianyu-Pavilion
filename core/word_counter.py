def is_latin_char(char):
    """检查字符是否属于拉丁字母（包括扩展区）"""
    code = ord(char)
    # 基本拉丁字母 (ASCII)
    if (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
        return True
    # 拉丁-1补充 (带重音符号的字母)
    if 0x00C0 <= code <= 0x00FF:
        return True
    # 拉丁扩展-A
    if 0x0100 <= code <= 0x017F:
        return True
    # 拉丁扩展-B
    if 0x0180 <= code <= 0x024F:
        return True
    return False


def is_word_char(char):
    """检查字符是否为单词字符（拉丁字母、撇号或连字符）"""
    if char in ["'", "-"]:
        return True
    if char.isalpha() and is_latin_char(char):
        return True
    return False


def count_words(text, only_total=True):
    """统计文本字数（西文单词算1字，其他字符每个算1字，西文单词间的空格不计字数）"""
    if not text:
        return 0

    word_count = 0  # 西文单词计数
    char_count = 0  # 其他字符计数
    index = 0
    n = len(text)
    last_non_space_type = None  # 记录上一个非空格字符的类型：'word'或'other'

    while index < n:
        char = text[index]

        if is_word_char(char):
            # 读取整个单词
            start = index
            index += 1
            while index < n and is_word_char(text[index]):
                index += 1
            word_count += 1  # 整个单词计为1字
            last_non_space_type = "word"

        elif char.isspace():
            # 读取连续的空格序列
            start = index
            index += 1
            while index < n and text[index].isspace():
                index += 1
            space_count = index - start

            # 处理空格后的字符
            if index < n:
                next_char = text[index]
                next_is_word = is_word_char(next_char)
            else:
                next_is_word = False

            # 只有当空格在"单词-空格-单词"之间时才忽略
            if last_non_space_type == "word" and next_is_word:
                pass  # 忽略这些空格
            else:
                char_count += space_count  # 其他情况计入空格

        else:
            # 其他字符：每个字符计1字
            char_count += 1
            index += 1
            last_non_space_type = "other"

    total = word_count + char_count
    return total if only_total else (total, word_count, char_count)


def main():
    """主函数：处理输入并输出统计结果"""
    text = "C'est un test français: 测试-123"

    total, word_count, char_count = count_words(text, False)
    print(f"\n统计结果：")
    print(f"总字数：{total}")
    print(f"西文单词数：{word_count}")
    print(f"其他字符数：{char_count}")


if __name__ == "__main__":
    main()
