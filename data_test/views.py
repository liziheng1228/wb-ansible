from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Host

class HostListView(ListView):
    model = Host
    template_name = 'data_test/test.html'  # 指定模板
    context_object_name = 'hosts'

class HostCreateView(CreateView):
    model = Host
    fields = ['hostname', 'ip', 'port', 'username']
    template_name = 'data_test/create_host.html'  # 创建和更新可以共用同一个表单模板
    success_url = reverse_lazy('data_test:host_list')  # 操作成功后跳转的URL名

class HostUpdateView(UpdateView):
    model = Host
    fields = ['hostname', 'ip', 'port', 'username']
    template_name = 'data_test/create_host.html'
    success_url = reverse_lazy('data_test:host_list')

class HostDeleteView(DeleteView):
    model = Host
    template_name = 'data_test/host_confirm_delete.html'  # 删除确认模板
    success_url = reverse_lazy('data_test:host_list')
