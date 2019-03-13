from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.db.models import Q, F
from .models import Issue
from django.urls import reverse_lazy
from .forms import IssueCreateForm
from product.models import Product
from .tasks import do_accept, do_rollback
from utils.get_now_time_for_issue import get_now_time
# Create your views here.


class IssueListView(LoginRequiredMixin, ListView):
    model = Issue
    template_name = 'issue/issues_list.html'
    context_object_name = 'issues'
    paginate_by = 10
    page_kwarg = 'page'
    ordering = ['-id']

    def __init__(self):
        super().__init__()
        #   当前页面
        self.current_page = 0
        #   用于前端展示页码范围
        self.page_range = ''

    def get_queryset(self):
        if self.request.user.is_sa:
            return super().get_queryset()
        else:
            #   根据不同用户,显示其对应的issue
            return Issue.objects.filter(product_name__employees__username__exact=self.request.user.username).order_by('-id')

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True, **kwargs):
        #   计算当前页,获取分页信息
        self.current_page = int(self.request.GET.get(self.page_kwarg, 1))
        paginator = super().get_paginator(queryset, per_page, **kwargs)
        if paginator.num_pages > 7:
            if (self.current_page - 3) < 1:
                self.page_range = range(1, 8)
            elif (self.current_page + 3) > paginator.num_pages:
                self.page_range = range(paginator.num_pages - 6, paginator.num_pages + 1)
            else:
                self.page_range = range(self.current_page - 3, self.current_page + 4)
        else:
            self.page_range = paginator.page_range
        return paginator

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        #   获取get_paginator() 获取的页面范围
        kwargs['page_range'] = self.page_range
        kwargs['current_flag'] = 'issue'
        kwargs['total_issues'] = Issue.objects.all().count()
        return kwargs


class IssueCreateView(LoginRequiredMixin, CreateView):
    model = Issue
    template_name = 'issue/issue_create.html'
    form_class = IssueCreateForm
    success_url = reverse_lazy('issues:issues_list')
    issue_error = ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product_name_list'] = Product.objects.filter(employees__username__exact=self.request.user.username)
        return kwargs

    def form_valid(self, form):
        issue = form.save(commit=False)
        user_is_issue_s_employees = self.request.user in issue.product_name.employees.all()
        if not user_is_issue_s_employees:
            self.issue_error = '你无权创建此提案,产品不属于你'
            return self.form_invalid(form)
        status_eq_1_2_3_count = Issue.objects.filter(Q(product_name=issue.product_name), Q(Q(status=1) | Q(status=2) | Q(status=3))).count()
        if status_eq_1_2_3_count >= 1:
            self.issue_error = '用户所提交产品上线申请冲突,请取消或者先上线或回滚未完成提案'
            return self.form_invalid(form)
        issue.creator = self.request.user.fullname
        if issue.need_sa_agree:
            issue.assigner = 'SA'
        else:
            issue.assigner = self.request.user.fullname
        issue.newest_version = Product.objects.get(name=issue.product_name).version + 1
        issue.timeline += get_now_time() + ': ' + self.request.user.fullname + '提交了上线申请\n'
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['issue_error'] = self.issue_error
        return super().get_context_data(**kwargs)


class IssueDetailView(LoginRequiredMixin, DetailView):
    model = Issue
    template_name = 'issue/issue_detail.html'
    context_object_name = 'issue'
    success_url = reverse_lazy('issues:issues_list')

    def get_object(self, queryset=None):
        issue = super().get_object()
        user_is_issue_s_employees = self.request.user in issue.product_name.employees.all()
        user_is_root = self.request.user.is_root
        if not user_is_issue_s_employees and not user_is_root:
            return HttpResponseForbidden('你无权查看此提案')
        else:
            return issue


def accept(request, pk):
    success_url = reverse_lazy('issues:issues_list')
    issue = get_object_or_404(Issue, pk=pk)
    #   当前登录用户是否是SA标志
    is_sa_flag = request.user.is_sa
    #   当前提案是否需要SA同意上线
    need_sa_agree_flag = issue.need_sa_agree
    #   当前用户是否是提案的拥有者
    user_is_issue_s_employees = request.user in issue.product_name.employees.all()
    #   当前提案状态
    status = issue.status
    #   当前产品的提案中是否有回滚状态的3
    issue_is_has_rollback_status = Issue.objects.filter(Q(product_name=issue.product_name), Q(status=3))
    if issue_is_has_rollback_status:
        return HttpResponseForbidden('当前产品的提案正在回滚,请在回滚完成后提交上线操作')
    if status == 1:
        if is_sa_flag:
            if (need_sa_agree_flag and user_is_issue_s_employees) or (
                    need_sa_agree_flag and not user_is_issue_s_employees) or (
                    not need_sa_agree_flag and user_is_issue_s_employees):
                #   更新状态为： 代码上线中
                issue.status = 2
                issue.timeline += get_now_time() + ': ' + request.user.fullname + '确认了上线申请\n'
                issue.timeline += get_now_time() + ': bos机器人受理了上线提案\n'
                issue.save()
                # if status == 3:
                #     return HttpResponseForbidden('当前提案状态不支持上线操作')
                do_accept.delay(issue)
                return HttpResponseRedirect(success_url)
            else:
                return HttpResponseForbidden('您无权上线此提案')
        elif not is_sa_flag:
            if not need_sa_agree_flag and user_is_issue_s_employees:
                #   更新状态为： 代码上线中
                issue.status = 2
                issue.timeline += get_now_time() + ': ' + request.user.fullname + '确认了上线申请\n'
                issue.timeline += get_now_time() + ': bos机器人受理了上线提案\n'
                issue.save()
                do_accept.delay(issue)
                return HttpResponseRedirect(success_url)
            else:
                return HttpResponseForbidden('您无权上线此提案')
    else:
        return HttpResponseForbidden('当前提案状态不支持上线操作')


def reject(request, pk):
    success_url = reverse_lazy('issues:issues_list')
    issue = get_object_or_404(Issue, pk=pk)
    #   当前登录用户是否是SA标志
    is_sa_flag = request.user.is_sa
    #   当前提案是否需要SA同意上线
    need_sa_agree_flag = issue.need_sa_agree
    #   当前用户是否是提案的拥有者
    user_is_issue_s_employees = request.user in issue.product_name.employees.all()
    #   当前提案状态
    status = issue.status
    if status == 1:
        if is_sa_flag:
            issue.status = 16
            issue.timeline += get_now_time() + ': ' + request.user.fullname + '驳回了提案\n'
            issue.save()
            return HttpResponseRedirect(success_url)
        elif not is_sa_flag:
            if not need_sa_agree_flag and user_is_issue_s_employees:
                issue.status = 16
                issue.timeline += get_now_time() + ': ' + request.user.fullname + '驳回了提案\n'
                issue.save()
                return HttpResponseRedirect(success_url)
            else:
                return HttpResponseForbidden('您无权驳回此提案')
    else:
        return HttpResponseForbidden('当前提案状态不支持驳回操作')


def rollback(request, pk):
    success_url = reverse_lazy('issues:issues_list')
    issue = get_object_or_404(Issue, pk=pk)
    #   当前登录用户是否是SA标志
    is_sa_flag = request.user.is_sa
    #   当前提案是否需要SA同意上线
    need_sa_agree_flag = issue.need_sa_agree
    #   当前用户是否是提案的拥有者
    user_is_issue_s_employees = request.user in issue.product_name.employees.all()
    status = issue.status
    #   当前产品的提案中是否有回滚状态的14
    issue_is_has_accept_status = Issue.objects.filter(Q(product_name=issue.product_name), Q(status=2))
    can_rollback = issue.can_rollback
    if not can_rollback:
        return HttpResponseForbidden('当前提案不支持回滚操作')
    if issue_is_has_accept_status:
        return HttpResponseForbidden('当前产品的提案有上线操作,请在上线完成后执行回滚操作')
    if not (status == 11 or status == 12):
        return HttpResponseForbidden('当前提案状态不支持回滚操作')
    if is_sa_flag:
        if (need_sa_agree_flag and user_is_issue_s_employees) or (
                need_sa_agree_flag and not user_is_issue_s_employees) or (
                not need_sa_agree_flag and user_is_issue_s_employees):
            issue.timeline += get_now_time() + ': ' + request.user.fullname + '选择回滚此提案\n'
            issue.status = 3
            issue.save()
            do_rollback.delay(issue)
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden('您无权回滚此提案')
    elif not is_sa_flag:
        if not need_sa_agree_flag and user_is_issue_s_employees:
            issue.timeline += get_now_time() + ': ' + request.user.fullname + '选择回滚此提案\n'
            issue.status = 3
            issue.save()
            do_rollback.delay(issue)
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden('您无权回滚此提案')
