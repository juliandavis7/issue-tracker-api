import re
import json
from django.test import TestCase

from projects.models import *
from rest_framework.test import APITestCase

class TestPersons(APITestCase):

  def setUp(self):
    self.p1 = Project.objects.create(name="Project 1")
    self.p2 = Project.objects.create(name="Project 2")

    self.u1 = User.objects.create(name="User 1", active=True)
    self.u1.projects.add(self.p1)
    self.u2 = User.objects.create(name="User 2", active=True)
    self.u2.projects.add(self.p2)

    self.p1_s1 = Sprint.objects.create(
      name="Project 1 - Sprint 1",
      start_date = "2022-03-04T19:06:21Z",
      end_date = "2022-03-11T19:06:26Z",
      project=self.p1
    )

    self.p1_s2 = Sprint.objects.create(
      name="Project 1 - Sprint 2",
      start_date = "2022-03-04T19:06:21Z",
      end_date = "2022-03-11T19:06:26Z",
      project=self.p1
    )

    self.p2_s1 = Sprint.objects.create(
      name="Project 2 - Sprint 1",
      start_date = "2022-03-04T19:06:21Z",
      end_date = "2022-03-11T19:06:26Z",
      project=self.p2
    )

    self.p1_i1 = Issue.objects.create(
      summary="Project 1 - Issue 1",
      desc="",
      type="task",
      project=self.p1,
      sprint=self.p1_s1

    )

    self.p1_i2 = Issue.objects.create(
      summary="Project 1 - Issue 2",
      desc="desc",
      type="bug",
      project=self.p1,
      sprint=self.p1_s1,
      assignee=self.u1
    )

    self.p1_i3 = Issue.objects.create(
      summary="Project 1 - Issue 3",
      desc="desc",
      type="bug",
      project=self.p1,
      sprint=self.p1_s1,
      assignee=self.u1
    )

    self.p2_i1 = Issue.objects.create(
      summary="Project 2 - Issue 1",
      desc="desc",
      type="task",
      project=self.p2,
      sprint=self.p2_s1
    )
    self.p2_i1.watchers.add(self.u2)

    self.l1 = Label.objects.create(value="Label 1")


  def test_create_project(self):
    expected_name = "New Project"
    project_json = {'name': expected_name}
    response = self.client.post('/projects/', project_json)
    self.assertEqual(response.status_code, 201)

    response_json = response.json()
    result_name = response_json['name']
    self.assertEqual(result_name, expected_name)

  def test_get_projects(self):
    response = self.client.get('/projects/')
    projects_json = response.json()
    self.assertEqual(response.status_code, 200)
    expected = [{"name": "Project 1"}, {"name": "Project 2"}]
    for i in range(len(projects_json)):
      result_name = projects_json[i]['name']
      expected_name = expected[i]['name']
      self.assertEqual(result_name, expected_name)

  def test_3get_project_details(self):
    project_id = self.p1.id
    expected_name = self.p1.name

    response = self.client.get('/projects/{}'.format(project_id))
    project_json = response.json()
    self.assertEqual(response.status_code, 200)
    result_name = project_json['name']
    self.assertEqual(result_name, expected_name)


  def test_create_issue(self):
    name = "New Issue"
    desc = "desc"
    type = "task"
    issue_json = {
      "summary": name,
      "desc": desc,
      "type": type,
      "project": self.p1.id,
      "sprint": self.p1_s1.id,
    }

    url = "/projects/{}/issues".format(self.p1.id)
    response = self.client.post(url, issue_json)
    self.assertEqual(response.status_code, 201)

    result_json = response.json()
    result_json.pop("id")
    result_json.pop("creation_date")

    expected_json = {
      'summary': name,
      'desc': desc,
      'type': type,
      'status': 'open',
      'project': self.p1.id, 
      'assignee': None,
      'sprint': self.p1_s1.id,
      'labels': [],
      'watchers': []}

    self.assertEqual(result_json, expected_json)


  def test_get_all_issues_of_project(self):
    url = "/projects/{}/issues".format(self.p1.id)
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    p1_issues_json = response.json()

    # expected issues, sorted from most recently created to least
    p1_issues = [self.p1_i3, self.p1_i2,self.p1_i1]
    for i in range(len(p1_issues_json)):
      expected_issue = p1_issues[i]
      result_issue = p1_issues_json[i]
      self.checkIssueEqual(expected_issue, result_issue)

  def test_assign_issue(self):
    assignee = self.u1.id
    url = "/projects/{}/issues/{}/assignee".format(self.p1.id, self.p1_i1.id)
    assign_json = {"assignee": assignee}

    # assignee is originally null
    self.assertEqual(None, self.p1_i1.assignee)
    response = self.client.patch(url, assign_json)
    self.assertEqual(response.status_code, 200)

    expected_assignee = assignee
    result_assignee = response.json()['assignee']

    # assignee is now 'User 1'
    self.assertEqual(expected_assignee, result_assignee)

  def test_issues_assigned_to_user(self):
    # get issues assigned to user
    url = "/users/{}/issues".format(self.u1.id)
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

    # User 1 should be assigned to Issues 2, 3
    user_issues = [self.p1_i3, self.p1_i2]
    result_issues = response.json()
    for i in range(len(result_issues)):
      expected_issue = user_issues[i]
      result_issue = result_issues[i]
      self.checkIssueEqual(expected_issue, result_issue)

  def test_add_label_to_issue(self):
    # issue originally has no labels
    self.checkLabelsEqual(self.p1_i1.labels, [])
    
    # add label to issue
    url = "/issues/{}/label".format(self.p1_i1.id)
    label_json = {"label": self.l1.id}
    response = self.client.patch(url, label_json)
    self.assertEqual(response.status_code, 200)
    issue_json = response.json()

    expected_labels = [self.l1]
    result_labels = issue_json["labels"]
    
    # Label 1 now added to Issue 1
    self.checkLabelsEqual(expected_labels, result_labels)

  # TO DO: need to refactor search, get() doesn't take in a request body
  # # search issues - search based on project id only
  # def test_search_issues(self):

  #   url = "/issues/search"
  #   search_json = {
  #     "logic": "and",
  #     "project": self.p1.id,
  #   }

  #   # NEED TO FIX: json not being recognized as parameter
  #   response = self.client.get(url, search_json, ACCEPT='application/json')

  #   # search should return all issues in p1


  def test_update_issue_status(self):
    url = "/issues/{}/status".format(self.p1_i1.id)
    status_json = {"status": "assigned"}
    response = self.client.patch(url, status_json)
    self.assertEqual(response.status_code, 200)
    issue_json = response.json()

    expected_status = "assigned"
    result_status = issue_json["status"]
    self.assertEqual(expected_status, result_status)


  def test_move_issues(self):
    source_sprint = self.p1_s1.id
    target_sprint = self.p1_s2.id

    # check Project 1, Issues 1, 2, 3 are in Sprint 1
    issues = [self.p1_i1, self.p1_i2, self.p1_i3]
    for issue in issues:
      self.assertEqual(source_sprint, issue.sprint.id)

    # move issues from Sprint 1 to 2
    url = "/projects/{}/issues".format(self.p1.id)
    body = {
      "issues": [issue.id for issue in issues],
      "source_sprint": source_sprint,
      "target_sprint": target_sprint
    }
    response = self.client.patch(url, body)
    self.assertEqual(response.status_code, 200)
    result_json = response.json()
    
    # check issues have moved to Sprint 2
    for result_issue in result_json:
      result_sprint = int(result_issue["sprint"])
      self.assertEqual(target_sprint, result_sprint)

  def test_add_comments(self):
    
    url = "/projects/{}/issues/{}/comments".format(self.p1.id, self.p1_i1.id)
    body = {
      "text": "Comment 1",
      "user": self.u1.id
    }
    response = self.client.post(url, body)
    self.assertEqual(response.status_code, 201)

    expected_comment = {
      'text': 'Comment 1', 
      'user': self.u1.id,
      'issue': self.p1_i1.id}
    result_comment = response.json()

    self.checkCommentEqual(expected_comment, result_comment)

  def test_add_watcher(self):

    # check Issue 1 originally has now watchers
    self.checkWatchersEqual(self.p1_i1.watchers, [])
    
    # add watcher
    url = "/projects/{}/issues/{}/watcher".format(self.p1.id, self.p1_i1.id)
    body = {
      "action": "add",
      "watcher": self.u1.id
    }
    response = self.client.patch(url, body)
    self.assertEqual(response.status_code, 200)
    result_json = response.json()

    # check Issue 1 has User 1 (u1) designated as a watcher
    expected_watchers = [self.u1]
    result_watchers = result_json["watchers"]
    self.checkWatchersEqual(expected_watchers, result_watchers)

  def test_mute_watcher(self):

    # check Project 2, Issue 1 orginially has User 2 (u2) assigned as a watcher
    self.checkWatchersEqual(self.p2_i1.watchers, [])
    
    # mute watcher
    url = "/projects/{}/issues/{}/watcher".format(self.p2.id, self.p2_i1.id)
    body = {
      "action": "mute",
      "watcher": self.u2.id
    }
    response = self.client.patch(url, body)
    self.assertEqual(response.status_code, 200)
    result_json = response.json()

    # check that User 2 (u2) is no longer a watcher for issue
    expected_watchers = []
    result_watchers = result_json["watchers"]
    self.checkWatchersEqual(expected_watchers, result_watchers)


  """
  TESTING HELPER FUNCTIONS
  """
  def checkIssueEqual(self, expected_issue, result_issue):
    self.assertEqual(expected_issue.summary, result_issue['summary'])
    self.assertEqual(expected_issue.desc, result_issue['desc'])
    self.assertEqual(expected_issue.type, result_issue['type'])
    self.assertEqual(expected_issue.status, result_issue['status'])
    self.assertEqual(expected_issue.project.id, result_issue['project'])
    if expected_issue.assignee != None:
      expected_issue_assignee = expected_issue.assignee.id
    else:
      expected_issue_assignee = expected_issue.assignee
    self.assertEqual(expected_issue_assignee, result_issue['assignee'])
    self.checkLabelsEqual(expected_issue.labels, result_issue["labels"])
    self.checkWatchersEqual(expected_issue.watchers, result_issue["watchers"])

  def checkLabelsEqual(self, expected_labels, result_labels):
    for i in range(len(result_labels)):
        expected_label = expected_labels[i].id
        result_label = result_labels[i]
        self.assertEqual(expected_label, result_label)

  def checkWatchersEqual(self, expected_watchers, result_watchers):
    for i in range(len(result_watchers)):
        expected_watcher = expected_watchers[i].id
        result_watcher = result_watchers[i]
        self.assertEqual(expected_watcher, result_watcher)

  def checkCommentEqual(self, expected_comment, result_comment):
    self.assertEqual(expected_comment["text"], result_comment["text"])
    self.assertEqual(expected_comment["user"], result_comment["user"])
    self.assertEqual(expected_comment["issue"], result_comment["issue"])