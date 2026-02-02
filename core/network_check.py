import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def quick_internet_check_china():
    """
    轻量级快速检测，适合频繁调用
    """
    try:
        # 使用阿里DNS，通常在中国大陆响应最快
        socket.setdefaulttimeout(2)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("223.5.5.5", 53))
        sock.close()
        return result == 0
    except:
        return False


def quick_http_test(url, timeout=3):
    """快速HTTP测试"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False


def check_internet_comprehensive_china():
    """
    针对中国用户的综合网络检测
    """
    # 第一层：快速DNS检测（国内DNS服务器）
    if quick_internet_check_china():
        return True

    # 第二层：HTTP检测（国内网站）
    test_urls = [
        "https://www.baidu.com",
        "https://httpbin.org/status/200",  # 备用国际站点
        "http://www.qq.com",
    ]

    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            http_futures = [executor.submit(quick_http_test, url) for url in test_urls]

            for future in as_completed(http_futures, timeout=5):
                try:
                    if future.result():
                        return True
                except:
                    continue
    except:
        return False

    return False


if __name__ == "__main__":
    print(check_internet_comprehensive_china())
