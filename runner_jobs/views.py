from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.views import View
import json
from .models import Job
# Create your views here.
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator


def go_jobs(request):
    return render(request, "index1.html")


# 获取所有任务列表（GET）
def job_list(request):
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 5)

    jobs = Job.objects.values()  # 获取所有任务并按创建时间排序
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
        data.append({
            "job_id": item['id'],
            'job_name': item['name'],
            'job_type': item['job_type'],
            'inventory': item['inventory'],
            'playbook_content': item['playbook_content'],
            'playbook_path': item['playbook_path'],
            'module_name': item['module_name'],
            'module_args': item['module_args'],
            'extra_vars': item['extra_vars'],
            'forks': item['forks'],
            'verbosity': item['verbosity'],

        })

    json_data = {
        'code': 0,
        'count': paginator.count,
        'data': data
    }

    return JsonResponse(json_data)
    #
    # jobs = Job.objects.all().values()
    # return JsonResponse(list(jobs), safe=False)


# 创建新任务（POST）
@csrf_exempt
def job_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            job = Job.objects.create(
                name=data.get('name'),
                job_type=data.get('job_type'),
                inventory=data.get('inventory'),
                playbook_content=data.get('playbook_content', ''),
                playbook_path=data.get('playbook_path', ''),
                module_name=data.get('module_name', ''),
                module_args=data.get('module_args', ''),
                extra_vars=data.get('extra_vars', ''),
                forks=data.get('forks', 5),
                verbosity=data.get('verbosity', 0)
            )

            return JsonResponse({
                'id': str(job.id),
                'name': job.name,
                'status': 'success'
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


# 删除指定任务（DELETE）
@csrf_exempt
def job_delete(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'DELETE':
        job.delete()
        return JsonResponse({'status': 'deleted'})

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Job

def job_detail(request, job_id):
    # job = Job.objects.get(id='5f409f031cca4c429b78a5f967e56444')
    # print(job.id)
    for job in Job.objects.all():
        print(job.id)
    job = get_object_or_404(Job, id=job_id)
    print(job)

    return render(request, 'job_detail.html', {'job': job})