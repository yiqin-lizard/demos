import pandas as pd
import os
import jieba
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# 准备工作
swords = open(r'D:\pycharmdata\pythonProject\self\documents\中文停用词库.txt', encoding='utf-8').read().splitlines()
pwords = open(r'D:\pycharmdata\pythonProject\self\documents\正面词语合集（中文）.txt', encoding='utf-8').read().splitlines()
nwords = open(r'D:\pycharmdata\pythonProject\self\documents\负面词语合集（中文）.txt', encoding='utf-8').read().splitlines()
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
tz_hours = 8


# 数据分析函数 -------------------------------------------------------------------------

# 清理评论数据
def CleanCmts(t):
    """
    1. 去除评论中特殊字符：
        换行符、空格
        【】类型的文字表情
        python能识别的表情不做处理，因为调用词库的时候会扔掉
    2. 将‘http、https的网址’替换为‘邀请码’
    3. 将‘MTI3OTIzMTEyNDU0Ng’18个大小写数字替换为‘邀请码’
    """
    text = str(t)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'https://\S+', '邀请码', text)
    text = re.sub(r'\b[A-Za-z0-9]{18}\b', '邀请码', text)

    return text.strip()


# 对清理后的评论jieba分词
def JbText(text):
    """
    jieba分词
    标点符号不用管，停用词会自然排除
    存储在列表里，便于后续操作
    """
    words = jieba.cut(text)
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    refine = []
    for word in words:
        if word not in swords and zhPattern.search(word):
            refine.append(word)
    return refine


# 对分词后的评论计算情感值
def FValue(refine):
    pos, neg = 0, 0
    for word in refine:
        if word in pwords:
            pos += 1
        elif word in nwords:
            neg += 1
    f_value = (pos - neg) / (pos + neg) if (pos + neg) != 0 else 0  
    f_value2 = (pos - neg) / len(refine) if len(refine) != 0 else 0

    return f_value, f_value2


# 建立词云
def BuildWordCloud(cleaned_df, max_words = 50):
    """
    col：df['列名']，需要处理的列
    max_words: 显示前多少个词语
    """
    all_words = []
    for word in cleaned_df['关键词']:
        all_words.extend(word)
    word_freq = Counter(all_words)
    print(f"总词汇数: {len(all_words)}")
    print(f"唯一词汇数: {len(word_freq)}")
    # top_wf = word_freq.most_common(max_words)

    wcloud = WordCloud(
        font_path=' C:\Windows\Fonts\simhei.ttf',
        width=800,
        height=600,
        background_color='white',
        max_words=max_words,
        colormap='viridis',
        max_font_size=100,
        random_state=42
    ).generate_from_frequencies(word_freq)

    keywords_df = pd.DataFrame(word_freq.most_common(), columns=['关键词', '频次'])
    
    return wcloud, keywords_df


# 计算时间趋势变化
def TimeAnal(cleaned_df, cat, start_time, end_time, freq='2H'):
    """
    计算随时间的一些数据，cleaned_df、cat必要，其余可选
    cleaned_df: 仅写清理过的dataframe名，列在函数中写有
    cat: '点赞' or '评论' 随时间分布
    start_time: 视频发布时间，如'2025-10-31 20:00:00'
    end_time: 统计结束时间，如'2025-11-02 20:00:00'
    freq: default '2H'
    """
    tl_df = cleaned_df[['用户id', '发布时间', '点赞数']].copy()
    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)
    time_ranges = pd.date_range(start=start_time, end=end_time, freq=freq)
    tl_df['时间区间'] = pd.cut(tl_df['发布时间'], bins=time_ranges)
    if cat == '点赞':
        time_stats = tl_df.groupby('时间区间').agg({'点赞数': ['sum', 'mean', 'count']}).round(2)
        time_stats.columns = ['总点赞数', '平均点赞数', '评论数量']
    elif cat == '评论':
        time_stats = tl_df.groupby('时间区间').agg({'用户id': 'count'}).round(2)
        time_stats.columns = ['总评论数']
    else:
        print('输入不正确。正确输入：点赞，评论')
        return
    time_stats = time_stats.reset_index()
    return time_stats


# 操作函数 --------------------------------------------------------------------------

def OpenCsv(path):
    """
    读取csv文件并创建dataframe
    将time转为datetime ‘2025-01-01 00:00:00’
    基本信息输出后，清洗评论、分词
    计算情感值, 公式为(pos-neg)/(pos+neg)
    """
    df = pd.read_csv(r'{}'.format(path))
    df['发布时间'] = pd.to_datetime(df['发布时间'], unit='s') + pd.Timedelta(hours=tz_hours)
    print(df.describe(include='all'))
    df.info()
    print(df.head(10))
    df.duplicated()
    df['清洗后评论'] = df['评论'].apply(CleanCmts)
    df['关键词'] = df['清洗后评论'].apply(JbText)
    df[['相对情感值', '绝对情感值']] = df['关键词'].apply(FValue).apply(pd.Series)
    df = df.sort_values('点赞数', ascending=False)
    return df  


def GetTopAccounts(df, num = 10):
    """
    评论最多的num个账户，以及所在行的所有信息, 按照id、时间排序
    df: 清洗后、去重前的dataframe
    num: 分析的账户数, default 10
    """
    top = df['用户id'].value_counts().head(num)
    top_accounts = df[df['用户id'].isin(top.index)]
    top_accounts = top_accounts.sort_values(['用户id', '发布时间'])
    return top_accounts


def GetCleanedDf(df):
    """
    去重：没有重复数据，但有同一人发的相同数据，只保留最高点赞
    df: 清洗后、去重前的dataframe
    """
    sort = df.sort_values('点赞数', ascending=False)
    cleaned = sort.drop_duplicates(subset=['用户id', '评论'], keep='first')
    cleaned_df = cleaned.sort_values('点赞数',ascending=False)
    return cleaned_df


def UseWordCloud(wcloud, folder, max_words=50):
    """
    使用构建好的词云，内置显示、保存，路径在D:\pycharmdata\pythonProject\self\\test\{}\WordCloud_top{}.png
    wcloud: BuildWordCloud构建好的词云
    folder: 文件夹名，命名成分析的对象名，如终末地
    max_words: 统计的词数，default 50
    keywords_df: 返回值，关键词频数表
    """
    plt.figure(figsize=(15, 10))
    plt.imshow(wcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('评论关键词词云图', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig(r'D:\pycharmdata\pythonProject\self\test\{}\WordCloud_top{}.png'.format(folder, max_words), dpi=300, bbox_inches='tight')
    plt.show()
    return


def InfosAnal(cleaned_df, column, folder):
    """
    统计账号信息：等级、性别
    cleaned_df: 清洗、去重后的dataframe
    column: 等级、性别、地区
    folder: 文件夹名，命名成分析的对象名，如终末地
    """
    plt.figure(figsize=(8, 8))
    yn_data = cleaned_df[cleaned_df[column] != '保密']
    counts = yn_data[column].value_counts()
    plt.pie(counts.values, labels=counts.index, autopct='%1.1f%%', startangle=90)
    plt.title(f'用户{column}分布')
    plt.savefig(r'D:\pycharmdata\pythonProject\self\test\{}\{}.png'.format(folder, column))
    plt.show()
    return


def UseTimeAnal(cleaned_df, cat, folder, start_time, end_time, freq='2H', mark=''):
    # TimeAnal(cleaned_df, cat, start_time, end_time, freq='2H')
    """
    嵌套TimeAnal函数，用来进行点赞数、评论数的分析、可视化展示、保存
    保存路径为 r'D:\pycharmdata\pythonProject\self\\test\{}\{}-{}.png'.format(folder, cat, mark)
    参数和TimeAnal设置的一样
    cleaned_df: 清洗、去重后的dataframe
    cat： ‘点赞’ or ‘评论’
    folder: 文件夹名，命名成分析的对象名，如终末地
    start_time: 视频发布时间，如'2025-10-31 20:00:00'
    end_time: 统计结束时间，如'2025-11-02 20:00:00'
    freq: 步长，default'2H'
    mark: 此主题下组图标记，用于进一步分析，str类型，default空
    """
    t_stats = TimeAnal(cleaned_df, cat, start_time, end_time, freq=freq)
    plt.figure(figsize=(15, 8))
    plt.plot(t_stats['时间区间'].astype(str), t_stats[f'总{cat}数'], 
             marker='o', linewidth=2, markersize=6, color='#FF6B6B')
    plt.title(f'{cat}数随时间变化趋势（{freq}区间）', fontsize=14, fontweight='bold')
    plt.ylabel(f'总{cat}数', fontsize=12)
    plt.xlabel('时间区间', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=90, fontsize=8)
    plt.tight_layout()
    plt.savefig(r'D:\pycharmdata\pythonProject\self\test\{}\{}-{}.png'.format(folder, cat, mark))
    plt.show()


def SaveSheets(folder):
    """
    保存到table的sheet里，文件名anal_comments.xlsx
    路径：D:\pycharmdata\pythonProject\self\\test\{}\\anal_comments.xlsx
    folder: 保存的文件夹名
    """
    os.makedirs(r'D:\pycharmdata\pythonProject\self\test\{}'.format(folder))
    with pd.ExcelWriter(r'D:\pycharmdata\pythonProject\self\test\{}\anal_comments.xlsx'.format(folder)) as writer:
        top_accounts.to_excel(writer, sheet_name='前十用户', index=False)
        cleaned_df.to_excel(writer,sheet_name='去重分词后', index=False)
        keywords_df.to_excel(writer, sheet_name = '关键词频次', index=False)
    return

# 应用函数 -----------------------------------------------------------------------------------

# 1 - 终末地
df = OpenCsv(r'D:\pycharmdata\pythonProject\self\test\zmd_comments.csv')
top_accounts = GetTopAccounts(df)
cleaned_df = GetCleanedDf(df)
wcloud, keywords_df = BuildWordCloud(cleaned_df)
SaveSheets('终末地')
UseWordCloud(wcloud, '终末地')
InfosAnal(cleaned_df, '等级', '终末地')
InfosAnal(cleaned_df, '性别', '终末地')
like_anal = UseTimeAnal(cleaned_df, '点赞', '终末地', start_time='2025-10-31 20:00:00', end_time='2025-11-02 20:00:00')
like_anal1 = UseTimeAnal(cleaned_df, '点赞', '终末地', start_time='2025-11-01 02:00:00', end_time='2025-11-02 02:00:00', freq='1H', mark=1)
like_anal11 = UseTimeAnal(cleaned_df, '点赞', '终末地', start_time='2025-11-02 02:00:00', end_time='2025-11-03 02:00:00', freq='1H', mark=2)
like_anal12 = UseTimeAnal(cleaned_df, '点赞', '终末地', start_time='2025-11-02 02:00:00', end_time='2025-11-02 23:00:00', freq='1H', mark=3)
cmt_anal = UseTimeAnal(cleaned_df, '评论', '终末地', start_time='2025-10-31 20:00:00', end_time='2025-11-04 23:59:59')
cmt_anal1 = UseTimeAnal(cleaned_df, '评论', '终末地', start_time='2025-11-01 02:00:00', end_time='2025-11-02 02:00:00', freq='1H', mark=1)
cmt_anal11 = UseTimeAnal(cleaned_df, '评论', '终末地', start_time='2025-11-02 02:00:00', end_time='2025-11-03 02:00:00', freq='1H', mark=2)

# 2 - 终末地玩法
df2 = OpenCsv(r'D:\pycharmdata\pythonProject\self\test\zmdwanfa.csv')
top_accounts2 = GetTopAccounts(df2)
cleaned_df2 = GetCleanedDf(df2)
wcloud2, keywords_df2 = BuildWordCloud(cleaned_df2)
SaveSheets('终末地玩法')
UseWordCloud(wcloud2, '终末地玩法')
InfosAnal(cleaned_df2, '等级', '终末地玩法')
InfosAnal(cleaned_df2, '性别', '终末地玩法')
like_anal2 = UseTimeAnal(cleaned_df2, '点赞', '终末地玩法', start_time='2025-11-12 10:00:00', end_time='2025-11-14 10:00:00')
like_anal3 = UseTimeAnal(cleaned_df2, '点赞', '终末地玩法', start_time='2025-11-12 16:00:00', end_time='2025-11-13 16:00:00', freq='1H', mark=1)
like_anal31 = UseTimeAnal(cleaned_df2, '点赞', '终末地玩法', start_time='2025-11-13 16:00:00', end_time='2025-11-14 16:00:00', freq='1H', mark=2)
cmt_anal2 = UseTimeAnal(cleaned_df2, '评论', '终末地玩法', start_time='2025-11-12 10:00:00', end_time='2025-11-16 10:00:00')
cmt_anal3 = UseTimeAnal(cleaned_df2, '评论', '终末地玩法', start_time='2025-11-12 16:00:00', end_time='2025-11-13 16:00:00', freq='1H', mark=1)
cmt_anal32 = UseTimeAnal(cleaned_df2, '评论', '终末地玩法', start_time='2025-11-13 16:00:00', end_time='2025-11-14 16:00:00', freq='1H', mark=2)
