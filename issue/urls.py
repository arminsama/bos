from django.urls import path
from .views import IssueCreateView, IssueDetailView, IssueListView, accept, reject, rollback


urlpatterns = [
    path('', IssueListView.as_view(), name='issues_list'),
    path('create/', IssueCreateView.as_view(), name='issue_create'),
    path('detail/<int:pk>', IssueDetailView.as_view(), name='issue_detail'),
    path('accept/<int:pk>', accept, name='issue_accept'),
    path('reject/<int:pk>', reject, name='issue_reject'),
    path('rollback/<int:pk>', rollback, name='issue_rollback'),
]
