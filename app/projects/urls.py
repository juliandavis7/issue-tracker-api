from django.urls import path, include
from rest_framework import routers
from . import views
from .views import ProjectView, UserView, IssueView, LabelView, SprintView, CommentView

project_list = ProjectView.as_view({
        'get': 'list',
        'post': 'create'
})

project_detail = ProjectView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

project_issues = IssueView.as_view({
    'get': 'get_all_issues_of_project',
    'post': 'create',
    'patch': 'move_issues'
})

issue_list = IssueView.as_view({
    'get': 'list',
})

issue_search = IssueView.as_view({
    'get': 'search_issues',
})

issue_detail = IssueView.as_view({
    'get': 'retrieve'
})

issue_assign = IssueView.as_view({
    'patch': 'assign_issue'
})

issue_watcher = IssueView.as_view({
    'patch': 'update_watcher'
})

issue_label = IssueView.as_view({
    'patch': 'add_label_to_issue'
})

issue_status = IssueView.as_view({
    'patch': 'update_issue_status'
})

issue_comment = IssueView.as_view({
    'get': 'get_issue_comments',
    'post': 'add_comment'
})

user_list = UserView.as_view({
    'get': 'list',
    'post': 'create',
})

user_detail = UserView.as_view({
    'get': 'retrieve',
    'patch': 'partial_update'
})

user_issues = UserView.as_view({
    'get': 'get_issues_assigned_to_user',
})

label_list = LabelView.as_view({
    'get': 'list',
    'post': 'create'
})

sprint_list = SprintView.as_view({
    'get': 'list',
    'post': 'create'
})

sprint_detail = SprintView.as_view({
    'get': 'retrieve'
})

comment_list = CommentView.as_view({
    'get': 'list',
    'post': 'create'
})

urlpatterns = [
    path("projects/", project_list),
    path('projects/<int:pk>', project_detail),
    path('projects/<int:pk>/issues', project_issues),
    path('issues/', issue_list),
    path('issues/search', issue_search),
    path('issues/<int:pk>', issue_detail),
    path('projects/<int:pid>/issues/<int:iid>/assignee', issue_assign),
    path('projects/<int:pid>/issues/<int:iid>/watcher', issue_watcher),
    path('issues/<int:iid>/label', issue_label),
    path('issues/<int:iid>/status', issue_status),
    path('projects/<int:pid>/issues/<int:iid>/comments', issue_comment),
    path('users/', user_list),
    path('users/<int:pk>', user_detail),
    path('users/<int:pk>/issues', user_issues),
    path('labels/', label_list),
    path('sprints/', sprint_list),
    path('sprints/<int:pk>', sprint_detail),
    path('comments/', comment_list)
]