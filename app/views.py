from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegistrationForm
from .models import Question, QuestionLike
from .models import Tag, Profile
from .utils import paginate


def QuestionsList(request):
    sort = request.GET.get('sort', 'new')
    tag_name = request.GET.get('tag')
    search_query = request.GET.get('search', '').strip()

    if sort == 'popular':
        queryset = Question.objects.popular()
    else:
        queryset = Question.objects.newest()

    tag = None
    if tag_name:
        tag = get_object_or_404(Tag, name=tag_name)
        queryset = queryset.filter(tags=tag)

    if search_query:
        queryset = queryset.filter(Q(title__icontains=search_query))

    active_users = User.objects.annotate(
        num_questions=models.Count('questions'),
        num_answers=models.Count('answers')
    ).order_by('-num_questions', '-num_answers')[:5]

    page_obj = paginate(queryset, request.GET.get('page', 1), per_page=10)

    popular_tags = Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]

    return render(request, 'QuestionsList.html', {
        'popular_tags': popular_tags,
        'selected_tag': tag_name,
        'page_obj': page_obj,
        'questions': page_obj.object_list,
        'best_members': active_users,
        'sort': sort,
        'search_query': search_query,
    })


def BestQuestions(request):
    questions = Question.objects.best()

    active_users = User.objects.annotate(
        num_questions=models.Count('questions'),
        num_answers=models.Count('answers')
    ).order_by('-num_questions', '-num_answers')[:5]

    page_number = request.GET.get("page", 1)
    page_obj = paginate(questions, page_number)

    popular_tags = Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]

    return render(request, "QuestionsList.html", {
        'popular_tags': popular_tags,
        'page_obj': page_obj,
        'best_members': active_users
    })

def Settings(request):
    active_users = User.objects.annotate(
        num_questions=models.Count('questions'),
        num_answers=models.Count('answers')
    ).order_by('-num_questions', '-num_answers')[:5]

    popular_tags = Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]

    return render(request, "Settings.html", {
        'popular_tags': popular_tags,
        'best_members': active_users,
    })

def Ask(request):
    active_users = User.objects.annotate(
        num_questions=models.Count('questions'),
        num_answers=models.Count('answers')
    ).order_by('-num_questions', '-num_answers')[:5]

    popular_tags = Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]

    return render(request, "AskQuestion.html", {
        'popular_tags': popular_tags,
        'best_members': active_users,
    })

def Login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('QuestionsList')

        else:
            messages.error(request, 'Неверный логин или пароль.')

    else:
        form = AuthenticationForm()

    active_users = User.objects.annotate(
        num_questions=models.Count('questions'),
        num_answers=models.Count('answers')
    ).order_by('-num_questions', '-num_answers')[:5]

    popular_tags = Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]

    return render(request, 'Login.html', {
        'popular_tags': popular_tags,
        'form': form,
        'best_members': active_users,
    })

def Register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            nickname = form.cleaned_data['nickname']
            password = form.cleaned_data['password']
            avatar = form.cleaned_data.get('avatar')

            user = User.objects.create_user(username=username, email=email, password=password)

            profile = Profile.objects.create(user=user)

            if avatar:
                fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                filename = fs.save('avatars/' + avatar.name, avatar)
                profile.avatar = 'avatars/' + avatar.name

            profile.save()

            messages.success(request, 'Регистрация прошла успешно! Вы можете войти в систему.')
            return redirect('Login')

        else:
            messages.error(request, 'Ошибка в регистрации. Пожалуйста, проверьте поля формы.')

    else:
        form = RegistrationForm()

    active_users = User.objects.annotate(
        num_questions=models.Count('questions'),
        num_answers=models.Count('answers')
    ).order_by('-num_questions', '-num_answers')[:5]

    popular_tags = Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]

    return render(request, 'Register.html',
                  {
                      'popular_tags': popular_tags,
                      'form': form,
                      'best_members': active_users,
                  })


def ListByTag(request):
    active_users = User.objects.annotate(
        num_questions=models.Count('questions'),
        num_answers=models.Count('answers')
    ).order_by('-num_questions', '-num_answers')[:5]

    popular_tags = Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]

    return render(request, "ListByTag.html",
                  {
                      'popular_tags': popular_tags,
                      'best_members': active_users,
                  })


def SingleQuestion(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    active_users = User.objects.annotate(
        num_questions=models.Count('questions'),
        num_answers=models.Count('answers')
    ).order_by('-num_questions', '-num_answers')[:5]

    popular_tags = Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]

    return render(request, 'SingleQuestion.html', {
        'popular_tags': popular_tags,
        'question': question,
        'best_members': active_users,
    })


def Logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('QuestionsList')


@login_required
def toggle_like(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    try:
        like = QuestionLike.objects.get(user=request.user, question=question)
        if like.is_like:
            like.is_like = False

        else:
            like.delete()
            like = QuestionLike.objects.create(user=request.user, question=question, is_like=True)

    except QuestionLike.DoesNotExist:
        QuestionLike.objects.create(user=request.user, question=question, is_like=True)

    return redirect('questions:question_detail', question_id=question.id)
