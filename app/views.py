from django.shortcuts import render, get_object_or_404
from .models import Question
from .utils import paginate

def QuestionsList(request):
    queryset = Question.objects.all().order_by('-created_at')

    page_number = request.GET.get('page', 1)
    page_obj = paginate(queryset, page_number, per_page=20)

    return render(request, 'QuestionsList.html',
                  {'page_obj': page_obj,
                           'questions': page_obj.object_list})

def QuestionDetail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    return render(request, "SingleQuestion.html", {"question": question})


def BestQuestions(request):
    questions = Question.objects.best()
    page_number = request.GET.get("page", 1)
    page_obj = paginate(questions, page_number)
    return render(request, "QuestionsList.html", {"page_obj": page_obj})

def Settings(request):
    return render(request, 'Settings.html')

def Ask(request):
    return render(request, "AskQuestion.html")

def Login(request):
    return render(request, "Login.html")

def Register(request):
    return render(request, "Register.html")

def ListByTag(request):
    return render(request, "ListByTag.html")


def SingleQuestion(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    return render(request, 'SingleQuestion.html', {'question': question})
