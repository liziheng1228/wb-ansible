import json

from celery.result import AsyncResult
from cryptography.fernet import InvalidToken
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import CeleryTask
from host_manager.models import Host
from .tasks import run_ansible_playbook,cancel_task
import re
# 跳转页面
@login_required(login_url="/login")
def go_index(request):
    return render(request, 'index.html')


@login_required(login_url="/login")
def go_task_list(request):
    return render(request, 'task_list.html')


@login_required(login_url="/login")
def go_result_page(request, task_id):
    return render(request, 'getResult.html', context={'task_id': task_id})


# 执行任务并将id入库
@login_required(login_url="/login")
def ansible_run(request):
    if request.method == 'POST':
        try:

            data = json.loads(request.body)
            hosts = data.get('inventory', '[]')

            hosts_info = Host.objects.filter(ip__in=hosts, users=request.user).values('ip', 'port', 'username',
                                                                                      'ssh_password_encrypted',
                                                                                      'become_password_encrypted')

            if not hosts_info.exists():
                return JsonResponse({'error': '未找到对应的目标主机'}, status=400)
            # print(data['playbook_content'])

            hosts_queryset = Host.objects.filter(ip__in=hosts, users=request.user)
            # 提取密码
            for host in hosts_queryset:
                try:
                    ssh_pass = host.get_ssh_password()
                except InvalidToken:
                    ssh_pass = None
                    print(f"[警告] 主机 {host.ip} 的 SSH 密码解密失败")

                try:
                    become_pass = host.get_become_password()
                except InvalidToken:
                    become_pass = None
                    print(f"[警告] 主机 {host.ip} 的提权密码解密失败")

            # 构建 inventory 字典格式
            inventory_dict = {
                "test": {
                    "hosts": {
                        host_info['ip']: {
                            "ansible_host": host_info['ip'],
                            "ansible_port": host_info['port'],
                            "ansible_user": host_info['username'],

                            # 添加其他需要的信息
                        }
                        for host_info in hosts_info
                    }
                }
            }

            # 构造 kwargs 字典
            kwargs = {
                'playbook': data['playbook_content'],  # playbook内容 （没有与Playbook管理做动态绑定，Playbook内容编辑之后需要新建任务）
                'job_type': data.get('job_type'),  # 任务类型
                'inventory': inventory_dict,
                'verbosity': data.get('verbosity'),  # 结果显示等级
                'forks': data.get('forks'),  # 并发量
                'module_args': data.get('module_args'),  # 模块参数
                'extra_vars': data.get('extra_vars'),  # 扩展变量
                'module_name': data.get('module_name'),  # 模块名称
                'ssh_pass': ssh_pass,
                'become_pass': become_pass,
            }
            # print(module_name, module_args)
            # 传参执行任务
            task_id = run_ansible_playbook.delay(**kwargs)
            test1 = CeleryTask(task_id=task_id)
            test1.save()
            # print(inventory_dict)
            json_data = {
                'task_id': task_id.task_id

            }
            return JsonResponse(json_data)
        except Exception as e:

            return JsonResponse({'error': str(e)}, status=500)

# 停止任务
@login_required(login_url="/login")
def cancel_task_view(request):
    if request.method == 'POST':
        body = json.loads(request.body)

        task_id = body.get('taskId')

        cancel_task.delay(task_id)
        return JsonResponse({'status': 'Task cancellation requested'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# 获取任务列表
@login_required(login_url="/login")
def get_task_list_api(request):
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 5)

    tasks = CeleryTask.objects.values().order_by('-created_at')  # 获取所有任务并按创建时间排序
    paginator = Paginator(tasks, limit)
    try:
        page_tasks = paginator.page(page)
    except PageNotAnInteger:
        page_tasks = paginator.page(1)
    except EmptyPage:
        page_tasks = paginator.page(paginator.num_pages)
    # 初始化空列表
    data = []

    # 遍历 tasks 中的每个元素
    for item in page_tasks:
        # 构造字典并添加到列表
        data.append({
            'task_id': item['task_id'],
            'created_at': item['created_at'],
            'is_used': item['is_used']
        })

    json_data = {
        'code': 0,
        'count': paginator.count,
        'data': data
    }

    return JsonResponse(json_data)


# csrf返给前端使用
@ensure_csrf_cookie  # 确保返回 CSRF 令牌
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


# 获取结果
@login_required(login_url="/login")
def get_result(request, task_id):
    # task_id = request.GET.get('task_id')
    # print('获取一下iD', task_id)
    if not task_id:
        return JsonResponse({'error': '缺少任务ID'}, status=400)

    task = AsyncResult(task_id)
    return JsonResponse({
        'status': task.status,
        'stdout': task.result.get('stdout', '') if task.ready() else '',
        'stderr': task.result.get('stderr', '') if task.ready() else '',
        'rc': task.result.get('rc', -1) if task.ready() else -1
    })
