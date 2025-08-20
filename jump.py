import time
import random

dancers = [
    r"(~˘▾˘)~",
    r"~(˘▾˘~)",
    r"♪┏(・o･)┛",
    r"┗(・o･)┓♪",
    r"ヽ(^。^)ノ",
    r"ヽ(^∇^)ノ",
]

colors = ["\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m"]

try:
    while True:
        dancer = random.choice(dancers)
        color = random.choice(colors)
        print(color + dancer.center(50) + "\033[0m", end="\r")
        time.sleep(0.3)
except KeyboardInterrupt:
    print("\n舞蹈结束啦！拜拜~ (￣▽￣)/")
