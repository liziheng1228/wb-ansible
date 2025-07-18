from django.contrib.auth.decorators import login_required
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
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

        hosts = Host.objects.filter(query, users=request.user)
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
from django.http import JsonResponse
from django.core.exceptions import ValidationError


@method_decorator(login_required(login_url="/login"), name='dispatch')
class HostCreateView(View):
    template_name = 'host_manager/create_host.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # 获取参数
        hostname = request.POST.get('hostname')
        ip = request.POST.get('ip')
        port = request.POST.get('port', 22)
        username = request.POST.get('username')
        ssh_password = request.POST.get('ssh_password')  # 新增字段
        become_password = request.POST.get('become_password')  # 新增字段
        pk = request.POST.get('pk')  # 新增字段：用于判断是否为编辑

        # 类型转换
        try:
            port = int(port)
        except (TypeError, ValueError):
            return JsonResponse({'error': '端口号必须为整数'}, status=400)

        # 参数校验
        if not all([hostname, ip, username]):
            return JsonResponse({'error': '请填写所有必填字段'}, status=400)

        # 统一错误处理
        try:
            if pk:
                host = get_object_or_404(Host, pk=pk, users=request.user)
                if Host.objects.filter(users=request.user, ip=ip).exclude(pk=pk).exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': f'您已有一个 {ip} 主机'
                    }, status=400)
            else:
                if Host.objects.filter(users=request.user, ip=ip).exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': '该用户已存在相同IP的主机'
                    }, status=400)
                host = Host()

            # 设置字段
            host.hostname = hostname
            host.ip = ip
            host.port = port
            host.username = username
            # 设置并加密密码（注意：即使为空也保留旧值）
            if ssh_password:
                host.set_ssh_password(ssh_password)
            if become_password:
                host.set_become_password(become_password)
            # 保存
            host.save()
            # 第一次创建时绑定用户
            if not pk:
                host.users.add(request.user)

            return JsonResponse({
                'status': 'success',
                'message': '保存成功',
                'id': host.id
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


# 更新主机
@method_decorator(login_required(login_url="/login"), name='dispatch')
class HostUpdateView(UpdateView):
    model = Host
    fields = ['hostname', 'ip', 'port', 'username']
    template_name = 'host_manager/create_host.html'
    success_url = reverse_lazy('host_manager:go_host_manager')

    def form_valid(self, form):
        response = super().form_valid(form)
        return JsonResponse({'success': True})

    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({'error': errors}, status=400)


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
