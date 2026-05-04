from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class M1(MiddlewareMixin):

    def process_request(self, request):
    
        if request.path_info == '/login/':
       
            return

        info_dict = request.session.get("info")
    

        if info_dict:
            
            return

        return redirect('/login/')



    
    
class M2(MiddlewareMixin):

    def process_request(self, request):
        if 'ti' in request.path_info :
            # print('++++++++++++')
            return

        elif request.path_info == '/logout/':
            return

        info_dict = request.session.get("info")
        if info_dict:
            
            job = info_dict.get('身份')
          
            if '新入职' not in job:
                print('========++++++++++')
                # 确保重定向的目标URL正确
                return 
            else:
                # 如果会话中没有信息，可能需要重定向到登录页面
                return redirect('/home/ti')
            
        return 
