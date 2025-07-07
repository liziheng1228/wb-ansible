from celery.result import AsyncResult
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from  .models import CeleryTask
from .tasks import run_ansible_playbook

# Create your views here.



# 执行任务并将id入库
def ansible_run_index(request):
    # celery_tasks = CeleryTask.objects.all()
    # print(celery_tasks)
    # celery_tasks=CeleryTask

    directory = '/root/project/ansible_runner'
    ply = "test.yaml"
    task_id = run_ansible_playbook.delay(directory, ply)
    test1 = CeleryTask(task_id=task_id)
    test1.save()
    print(task_id)
    return render(request, 'index.html', )


def get_task_id(request):
    tasks = CeleryTask.objects.all().order_by('-created_at')  # 获取所有任务并按创建时间排序
    # print(tasks)
    return render(request, 'task_list.html', {'tasks': tasks})


# 暂时没用
@ensure_csrf_cookie  # 确保返回 CSRF 令牌
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

def go_result_page(request, task_id):

    print(task_id)
    return render(request, 'getResult.html', context={'task_id': task_id})


# 获取结果
def get_result(request,task_id):
    # task_id = request.GET.get('task_id')
    print('获取一下iD',task_id)
    if not task_id:
        return JsonResponse({'error': '缺少任务ID'}, status=400)

    task = AsyncResult(task_id)
    return JsonResponse({
        'status': task.status,
        'stdout': task.result.get('stdout', '') if task.ready() else '',
        'stderr': task.result.get('stderr', '') if task.ready() else '',
        'rc': task.result.get('rc', -1) if task.ready() else -1
    })