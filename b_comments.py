# 本次爬取json数据，不在网页源代码，不用bs4
# 评论的回复在另外的列表里，距离太远，暂不考虑
# 置顶在另外的列表里，暂不考虑

import requests
import time
import random
import hashlib
from urllib.parse import unquote, quote
from pandas import DataFrame 


def GetDict(p_1):
    """
    把传入的字符串params变成字典形式
    pagination_str需要解码url编码
    """
    l1 = []
    l2 = []
    p_split = p_1.split('&')
    for i in p_split:
        l1.append(i.split('=')[0])
        l2.append(str(i.split('=')[-1]))
    p_dict = dict(zip(l1, l2))
    p_dict['pagination_str'] = unquote(p_dict['pagination_str'])
    return p_dict


def Getw_rid(i, wts, p_dict, pag=''):
    """
    获取加密的wrid
    """
    if i == 1:
        w_rid = p_dict['w_rid']
    else:
        offset = quote('{"offset":"%s"}' % pag)
        lst = [
            "mode=3",
            f"oid={p_dict['oid']}",
            f"pagination_str={offset}",
            "plat=1",
            "type=1",
            f"web_location={p_dict['web_location']}",
            f"wts={wts}"
        ]
        v = '&'.join(lst)
        a = 'ea1db124af3c7062474693fa704f4ff8'
        v_a = v + a
        at = hashlib.md5()
        at.update(v_a.encode('utf-8'))
        w_rid = at.hexdigest()
    # print(w_rid)
    return w_rid


def Getparams(i, w_rid, wts, p_dict, pag=''):
    """
    获取完整的参数信息
    第一页直接复制检查-负载-源
    后面的页要更新：
        pag：上一页会返回一个新的部分，添加到最初的空字典中
        w_rid：md5加密
        wts：时间戳，用time.time()获取
    """
    p_dict['pagination_str'] = '{"offset":"%s"}' % pag
    p_dict['w_rid'] = w_rid
    p_dict['wts'] = wts if i > 1 else p_dict['wts']
    if i > 1 and 'seek_rpid' in p_dict:
        del p_dict['seek_rpid']
    # print(p_dict)
    return p_dict


def GetResp(url, params, headers):
    """
    获取json信息
    """
    resp = requests.get(url=url, params=params, headers=headers)
    time.sleep(random.randint(0,4))
    j_data = resp.json()
    return j_data


def GetContent(page, j_data, file_name):
    """
    获取json里所需的信息
    获取更新的pag，以传递给后续的页
    """
    count = (page - 1) * 20
    
    replies = j_data['data']['replies']
    for i in replies:
        msg = i['content']['message']
        mid = i['member']['mid']
        sex = i['member']['sex']
        level = i['member']['level_info']['current_level']
        ctime = i['ctime']   # 评论时间，time.time8位
        try:
            likes = i['like']
        except:
            likes = 0
        df_csv.loc[count + 1] = [mid, sex, level, msg, ctime, likes]
        count += 1
        df_csv.to_csv(f'D:\pycharmdata\pythonProject\self\\test\{file_name}.csv', encoding = 'utf-8-sig', index = False)
        print(f'本页索引为{count}的评论录入完成')

    try:
        pag = j_data['data']['cursor']['pagination_reply']['next_offset']
    except:
        print('已经是最后一页')
        pag = 'NULL'

    return pag


if __name__ == '__main__':
    df_csv = DataFrame(columns=['用户id', '性别', '等级', '评论', '发布时间', '点赞数'])
    count = 0

    num = int(input('请输入一个整数，评论总数：')) // 20 + 1
    p_1 = str(input('请输入负载-字符串参数-源：'))
    url = str(input('请输入要爬取的网页网址，?oid前'))
    cookie = str(input('请输入cookie，位置在检查-main?oid页-标头，以CURRENT_FNVAL=4048结尾：'))
    file_name = input('请输入文件名，英文，路径在D:\pycharmdata\pythonProject\self\\test：')

#    p_1 = 'oid=115466588654306&type=1&mode=3&pagination_str=%7B%22offset%22:%22%22%7D&plat=1&seek_rpid=&web_location=1315875&w_rid=2928064eab72106566990fb1cd2eba8a&wts=1763031719'
#    url = 'https://api.bilibili.com/x/v2/reply/wbi/main'
#    cookie = 'buvid3=8F15FDE8-DBFE-6353-258D-1574C9457C1068263infoc; b_nut=1760938468; _uuid=8669AA18-65B8-43A7-9ED6-7D51A10F8211F68109infoc; CURRENT_QUALITY=0; buvid_fp=99d111ce44256bdb1217bbb97bc89420; buvid4=3D9EE23C-1996-4163-5FCD-3EAF57D9399669337-025102013-f/GBcxrC5TUzSi6VZ3YyMQ%3D%3D; rpdid=|(J|lYYklk|l0J\'u~Y|mJ)R~J; home_feed_column=4; browser_resolution=1225-676; SESSDATA=a342d2fa%2C1778478979%2C9947b%2Ab1CjCI4SKjZpTm7TBZr3YYQQ5Od7kgGuk7ICLZs4uN4Ng5wiQo6wdhxgl38DaP03MtvUASVmlsb0Vka01fVzVsUnhfNlR5d1ZkaHdlWjVWNUExV0FZR280Y0xsQ1B6V2lfaDJiUHNpVTJYY1kwZnQyMFZlRlBpTlFNTk1QN3JoUEwteDBnMlZQa013IIEC; bili_jct=7082bfdd38c866e7dc1ceb8823a2caee; DedeUserID=567047401; DedeUserID__ckMd5=bba1d852eaec3382; sid=5m2ezfm9; theme-tip-show=SHOWED; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjMxODYxOTksImlhdCI6MTc2MjkyNjkzOSwicGx0IjotMX0.Movuq4bHJve_twrPEoLDGe6xcvybDKTLgNOkmCZck1Q; bili_ticket_expires=1763186139; CURRENT_FNVAL=4048'

    headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
    'cookie': f'{cookie}'
}
    
    p_dict = GetDict(p_1)
    
    for i in range(1, num + 1):
        wts = int(time.time())
        w_rid = Getw_rid(i, wts, p_dict, pag=pag if i > 1 else '')
        param = Getparams(i, w_rid, wts, p_dict, pag=pag if i > 1 else '')
        j_data = GetResp(url=url, params=param, headers=headers)
        pag = GetContent(i, j_data, file_name)    # 需要的内容在函数内部就打包好传进csv了，这里只接受下一页需要的pag
        if pag == 'NULL':
            break

        print(f'第{i}页爬取完成')


