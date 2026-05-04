#%%
#%%
import sqlite3 as sl
import pandas as pd
from pathlib import Path
import hashlib
import random
def md5(str):
    salt='poxcc'
    obj=hashlib.md5(salt.encode('utf-8'))
    obj.update(str.encode('utf-8'))
    return obj.hexdigest()

# 获取当前文件的路径
current_file_path = Path(__file__)

# 获取上一级目录的路径
parent_directory_path = current_file_path.parent

# 获取上两级目录的路径
grandparent_directory_path = parent_directory_path.parent

# # 打印上两级目录的路径
# print(grandparent_directory_path)

# #%%



# # def generate_password():
# #     # 生成一个6位随机数字密码
# #     password = ''.join(random.choices('0123456789', k=6))
# #     return password

# # # 调用函数生成密码
# # password = generate_password()
# # print(password)




# # df.columns = ['id', 'question_type', 'ident', 'question', 'options', 'correct_answer']
# # df=df.fillna('')
# # df
# # #%%

# df=pd.read_excel('D:/OneDrive/A捷祥爆破资料/危险品装卸答案.xlsx')
# df=df.fillna('')
# print(df.columns)
# #%%

# with sl.connect(grandparent_directory_path/'db.sqlite3') as con:
    
    
#     # df=pd.read_sql('''
#     #     SELECT *
#     #     FROM app01_jskjgquestion
#     # ''', con)   
#     # print(df.columns)
   
    
#     df.to_sql('app01_wxpzxquestion', con, index=False, if_exists='append')

# df
















#%%


model_name='admin'
# model_name='ExplosiveInventoryItem'
df = pd.read_excel('/Users/sunhongchen/Downloads/admin.xlsx')
df['password'] = df['password'].apply(lambda x: md5(str(x)))



with sl.connect(grandparent_directory_path/'db.sqlite3') as con:
    df.to_sql(f'app01_{model_name.lower()}', con, index=False, if_exists='append')
#%%
# 使用with语句连接到数据库
# with sl.connect(grandparent_directory_path/'db.sqlite3') as con:
#     cursor = con.cursor()
    
#     # 执行DELETE语句
#     cursor.execute(f'DELETE FROM app01_{model_name.lower()}')
    
#     # 提交更改
#     con.commit()



with sl.connect(grandparent_directory_path/'db.sqlite3') as con:
 

    
    df=pd.read_sql(f'''
        SELECT *
        FROM app01_{model_name.lower()}
    ''', con)

df
#%%

















df=pd.read_excel('/Users/sunhongchen/Library/CloudStorage/OneDrive-个人/A捷祥爆破资料/出库/项目人员.xlsx')
df.columns = ['category', 'content']
df
#%%



with sl.connect(grandparent_directory_path/'db.sqlite3') as con:
    df.to_sql(f'app01_{model_name.lower()}', con, index=False, if_exists='append')
#%%