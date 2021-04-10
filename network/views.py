import json
import datetime
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.paginator import Paginator
from django.core import serializers


from .models import User, Post, Like, Follow

@csrf_exempt
def index(request):
    postings = Post.objects.all().order_by('-timestamp')
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
    liked_posts = []
    for page in page_obj:
        a = Like.objects.filter(post=page)
        print(a)
        if len(a) > 0:
            for x in a:
                if x.name.username == request.user.username:
                    liked_posts.append(x.post)
        #print(a)
        #if len(a) > 0:
        #print(a.post)
        #liked_posts.append(page)
    print('---------------')
    print(liked_posts)
    print('---------------')
    return render(request, "network/index.html", {
    "page_obj": page_obj, "next": next, "previous": "false", "extra_space": len(paginator.page(1).object_list), "liked_posts": liked_posts
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


@csrf_exempt
def editpost(request):
    data = json.loads(request.body)
    id = data.get("id", "")
    body = data.get("body", "")
    post = Post.objects.get(pk=id)
    post.content = body
    post.save()
    print(post.content)
    print('In editpost')
    print(body)
    return JsonResponse({"message": "Test ok", "date": datetime.datetime.now().strftime("%b %d %Y, %I:%M %p")})

@csrf_exempt
def likepost(request):
    user = User.objects.get(pk=request.user.id)
    data = json.loads(request.body)
    id = data.get("id", "")
    post = Post.objects.get(pk=id)
    print(post,user)
    likedpost = Like(name=user, post=post)
    print(likedpost)
    likedpost.save()
    post.likes += 1
    post.save()
    return JsonResponse({"message": "Post liked successfully."}, status=201)

@csrf_exempt
def unlikepost(request):
    user = User.objects.get(pk=request.user.id)
    data = json.loads(request.body)
    id = data.get("id", "")
    post = Post.objects.get(pk=id)
    print(post,user)
    unlikedpost = Like.objects.filter(post=post).all()
    for post_a in unlikedpost:
        if post_a.name.username == request.user.username:
            post_a.delete()
    print(unlikedpost)
    post.likes -= 1
    post.save()
    return JsonResponse({"message": "Post unliked successfully."}, status=201)

def users(request, name):
    user = User.objects.get(username=name)
    posts = Post.objects.filter(name=user).all().order_by('-timestamp')
    follows = Follow.objects.filter(name=request.user).all()
    following_count = len(Follow.objects.filter(name=user).all())
    followers_count = len(Follow.objects.filter(following=user).all())
    is_following = "false"
    for follow in follows:
        if follow.following == user:
            is_following = "true"
    liked_posts = []
    for post in posts:
        a = Like.objects.filter(post=post)
        print(a)
        if len(a) > 0:
            for x in a:
                if x.name.username == request.user.username:
                    liked_posts.append(x.post)
    return render(request, "network/profile.html", {
    "user": user, "posts": posts, "liked_posts": liked_posts, "is_following": is_following, "following_count": following_count, "followers_count": followers_count
    })
    return HttpResponse(f"Hello {name}")

@csrf_exempt
def follow(request):
    data = json.loads(request.body)
    id = data.get("id", "")
    user = User.objects.get(pk=id)
    follow = Follow(name=request.user, following=user)
    follow.save()
    return JsonResponse({"message": "Follwed User"}, status=201)

@csrf_exempt
def unfollow(request):
    data = json.loads(request.body)
    id = data.get("id", "")
    users = Follow.objects.filter(name=request.user).all()
    for user in users:
        if user.following.id == id:
            user.delete()
    return JsonResponse({"message": "UnFollwed User"}, status=201)


def following(request):
    posts = Post.objects.all().order_by('-timestamp')
    a = []
    b = []
    following = Follow.objects.filter(name=request.user).all()
    for f in following:
        b.append(f.following)
    for post in posts:
        if post.name in b:
            a.append(post)
    return render(request, "network/following.html", {
    "posts": a
    })
