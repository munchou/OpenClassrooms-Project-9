from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Profile
from website.models import Review, Ticket


admin.site.unregister(Group)


# Mix Profile info into User info
class ProfileInline(admin.StackedInline):
    model = Profile


# Extend User Model
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [ProfileInline]


admin.site.unregister(User)


admin.site.register(User, UserAdmin)
# admin.site.register(Profile)

admin.site.register(Review)
admin.site.register(Ticket)
