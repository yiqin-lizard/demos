import pandas as pd
import numpy as np

'''
DataFrame 表示一个矩形数据表，并包含一个有序的命名列集合，每个列可以是不同的值类型（数字、字符串、布尔值等）
DataFrame 同时具有行索引和列索引;它可以被认为是一个 Series 的字典，所有 Series 都共享同一个索引。
'''

# 1. 创建和删除
# 最常见的一种是从等长列表或 NumPy 数组的字典中构造，可以重复：
data1 = {
    'State': ["Ohio", "Ohio", "Beijing", "Tokyo"],
    'Population': ['1000', '1500', '2000', '2500'],
    'Country': ['USA', "USA", 'CHI', "JAN"]
}
frame1 = pd.DataFrame(data1)
''' # 会自动标记索引，从0开始
     State Population Country
0     Ohio       1000     USA
1     Ohio       1500     USA
2  Beijing       2000     CHI
3    Tokyo       2500     JAN
'''
ind = ["a", "b", "c", "d"]
frame1_1 = pd.DataFrame(data1, index=ind)       # 也可以指定索引
'''
     State Population Country
a     Ohio       1000     USA
b     Ohio       1500     USA
c  Beijing       2000     CHI
d    Tokyo       2500     JAN
'''
del frame1_1['Population']
del frame1_1
# 将嵌套字典传递给DataFrame，pandas会将外部字典键解释为列，将内部键解释为行索引
data2 = {
    "Ohio": {2000: 1.5, 2001: 1.7, 2002: 3.6},
    "Nevada": {2001: 2.4, 2002: 2.9}
}
frame2 = pd.DataFrame(data2)
'''
      Ohio  Nevada
2000   1.5     NaN
2001   1.7     2.4
2002   3.6     2.9
'''

# 2. 简略返回
frame1.head()       # 前五
frame1.tail()       # 后五
print(frame1.columns)        # 返回表头  Index(['State', 'Population', 'Country'], dtype='object')

# 3. 指定序列排列
col = ["Population", "State", 'new_1']
frame1_2 = pd.DataFrame(data1, columns=col)
'''     # 空值为nan，重新排列各列
  Population    State new_1
0       1000     Ohio   NaN
1       1500     Ohio   NaN
2       2000  Beijing   NaN
3       2500    Tokyo   NaN
'''

# 4. 检索列，两种方法同样效果。如果列名不存在，自动创建新列
print(frame1.State)
print(frame1['State'])
'''
0       Ohio
1       Ohio
2    Beijing
3      Tokyo
Name: State, dtype: object
'''

# 5. 检索行
print(frame1.loc[1])        # or  frame1.iloc[1]
'''
State         Ohio
Population    1500
Country        USA
Name: 1, dtype: object
'''

# 6. 修改/新增列
frame1['is_Ohio'] = pd.Series(np.arange(3.), index=[0, 2, 3])
'''     # 空值被nan自动填充
     State Population Country  is_Ohio
0     Ohio       1000     USA      0.0
1     Ohio       1500     USA      NaN
2  Beijing       2000     CHI      1.0
3    Tokyo       2500     JAN      2.0
'''
# 7. 转置
print(frame1.T)
'''
               0     1        2      3
State       Ohio  Ohio  Beijing  Tokyo
Population  1000  1500     2000   2500
Country      USA   USA      CHI    JAN
is_Ohio      0.0   NaN      1.0    2.0
'''

# 8. 命名
frame1.name = 'total_name'
frame1.columns.name = 'col_name'
frame1.index.name = 'ind_name'
'''
col_name    State Population Country  is_Ohio
ind_name                                     
0            Ohio       1000     USA      0.0
1            Ohio       1500     USA      NaN
2         Beijing       2000     CHI      1.0
3           Tokyo       2500     JAN      2.0
'''
