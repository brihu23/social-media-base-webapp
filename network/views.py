from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.core.exceptions import SuspiciousOperation 
from django.urls import reverse
from django import forms
from .models import User, Profile, Post
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from datetime import datetime


def index(request):
    #return render(request, "network/index.html")
    return HttpResponseRedirect(reverse("all_post", args=(1, 0, 0)))


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
            profile = Profile.objects.create(user=user)
            
            user.save()
            profile.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def new_post(request):

    try: 
        content = request.POST["post"]
    except KeyError:
        raise SuspiciousOperation('Wrong method')


    post = Post(
        author= request.user,
        content=content,
        )
    post.save()

    return HttpResponseRedirect(reverse("all_post", args=(1, 0, 0)))
    #return HttpResponseRedirect(reverse("index"))

def all_post(request, page_num, types, profid):

    #0 all posts, 1 for following, 2 for user posts
    allposts = True
    profile = False
    same = False
    following = False
    followingposts = False
    person_profile = request.user
    numfollowers = 0
    numfollowing = 0
    title = False

    if types == 0:
        posts = Post.objects.all().order_by('-timestamp')
        title = "all posts"
    elif types == 1:
        print (Profile.objects.filter(followers__username=request.user.username).values_list("user"))
        posts = Post.objects.filter(author__in = Profile.objects.filter(followers__username=request.user.username).values("user")).order_by('-timestamp')
        allposts= False
        followingposts = True
        title = "following"
    elif types == 2:
        #swithc 1 for useid
        person_profile = User.objects.get(pk=profid)
        posts = Post.objects.filter(author = person_profile).order_by('-timestamp')
        allposts = False
        profile = True
        numfollowers = len(Profile.objects.get(user = person_profile).followers.all())
        numfollowing = len(Profile.objects.filter(followers__username=person_profile.username))



        print (numfollowers)
        if person_profile.username == request.user.username:
            same = True


        if Profile.objects.filter(user = person_profile, followers__username=request.user.username).exists():
            following = True

    

        

    p = Paginator(posts, 10)
    print(following)
    
    likes = []
    

    for post in p.page(page_num):
        likecount = len(post.likes.all())
        hasliked = Post.objects.filter(pk=post.id, likes__username=request.user.username).exists()
        info = [likecount, hasliked]
        likes.append(info)

    print()

 
    posts = zip(p.page(page_num), likes)

    context = {
        "allposts" : allposts,
        "profile": profile,
        "current_page_num" : page_num,
        "next_page": page_num + 1,
        "previous_page": page_num - 1,
        "num_pages" : p.num_pages,
        "rnum_pages": range(1, p.num_pages + 1),
        "posts" : posts,
        "profname": person_profile,
        "same": same,
        "following": following,
        "numfollowers": numfollowers,
        "numfollowing": numfollowing,
        "followingposts" : followingposts,
        "type": types,
        "title": title,



    }

    return render(request, "network/index.html", context)

def like(request, post_id):

    if request.method == "PUT":
        #return JsonResponse({"hi": "hello"})
        data = json.loads(request.body)
        if data.get("liker") is not None:
            liker = data["liker"]
            post = Post.objects.get(pk= post_id)
            likerobj = User.objects.get(username=liker)      
        
            if post.author.username == liker:
                return JsonResponse({"message": "own"})        

            elif Post.objects.filter(pk = post_id, likes__username=liker).exists():
                post.likes.remove(likerobj)
                post.save()
                return JsonResponse({"message": "unlike", "likes": len(post.likes.all())})
            else:
                post.likes.add(likerobj)
                #return JsonResponse({"hi": likerobj.id})
                post.save()
                return JsonResponse({"message": "like", "likes": len(post.likes.all())})
        else:
            return JsonResponse({"message": "account error"}, status=500)

def follow(request):

    if request.method == "PUT":
        data = json.loads(request.body)
        ptof = data['ptof']        

        profile = Profile.objects.get(user = (User.objects.get(pk = ptof)))
        print(profile)
        print (len(profile.followers.all()))

        if profile.user.username == request.user.username:
            return JsonResponse({"message": "own"})  
        elif Profile.objects.filter(pk = profile.id, followers__username=request.user.username).exists():
            profile.followers.remove(request.user)
            profile.save()
            print (len(profile.followers.all()))
            return JsonResponse({"message": "unfollowed", "numfoll": len(profile.followers.all())})
        else:
            profile.followers.add(request.user)
            profile.save()
            print (len(profile.followers.all()))
            return JsonResponse({"message": "followed", "numfoll": len(profile.followers.all()) })


def post(request):

    if request.method == "PUT":
        data = json.loads(request.body)

        post_id = data["post_id"]
        newContent = data["newContent"]
        post = Post.objects.get(pk = post_id)

        if post.author != request.user:
            return JsonResponse({"message": "jerk"})
        else:
            post.content = newContent
            post.timestamp = datetime.now()
            post.save()
            return JsonResponse({"message": newContent })









   





