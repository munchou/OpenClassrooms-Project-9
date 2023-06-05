from itertools import chain
from django.db.models import CharField, Value
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from . import forms
from . import models
from authentication.models import UserFollow, Profile

from django.contrib.auth.models import User


def get_user_follows(user):
    """Gets the list of users followed by the current user"""

    follows = UserFollow.objects.filter(user=user)
    followed_users = []
    for follow in follows:
        followed_users.append(follow.followed_user)

    return followed_users


def get_user_viewable_reviews(user: User):
    """Get the reviews according to filtering conditions."""

    followed_users = get_user_follows(user)
    followed_users.append(user)

    reviews = []
    all_reviews = models.Review.objects.filter(user__in=followed_users).distinct()
    for review in all_reviews:
        reviews.append(review.id)

    user_tickets = models.Ticket.objects.filter(user=user)
    for ticket in user_tickets:
        review_responses = models.Review.objects.filter(ticket=ticket)
        for review in review_responses:
            reviews.append(review.id)

    reviews = models.Review.objects.filter(id__in=reviews).distinct()

    return reviews


def get_user_viewable_tickets(user: User):
    """Get the tickets according to filtering conditions.
    Optional: hides tickets that got a reply."""

    followed_users = get_user_follows(user)
    followed_users.append(user)

    tickets = models.Ticket.objects.filter(user__in=followed_users)

    # To hide the tickets in the feed that got a review:
    # for ticket in tickets:
    #     if ticket.reply:
    #         tickets = tickets.exclude(id=ticket.id)

    return tickets


@login_required
def feed(request):
    """Feed page where the tickets and reviews are displayed,
    according to specific constraints.
    The tickets and reviews are sorted according to the
    date of their creation (descending)."""

    # Get ALL the tickets and reviews for the reply function:
    ticket_all = models.Ticket.objects.all()
    review_all = models.Review.objects.all()

    tickets_and_reviews_all = sorted(chain(ticket_all, review_all), key=lambda instance: instance.time_created, reverse=True)

    reviews = get_user_viewable_reviews(request.user)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_user_viewable_tickets(request.user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    

    tickets_and_reviews = sorted(
        chain(tickets, reviews),
        key=lambda instance: instance.time_created,
        reverse=True)

    paginator = Paginator(tickets_and_reviews, 4)

    page_number = request.GET.get("page")
    tickets_and_reviews_pages = paginator.get_page(page_number)

    context = {"tickets_and_reviews": tickets_and_reviews_pages, "tickets_and_reviews_all": tickets_and_reviews_all}
    return render(request, "website/feed.html", context)


@login_required
def user_posts(request):
    """Displays the current user's content
    (tickets and reviews they posted)."""

    # Get ALL the tickets and reviews for the reply function
    # (or else the replied tickets won't show):
    ticket_all = models.Ticket.objects.all()
    review_all = models.Review.objects.all()

    tickets_and_reviews_all = sorted(chain(ticket_all, review_all), key=lambda instance: instance.time_created, reverse=True)

    tickets = models.Ticket.objects.filter(user=request.user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    reviews = models.Review.objects.filter(user=request.user)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets_and_reviews = sorted(
        chain(tickets, reviews),
        key=lambda instance: instance.time_created,
        reverse=True)

    paginator = Paginator(tickets_and_reviews, 4)

    page_number = request.GET.get("page")
    tickets_and_reviews_pages = paginator.get_page(page_number)

    context = {"tickets_and_reviews": tickets_and_reviews_pages, "tickets_and_reviews_all": tickets_and_reviews_all}
    return render(request, "website/user_posts.html", context)


@login_required
def new_ticket(request):
    """Form to post a new ticket."""

    form = forms.CreateTicket()
    if request.method == "POST":
        form = forms.CreateTicket(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect("feed")
    return render(request, "website/newticket.html", context={"ticket_form": form})


@login_required
def edit_ticket(request, ticket_id):
    """Form to update or delete an existing ticket,
    with the possibility of changing the book's picture.
    Compares the pictures' names, resizes/crops the
    new one if necessary.
    The previous picture is erased from the server."""

    ticket = get_object_or_404(models.Ticket, id=ticket_id)
    edit_ticket = forms.CreateTicket(instance=ticket)
    delete_ticket = forms.DeleteTicket()

    if ticket.user != request.user:
        print("You cannot edit that page.")
        return redirect("feed")

    elif request.method == "POST":
        if "edit_ticket" in request.POST:
            edit_ticket = forms.CreateTicket(request.POST, request.FILES, instance=ticket)
            original_image = ticket.image
            if edit_ticket.is_valid():
                new_image = ticket.image
                if original_image and original_image != new_image:
                    ticket.delete_image(original_image)
                edit_ticket.save()
                return redirect("feed")
        if "delete_ticket" in request.POST:
            delete_ticket = forms.DeleteTicket(request.POST, request.FILES)
            if delete_ticket.is_valid():
                ticket.delete()
                return redirect("feed")
    
    context = {"edit_ticket": edit_ticket, "delete_ticket": delete_ticket}

    return render(request, "website/edit_ticket.html", context)


@login_required
def delete_ticket(request, ticket_id):
    """Allows the user to delete one of
    their tickets directly from the feed page
    in one simple click (no confirmation message)."""

    ticket = models.Ticket.objects.get(id=ticket_id)

    if ticket.user != request.user:
        print("You cannot edit that page.")
        return redirect("feed")
    ticket.delete()
    messages.success(request, ("You have deleted your ticket"))
    return redirect("feed")


@login_required
def new_review(request):
    """Form to post a new review
    (includes a ticket as well)."""

    form_ticket = forms.CreateTicket()
    form_review = forms.CreateReview()
    if request.method == "POST":
        form_ticket = forms.CreateTicket(request.POST, request.FILES)
        form_review = forms.CreateReview(request.POST)
        if form_ticket.is_valid() and form_review.is_valid():
            ticket = form_ticket.save(commit=False)
            review = form_review.save(commit=False)
            review.ticket = ticket
            ticket.user = request.user
            ticket.reply = True
            review.user = request.user
            ticket.save()
            review.save()
            return redirect("feed")
    
    context = {"ticket_form": form_ticket, "review_form": form_review}
    return render(request, "website/newreview.html", context)


@login_required
def edit_review(request, review_id):
    """Form to update or delete an existing review.
    If deleted, its linked ticket's reply value is
    changed to False so that it can get a new reply."""

    review = get_object_or_404(models.Review, id=review_id)
    edit_review = forms.CreateReview(instance=review)
    delete_review = forms.DeleteReview()

    if review.user != request.user:
        print("You cannot edit that page.")
        return redirect("feed")

    elif request.method == "POST":
        if "edit_review" in request.POST:
            edit_review = forms.CreateReview(request.POST, instance=review)
            if edit_review.is_valid():
                edit_review.save()
                return redirect("feed")

        if "delete_review" in request.POST:
            delete_review = forms.DeleteReview(request.POST)
            if delete_review.is_valid():
                review.ticket.reply = False
                review.ticket.save()
                review.delete()
                return redirect("feed")

    context = {"edit_review": edit_review, "delete_review": delete_review}

    return render(request, "website/edit_review.html", context)


@login_required
def ticket_reply(request, ticket_id):
    """Form to post a review as a reply to a ticket.
    The reply value is changed to True so that the icket
    can not get another reply. That boolean is also
    used to change the appearance of the "Reply" button."""

    ticket = get_object_or_404(models.Ticket, id=ticket_id)

    if request.method == "POST":
        post_review = forms.CreateReview(request.POST)
        if post_review.is_valid():

            models.Review.objects.create(    
                ticket=ticket,
                user=request.user,
                headline=request.POST['headline'],
                rating=request.POST['rating'],
                comment=request.POST['comment']
            )
            ticket.reply = True
            ticket.save()
            messages.success(request, f'Your response to "{ticket.title}" has been posted!')
            return redirect("feed")

    else:
        post_review = forms.CreateReview()

    context = {
        "review_form": post_review,
        "ticket": ticket
    }

    return render(request, "website/newreview.html", context)


@login_required
def delete_review(request, review_id):
    """Allows the user to delete one of
    their reviews directly from the feed page
    in one simple click (no confirmation message).
    Updates its linked ticket's reply value to False
    so that it can get a new reply."""

    review = models.Review.objects.get(id=review_id)

    if review.user != request.user:
        messages.error(request, ("Only the author has permissions to do so"))
        print("You cannot edit that page.")
        return redirect("feed")
    review.ticket.reply = False
    review.ticket.save()
    review.delete()
    messages.success(request, ("You have deleted your review"))
    return redirect("feed")


def page_not_found_view(request, exception):
    """A customized 404 page."""

    return render(request, '404.html', status=404)
