from django.contrib.auth.decorators import login_required
from django.core import paginator
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.edit import DeleteView

from django.urls import reverse_lazy, reverse
from .models import Host

@login_required(login_url="/login")
def go_host_manager(request):
    return render(request, "host_manager/host_list.html")

@login_required(login_url="/login")
def get_hosts_list_api(request):
    # 验证是否登录
    print(request.user.is_authenticated)
    if not request.user.is_authenticated:
        json_data = {
            'code': 0,
            'count': 0,
            # 'data': data
        }
        return JsonResponse(json_data)
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 5)
    hosts = Host.objects.filter(users=request.user)
    # hosts = Host.objects.values()  # 获取所有任务并按创建时间排序
    paginator = Paginator(hosts, limit)
    try:
        page_hosts = paginator.page(page)
    except PageNotAnInteger:
        page_hosts = paginator.page(1)
    except EmptyPage:
        page_hosts = paginator.page(paginator.num_pages)
    # 初始化空列表
    print(1)
    data = []


    for host in page_hosts:
        data.append({
            'id': host.id,
            'hostname': host.hostname,
            'ip': host.ip,
            'port': host.port,
            'username': host.username,
        })
    json_data = {
        'code': 0,
        'count': paginator.count,
        'data': data
    }

    return JsonResponse(json_data)
@method_decorator(login_required(login_url="/login"), name='dispatch')
class HostCreateView(View):
    template_name = 'host_manager/create_host.html'

    def get(self, request, *args, **kwargs):
        # 显示空表单页面（可选）
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # 从 POST 数据中获取字段值
        hostname = request.POST.get('hostname')
        ip = request.POST.get('ip')
        port = request.POST.get('port', 22)
        username = request.POST.get('username')

        # 创建主机对象
        host = Host.objects.create(
            hostname=hostname,
            ip=ip,
            port=port,
            username=username
        )

        # 将当前用户添加到 users 多对多字段中
        current_user = request.user
        print(type(current_user))
        host.users.add(current_user)

        # 可选：添加其他指定用户（例如从前端传来的用户ID列表）
        # user_ids = request.POST.getlist('user_ids')
        # users = User.objects.filter(id__in=user_ids)
        # host.users.add(*users)

        # 跳转成功页面
        return redirect(reverse('host_manager:go_host_manager'))

@method_decorator(login_required(login_url="/login"), name='dispatch')
class HostUpdateView(UpdateView):
    model = Host
    fields = ['hostname', 'ip', 'port', 'username']
    template_name = 'host_manager/create_host.html'
    success_url = reverse_lazy('host_manager:go_host_manager')

@method_decorator(login_required(login_url="/login"), name='dispatch')
class HostDeleteView(DeleteView):
    model = Host
    context_object_name = 'host'

    # success_url = reverse_lazy('host_manager:host_list')
    def get_success_url(self):
        # 直接返回 None 或者 raise 不触发跳转
        return None  # 或者 raise NotImplementedError("No redirect needed")

    # 重新方法禁止跳转 返回json
    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': 'success'})
