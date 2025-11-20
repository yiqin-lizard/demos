# bs4

import requests    # 发送HTTP请求，获取网页内容
from bs4 import BeautifulSoup
from pandas import DataFrame
from concurrent.futures import ThreadPoolExecutor    # 简化多线程编程，管理线程池
import time
import threading    # 创建和管理线程，实现多线程编程

# table
df_csv = DataFrame(columns=['译名', '片名', '年代', '产地', '分类', '语言', '上映日期', '评分'])
output_lock = threading.Lock()

# headers
my_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'Cookie': '__51uvsct__KSHU1VNqce379XHB=1; __51vcke__KSHU1VNqce379XHB=50d3bff5-9129-57af-a758-75127470dc2f; __51vuft__KSHU1VNqce379XHB=1724392057846; Hm_lvt_0113b461c3b631f7a568630be1134d3d=1724426222,1724426975,1724469459,1724490260; HMACCOUNT=374D5D9A947547F7; Hm_lvt_8e745928b4c636da693d2c43470f5413=1724426222,1724426975,1724469460,1724490260; Hm_lvt_93b4a7c2e07353c3853ac17a86d4c8a4=1724426222,1724426975,1724469460,1724490260; guardok=CnpO0GRVGpEuClZbtJZr2AmFKYgrfdvo+/8RrGDoAUvgDK6uSOJTRc8ybm7pKdJTY4qCFN2vJ4WoUslEIBkgvA==; Hm_lpvt_93b4a7c2e07353c3853ac17a86d4c8a4=1724490495; Hm_lpvt_8e745928b4c636da693d2c43470f5413=1724490495; Hm_lpvt_0113b461c3b631f7a568630be1134d3d=1724490495'
        }

# 定义单线程
def dld_one_page(url, count):
    count1 = 1
    # url = 'https://www.dy2018.com/html/gndy/dyzz/index.html'
    resp = requests.get(url, headers=my_headers)
    resp.encoding = 'gb2312'
    # print(resp.text)

    # 开爬
    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('div', class_='co_content8')
    # print(table)
    infos = soup.findAll('td', colspan='2', style="padding-left:3px")    # 三个查找条件，标签、属性、样式

    # 转换为好操作的str，list
    infos_list = []
    for i in range(len(infos)):
        shift = infos[i].text.replace('◎', '')
        infos_list.append(shift)
        # print(infos[i].text)
    infos_list = [line for line in infos_list if line.strip()]    # strip 清除空格

    # 填csv的每一行
    for i in infos_list:
        line = i.replace('\r', '').replace('/', '-').rstrip('\n').split('\n')  # r-去除最右侧的\n，中间的\n作为分隔符
        length = len(line)
        ori_name = line[0][5:] if length > 0 else None
        chi_name = line[1][5:] if length > 1 else None
        year = line[2][5:] if length > 2 else None
        place = line[3][5:] if length > 3 else None
        clas = line[4][5:] if length > 4 else None
        lang = line[5][5:] if length > 5 else None
        date = line[7][5:] if length > 7 else None
        rank = line[8][5:] if length > 8 else None
        # print(ori_name, chi_name)
        # print(line)
        with output_lock:
            df_csv.loc[count1+(count*25-25)] = [ori_name, chi_name, year, place, clas, lang, date, rank]
            df_csv.to_csv(r'D:\pycharmdata\pythonProject\self\test\2024newest.csv')
            count1 += 1
    print(f'打印完毕第{count}页！')
    time.sleep(2)

# 50个线程一起干活
if __name__ == '__main__':
    with ThreadPoolExecutor(50) as t:
        for i in range(1, 301):
            if i == 1:
                t.submit(dld_one_page, 'https://www.dy2018.com/html/gndy/dyzz/index.html', i)    # 用的函数，第一个参，第二个参
            else:
                t.submit(dld_one_page, f'https://www.dy2018.com/html/gndy/dyzz/index_{i}.html', i)
