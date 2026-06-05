
from django.shortcuts import render,HttpResponse,redirect
from app01.models import *
from app01.modelform import *
from app01.func import *

from app01 import models
from app01 import modelform as _mf 
import datetime
import arrow 
import pandas as pd
import sqlite3 as sl
import pandas as pd
from sqlite3 import IntegrityError
import random
from pyecharts.charts import Bar
from pyecharts import options as opts
from django.shortcuts import render
import sqlite3 as sl




from pathlib import Path

# 获取当前文件的路径
current_file_path = Path(__file__)

# 获取上一个文件夹的路径
previous_folder_path = current_file_path.parent.parent

print(previous_folder_path)







date= arrow.now().shift(days=0).format('YYYY-MM-DD')
#login




def questions_reload(request):    

    
    if 'question_data' in request.session:
        del request.session['question_data']    

    return redirect('/home/ti')

##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################


def wxpzxquestions_reload(request):    

    
    if 'question_data' in request.session:
        del request.session['question_data']    

    return redirect('/home/wxpzxti')






333333333333333333333333333333333333333333













def jskjgquestions_reload(request):    

    
    if 'question_data' in request.session:
        del request.session['question_data']    

    return redirect('/home/jskjgti')








def grades(request):
    # 连接数据库并读取数据
    with sl.connect(previous_folder_path/'db.sqlite3') as con:
        sql = "select * from app01_useranswer"
        df = pd.read_sql(sql, con)       
        
        sql = "select * from app01_admin"
        
        df_admin = pd.read_sql(sql, con)
    df=pd.merge(df,df_admin,on='ident',how='left')
    df = df.drop_duplicates(subset=['tihao', 'ti_type'], keep='first')
    
    df = df[['ident', 'username', 'date', 'ti_type']]
    df=df[~df['username'].isnull()]
    



    # 数据处理
    df['数量'] = 1
    df = df.groupby(['username', 'date']).agg({'数量': 'sum'}).reset_index()
    
    df = df.sort_values(by=['username', 'date'], ascending=[True, False])


# 创建DataFrame
    # df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    # 按date和username整理数据
    date_list = sorted(df['date'].unique())
    name_list = df['username'].unique()

    # 创建柱状图数据
    bar_data = {}
    for name in name_list:
        bar_data[name] = df[df['username'] == name].set_index('date')['数量'].reindex(date_list, fill_value=0).tolist()

    # 绘制柱状图
    bar = Bar()
    bar.add_xaxis(date_list)  # x轴为date

    # 添加每个username的数据
    for name in name_list:
        bar.add_yaxis(name, bar_data[name])

    # 设置全局配置
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="每日数量统计"),
        xaxis_opts=opts.AxisOpts(name="date"),
        yaxis_opts=opts.AxisOpts(name="数量"),
        legend_opts=opts.LegendOpts(pos_top="10%")
    )

    # 渲染图表
    chart_html=bar.render_embed()

    return render(request, "chart_qi.html", {'myechart1': chart_html})



   
   
   # 删除会话中的 question_data
