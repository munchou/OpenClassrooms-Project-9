from django.contrib import messages


# USERS

def signup_page_error(request):
    messages.error(request, "The passwords do not match!")


def edit_profile_success(request):
    messages.success(request, 'Profile updated successfully')


def edit_profile_error(request):
    messages.error(request, 'Error updating your profile')


def follow_success(request, user_to_follow):
    messages.success(request, f"Now following {user_to_follow}")


def follow_error(request, user_to_follow):
    messages.error(request, f"You are already following {user_to_follow}")


def unfollow_warning(request, user_to_delete):
    messages.warning(request, f"You are not following {user_to_delete.followed_user} anymore")


def subscribe_cannot_follow(request):
    messages.error(request, f"You cannot follow yourself")


def subscribe_success(request, user_to_follow):
    messages.success(request, f"Now following {user_to_follow}")


def subscribe_already_following(request, user_to_follow):
    messages.error(request, f"You are already following {user_to_follow}")


def subscribe_no_user(request, input):
    messages.error(request, f"The user {input} does not exist")


# TICKETS and REVIEWS

def delete_ticket_success(request):
    messages.success(request, ("You have deleted your ticket"))


def ticket_reply_success(request, ticket):
    messages.success(request, f'Your response to "{ticket.title}" has been posted!')


def delete_review_error(request):
    messages.error(request, ("Only the author has permissions to do so"))


def delete_review_success(request):
    messages.success(request, ("You have deleted your review"))