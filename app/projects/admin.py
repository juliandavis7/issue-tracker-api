from django.contrib import admin

from .models import Project, User, Issue, Label, Sprint, Comment

admin.site.register(Project)
admin.site.register(User)
admin.site.register(Issue)
admin.site.register(Label)
admin.site.register(Sprint)
admin.site.register(Comment)



