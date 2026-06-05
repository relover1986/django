
from django.shortcuts import render,HttpResponse,redirect
from .models import *
from .modelform import *
from .func import *

from app01 import models
from app01 import modelform 
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




def ti_list(request):
    title = "辽宁捷祥民用爆破三大员培训题库"
    
    # 检查会话中是否已经存在题目数据
    
    
    def 题数 ():
        
        data = models.Question.objects.filter(category="爆破").values('tihao', 'question_type', 'question', 'options', 'correct_answer')
        df = pd.DataFrame(data)
        
        ident=request.session['info']['ident']
        ident_data = models.UserAnswer.objects.values('ident', 'tihao').filter(ident=ident)
        
        df_ident = pd.DataFrame(ident_data) 

        if len(df_ident) > 0 :      
     

            df = df.merge(df_ident, on='tihao', how='left')
        
            df = df[df['ident'].isnull()]
        df = df[['tihao', 'question_type', 'question', 'options', 'correct_answer']]
        
        题数=len(df)    
        return 题数,df


    
    
  
    
    
    
    
    
    n,df=题数 ()
    
    if 'question_data' not in request.session:

        
        n,df=题数 ()
        
         
        
        df.columns = ['tihao', '题型', '题目', '选项', '正确答案']

        # 获取单选题数据，若数量不足5个则取全部
        df_单选题 = df[df['题型'] == '单选题']
        n_单选题 = min(len(df_单选题), 5)
        df_单选题 = df_单选题.sample(n=n_单选题)
        df_单选题['序号'] = range(1, n_单选题 + 1)

        # 获取多选题数据，若数量不足5个则取全部，若没有则为空DataFrame
        df_多选题 = df[df['题型'] == '多选题']
        n_多选题 = min(len(df_多选题), 5)
        df_多选题 = df_多选题.sample(n=n_多选题)
        df_多选题['序号'] = range(1, n_多选题 + 1)

        # 获取判断题数据，若数量不足10个则取全部
        df_判断题 = df[df['题型'] == '判断题']
        n_判断题 = min(len(df_判断题), 10)
        df_判断题 = df_判断题.sample(n=n_判断题)
        df_判断题['序号'] = range(1, n_判断题 + 1)

        df = pd.concat([df_单选题, df_多选题, df_判断题])
        df = df[['序号', 'tihao', '题型', '题目', '选项', '正确答案']]
        
        # 将生成的题目数据存储在会话中
        request.session['question_data'] = df.to_dict(orient='records')
    
    # 从会话中获取题目数据
    question_data = request.session['question_data']
    df = pd.DataFrame(question_data)
    
    df2 = df.copy()
    global df3
    df3 = df.copy()
    del df2['正确答案']
    
    df3['题号'] = df3['题型'].str.replace('题', '') + df3['序号'].astype('str')
    
    print('get------------')
    
    lst = dframe(question_data)
    cols = []
 
    data = df2.values
    for i in lst:
        cols.append({'age': i})
    cols[5] = {'age': '你的答案'}
    print(cols)
 
    username = request.session['info']['name']
   
    
    if request.method == "GET":
        form = modelform.Ti()
        return render(request, 'baopo_ti.html', {"form": form, "data": data, "cols": cols, "title": title + '--' + username+'还有' + str(n) + '题'})
    
    form = modelform.Ti(data=request.POST)
    
    if form.is_valid():
        print('post------------')
        data = []
        for i, v in enumerate(models.Tihao.objects.values('题号')):
            da = request.POST.getlist(v['题号'])
            da = ''.join(da)
            df = pd.DataFrame({'题号': v['题号'], '我的答案': str(da)}, index=[0])
            data.append(df)
        
        df = pd.concat(data)
        df = df3.merge(df, on='题号', how='left')
        df = df[['tihao', '题号', '题目', '选项', '正确答案', '我的答案']]
        
        df['我的答案'] = df['我的答案'].str.replace('[^a-zA-Z0-9\u4e00-\u9fa5]', '')
        
        df['得分'] = '正确'
        df.loc[df['我的答案'] != df['正确答案'], '得分'] = "错误"
        df_right = df[df['得分'] == "正确"]
        print(df_right)
        df_right = df_right[['tihao']]
      
        df_right['ti_type'] = '爆破'
        df_right['date'] = date
        df_right['ident'] = request.session['info']['ident']
        
        with sl.connect(previous_folder_path/'db.sqlite3') as con:
            df_right.to_sql('app01_useranswer', con, index=False, if_exists='append')
        
        df = df[df['得分'] == "错误"]
        df['分值'] = 1
        df.loc[df['题号'].str.contains('多选'), '分值'] = 2
        
        fens = df['分值'].sum()
        项目 = '扣分--' + str(fens)
        
        df = df[['题号', '题目', '选项', '正确答案', '我的答案']]
        myechart1 = table(df, 项目).render_embed()
        
        return render(request, "chart_qi.html", {'项目': 项目, 'myechart1': myechart1})
    
    else:
        form.errors
        title = form.errors
        return render(request, 'baopo_ti.html', {"title": title, "form": form})






def questions_reload(request):    

    
    if 'question_data' in request.session:
        del request.session['question_data']    

    return redirect('/home/ti')

##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################


def wxpzxti_list(request):
    title = "辽宁捷祥危险品装卸培训题库"
    
    # 检查会话中是否已经存在题目数据
    
    
    def 题数 ():
        
        data = models.Question.objects.filter(category="危装").values('tihao', 'question_type', 'question', 'options', 'correct_answer')
        df = pd.DataFrame(data)
        
        ident=request.session['info']['ident']
        ident_data = models.UserAnswer.objects.values('ident', 'tihao').filter(ident=ident)
        
        df_ident = pd.DataFrame(ident_data) 

        if len(df_ident) > 0 :      
     

            df = df.merge(df_ident, on='tihao', how='left')
        
            df = df[df['ident'].isnull()]
        df = df[['tihao', 'question_type', 'question', 'options', 'correct_answer']]
        
        题数=len(df)    
        return 题数,df


    
    
  
    
    
    
    
    
    n,df=题数 ()
    
    if 'question_data' not in request.session:

        
        n,df=题数 ()
        
         
        
        df.columns = ['tihao', '题型', '题目', '选项', '正确答案']

        # 获取单选题数据，若数量不足5个则取全部
        df_单选题 = df[df['题型'] == '单选题']
        n_单选题 = min(len(df_单选题), 5)
        df_单选题 = df_单选题.sample(n=n_单选题)
        df_单选题['序号'] = range(1, n_单选题 + 1)

        # 获取多选题数据，若数量不足5个则取全部，若没有则为空DataFrame
        df_多选题 = df[df['题型'] == '多选题']
        n_多选题 = min(len(df_多选题), 5)
        df_多选题 = df_多选题.sample(n=n_多选题)
        df_多选题['序号'] = range(1, n_多选题 + 1)

        # 获取判断题数据，若数量不足10个则取全部
        df_判断题 = df[df['题型'] == '判断题']
        n_判断题 = min(len(df_判断题), 10)
        df_判断题 = df_判断题.sample(n=n_判断题)
        df_判断题['序号'] = range(1, n_判断题 + 1)

        df = pd.concat([df_单选题, df_多选题, df_判断题])

        
        df = df[['序号', 'tihao', '题型', '题目', '选项', '正确答案']]
        
        # 将生成的题目数据存储在会话中
        request.session['question_data'] = df.to_dict(orient='records')
    
    # 从会话中获取题目数据
    question_data = request.session['question_data']
    df = pd.DataFrame(question_data)
    
    df2 = df.copy()
    global df3
    df3 = df.copy()
    del df2['正确答案']
    
    df3['题号'] = df3['题型'].str.replace('题', '') + df3['序号'].astype('str')
    
    print('get------------')
    
    lst = dframe(question_data)
    cols = []
 
    data = df2.values
    for i in lst:
        cols.append({'age': i})
    cols[5] = {'age': '你的答案'}
    print(cols)
 
    username = request.session['info']['name']
   
    
    if request.method == "GET":
        form = modelform.Ti1()
        url='/home/ti_reload'
        return render(request, 'wxpzx_ti.html', {"form": form, "data": data, "cols": cols, "title": title + '--' + username+'还有' + str(n) + '题','lj':url})
    
    form = modelform.Ti1(data=request.POST)
    
    if form.is_valid():
        print('post------------')
        data = []
        for i, v in enumerate(models.Tihao.objects.values('题号')):
            da = request.POST.getlist(v['题号'])
            da = ''.join(da)
            df = pd.DataFrame({'题号': v['题号'], '我的答案': str(da)}, index=[0])
            data.append(df)
        
        df = pd.concat(data)
        
        print(df3)
        df = df3.merge(df, on='题号', how='left')
        df = df[['tihao', '题号', '题目', '选项', '正确答案', '我的答案']]
        
        df['我的答案'] = df['我的答案'].str.replace('[^a-zA-Z0-9\u4e00-\u9fa5]', '')
        
        df['得分'] = '正确'
        df.loc[df['我的答案'] != df['正确答案'], '得分'] = "错误"
        df_right = df[df['得分'] == "正确"]
        print(df_right)
        df_right = df_right[['tihao']]
      
        df_right['ti_type'] = '危险品装卸'
        df_right['date'] = date
        df_right['ident'] = request.session['info']['ident']
        
        with sl.connect(previous_folder_path/'db.sqlite3') as con:
            df_right.to_sql('app01_useranswer', con, index=False, if_exists='append')
        
        df = df[df['得分'] == "错误"]
        df['分值'] = 1
        df.loc[df['题号'].str.contains('多选'), '分值'] = 2
        
        fens = df['分值'].sum()
        项目 = '扣分--' + str(fens)
        
        df = df[['题号', '题目', '选项', '正确答案', '我的答案']]
        myechart1 = table(df, 项目).render_embed()
        
        return render(request, "chart_qi.html", {'项目': 项目, 'myechart1': myechart1})
    
    else:
        print(df3)
        form.errors
        title = form.errors
        return render(request, 'wxpzx_ti.html', {"title": title, "form": form})






def wxpzxquestions_reload(request):    

    
    if 'question_data' in request.session:
        del request.session['question_data']    

    return redirect('/home/wxpzxti')






333333333333333333333333333333333333333333













def jskjgti_list(request):
    title = "辽宁捷祥非煤矿山井工培训题库"
    
    # 检查会话中是否已经存在题目数据
    
    
    def 题数 ():
        
        data = models.Question.objects.filter(category="井工").values('tihao', 'question_type', 'question', 'options', 'correct_answer')
        df = pd.DataFrame(data)
        
        ident=request.session['info']['ident']
        ident_data = models.UserAnswer.objects.values('ident', 'tihao').filter(ident=ident)
        
        df_ident = pd.DataFrame(ident_data) 

        if len(df_ident) > 0 :      
     

            df = df.merge(df_ident, on='tihao', how='left')
        
            df = df[df['ident'].isnull()]
        df = df[['tihao', 'question_type', 'question', 'options', 'correct_answer']]
        
        题数=len(df)    
        return 题数,df


    
    
  
    
    
    
    
    
    n,df=题数 ()
    
    if 'question_data' not in request.session:

        
        n,df=题数 ()
        
         
        
        df.columns = ['tihao', '题型', '题目', '选项', '正确答案']

        # 获取单选题数据，若数量不足5个则取全部
        df_单选题 = df[df['题型'] == '单选题']
        n_单选题 = min(len(df_单选题), 5)
        df_单选题 = df_单选题.sample(n=n_单选题)
        df_单选题['序号'] = range(1, n_单选题 + 1)

        # 获取多选题数据，若数量不足5个则取全部，若没有则为空DataFrame
        df_多选题 = df[df['题型'] == '多选题']
        n_多选题 = min(len(df_多选题), 5)
        df_多选题 = df_多选题.sample(n=n_多选题)
        df_多选题['序号'] = range(1, n_多选题 + 1)

        # 获取判断题数据，若数量不足10个则取全部
        df_判断题 = df[df['题型'] == '判断题']
        n_判断题 = min(len(df_判断题), 10)
        df_判断题 = df_判断题.sample(n=n_判断题)
        df_判断题['序号'] = range(1, n_判断题 + 1)

        df = pd.concat([df_单选题, df_多选题, df_判断题])
        df = df[['序号', 'tihao', '题型', '题目', '选项', '正确答案']]
        
        # 将生成的题目数据存储在会话中
        request.session['question_data'] = df.to_dict(orient='records')
    
    # 从会话中获取题目数据
    question_data = request.session['question_data']
    df = pd.DataFrame(question_data)
    
    df2 = df.copy()
    global df3
    df3 = df.copy()
    del df2['正确答案']
    
    df3['题号'] = df3['题型'].str.replace('题', '') + df3['序号'].astype('str')
    
    print('get------------')
    
    lst = dframe(question_data)
    cols = []
 
    data = df2.values
    for i in lst:
        cols.append({'age': i})
    cols[5] = {'age': '你的答案'}
    print(cols)
 
    username = request.session['info']['name']
   
    
    if request.method == "GET":
        form = modelform.Ti()
        url='/home/ti_reload'
        return render(request, 'jskjg_ti.html', {"form": form, "data": data, "cols": cols, "title": title + '--' + username+'还有' + str(n) + '题','lj':url})
    
    form = modelform.Ti(data=request.POST)
    
    if form.is_valid():
        print('post------------')
        data = []
        for i, v in enumerate(models.Tihao.objects.values('题号')):
            da = request.POST.getlist(v['题号'])
            da = ''.join(da)
            df = pd.DataFrame({'题号': v['题号'], '我的答案': str(da)}, index=[0])
            data.append(df)
        
        df = pd.concat(data)
        df = df3.merge(df, on='题号', how='left')
        df = df[['tihao', '题号', '题目', '选项', '正确答案', '我的答案']]
        
        df['我的答案'] = df['我的答案'].str.replace('[^a-zA-Z0-9\u4e00-\u9fa5]', '')
        
        df['得分'] = '正确'
        df.loc[df['我的答案'] != df['正确答案'], '得分'] = "错误"
        df_right = df[df['得分'] == "正确"]
        print(df_right)
        df_right = df_right[['tihao']]
      
        df_right['ti_type'] = '煤矿山井工'
        df_right['date'] = date
        df_right['ident'] = request.session['info']['ident']
        
        with sl.connect(previous_folder_path/'db.sqlite3') as con:
            df_right.to_sql('app01_useranswer', con, index=False, if_exists='append')
        
        df = df[df['得分'] == "错误"]
        df['分值'] = 1
        df.loc[df['题号'].str.contains('多选'), '分值'] = 2
        
        fens = df['分值'].sum()
        项目 = '扣分--' + str(fens)
        
        df = df[['题号', '题目', '选项', '正确答案', '我的答案']]
        myechart1 = table(df, 项目).render_embed()
        
        return render(request, "chart_qi.html", {'项目': 项目, 'myechart1': myechart1})
    
    else:
        form.errors
        title = form.errors
        return render(request, 'jskjg_ti.html', {"title": title, "form": form})






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
