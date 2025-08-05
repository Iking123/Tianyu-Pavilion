import jieba
import jieba.analyse
import random
import os
import warnings

# 忽略 pkg_resources 的警告（不影响功能）
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API.")


# 获取 jieba 内置词典路径（通过安装目录推导，兼容所有版本）
def get_jieba_dict_path():
    # 获取 jieba 模块的安装目录（如 site-packages/jieba）
    jieba_dir = os.path.dirname(jieba.__file__)
    # 词典文件固定名为 dict.txt，位于 jieba 目录下
    dict_path = os.path.join(jieba_dir, "dict.txt")
    return dict_path


# 读取词典文件，提取所有词语
def load_jieba_dict_words():
    dict_path = get_jieba_dict_path()
    if not os.path.exists(dict_path):
        raise FileNotFoundError(
            f"jieba 词典文件不存在：{dict_path}，请检查 jieba 是否正确安装"
        )

    words = []
    with open(dict_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):  # 跳过空行和注释
                # 词典格式：词语 词频 词性（提取第一个元素）
                word = line.split(" ")[0]
                words.append(word)
    return words


# 加载内置词典词语
jieba_dict_words = load_jieba_dict_words()


def generate_associate_words(phrase, n_words):
    """生成联想词（基于分词关键词，随机返回指定数量）"""
    # 1. 对输入短语分词并过滤停用词
    keywords = jieba.lcut(phrase)
    stopwords = {
        "在",
        "了",
        "是",
        "吗",
        "呢",
        "的",
        "地",
        "得",
        "着",
        "于",
        "之",
        "和",
        "就",
        "也",
    }
    keywords = [kw for kw in keywords if kw.strip() and kw not in stopwords]

    if not keywords:
        return []

    # 2. 基于每个关键词匹配词典中的词语
    all_matched = []
    for kw in keywords:
        matched = [word for word in jieba_dict_words if kw in word]
        all_matched.extend(matched)

    # 3. 去重
    unique_matched = list(set(all_matched))

    # 4. 不足时用关键词提取补充
    missing_count = n_words - len(unique_matched)
    if missing_count > 0:
        extracted = jieba.analyse.extract_tags(phrase, topK=missing_count)
        unique_matched.extend(extracted)
        unique_matched = list(set(unique_matched))  # 再次去重

    # 5. 随机返回结果
    if len(unique_matched) >= n_words:
        return random.sample(unique_matched, n_words)
    else:
        return unique_matched


if __name__ == "__main__":
    input_phrase = input("请输入一个短语（如「生活在树上」）：")
    try:
        n_words = int(input("请输入需要的联想词数量："))
        if n_words <= 0:
            print("数量必须为正整数！")
        else:
            result = generate_associate_words(input_phrase, n_words)
            print(f"\n联想词（共 {len(result)} 个）：")
            for i, word in enumerate(result, 1):
                print(f"{i}. {word}")
    except ValueError:
        print("请输入有效的正整数！")
    except Exception as e:
        print(f"运行出错：{str(e)}")
