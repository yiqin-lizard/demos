# bs4

import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import aiofiles

'''
写异步的流程：
1.确定好框架，比如：同步-异步-main
2.写框架，def同步()-def异步()-main，然后把各个环节需要的参数和传参写进去
3.按照平时的逻辑写
'''

# 每个任务--每一页具体的操作
async def async_dld(per_url, title):
    # 异步打开
    async with aiohttp.ClientSession() as session:
        async with session.get(per_url) as resp:
            content = await resp.text()
            soup = BeautifulSoup(content, 'html.parser')
            art = soup.find('div', class_='grap').text
            # 异步下载
            async with aiofiles.open(fr'D:\pycharmdata\pythonProject\self\test\xiyouji\{title}.doc', mode='w', encoding='utf-8') as f:
                await f.write(art)
            await asyncio.sleep(1)

# 获取章节和章节链接的函数
async def get_infos(main_url):
    tasks = []
    # 正常写网页信息的获取
    resp = requests.get(main_url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    infos = soup.findAll('li', class_='p-2')
    # 获取两个第二函数需要的参数
    for info in infos:
        title = info.text
        per_url = info.find('a').get('href')
        # 加入到任务列表里
        tasks.append(asyncio.create_task(async_dld(per_url, title)))
    # 异步执行这些任务
    await asyncio.wait(tasks)
    # .gather()收集所有结果；.wait()等待所有任务完成，返回完成和未完成的任务集
    # done, pending = await asyncio.wait(tasks)        done-成功/失败，已结束；pending-卡住，未结束

# 主程，传入最开始的参数，运行(run)函数
if __name__ == '__main__':
    main_url = 'https://xiyouji.5000yan.com/'
    asyncio.run(get_infos(main_url))
