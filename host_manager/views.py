from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView

from django.views.generic.edit import DeleteView

from django.urls import reverse_lazy
from .models import Host

class HostListView(ListView):
    model = Host
    template_name = 'host_manager/test.html'  # 指定模板
    context_object_name = 'hosts'

class HostCreateView(CreateView):
    model = Host
    fields = ['hostname', 'ip', 'port', 'username']
    template_name = 'host_manager/create_host.html'  # 创建和更新可以共用同一个表单模板
    success_url = reverse_lazy('host_manager:host_list')  # 操作成功后跳转的URL名

class HostUpdateView(UpdateView):
    model = Host
    fields = ['hostname', 'ip', 'port', 'username']
    template_name = 'host_manager/create_host.html'
    success_url = reverse_lazy('host_manager:host_list')


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