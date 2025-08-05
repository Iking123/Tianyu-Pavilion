import requests
import re


def get_baidu_suggestions(keyword):
    """
    调用百度搜索联想词API，获取联想词列表
    :param keyword: 要查询的关键词
    :return: 联想词列表（若失败则返回空列表）
    """
    api_url = "https://suggestion.baidu.com/su"
    params = {"wd": keyword, "cb": "百度"}  # 添加cb参数确保返回格式一致

    try:
        # 发送GET请求，设置超时时间10秒
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()  # 检查请求是否成功

        # 处理响应内容
        content = response.text
        # 提取JSON部分（去掉开头的函数名和括号，以及结尾的括号和分号）
        start_index = content.find("(") + 1
        end_index = content.rfind(")")
        json_str = content[start_index:end_index]

        # 删除掉换行符
        json_str = json_str.replace("\n", "")

        # 删除值中的"引号
        rm_str = ""
        for i in range(len(json_str)):
            if (
                i > 5
                and json_str[i] == '"'
                and not (json_str[i - 1] in ["[", ","])
                and i < len(json_str)
                and not (json_str[i + 1] in ["]", ","])
            ):
                continue
            rm_str += json_str[i]

        # 为字段名添加引号
        json_str = (
            rm_str.replace("q:", '"q":', 1)
            .replace("p:", '"p":', 1)
            .replace("s:", '"s":', 1)
        )

        # 解析JSON
        import json

        data = json.loads(json_str)
        return data.get("s", [])  # 联想词存储在"s"字段中

    except requests.RequestException as e:
        print(f"❌ 请求失败：{e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败：{e}")
        print(f"解析失败的内容: {json_str}")
        return []
    except Exception as e:
        print(f"❌ 发生错误：{e}")
        return []


if __name__ == "__main__":
    # 输入查询关键词
    keyword = input("请输入要查询的百度联想词关键词：")

    # 获取联想词
    suggestions = get_baidu_suggestions(keyword)

    # 输出结果
    if suggestions:
        print(f"\n🔍 「{keyword}」的百度联想词如下：")
        for i, sug in enumerate(suggestions, start=1):
            print(f"{i}. {sug}")
    else:
        print("❌ 未获取到联想词，请检查网络或关键词。")
