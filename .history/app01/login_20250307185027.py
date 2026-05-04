#%%
from django.shortcuts import render,HttpResponse,redirect
from app01 import models
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.decorators.csrf import csrf_protect
from .func import *
from app01 import modelform
#%%
import arrow 
from django.utils import timezone
date= arrow.now().shift(days=1).format('YYYY-MM-DD')



@csrf_protect
def login(request):
    title='登录'
    if request.method == "GET":
        form = modelform.Login()
        return render(request,'create.html',{"form":form,"title":title })

    form=modelform.Login(data=request.POST)


    
    if form.is_valid():
        user=models.Admin.objects.filter(**form.cleaned_data).first()        
        if not user :
 
            form.add_error("password","用户名或密码错误")
            form.add_error("ident","用户名或密码错误")          

            return render(request,'create.html',{'form':form})
        


        # 设置时区为北京时间并加上八小时
        now = arrow.now().shift(hours=0).strftime("%Y-%m-%d %H:%M:%S")

        
        request.session['info']={'ident':user.ident,'name':user.username,'role':user.身份,'time':arrow.now().shift(hours=0).strftime("%Y-%m-%d %H:%M:%S"),'类型':'登录'}
        request.session.set_expiry(60*60*24*7)
        
        user_ip = request.META.get('REMOTE_ADDR')  
        print('User IP address:', user_ip)      
        models.LoginRecords.objects.create(ident=user.ident,name=user.username,job=user.身份,time=arrow.now().shift(hours=0).strftime("%Y-%m-%d %H:%M:%S"),type='登录',ip=user_ip)
         
        

        if user.身份=='新入职':
            return redirect('/home/ti')
            
        return redirect('/home')
    return render(request,'create.html',{'form':form})

def logout(request):    

    
    now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user=request.session['info']
    request.session.clear()
    models.LoginRecords.objects.create(ident=user['ident'],name=user['name'],job=user['role'],time=now,type='登出')
    print('登出')
    return redirect('/login/')