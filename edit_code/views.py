from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from edit_code.models import PlaybookCode


# Create your views here.
@login_required(login_url="/login")
def playbook_list_page(request):
    return render(request, 'get_playbook_list.html')

@login_required(login_url="/login")
def edit_code(request):
    return render(request, 'edit_code.html')

@login_required(login_url="/login")
def playbook_detail(request, playbook_id):
    return render(request, 'playbook_detail.html', {'playbook_id': playbook_id})

@login_required(login_url="/login")
def get_playbook_detail_api(request, playbook_id):
    try:
        playbook = PlaybookCode.objects.get(id=playbook_id, created_by=request.user)

        data = {
            'id': playbook.id,
            'name': playbook.name,
            'description': playbook.description or '',
            'content': playbook.content,
            'created_at': playbook.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': playbook.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

        return JsonResponse({
            'code': 0,
            'data': data
        })

    except PlaybookCode.DoesNotExist:
        return JsonResponse({
            'code': 1,
            'message': 'Playbook 不存在或无权访问'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'code': 2,
            'message': f'发生未知错误：{str(e)}'
        }, status=500)

@login_required(login_url="/login")
def save_code(request):
    if request.method == "POST":
        code = request.POST.get('code')
        code_name = request.POST.get('code_name')
        code_describe = request.POST.get('code_describe')

        # 校验必要字段
        if not code or not code_name:
            return JsonResponse({
                'status': 'error',
                'message': '缺少必要参数'
            }, status=400)

        # 判断当前用户是否已经存在同名脚本
        if PlaybookCode.objects.filter(created_by=request.user, name=code_name).exists():
            return JsonResponse({
                'status': 'error',
                'message': f'您已有一个名为 {code_name} 的脚本'
            }, status=400)

        # 创建记录
        try:
            playbook = PlaybookCode.objects.create(
                name=code_name,
                description=code_describe,
                content=code,
                created_by=request.user
            )
            data = {
                'status': 'success',
                'message': '保存成功',
                'playbook_id': str(playbook.id)
            }
            print(data)
            return JsonResponse(data)


        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'保存失败: {str(e)}'
            }, status=500)

    else:
        return JsonResponse({
            'status': 'error',
            'message': '无效请求方法'
        }, status=405)




@login_required(login_url="/login")
def get_playbook_list_api(request):
    print(1)
    if not request.user.is_authenticated:
        print("没登录")
        return JsonResponse({
            'code': 1,
            'count': 0,
            'data': []
        })

    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 5)

    # 获取当前用户的 playbook 列表
    playbooks = PlaybookCode.objects.filter(created_by=request.user).order_by('-created_at')

    # 分页处理
    paginator = Paginator(playbooks, limit)
    print(123)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 构造数据
    data = []
    for playbook in page_obj:
        data.append({
            'id': playbook.id,
            'name': playbook.name,
            'description': playbook.description or '',  # 防止为 None
            'created_at': playbook.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': playbook.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    data = {
        'code': 0,
        'count': paginator.count,
        'data': data
    }
    print(data)
    # 返回 JSON
    return JsonResponse(data)

# 删除
@method_decorator(login_required(login_url="/login"), name='dispatch')
class PlaybookDeleteView(DeleteView):
    model = PlaybookCode
    context_object_name = 'Playbook'

    # success_url = reverse_lazy('host_manager:host_list')
    def get_success_url(self):
        # 直接返回 None 或者 raise 不触发跳转
        return None  # 或者 raise NotImplementedError("No redirect needed")

    # 重新方法禁止跳转 返回json
    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': 'success'})