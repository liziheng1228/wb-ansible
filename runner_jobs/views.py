from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

from playbook.models import PlaybookCode
from host_manager.models import Host
from .models import Job
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator


@login_required(login_url="/login")
def go_jobs(request):
    playbooks = PlaybookCode.objects.filter(created_by=request.user)
    return render(request, "create_job.html", {'playbooks': playbooks})


@login_required(login_url="/login")
def get_hosts(request):
    hosts = Host.objects.values('id', 'hostname', 'ip', 'port', 'username')
    return JsonResponse(list(hosts), safe=False)


# 获取所有任务列表（GET）传给前端再传给ansible-task执行
@login_required(login_url="/login")
def job_list(request):

    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 5)

    # 从GET参数获取搜索关键词
    keyword = request.GET.get('host_search', '').strip()

    if not keyword:
        # 如果没有关键词，返回所有主机
        # hosts = Host.objects.all().values()
        jobs = Job.objects.filter(user=request.user)

    else:
        # 使用Q对象实现多字段联合搜索
        query = Q(name__icontains=keyword)

        # jobs = Job.objects.filter(query, user=request.user)

        jobs = Job.objects.filter(query,user=request.user).prefetch_related('inventory').order_by('-created_at')

    paginator = Paginator(jobs, limit)
    try:
        page_jobs = paginator.page(page)
    except PageNotAnInteger:
        page_jobs = paginator.page(1)
    except EmptyPage:
        page_jobs = paginator.page(paginator.num_pages)
    # 初始化空列表

    data = []
    # 遍历 tasks 中的每个元素

    for item in page_jobs:
        # 构造字典并添加到列表
        host_ips = list(item.inventory.values_list('ip', flat=True))
        # print(type(item))

        data.append({
            "job_id": str(item.id),
            'job_name': item.name,
            'job_type': item.job_type,
            'inventory': host_ips,
            'playbook_content': item.playbook_content,
            'playbook_path': item.playbook_path,
            'module_name': item.module_name,
            'module_args': item.module_args,
            'extra_vars': item.extra_vars,
            'forks': item.forks,
            'verbosity': item.verbosity,

        })

    json_data = {
        'code': 0,
        'count': paginator.count,
        'data': data
    }
    # print(json_data)
    return JsonResponse(json_data, safe=False)


# 创建新任务（POST）
@csrf_exempt
@login_required(login_url="/login")
def job_create(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            # 安全处理数值字段
            forks = data.get('forks')
            verbosity = data.get('verbosity')

            try:
                forks = int(forks) if forks not in (None, '') else 5
            except (TypeError, ValueError):
                forks = 5

            try:
                verbosity = int(verbosity) if verbosity not in (None, '') else 0
            except (TypeError, ValueError):
                verbosity = 0

            # 获取 playbook 实例（如果 job_type 是 playbook）
            playbook = None
            print(data.get('job_type'))

            if data.get('job_type') == 'playbook':
                playbook_id = data.get('playbook')
                if playbook_id:
                    try:
                        playbook = PlaybookCode.objects.get(id=playbook_id, created_by=request.user)
                    except PlaybookCode.DoesNotExist:
                        return JsonResponse({'error': '指定的 Playbook 不存在或不属于当前用户'}, status=400)

                job = Job.objects.create(
                    name=data.get('name'),
                    job_type=data.get('job_type'),
                    playbook_path=data.get('playbook_path', ''),
                    module_name=data.get('module_name', ''),
                    module_args=data.get('module_args', ''),
                    extra_vars=data.get('extra_vars', ''),
                    user=request.user,  # 绑定当前登录用户
                    forks=forks,
                    verbosity=verbosity,
                    playbook=playbook,  # 绑定playbook
                    playbook_content=playbook.content,  # 内容取出来保存

                )
            elif data.get('job_type') == 'ad-hoc':
                job = Job.objects.create(
                    name=data.get('name'),
                    job_type=data.get('job_type'),
                    module_name=data.get('module_name', ''),
                    module_args=data.get('module_args', ''),
                    extra_vars=data.get('extra_vars', ''),
                    user=request.user,  # 绑定当前登录用户
                    forks=forks,
                    verbosity=verbosity,
                )
            # inventory = data.get('inventory'),
            host_ids = data.get('inventory', [])

            # 设置多对多关系
            if host_ids:
                job.inventory.add(*host_ids)  # 注意：你的 ManyToManyField 名字叫 inventory

            return JsonResponse({
                'id': str(job.id),
                'name': job.name,
                'status': '123'
            }, status=201)

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


# 删除指定任务（DELETE）
@csrf_exempt
@login_required(login_url="/login")
def job_delete(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'DELETE':
        job.delete()
        return JsonResponse({'status': 'deleted'})

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


# 批量删除
@login_required(login_url="/login")
def batch_delete(request):
    """
    批量删除任务视图函数
    """
    # 确保只处理POST请求
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': '仅支持POST请求'
        }, status=405)

    # 获取要删除的任务ID列表
    job_ids = request.POST.getlist('job_ids[]')

    if not job_ids:
        # 如果没有选择任何任务
        return JsonResponse({
            'status': 'error',
            'message': '请选择要删除的任务'
        })

    job_ids = [job_id for job_id in job_ids]

    try:
        # 获取当前用户有权删除的任务
        jobs = Job.objects.filter(
            id__in=job_ids,
            user=request.user  # 确保用户只能删除自己的任务
        )

        # 记录删除的任务数量
        deleted_count = jobs.count()

        if deleted_count == 0:
            # 如果没有找到符合条件的记录

            return JsonResponse({
                'status': 'error',
                'message': '没有找到符合条件的任务'
            })
        # 执行批量删除
        jobs.delete()
        # 返回成功响应
        return JsonResponse({
            'status': 'success',
            'message': f'成功删除 {deleted_count} 个任务'
        })
    except Exception as e:
        # 处理删除过程中的异常
        error_message = f'删除失败: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': error_message
            })


# 任务详细信息
@login_required(login_url="/login")
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # 获取所有关联的 host，并取它们的 ip
    host_ips = list(job.inventory.values_list('ip', flat=True))
    job = {
        'job': job,
        'hosts': host_ips,
    }
    # print(job)
    return render(request, 'job_detail.html', job)
