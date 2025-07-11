import json

from celery.result import AsyncResult
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import CeleryTask
from host_manager.models import Host
from .tasks import run_ansible_playbook
import re


# 跳转页面
def go_index(request):
    return render(request, 'index.html')


def go_task_list(request):
    return render(request, 'task_list.html')


def go_result_page(request, task_id):
    return render(request, 'getResult.html', context={'task_id': task_id})


# 执行任务并将id入库
def ansible_run(request):
    if request.method == 'POST':
        try:

            data = json.loads(request.body)

            host_ids = json.loads(data.get('inventory', '[]'))
            hosts = Host.objects.filter(id__in=host_ids)
            if not hosts.exists():
                return JsonResponse({'error': '未找到对应的目标主机'}, status=400)
            # 构建 inventory 字典格式
            inventory_dict = {
                "test": {
                    "hosts": {
                        host.ip: {
                            "ansible_host": host.ip,
                            "ansible_port": host.port,
                            "ansible_user": host.username,
                            # "ansible_ssh_pass": host.password,
                        }
                        for host in hosts
                    }
                }
            }
            job_type = data.get('job_type')  # 任务类型
            module_name = data.get('module_name')  # 模块名称
            module_args = data.get('module_args')  # 模块参数
            extra_vars = data.get('extra_vars')  # 扩展变量
            forks = data.get('forks')  # 并发量
            verbosity = data.get('verbosity')  # 结果显示等级

            directory = './ansible_runner'
            ply = "test.yaml"
            task_id = run_ansible_playbook.delay(directory=directory, playbook=ply, job_type=job_type, inventory=inventory_dict,
                                                 verbosity=verbosity, forks=forks,
                                                 module_args=module_args, extra_vars=extra_vars, module_name=module_name)
            test1 = CeleryTask(task_id=task_id)
            test1.save()
            # print(inventory_dict)
            json_data = {
                'task_id': task_id.task_id

            }
            return JsonResponse(json_data)
        except Exception as e:
            print(e)
            # return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'status': 'success'}, status=200)


""" 
directory = './ansible_runner'
    ply = "test.yaml"
    inventory = {
        "test1": {
            "hosts": {
                "ip1": {},
                "ip2": {}
            }
        }
    }
    task_id = run_ansible_playbook.delay(directory, ply, inventory)
    test1 = CeleryTask(task_id=task_id)
    test1.save()
    # print()

    json_data = {
        'task_id': task_id.task_id

    }
    return JsonResponse(json_data)
    """


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
    print(1)
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


# 暂时没用
@ensure_csrf_cookie  # 确保返回 CSRF 令牌
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


# 获取结果
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
