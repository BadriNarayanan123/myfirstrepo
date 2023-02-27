from cmath import log
from urllib import response
from .forms import RoomForm,UserForm,MyUserCreationForm
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Room,Topic,Message,User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def logoutUser(request):
    logout(request)
    return redirect('home')

def loginPage(request):
    page = 'login'
    context = {'page':page}
    
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is not valid')

    return render(request,'base/login_register.html',context)

def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()
    context = {'page':page,'form':form}
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Error during registration')
    
    return render(request,'base/login_register.html',context)




def home(request):
    q = request.GET.get('q') if request.GET.get('q')!= None else ''
    room= Room.objects.filter(
        Q(topic__name__icontains = q) | 
        Q(name__icontains = q) | 
        Q(description__icontains=q)
        )

    room_count = room.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    topics = Topic.objects.all()
    context = {'rooms':room,'topics':topics,'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            body = request.POST.get('body'),
            room = room
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    context = {'rooms':room,'room_messages':room_messages,'participants':participants} 
    return render(request,'base/room.html',context)

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms,'topics':topics,'room_messages':room_messages}
    return render(request,'base/profile.html',context)

def test(request):  
    return render(request,'child.html')

@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm(request.POST)
    topic = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
            topic = topic
        )
        return redirect('home')
    context = {'forms':form,'topics':topic}
    return render(request,'base/room_form.html',context)

@login_required(login_url='/login') 
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topic_room = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse('You are not allowed to Edit')

    context = {'forms':form,'rooms':room,'topics':topic_room}
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()
        return redirect('home')
        # if form.is_valid():
        #     form = RoomForm(request.POST,instance=room)
        #     form.save()
        #     return redirect('home')

    return render(request,'base/room_form.html',context)


@login_required(login_url='/login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    context = {'obj':room}
    if request.method == 'POST':
        #Room.objects.filter(id=pk).delete()
        room.delete()
        return redirect('home')
    
    return render(request,'base/delete.html',context)

@login_required(login_url='/login')
def deleteMessage(request,pk):
    messages = Message.objects.get(id=pk)
    context = {'obj':messages}

    if request.user != messages.user:
        return HttpResponse('You are not allowed to delete here')

    if request.method == 'POST':
        #Room.objects.filter(id=pk).delete()
        messages.delete()
        return redirect('home')
    
    return render(request,'base/delete.html',context)


def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    context = {'form':form}

    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)

    return render(request,'base/update-user.html',context)

def topicPage(request):
    q = request.GET.get('q') if request.GET.get('q')!=None else ''
    topics = Topic.objects.filter(name__icontains = q)
    return render(request,'base/topics.html',{'topics':topics})

def activity(request):
    room_messages = Message.objects.all()
    return render(request,'base/activity.html',{'room_messages':room_messages})