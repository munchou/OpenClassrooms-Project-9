"""
URL configuration for litreview project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
# from django.conf.urls import (handler400, handler403, handler404, handler500)

import authentication.views
import website.views


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", LoginView.as_view(
        template_name="authentication/login.html",
        redirect_authenticated_user=True),
        name="login"
        ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("home/", website.views.feed, name="feed"),
    path("signup/", authentication.views.signup_page, name="signup"),
    path("profile/", authentication.views.edit_profile, name="editprofile"),
    path("unfollow/<int:pk>/", authentication.views.unfollow, name="unfollow"),
    path("follow/<int:pk>/", authentication.views.follow, name="follow"),
    path("subscribe/", authentication.views.subscribe_textinput, name="subscribe"),

    path("ticket/new-ticket/", website.views.new_ticket, name="newticket"),
    path("ticket/<int:ticket_id>/edit/", website.views.edit_ticket, name="editticket"),
    path("deleteticket/<int:ticket_id>/", website.views.delete_ticket, name="deleteticket"),
    path("ticket/<int:ticket_id>/reply/", website.views.ticket_reply, name="replyticket"),
    path("review/new-review/", website.views.new_review, name="newreview"),
    path("review/<int:review_id>/edit/", website.views.edit_review, name="editreview"),
    path("deletereview/<int:review_id>/", website.views.delete_review, name="deletereview"),
    path("mycontent/", website.views.user_posts, name="userposts"),
]

handler404 = website.views.page_not_found_view


if settings.DEBUG:
    from django.views import defaults as default_views
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += [
         path( 
             "404/", 
             default_views.page_not_found, 
             kwargs={"exception": Exception("Page not Found")}, 
         ),
     ]
