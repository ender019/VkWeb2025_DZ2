import copy
from random import randint

from django.core.paginator import Paginator
from django.shortcuts import render

QUESTIONS = [
    {
        "id": i,
        "title": f"question #{i}",
        "img_path": "/img/PELMEN.PNG",
        "text": "question " * (i + 1) + str(i),
        "tags": [f"t{i}", "tag"],
        "posted": f"{(i * 13) % 60 + 1} minutes",
        "comments": [i for i in range(randint(1, 10))]
    } for i in range(100)
]


def paginate(objects_list: list, request, per_page=10, pag_size=7):
    num = int(request.GET.get('page', 1))
    paginator = Paginator(objects_list, per_page)
    page = paginator.page(num)
    if page.paginator.num_pages < pag_size:
        pag = page.paginator.page_range
    else:
        l = max(min(page.paginator.num_pages - pag_size + 1, page.number - pag_size // 2), 1)
        pag = [l + i for i in range(0, pag_size)]
    return {"pagination": pag, "page": page}


# Create your views here.
def index(request):
    pagination = paginate(QUESTIONS, request, 5)
    return render(request, 'index.html',
                  context={
                      **pagination,
                      "head": ["New questions", "Hot questions", "hot"]
                  }
            )


def hot(request):
    pagination = paginate(QUESTIONS[::-1], request, 5)
    return render(request, 'index.html',
                  context={
                      **pagination,
                      "head": ["New questions", "List questions", "index"]
                  }
            )


def tag(request, name):
    return render(request, 'question.html',
                  context={
                      "question": list(filter(lambda x: name in x["tags"], QUESTIONS))[0],
                      "head": ["New questions", "List questions", "index"]
                  }
            )


def question(request, question_id):
    question = list(filter(lambda x: x["id"] == question_id, QUESTIONS))[0]
    pagination = paginate(question["comments"], request, 5)
    return render(request, 'question.html',
                  context={
                      "question": question,
                      **pagination,
                      "head": ["New questions", "List questions", "index"]
                  }
            )


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'signup.html')


def ask(request):
    return render(request, 'ask.html')


def settings(request):
    return render(request, 'settings.html')
