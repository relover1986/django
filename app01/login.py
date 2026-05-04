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
        print('Form is valid, cleaned data:', form.cleaned_data)
        user=models.Admin.objects.filter(**form.cleaned_data).first()        
        print('Found user:', user)
        if not user :
            print('User not found, adding errors')
            form.add_error("password","用户名或密码错误")
            form.add_error("ident","用户名或密码错误")          

            return render(request,'create.html',{'form':form})
        


        # 设置时区为北京时间并加上八小时role
        now = arrow.now().shift(hours=0).strftime("%Y-%m-%d %H:%M:%S")

        
        request.session['info']={'ident':user.ident,'name':user.username,'role':user.role,'time':arrow.now().shift(hours=0).strftime("%Y-%m-%d %H:%M:%S"),'类型':'登录'}
        request.session.set_expiry(60*60*24*7)
        
        user_ip = request.META.get('REMOTE_ADDR')  
        print('User IP address:', user_ip)      
        print('Creating login record...')
        try:
            models.LoginRecords.objects.create(
                ident=user.ident,
                name=user.username,
                job=user.role,
                type='登录',
                ip=user_ip
            )
            print('Login record created successfully')
        except Exception as e:
            print('Error creating login record:', str(e))
         
        

        if user.role=='新入职':
            return redirect('/home/ti')
            
        return redirect('/home/')
    return render(request,'create.html',{'form':form})

def logout(request):    

    
    now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    
    
    if 'info' in request.session:
        user = request.session['info']
    
        models.LoginRecords.objects.create(ident=user['ident'],name=user['name'],job=user['role'],time=now,type='登出')
    print('登出')
    request.session.clear()
    return redirect('/login/')