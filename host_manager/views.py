from django.contrib.auth.decorators import login_required
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import UpdateView
from django.views.generic.edit import DeleteView

from .models import Host


# 跳转到host页面
@login_required(login_url="/login")
def go_host_manager(request):
    return render(request, "host_manager/host_list.html")


# 获取host列表APi
@login_required(login_url="/login")
def get_hosts_list_api(request):
    # 支持按主机名、IP地址和用户名搜索
    """

    # 验证是否登录

    逻辑还没写完
    """

    if not request.user.is_authenticated:
        json_data = {
            'code': 0,
            'count': 0,
            # 'data': data
        }
        return JsonResponse(json_data)

    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 5)
    # 从GET参数获取搜索关键词
    keyword = request.GET.get('host_search', '').strip()

    if not keyword:
        # 如果没有关键词，返回所有主机
        # hosts = Host.objects.all().values()
        hosts = Host.objects.filter(users=request.user)

    else:
        # 使用Q对象实现多字段联合搜索
        query = Q(hostname__icontains=keyword) | \
                Q(ip__icontains=keyword) | \
                Q(username__icontains=keyword) | \
                Q(port__icontains=keyword)

        hosts = Host.objects.filter(query,users=request.user)
    paginator = Paginator(hosts, limit)
    try:
        page_hosts = paginator.page(page)
    except PageNotAnInteger:
        page_hosts = paginator.page(1)
    except EmptyPage:
        page_hosts = paginator.page(paginator.num_pages)
    # 初始化空列表

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


# 创建主机
@method_decorator(login_required(login_url="/login"), name='dispatch')
class HostCreateView(View):
    template_name = 'host_manager/create_host.html'

    def get(self, request, *args, **kwargs):
        # 返回创建主机的页面
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
        host.users.add(current_user)

        # 跳转成功页面
        return redirect(reverse('host_manager:go_host_manager'))


# 更新主机
@method_decorator(login_required(login_url="/login"), name='dispatch')
class HostUpdateView(UpdateView):
    model = Host
    fields = ['hostname', 'ip', 'port', 'username']
    template_name = 'host_manager/create_host.html'
    success_url = reverse_lazy('host_manager:go_host_manager')


# 删除主机
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


# 批量删除
def batch_delete(request):
    """
    批量删除主机视图函数
    """
    # 确保只处理POST请求
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': '仅支持POST请求'
        }, status=405)

    # 获取要删除的主机ID列表
    host_ids = request.POST.getlist('host_ids[]')

    if not host_ids:
        # 如果没有选择任何主机
        return JsonResponse({
            'status': 'error',
            'message': '请选择要删除的主机'
        })

    try:
        # 转换ID为整数
        host_ids = [int(id) for id in host_ids]
    except ValueError:
        # 处理无效ID格式
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': '无效的主机ID格式'
            })

    try:

        # 获取当前用户有权删除的主机
        hosts = Host.objects.filter(
            id__in=host_ids,
            users=request.user  # 确保用户只能删除自己的主机
        )

        # 记录删除的主机数量
        deleted_count = hosts.count()

        if deleted_count == 0:
            # 如果没有找到符合条件的记录

            return JsonResponse({
                'status': 'error',
                'message': '没有找到符合条件的主机'
            })

        # 执行批量删除
        hosts.delete()

        # 返回成功响应

        return JsonResponse({
            'status': 'success',
            'message': f'成功删除 {deleted_count} 台主机'
        })



    except Exception as e:
        # 处理删除过程中的异常
        error_message = f'删除失败: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': error_message
            })
