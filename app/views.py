from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import render
from app.models import Question, Tag, Profile, Answer


def paginate(objects_list, request, per_page=10, pag_size=7):
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
    profile = Profile.objects.first()
    pagination = paginate(Question.objects.get_listing(), request, 5)
    pagination["page"].object_list = (Question.objects.full_listing(pagination["page"]))
    return render(request, 'index.html',
                  context={
                      "profile": profile,
                      **pagination,
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                      "head": ["List of questions", "Hot questions", "hot"]
                  }
            )


def hot(request):
    profile = Profile.objects.first()
    pagination = paginate(Question.objects.get_hot(), request, 5)
    pagination["page"].object_list = (Question.objects.full_listing(pagination["page"]))
    return render(request, 'index.html',
                  context={
                      "profile": profile,
                      **pagination,
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                      "head": ["Hot questions", "List of questions", "index"]
                  }
            )


def tag(request, name):
    profile = Profile.objects.first()
    pagination = paginate(Question.objects.get_by_tag(name), request, 5)
    pagination["page"].object_list = (Question.objects.full_listing(pagination["page"]))
    return render(request, 'index.html',
                  context={
                      "profile": profile,
                      **pagination,
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                      "head": [name, "List of questions", "index"]
                  }
            )


def question(request, question_id):
    profile = Profile.objects.first()
    quest = Question.objects.get_by_id(question_id)
    pagination = paginate(Answer.objects.get_by_question_id(question_id), request, 5)
    pagination["page"].object_list = (Answer.objects.full_answers(pagination["page"]))
    return render(request, 'question.html',
                  context={
                      "profile": profile,
                      "question": quest,
                      **pagination,
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                      "head": [quest.title, "List questions", "index"]
                  }
            )


def login(request):
    return render(request, 'login.html',
                  context={
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                  }
            )


def signup(request):
    return render(request, 'signup.html',
                  context={
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                  }
            )


def ask(request):
    profile = Profile.objects.first()
    return render(request, 'ask.html',
                  context={
                      "profile": profile,
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                  }
            )


def settings(request):
    profile = Profile.objects.first()
    return render(request, 'settings.html',
                  context={
                      "profile": profile,
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                  }
            )
