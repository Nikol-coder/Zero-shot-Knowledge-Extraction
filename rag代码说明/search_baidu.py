import requests
from bs4 import BeautifulSoup
from urllib import parse
import json

# 函数
def search(entity_type, entity_name):
    # print("entity:", word)
    # 目标URL
    url = "http://baike.baidu.com/item/%s" % parse.quote(entity_name)

    # 发送HTTP请求
    response = requests.get(url)
    # 检查请求是否成功
    if response.status_code == 200:
        # 解析HTML内容
        soup = BeautifulSoup(response.content, 'html.parser')
        # 输出解析后的HTML内容到文件中
        with open('output.html', 'w', encoding='utf-8') as file:
            file.write(soup.prettify())
        # 提取属性信息
        attributes = {}
        # 选择所有符合条件的 <dt> 和 <dd> 元素
        dt_key = soup.select('dt.basicInfoItem_V16ze.itemName_oQNFP')
        dd_value = soup.select('dd.basicInfoItem_V16ze.itemValue_Pxm7m')

        # 确保 <dt> 和 <dd> 元素数量匹配
        if len(dt_key) == len(dd_value):
            for dk, dv in zip(dt_key, dd_value):
                key = dk.get_text(strip=True).replace(" ", "")  # 去除空格
                value = dv.get_text(strip=True)
                attributes[key] = value
        else:
            print("Error: The number of <dt> and <dd> elements does not match.")
            return

        # 构建JSON格式的输出
        result = {
            entity_type: {
                entity_name: attributes
            }
        }

        # 输出JSON格式的字符串
        # print(json.dumps(result, ensure_ascii=False))
        return json.dumps(result, ensure_ascii=False)
    else:
        print("未运行")
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

# 示例调用
# search("孟兴")