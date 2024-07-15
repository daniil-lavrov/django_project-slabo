import datetime
import random
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.db.models import Q, F
from django.utils import timezone

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from .models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, FriendShip, Challenges, Comment

from .forms import UserRegistrationForm, ChallCreatingForm


def about(request):
    return render(request, 'main/about.html')

def check_deadline():
    current_time = timezone.now().date()
    challs = Challenges.objects.filter((Q(deadline__lt=current_time) | Q(progress=F('duration'))))

    if challs:
        for chall in challs:
            chall.is_active = False
            chall.save()

@login_required(login_url="login")
def cur(request):
    check_deadline()
    list_of_chall_todo = Challenges.objects.filter((Q(owner=request.user.nick) | Q(added_friend=request.user.nick)) & Q(is_active=True, deadline=timezone.now().date()))
    list_of_chall_done = Challenges.objects.filter((Q(owner=request.user.nick) | Q(added_friend=request.user.nick)) & Q(is_active=True, deadline__gt=timezone.now().date()))
    context = {'list_of_chall': list_of_chall_todo, 'list_of_chall_done': list_of_chall_done}
    return render(request, 'main/cur.html', context)

@login_required(login_url="login")
def done(request):
    check_deadline()
    list_of_chall = Challenges.objects.filter(
        (Q(owner=request.user.nick) | Q(added_friend=request.user.nick)) & Q(is_active=False))
    if list_of_chall:
        context = {'list_of_chall': list_of_chall}
        return render(request, 'main/done.html', context)
    else:
        return render(request, 'main/done.html')

@csrf_exempt
def delete_chall(request):
    if request.method == 'POST':
        chall_id = request.POST.get('chall', '')
        if chall_id:
            try:
                cur_line = Challenges.objects.get(id=chall_id)
                cur_line.delete()
                return JsonResponse({'status': 'success'})
            except Challenges.DoesNotExist:
                return JsonResponse({'status': 'error'}, status=404)
        else:
            return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required(login_url="login")
def save_comment(request, chall_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        comment = data.get('comment')
        if comment:
            # Assuming you have a Challenge model and a Comment model
            challenge = Challenges.objects.get(id=chall_id)
            comment = '(' + request.user.nick + '): ' + comment
            new_comment = Comment(challenge=challenge, text=comment)
            new_comment.save()

            return JsonResponse({'success': True, 'comment': comment})

    return JsonResponse({'success': False})

@csrf_exempt
@login_required(login_url="login")
def get_comments(request, chall_id):
    try:
        challenge = Challenges.objects.get(id=chall_id)
        list_of_comments = list(Comment.objects.filter(challenge=challenge).values_list('text', flat=True))
        data = {
            'success': True,
            'comments': list_of_comments
        }
        return JsonResponse(data)
    except:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required(login_url="login")
def friends(request):
    user_friends = FriendShip.objects.filter(user=request.user.nick, confirmed=True)
    new_friends_count = FriendShip.objects.filter(friend=request.user.nick, confirmed=False).count()
    if user_friends:
        context = {'list_of_friends': user_friends, 'new_apply': new_friends_count}
        return render(request, 'main/friends.html', context)
    else:
        context = {'new_apply': new_friends_count}
        return render(request, 'main/friends.html', context)

@login_required(login_url="login")
@csrf_exempt
def new_applays(request):
    #FriendShip.objects.all().delete()
    #Challenges.objects.all().delete()
    #Comment.objects.all().delete()
    if request.method == 'POST':
        nick = request.POST.get('nick', '')
        if nick:
            FriendShip.objects.filter(user=nick, friend=request.user.nick).update(confirmed=True)
            user = request.user.nick
            friend = nick
            FriendShip.objects.get_or_create(user=user, friend=friend, defaults={'confirmed': True})
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error'}, status=400)
    else:
        new_friends = FriendShip.objects.filter(friend=request.user.nick, confirmed=False)
        if new_friends:
            context = {'list_of_new_friends': new_friends}
            return render(request, 'main/new_friends.html', context)
        else:
            return render(request, 'main/new_friends.html')

@login_required(login_url="login")
def chall(request):
    return render(request, 'main/look_at_chall.html')

@csrf_exempt
@login_required(login_url="login")
def create(request):
    friend_to_invite = request.GET.get('friend', None)
    if request.method == 'POST':
        form = ChallCreatingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            descr = form.cleaned_data['descr']
            owner = request.user.nick
            added_friend = form.cleaned_data['added_friend']
            duration = form.cleaned_data['duration']
            progress = 0
            is_active = True

            chat = GigaChat(credentials='ZThhMjQxNWMtMzllNi00YWI4LTliY2MtYTY4Yzg4NjYxMzRlOjk3Yzc3YThkLTc1ZmUtNDI4MC1hN2NmLWU0NDk5YzlmZmY0Nw==', verify_ssl_certs=False)
            messages = [
                SystemMessage(
                    content="Тебе предоставяют заголовок, описание и длительность челленджа. Твоя задача оценить "
                            "сложность его выполнения от 1 до 99, где 1 - совершенно не требует усилий, а 99 - на грани невозможного"
                            "В качестве ответа ты должен предоставить просто число."
                            "Примеры:"
                            "Запрос 1: Бегать + очень быстро по 30 километров + 30 дней. Твой ответ: 80"
                            "Запрос 2: Лежать на диване + ничего не делать + 30 дней. Твой ответ: 1"
                )
            ]

            new_chall = title + '+' + descr + '+' + str(duration)
            messages.append(HumanMessage(content=new_chall))
            res = chat(messages)
            messages.append(res)

            score_for_win = int(res.content)
            deadline = timezone.now().date()
            Challenges.objects.create(
                title=title,
                descr=descr,
                owner=owner,
                added_friend=added_friend,
                duration=duration,
                progress=progress,
                is_active=is_active,
                score_for_win=score_for_win,
                deadline=deadline
            )
            return redirect('cur')
        else:
            form = ChallCreatingForm()
            user_friends = FriendShip.objects.filter(user=request.user.nick, confirmed=True)
            if user_friends:
                context = {'list_of_friends': user_friends, 'form': form, 'extra_param': 'Некорректные данные, выберите друга'}
                return render(request, 'main/create_chall.html', context)
            else:
                return render(request, 'main/create_chall.html', {'form': form, 'extra_param': 'Некорректные данные, выберите друга'})
    else:
        form = ChallCreatingForm()
        user_friends = FriendShip.objects.filter(user=request.user.nick, confirmed=True)
        if user_friends:
            context = {'list_of_friends': user_friends, 'form': form, 'friend_to_invite': friend_to_invite}
            return render(request, 'main/create_chall.html', context)
        else:
            return render(request, 'main/create_chall.html', {'form': form, 'friend_to_invite': friend_to_invite})

@csrf_exempt
def chall_is_done(request):
    if request.method == 'POST':
        chall_id = request.POST.get('chall', '')
        if chall_id:
            try:
                cur_line = Challenges.objects.get(id=chall_id)
                cur_line.deadline += timezone.timedelta(days=1)
                cur_line.progress += 1
                cur_line.save()
                return JsonResponse({'status': 'success'})
            except Challenges.DoesNotExist:
                return JsonResponse({'status': 'error'}, status=404)
        else:
            return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('about')
        else:
            form = UserRegistrationForm()
            return render(request, 'registration/register.html', {'form': form, 'extra_param': 'Пожалуйста, придумайте более сложный пароль'})
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password1')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('about')  # Redirect to a success page
        else:
            # Handle invalid login
            return render(request, 'registration/login.html', context={'extra_param': 'Неверный логин или пароль'})

    return render(request, 'registration/login.html')

@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_exempt
@login_required(login_url="login")
def searching_friends(request):
    if request.method == 'GET':
        query = request.GET.get('q', '')
        all_users = User.objects.filter(nick__icontains=query).exclude(nick=request.user.nick).all().values('nick')
        user_friends = FriendShip.objects.filter(user=request.user.nick, confirmed=True).all().values('friend')
        results = all_users.difference(user_friends)
        context = {'results': results}
        return render(request, 'main/search_fr.html', context)
    elif request.method == 'POST':
        nick = request.POST.get('nick', '')
        if nick:
            user = request.user.nick
            friend = nick
            friendship, created = FriendShip.objects.get_or_create(user=user, friend=friend,
                                                                   defaults={'confirmed': False})
            if created:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'exists'})
        else:
            return JsonResponse({'status': 'error'}, status=400)
    else:
        return render(request, 'main/search_fr.html')
