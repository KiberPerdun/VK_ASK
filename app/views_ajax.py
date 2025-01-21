from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .models import Question, QuestionLike, Answer, Tag


@require_POST
@login_required
def toggle_like(request):
    question_id = request.POST.get('question_id')
    like_type = request.POST.get('like_type')

    if not question_id or like_type not in {"like", "dislike"}:
        return JsonResponse({"success": False, "error": "Некорректные параметры"})

    question = get_object_or_404(Question, id=question_id)
    is_like = like_type == "like"

    qlike, created = QuestionLike.objects.get_or_create(
        user=request.user, question=question,
        defaults={"is_like": is_like}
    )

    if not created:
        if qlike.is_like == is_like:
            qlike.delete()
        else:
            qlike.is_like = is_like
            qlike.save()

    likes_count = question.likes.filter(is_like=True).count()
    dislikes_count = question.likes.filter(is_like=False).count()
    like_difference = likes_count - dislikes_count

    return JsonResponse({
        "success": True,
        "likes_count": likes_count,
        "dislikes_count": dislikes_count,
        "like_difference": like_difference
    })


@require_POST
@login_required
def mark_correct(request):
    question_id = request.POST.get('question_id')
    answer_id = request.POST.get('answer_id')

    if not question_id or not answer_id:
        return JsonResponse({"success": False, "error": "Отсутствуют параметры."})

    question = get_object_or_404(Question, id=question_id)

    if question.author != request.user:
        return JsonResponse({"success": False, "error": "Только автор вопроса может выбрать правильный ответ."})

    answer = get_object_or_404(Answer, id=answer_id, question=question)

    question.answers.update(is_correct=False)

    answer.is_correct = True
    answer.save()

    return JsonResponse({"success": True, "message": "Ответ помечен как правильный."})


@require_POST
@login_required
def post_answer(request, question_id):
    text = request.POST.get('text', '').strip()
    question = get_object_or_404(Question, id=question_id)

    if text:
        answer = Answer.objects.create(
            text=text,
            author=request.user,
            question=question,
            created_at=now()
        )

        avatar_url = request.user.profile.avatar.url if request.user.profile.avatar else '/static/img/photo.jpg'
        total_answers = question.answers.count()

        return JsonResponse({
            'success': True,
            'author': request.user.username,
            'avatar': avatar_url,
            'text': answer.text,
            'created_at': answer.created_at.strftime("%d %b %Y %H:%M"),
            'total_answers': total_answers
        })

    return JsonResponse({'success': False, 'error': "Текст ответа не может быть пустым!"}, status=400)


@require_GET
def get_likes_data(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    likes_count = question.likes.filter(is_like=True).count()
    dislikes_count = question.likes.filter(is_like=False).count()
    like_difference = likes_count - dislikes_count

    return JsonResponse({
        "likes_count": likes_count,
        "dislikes_count": dislikes_count,
        "like_difference": like_difference
    })


@require_GET
def get_tags(request):
    term = request.GET.get("term", "").strip().lower()

    if term:
        tags = list(Tag.objects.filter(name__icontains=term).values_list("name", flat=True)[:10])
        return JsonResponse(tags, safe=False)

    return JsonResponse([])


@require_POST
@login_required
def add_tag(request):
    tag_name = request.POST.get("tag", "").strip().lower()

    if tag_name and not Tag.objects.filter(name=tag_name).exists():
        Tag.objects.create(name=tag_name)
        return JsonResponse({"success": True, "tag": tag_name})

    return JsonResponse({"success": False}, status=400)


@csrf_exempt
@login_required
def submit_question(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        text = request.POST.get("text", "").strip()
        tags_input = request.POST.getlist("tags[]")

        if not title or not text:
            return JsonResponse({"success": False, "error": "Заполните все поля!"})

        if len(tags_input) > 5:
            return JsonResponse({"success": False, "error": "Можно добавить максимум 5 тегов!"})

        tags = []
        for tag_name in tags_input:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)

        question = Question.objects.create(title=title, text=text, author=request.user)
        question.tags.set(tags)

        return JsonResponse({
            "success": True,
            "redirect_url": question.get_absolute_url(),
        })

    return JsonResponse({"success": False, "error": "Некорректный запрос!"})
