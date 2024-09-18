import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib import parse
import json

app = Flask(__name__)

def autosearch(search_term):
    # 初始化 WebDriver
    driver = webdriver.Chrome()
    driver.get('https://www.baidu.com/')

    try:
        # 使用 By.ID 来定位搜索框并输入搜索词
        search_box = driver.find_element(By.ID, "kw")
        search_box.send_keys(search_term)

        # 点击搜索按钮
        search_button = driver.find_element(By.ID, "su")
        search_button.click()

        # 等待搜索结果加载
        time.sleep(2)

        # 定位第一个百度百科项的链接
        try:
            # 使用 XPath 定位第一个百度百科项的链接
            baike_link = driver.find_element(By.XPATH, '//a[contains(@href, "baidu.com/link") and contains(@class, "sc-link")]')
            baike_url = baike_link.get_attribute('href')
            print("第一个百度百科项的 URL:", baike_url)
            return baike_url
        except Exception as e:
            print("未找到百度百科项:", e)
            return None
    finally:
        # 关闭浏览器
        driver.quit()

def search(entity_type, entity_name, url=None):
    # 目标URL
    if url is None:
        url = "http://baike.baidu.com/item/%s" % parse.quote(entity_name)
    else:
        url = url
    print("url:", url)
    
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
        dt_key = soup.select('dt.basicInfoItem_BorfF.itemName_mdRad')
        dd_value = soup.select('dd.basicInfoItem_BorfF.itemValue_y3bhg')
        
        print(dt_key)
        print(dd_value)
        
        # 确保 <dt> 和 <dd> 元素数量匹配
        if len(dt_key) == len(dd_value):
            for dk, dv in zip(dt_key, dd_value):
                key = dk.get_text(strip=True).replace(" ", "")  # 去除空格
                value = dv.get_text(strip=True)
                attributes[key] = value
        else:
            print("Error: The number of <dt> and <dd> elements does not match.")
            return

        # # 提取图片 URL
        # images = []
        # for img in soup.select('div.summary-pic img'):
        #     img_url = img.get('src')
        #     if img_url:
        #         images.append(img_url)

        # # 添加 URL 到属性信息中
        # attributes['url'] = url
        # attributes['images'] = images

        # 构建JSON格式的输出
        result = {
            entity_type: {
                entity_name: attributes
            }
        }

        # 输出JSON格式的字符串
        return json.dumps(result, ensure_ascii=False)
    else:
        print("未运行")
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_route():
    search_term = request.form['search_term']
    if search_term:
        baike_url = autosearch(search_term)
        if baike_url:
            result = search("百度百科", search_term, baike_url)
            return jsonify({"status": "success", "data": json.loads(result)})
        else:
            return jsonify({"status": "error", "message": "未找到相关信息"})
    else:
        return jsonify({"status": "error", "message": "请输入搜索词"})

if __name__ == '__main__':
    app.run(debug=True)