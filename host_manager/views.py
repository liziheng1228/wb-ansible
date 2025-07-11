from django.core import paginator
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView

from django.views.generic.edit import DeleteView

from django.urls import reverse_lazy
from .models import Host


def go_host_manager(request):
    return render(request, "host_manager/host_list.html")


def get_task_list_api(request):
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 5)

    tasks = Host.objects.values()  # 获取所有任务并按创建时间排序
    paginator = Paginator(tasks, limit)
    try:
        page_tasks = paginator.page(page)
    except PageNotAnInteger:
        page_tasks = paginator.page(1)
    except EmptyPage:
        page_tasks = paginator.page(paginator.num_pages)
    # 初始化空列表
    print(1)
    data = []

    # 遍历 tasks 中的每个元素
    for item in page_tasks:
        # 构造字典并添加到列表
        data.append({
            'id': item['id'],
            'hostname': item['hostname'],
            'ip': item['ip'],
            'port': item['port'],
            'username': item['username'],
        })

    json_data = {
        'code': 0,
        'count': paginator.count,
        'data': data
    }

    return JsonResponse(json_data)


class HostCreateView(CreateView):
    model = Host
    fields = ['hostname', 'ip', 'port', 'username']
    template_name = 'host_manager/create_host.html'  # 创建和更新可以共用同一个表单模板
    success_url = reverse_lazy('host_manager:go_host_manager')  # 操作成功后跳转的URL名


class HostUpdateView(UpdateView):
    model = Host
    fields = ['hostname', 'ip', 'port', 'username']
    template_name = 'host_manager/create_host.html'
    success_url = reverse_lazy('host_manager:go_host_manager')


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
