from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.http import HttpResponseNotFound, HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Project, User, Issue, Label, Sprint, Comment
from .serializers import ProjectSerializer, UserSerializer, IssueSerializer, LabelSerializer, SprintSerializer, CommentSerializer
from django.core import serializers

class ProjectView(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['get'])
    def get_issues_assigned_to_user(self, request, pk):
        issues = Issue.objects.filter(assignee=pk).order_by('-creation_date')
        response = IssueSerializer(issues, many=True)
        return Response(response.data)
    

class IssueView(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer


    @action(detail=True, methods=['get'])
    def get_all_issues_of_project(self, request, pk):

        # check if project exists
        project = safeGet(pk, Project)
        if type(project) == HttpResponseNotFound:
            return project

        
        issues = Issue.objects.filter(project=pk).order_by('-creation_date')
        response = IssueSerializer(issues, many=True)
        return Response(response.data)
        
        # issues = Issue.objects.filter(project=pk).order_by('-creation_date')
        # paginator = Paginator(issues, 2) # show 50 issues per page
        # page_number = request.GET.get('page')
        # page_obj = paginator.get_page(page_number)
        # return render(request, {'page_obj': page_obj})
        
        # return response

    @action(detail=True, methods=['patch'])
    def assign_issue(self, request, pid, iid):
        data = request.data
        response = None
        user_id = data['assignee']

        # check if project exists
        project = safeGet(pid, Project)
        if type(project) == HttpResponseNotFound:
            response = project

        # check if issue exists
        issue = safeGet(iid, Issue)
        if type(issue) == HttpResponseNotFound:
            response = issue

        # check if user exists
        user = safeGet(user_id, User)
        if type(user) == HttpResponseNotFound:
            response = user

        response = self.checkUserValid(user, project)
        
        # upon success, save issue and formulate serialized response
        if response == None:
            # assign user to issue
            issue.setAssignee(user)
            issue.save()
            response = IssueSerializer(issue)
            response = Response(response.data)
        return response

    def checkUserValid(self, user, project):
        response = None

        # booleans
        notActive = not user.isActive()
        notInProject = not user.inProject(project.id)

        # check if user active
        if notActive:
            response = HttpResponse("Inactive User: User {} is marked as inactive".format(user.name))

        # check if user is a part of the project
        if notInProject:
            response = HttpResponse("Unqualified User: User {} is not a part of project {}.".format(user.name, project.name))

        if notActive and notInProject:
            response = HttpResponse("Inactive User: User {0} is marked as inactive\nUnqualified User: User {0} is not a part of project {1}.".format(user.name, project.name))
        
        return response

    @action(detail=True, methods=['patch'])
    def add_label_to_issue(self, request, iid):
        data = request.data
        label_id = data['label']

        # check if label exists
        label = safeGet(label_id, Label)
        if type(label) == HttpResponseNotFound:
            return issue

        # check if issue exists
        issue = safeGet(iid, Issue)
        if type(issue) == HttpResponseNotFound:
            return issue

        # add label to issue
        issue.addLabel(label)
        issue.save()

        response = IssueSerializer(issue)
        return Response(response.data)

    @action(detail=True, methods=['patch'])
    def update_issue_status(self, request, iid):
        data = request.data
        updated_status = data['status']
        
        # check if issue exists
        issue = safeGet(iid, Issue)
        if type(issue) == HttpResponseNotFound:
            return issue

        # update issue status
        issue.updateStatus(updated_status)
        issue.save()
        
        response = IssueSerializer(issue)
        return Response(response.data)

    @action(detail=True, methods=['get'])
    def search_issues(self, request):
        data = request.data
        
        logic = data.get('logic')
        project = data.get('project')
        type = data.get('type')
        status = data.get('status')
        assignee = data.get('assignee')
        label = data.get('label')
        desc = data.get('desc')

        response = None
        issues = Issue.objects.all()
        if logic == "and":
            if project: issues = issues.filter(project=project)
            if type: issues = issues.filter(type=type)
            if status: issues = issues.filter(status=status)
            if assignee: issues = issues.filter(assignee=assignee)
            if desc: issues = issues.filter(desc=desc)
            if label: issues = issues.filter(labels=label)
        elif logic == "or":
            issues = issues.filter(Q(project=project) | 
                        Q(type=type) | 
                        Q(status=status) | 
                        Q(assignee=assignee) | 
                        Q(desc=desc) | 
                        Q(labels=label))
        else:
            response = HttpResponseNotFound("Logic operation '{}' does not exist.  Must be one of ['and', 'or']".format(logic))

        if response == None:
            response = IssueSerializer(issues, many=True)
            response = Response(response.data)
        return response

    # TODO: add exception handling
    @action(detail=True, methods=['patch'])
    def move_issues(self, request, pk):
        data = request.data

        iids = data.getlist("issues")
        issue_ids = []
        for iid in iids:
            issue_ids.append(int(iid))
        source_sprint = data.get("source_sprint")
        target_sprint = data.get("target_sprint")

        # check if project exists
        project = safeGet(pk, Project)
        if type(project) == HttpResponseNotFound:
            return project

        # check if source sprint exists
        checkSprint = safeGet(source_sprint, Sprint)
        if type(checkSprint) == HttpResponseNotFound:
            return checkSprint

        issues = (Issue.objects
                        .filter(project=pk)
                        .filter(sprint=source_sprint)
                        .filter(id__in=issue_ids))

        # check if target sprint exists
        newSprint = safeGet(target_sprint, Sprint)
        if type(newSprint) == HttpResponseNotFound:
            return newSprint

        # move issues to new sprint
        for issue in issues:
            issue.setSprint(newSprint)
            issue.save()

        response = IssueSerializer(issues, many=True)
        return Response(response.data)

    @action(detail=True, methods=['get'])
    def get_issue_comments(self, request, pid, iid):
        # check if project exists
        project = safeGet(pid, Project)
        if type(project) == HttpResponseNotFound:
            return project

        # check if issue exists
        issue = safeGet(iid, Issue)
        if type(issue) == HttpResponseNotFound:
            return issue

        comments = Comment.objects.filter(issue=iid) # .order_by('-creation_date')
        response = CommentSerializer(comments, many=True)
        return Response(response.data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pid, iid):

        # check if project exists
        project = safeGet(pid, Project)
        if type(project) == HttpResponseNotFound:
            return project

        # check if issue exists
        issue = safeGet(iid, Issue)
        if type(issue) == HttpResponseNotFound:
            return issue

        data = request.data
        text = data.get("text")
        user_id = data.get("user")

        # check if user exists
        user = safeGet(pid, User)
        if type(user) == HttpResponseNotFound:
            return user
        
        comment = Comment()
        comment.setText(text)
        comment.setUser(user)
        comment.setIssue(issue)
        comment.save()
        response = CommentSerializer(comment)
        return Response(response.data, status=201)

    @action(detail=True, methods=['patch'])
    def update_watcher(self, request, pid, iid):
        data = request.data
        response = None

        # check if project exists
        project = safeGet(pid, Project)
        if type(project) == HttpResponseNotFound:
            return project

        # check if issue exists
        issue = safeGet(iid, Issue)
        if type(issue) == HttpResponseNotFound:
            return issue

        # check is issue has an assignee
        if issue.assignee != None:
            assignee_id = issue.assignee.id
        else:
            assignee_id = "null"

        watcher_id = data['watcher']

        # check if watcher is a user that exists
        watcher = safeGet(watcher_id, User)
        if type(watcher) == HttpResponseNotFound:
            response = watcher

        # make sure watcher is a valid user (active & part of project)
        response = self.checkUserValid(watcher, project)

        watcher_name = watcher.name

        if response == None:
            action = data["action"]
            if action == "add": # add watcher to issue
                if (watcher_id == assignee_id):
                    response = HttpResponse(
                        "Watcher Designation Error: User {} is already an assignee.  User cannot be designated as both an assignee and a watcher."
                        .format(watcher_name))
                else:
                    # perform add
                    issue.addWatcher(watcher)
                    issue.save()
            elif action == "mute": # mute watcher from issue
                if not issue.isWatcher(watcher):
                    response = HttpResponse(
                        "Watcher Designation Error: User {} is not a watcher for issue {}.  Can only mute users that are already watchers."
                        .format(watcher_name, issue.summary))
                else:
                    # perform mute
                    issue.removeWatcher(watcher)
                    issue.save()
            else:
                response = HttpResponseNotFound(
                    "Not Found Error: Action {} does not exist.  User {} can either be added ('add') or muted ('mute') from an issue's watchlist."
                    .format(action, watcher_name))
        
        # upon success, serialize response and return
        if response == None:
            response = IssueSerializer(issue)
            response = Response(response.data)
        return response


class SprintView(viewsets.ModelViewSet):
    queryset = Sprint.objects.all()
    serializer_class = SprintSerializer


class LabelView(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer


class CommentView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


'''
error handling functions
'''
def safeGet(entityId, Entity):
    try:
        entity = Entity.objects.get(pk=entityId)
    except:
        return HttpResponseNotFound("Not Found Error: {} with id = {} does not exist.".format(Entity.__name__, entityId))
    return entity