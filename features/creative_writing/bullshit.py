import random
import time
from PyQt6.QtCore import QThread, pyqtSignal
from funcs import read_json, resource_path
from core.hitokoto import get_hitokoto_with_speaker, is_punctuation
from core.jieba_asso import generate_associate_words
from core.baidu_asso import get_baidu_suggestions
from core.word_counter import count_words

data = read_json(resource_path("resources/data/bullshit_data.json"))
pre = data["before"]  # 在名人名言前面弄点废话
back = data["after"]  # 在名人名言后面弄点废话
废话 = data["bosh"]  # 代表文章主要废话来源
quote = data["quote"]  # 引用名言的格式

for i in pre:
    for j in back:
        quote.append(f"${{n}}{i}：${{s}}{j}")

print(len(quote))
重复度 = 1


def 洗牌遍历(列表):
    global 重复度
    池 = list(列表) * 重复度
    while True:
        random.shuffle(池)
        for 元素 in 池:
            yield 元素


下一句废话 = 洗牌遍历(废话)
下一句名人名言 = 洗牌遍历(quote)


def 来点名人名言():
    global 下一句名人名言
    xx = next(下一句名人名言)
    time.sleep(1)
    s = get_hitokoto_with_speaker()
    xx = xx.replace("${n}", s.get("from_who"))
    xx = xx.replace("${s}", s.get("content"))
    return xx


def 另起一段():
    xx = "\r\n"
    return xx


def circular_access(arr, index):
    return arr[index % len(arr)]


def check_end(article):
    c = article[-1]
    return is_punctuation(c) and c != "　" and c != "，"


def process_string(s, xx, my_list):
    s = s.replace("${x}", xx)
    if "${w" in s:
        n_words = 1
        while f"${{w{n_words+1}}}" in s:
            n_words += 1
        words = (
            random.choice(my_list)
            if len(my_list) and random.random() < 0.5
            else generate_associate_words(xx, n_words)
        )
        for i in range(n_words):
            s = s.replace(f"${{w{i+1}}}", circular_access(words, i))
    return s


if __name__ == "__main__":

    print("${x}")
    xx = input("请输入文章主题:")
    my_list = get_baidu_suggestions(xx)
    article = process_string(f"# {xx}\r\n　　{来点名人名言()}", xx, my_list)
    print(article, end="", flush=True)
    can_end = check_end(article)
    while count_words(article) < 950 or not can_end:
        分支 = random.randint(0, 100)
        if 分支 < 10 and can_end:
            delta = 另起一段()
        elif 分支 < 23:
            delta = 来点名人名言()
        else:
            delta = next(下一句废话)
        delta = process_string(delta, xx, my_list)
        print(delta, end="", flush=True)
        article += delta
        can_end = check_end(article)


class BullshitWorker(QThread):
    """写抽象作文的后台工作线程"""

    status_signal = pyqtSignal(str)
    update_signal = pyqtSignal(str)

    def __init__(self, heading, length=950):
        super().__init__()
        self.heading = heading
        self.length = length

    def run(self):
        self.status_signal.emit("✍ 正在创作抽象作文")
        xx = self.heading
        my_list = get_baidu_suggestions(xx)
        article = process_string(f"{来点名人名言()}", xx, my_list)
        self.update_signal.emit(article)
        can_end = check_end(article)
        while count_words(article) < self.length or not can_end:
            分支 = random.randint(0, 100)
            if 分支 < 10 and can_end:
                delta = 另起一段()
            elif 分支 < 23:
                delta = 来点名人名言()
            else:
                delta = next(下一句废话)
            delta = process_string(delta, xx, my_list)
            self.update_signal.emit(delta)
            article += delta
            can_end = check_end(article)
        print(article)
        self.status_signal.emit("✅ 杰作大功告成！")
