import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter import messagebox, ttk

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
            return None
    finally:
        # 关闭浏览器
        driver.quit()

def on_search():
    search_term = entry.get()
    if search_term:
        result = autosearch(search_term)
        if result:
            messagebox.showinfo("搜索结果", f"第一个百度百科项的 URL: {result}")
        else:
            messagebox.showinfo("搜索结果", "未找到百度百科项")
    else:
        messagebox.showwarning("输入错误", "请输入搜索词")

# 创建主窗口
root = tk.Tk()
root.title("百度搜索工具")
root.geometry("400x200")
root.configure(bg="#f0f0f0")

# 创建样式
style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#0078d7", foreground="white")
style.configure("TLabel", background="#f0f0f0", foreground="#333333")
style.configure("TEntry", fieldbackground="#ffffff", foreground="#333333")

# 创建输入框
label = ttk.Label(root, text="请输入搜索词:")
label.pack(pady=10)

entry = ttk.Entry(root, width=40)
entry.pack(pady=10)

# 创建搜索按钮
search_button = ttk.Button(root, text="搜索", command=on_search)
search_button.pack(pady=20)

# 运行主循环
root.mainloop()