import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.paginator import Paginator
from django.core import serializers


from .models import User, Post

@csrf_exempt
def index(request):
    postings = Post.objects.all()
    paginator = Paginator(postings, 10)
    #print(p.page(1).has_next(), p.count)
    #next = p.page(1).has_next()
    #print(next)
    #if p.page(1).has_next():
    #    next = "true"
    #else:
    #    next = "false"
    #print(f"Next value {next}")
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
    "page_obj": page_obj, "next": next, "previous": "false", "extra_space": len(paginator.page(1).object_list)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
def addpost(request):
    data = json.loads(request.body)
    content = data.get("body", "")
    user = User.objects.get(username=request.user.username)
    post = Post(name=user, content=content)
    post.save()
    return JsonResponse({"message": "Post added successfully."}, status=201)
