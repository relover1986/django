from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class M1(MiddlewareMixin):

    def process_request(self, request):
        print('M1 middleware processing request:', request.path_info)
        print('Session keys:', list(request.session.keys()))
        print('Session info:', request.session.get("info"))
        
        if request.path_info == '/login/' or request.path_info == '/staff_login/' or request.path_info.startswith('/api/') or request.path_info == '/manifest.json' or request.path_info == '/sw.js':
            print('Path is login or api, returning')
            return

        info_dict = request.session.get("info")
    

        if info_dict:
            print('Session info found, returning')
            return

        print('Session info not found, redirecting to login')
        return redirect('/login/')



    
    
class M2(MiddlewareMixin):

    def process_request(self, request):
        if 'ti' in request.path_info :

            return
        
        elif 'candidateprofile_add' in request.path_info :
            return     
        elif 'explosivestaff_add' in request.path_info :
            return     
        elif 'photo_add' in request.path_info or 'photo_list' in request.path_info:#weighingrecord_list/
            return                    
        elif 'weighingrecord_add' in request.path_info or 'weighingrecord_list' in request.path_info:#weighingrecord_list/
            return        
        elif 'blastingcertificate_add' in request.path_info or 'blastingcertificate_list' in request.path_info:#weighingrecord_list/
            return       

        elif request.path_info == '/logout/':
            return



        info_dict = request.session.get("info")
        if info_dict:

            job = info_dict.get('role')
            if job == 'staff':
                # staff 只能访问答题页、登出和登录页
                if any(p in request.path_info for p in ['/home/baopo_ti_new', '/logout/', '/staff_login/']):
                    return
                return redirect('/home/baopo_ti_new')

            if '新入职'  in job:
                # 如果会话中没有信息，可能需要重定向到登录页面
                return redirect('/home/ti')            
                      
            elif '面试'  in job:
                # 如果会话中没有信息，可能需要重定向到登录页面
                return redirect('/home/candidateprofile_add') 
            
            elif '三大员考试'  in job:
                # 如果会话中没有信息，可能需要重定向到登录页面
                return redirect('/home/blastingcertificate_add')           
            
            elif '访客'  in job:
                # 如果会话中没有信息，可能需要重定向到登录页面
                return redirect('/home/photo_add')      
            elif '大车司机'  in job:
                # 如果会话中没有信息，可能需要重定向到登录页面
                return redirect('/home/weighingrecord_add')              
            
            elif '安全员'  in job:
                return redirect('/home/blasting_summary_add/') 
            
                    
            
            elif '学前班同学'  in job:
            # 如果会话中没有信息，可能需要重定向到登录页面
                return redirect('/home/photo_add')                
                            
            else:
                # 确保重定向的目标URL正确
                return 
            
        return 
    
    
    
    
    
    
    
    
class CorsOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            from django.http import HttpResponse
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,X-CSRFToken'
            return response
        return self.get_response(request)