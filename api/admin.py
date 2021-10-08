from django.contrib import admin

from .models import (Announce, Comment, Follow, Idea, Like, Memo, Notification,
                     Profile, Report, Thread, Topic, User)

# Register your models here.

admin.site.register(Announce)
admin.site.register(Comment)
admin.site.register(Follow)
admin.site.register(Idea)
admin.site.register(Like)
admin.site.register(Memo)
admin.site.register(Notification)
admin.site.register(Profile)
admin.site.register(Report)
admin.site.register(Thread)
admin.site.register(Topic)
admin.site.register(User)
