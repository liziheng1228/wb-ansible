from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView, UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from scripts.models import Script


# Create your views here.
@login_required(login_url="/login")
def playbook_list_page(request):
    return render(request, 'get_playbook_list.html')


@login_required(login_url="/login")
def edit_code_page(request):
    return render(request, 'edit_code.html')


@login_required(login_url="/login")
def playbook_detail_page(request, playbook_id):
    return render(request, 'playbook_detail.html', {'playbook_id': playbook_id})


# 获取Playbook详情
@login_required(login_url="/login")
def get_playbook_detail_api(request, playbook_id):
    try:
        playbook = Script.objects.get(id=playbook_id, created_by=request.user)

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

    except Script.DoesNotExist:
        return JsonResponse({
            'code': 1,
            'message': 'Playbook 不存在或无权访问'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'code': 2,
            'message': f'发生未知错误：{str(e)}'
        }, status=500)

# 更新playbook
@method_decorator(login_required(login_url="/login"), name='dispatch')
class PlaybookUpdateView(UpdateView):
    """
    Tip：此代码不能删除，虽然更新代码在save_code中，但是需要此代码的上下文变量
    """
    model = Script
    fields = ['name', 'description', 'content','script_type']
    template_name = 'edit_code.html'
    success_url = reverse_lazy('playbook:list_page')

# 保存/编辑Playbook代码
@login_required(login_url="/login")
def save_code(request):
    if request.method == "POST":
        code = request.POST.get('code')
        code_name = request.POST.get('code_name')
        code_describe = request.POST.get('code_describe')
        pk = request.POST.get('pk')  # 新增字段：用于判断是否为编辑
        script_type = request.POST.get('type') # 判断是Playbook还是shell脚本


        # 校验必要字段
        if not code or not code_name:
            return JsonResponse({
                'status': 'error',
                'message': '缺少必要参数'
            }, status=400)

        # 判断是否为编辑模式
        if pk:
            # 编辑已有脚本
            playbook = get_object_or_404(Script, pk=pk, created_by=request.user)

            # 检查是否改名后与其他脚本冲突（允许保留原名）
            if Script.objects.filter(created_by=request.user, name=code_name).exclude(pk=pk).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'您已有一个名为 {code_name} 的脚本'
                }, status=400)

            # 更新内容
            playbook.name = code_name
            playbook.description = code_describe
            playbook.content = code
            playbook.script_type = script_type

            playbook.save()

            return JsonResponse({
                'status': 'success',
                'message': '更新成功',
                'playbook_id': str(playbook.id)
            })

        else:
            # 新增脚本
            if Script.objects.filter(created_by=request.user, name=code_name).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': f'您已有一个名为 {code_name} 的脚本'
                }, status=400)

            try:
                playbook = Script.objects.create(
                    name=code_name,
                    description=code_describe,
                    content=code,
                    script_type=script_type,
                    created_by=request.user
                )
                return JsonResponse({
                    'status': 'success',
                    'message': '保存成功',
                    'playbook_id': str(playbook.id)
                })
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


# 获取Playbook列表
@login_required(login_url="/login")
def get_playbook_list_api(request):
    if not request.user.is_authenticated:
        print("没登录")
        return JsonResponse({
            'code': 1,
            'count': 0,
            'data': []
        })

    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 5)
    # 从GET参数获取搜索关键词
    keyword = request.GET.get('playbook_search', '').strip()

    if not keyword:
        # 如果没有关键词，返回所有playbook

        playbooks = Script.objects.filter(created_by=request.user)

    else:
        # 使用Q对象实现多字段联合搜索
        query = Q(name__icontains=keyword)
        # playbooks = PlaybookCode.objects.filter(query)
    # 获取当前用户的 playbook 列表
        playbooks = Script.objects.filter(query, created_by=request.user).order_by('-created_at')

    # 分页处理
    paginator = Paginator(playbooks, limit)

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
            'script_type': playbook.script_type,
        })
    data = {
        'code': 0,
        'count': paginator.count,
        'data': data
    }

    # 返回 JSON
    return JsonResponse(data)


# 删除
@method_decorator(login_required(login_url="/login"), name='dispatch')
class PlaybookDeleteView(DeleteView):
    model = Script
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

# 批量删除
def batch_delete(request):
    """
    批量删除playbook视图函数
    """
    # 确保只处理POST请求
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': '仅支持POST请求'
        }, status=405)

    # 获取要删除的主机ID列表
    playbook_ids = request.POST.getlist('playbook_ids[]')

    if not playbook_ids:
        # 如果没有选择任何主机
        return JsonResponse({
            'status': 'error',
            'message': '请选择要删除的Playbook'
        })

    try:
        # 转换ID为整数
        playbook_ids = [int(id) for id in playbook_ids]
    except ValueError:
        # 处理无效ID格式
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': '无效的ID格式'
            })

    try:

        # 获取当前用户有权删除的主机
        playbooks = Script.objects.filter(
            id__in=playbook_ids,
            created_by=request.user  # 确保用户只能删除自己的主机
        )

        # 记录删除的主机数量
        deleted_count = playbooks.count()

        if deleted_count == 0:
            # 如果没有找到符合条件的记录

            return JsonResponse({
                'status': 'error',
                'message': '没有找到符合条件的内容'
            })

        # 执行批量删除
        playbooks.delete()

        # 返回成功响应

        return JsonResponse({
            'status': 'success',
            'message': f'成功删除 {deleted_count} 个Playbook'
        })



    except Exception as e:
        # 处理删除过程中的异常
        error_message = f'删除失败: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': error_message
            })

