import time
from selenium import webdriver
from selenium.webdriver.common.by import By

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
        time.sleep(10)

        # 定位第一个百度百科项的链接
        try:
            # 使用 XPath 定位第一个百度百科项的链接
            baike_link = driver.find_element(By.XPATH, '//a[contains(@href, "baidu.com/link") and contains(@class, "sc-link")]')
            baike_url = baike_link.get_attribute('href')
            print("第一个百度百科项的 URL:", baike_url)
            return baike_url
        except Exception as e:
            print("未找到百度百科项:", e)
            
        # time.sleep(10)
    finally:
        # 关闭浏览器
        driver.quit()

# 示例调用
# autosearch(u"习郁，字文通。襄阳人，融子。初为侍中。 习郁乃习融之子，汉光武帝刘秀时人，曾官侍中。建武五年（公元29年）")