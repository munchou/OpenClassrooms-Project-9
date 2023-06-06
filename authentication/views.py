from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

from website import messages
from .forms import UserRegistrationForm, ProfileUpdateForm, SubscribeForm
from .models import Profile, UserFollow

from urllib.parse import urlparse
import os


def signup_page(request):
    """Sign up page that connects and redirects
    the user right after having registered."""
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            # new_user.set_password(user_form.cleaned_data["password"])
            if user_form.cleaned_data["password"] == user_form.cleaned_data["confirm_password"]:
                new_user.set_password(user_form.cleaned_data["password"])
                new_user.save()
                Profile.objects.create(user=new_user)
                login(request, new_user)
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.signup_page_error(request)
    else:
        user_form = UserRegistrationForm()
    return render(
        request,
        "authentication/signup.html",
        {"user_form": user_form})


@login_required
def edit_profile(request):
    """Allows the user to change their profile picture by
    uploading a new one. The new file is resized/cropped,
    and the previous file is deleted from the server."""
    if request.method == 'POST':
        original_image = request.user.profile.profile_photo
        profile_form = ProfileUpdateForm(
                                    instance=request.user.profile,
                                    data=request.POST,
                                    files=request.FILES)
        if profile_form.is_valid():
            new_image = request.user.profile.profile_photo
            try:
                if original_image != "profile_pics/default.png" and original_image != new_image:
                    os.remove(f".{original_image.url}")
            except FileNotFoundError:
                pass
            profile_form.save()
            messages.edit_profile_success(request)
        else:
            messages.edit_profile_error(request)
    else:
        profile_form = ProfileUpdateForm(
                                    instance=request.user.profile)
    return render(request,
                  'authentication/profile.html',
                  {'profile_form': profile_form})


@login_required
def user_list(request):
    """Gets the list of all existing user except the
    requesting user, so that all users but him/her
    is displayed on the page."""
    users = Profile.objects.exclude(user=request.user)
    return render(request, "authentication/user_list.html", {"users": users})


@login_required
def user_detail(request, pk):
    """Allows the user to follow/unfollow another user
    directly from their user page. The button state changes
    depending on the following status."""
    profile = Profile.objects.get(user=pk)
    
    following_users = UserFollow.objects.filter(user=request.user).order_by('followed_user')
    followed_by = UserFollow.objects.filter(followed_user=request.user).order_by('user')

    context = {
        "user": profile,
        "following_user": following_users,
        "followed_by": followed_by}

    return render(request, "authentication/user_detail.html", context)


@login_required
def follow(request, pk):
    """Allows the user to follow a given user by
    pressing its corresponding button. Shows an
    error message if the given user is already
    being followed or does not exist."""
    profile = Profile.objects.get(user_id=pk)
    users = User.objects.all()
    following_users = UserFollow.objects.filter(user=request.user).order_by('followed_user')
    print(f"FOLLOWING USERS: {following_users}")
    for item in following_users:
        print(f"ITEM: {item.followed_user}")

    for user in users:
        if str(profile.user) == user.username:
            user_to_follow = User.objects.get(username=user.username)
            if user_to_follow not in following_users:
                try:
                    UserFollow.objects.create(user=request.user, followed_user=user_to_follow)
                    messages.follow_success(request, user_to_follow)
                    break
                except IntegrityError:
                    messages.follow_error(request, user_to_follow)
                    break
                
            break
    
    frontend_url = request.META.get('HTTP_REFERER')
    url = urlparse(frontend_url)
    print(f"\nURL:{url}\n")
    print(url.path)

    return redirect(f"../..{url.path}")


@login_required
def unfollow(request, pk):
    """Allows the user to unfollow a given user by
    pressing its corresponding button."""
    profile = Profile.objects.get(user_id=pk)
    user_to_delete = UserFollow.objects.get(user=request.user, followed_user=profile.user)
    messages.unfollow_warning(request, user_to_delete)
    user_to_delete.delete()

    frontend_url = request.META.get('HTTP_REFERER')
    url = urlparse(frontend_url)
    print(f"\nURL:{url}\n")
    print(url.path)

    return redirect(f"../..{url.path}")


@login_required
def subscribe_textinput(request):
    """Allows the user to follow another user by entering their
    name inside the text field. Shows an error message if the given
    user is already being followed or does not exist."""
    users_list = Profile.objects.exclude(user=request.user)

    if request.method == "POST":
        form = SubscribeForm(request.POST)
        current_user_profile = request.user
        input = request.POST.get('followed_user')
        users = User.objects.all()
        no_user = True

        if form.is_valid():
            for user in users:
                if input == user.username:
                    user_to_follow = User.objects.get(username=input)
                    if user_to_follow == current_user_profile:
                        messages.subscribe_cannot_follow(request)
                        no_user = False
                        break
                    else:
                        try:
                            UserFollow.objects.create(user=request.user, followed_user=user_to_follow)
                            messages.subscribe_success(request, user_to_follow)
                            no_user = False
                            break
                        except IntegrityError:
                            messages.subscribe_already_following(request, user_to_follow)
                            no_user = False
                            break

            if no_user:
                messages.subscribe_no_user(request, input)
                form = SubscribeForm()

    else:
        form = SubscribeForm()
    
    following_users = UserFollow.objects.filter(user=request.user).order_by('followed_user')
    followed_by = UserFollow.objects.filter(followed_user=request.user).order_by('user')

    context = {
        "user_form": form,
        "users": users_list,
        "following_user": following_users,
        "followed_by": followed_by}

    return render(request, "authentication/subscriptions.html", context)
