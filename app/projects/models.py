from statistics import mode
from xml.etree.ElementTree import TreeBuilder
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=32)
    desc = models.CharField(max_length=100, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class User(models.Model):
    name = models.CharField(max_length=32)
    active = models.BooleanField()
    projects = models.ManyToManyField(Project, blank=True)

    def isActive(self):
        if self.active == True:
            return True
        else:
            return False

    def inProject(self, pid):
        if self.projects.filter(pk=pid).exists():
            return True
        else:
            return False

    def __str__(self):
        return self.name

    def __repr__(self):
        return "User name: {}".format(self.name)


class Sprint(models.Model):
    name = models.CharField(max_length=32)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('name', 'project'))


class Label(models.Model):
    value = models.CharField(max_length=32)

    def __str__(self):
        return self.value


class Issue(models.Model):
    summary = models.CharField(max_length=32)
    creation_date = models.DateTimeField(auto_now_add=True)
    desc = models.CharField(max_length=100, blank=True)

    # type - either bug or task
    type = models.CharField(max_length=32)

    # status - the order below must be followed:
    # open -> assigned -> inprogress -> under review -> done -> close
    status = models.CharField(max_length=32, default="open", blank=True)
    statusList = ["open", "assigned", "inprogress", "under review", "done", "close"]

    labels = models.ManyToManyField(Label, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="assignee")
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    watchers = models.ManyToManyField(User, blank=True, related_name="watchers")

    def __str__(self):
        return self.summary

    class Meta:
        unique_together = (('summary', 'project'))

    def setAssignee(self, user):
        self.assignee = user

    def setSprint(self, newSprint):
        self.sprint = newSprint

    def addLabel(self, label):
        self.labels.add(label)

    def addWatcher(self, watcher):
        self.watchers.add(watcher)

    def removeWatcher(self, watcher):
        self.watchers.remove(watcher)

    def isWatcher(self, watcher):
        if watcher in self.watchers.all():
                return True
        return False

    def updateStatus(self, updated_status):
        lastStatus = "close"
        if self.status == lastStatus:
            print("Issues status = {}, it can no longer be updated".format(self.status))
        else:
            statusList = self.statusList
            for i in range(len(statusList)):
                if self.status == statusList[i]:
                    break

            if updated_status == statusList[i + 1]:
                print(
                    "Issue status successfully updated from {} to {}"
                    .format(self.status, updated_status))
                self.status = updated_status
            else:
                print(
                    "Issue status cannot be updated from {} to {}"
                    .format(self.status, updated_status))


class Comment(models.Model):
    text = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    def setText(self, newText):
        self.text = newText

    def setUser(self, newUser):
        self.user = newUser

    def setIssue(self, newIssue):
        self.issue = newIssue
    
    def __str__(self):
        return self.text








