import json
from datetime import datetime

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse

from app.forms import LoginForm, SettingsForm, RegisterForm, AskForm, AnswerForm
from app.models import Question, Tag, Profile, Answer, QuestionsTags, QuestionsLikes, AnswersLikes


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
    profile = Profile.objects.get_current(request.user)
    pagination = paginate(Question.objects.get_listing(), request, 5)
    pagination["page"].object_list = (Question.objects.full_listing(pagination["page"], profile.id if profile else -1))
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
    profile = Profile.objects.get_current(request.user)
    pagination = paginate(Question.objects.get_hot(), request, 5)
    pagination["page"].object_list = (Question.objects.full_listing(pagination["page"], profile.id if profile else -1))
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
    profile = Profile.objects.get_current(request.user)
    pagination = paginate(Question.objects.get_by_tag(name), request, 5)
    pagination["page"].object_list = (Question.objects.full_listing(pagination["page"], profile.id if profile else -1))
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
    profile = Profile.objects.get_current(request.user)
    quest = Question.objects.get_by_id(question_id, profile.id if profile else -1)
    pagination = paginate(Answer.objects.get_by_question_id(question_id), request, 5)
    pagination["page"].object_list = (Answer.objects.full_answers(pagination["page"], profile.id if profile else -1))
    print(pagination["page"].object_list[0].fase)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            Answer.objects.create(text=form.cleaned_data['text'], question=quest, posted=datetime.now())
            return redirect('question', question_id=question_id)
    else:
        form = AnswerForm()
    return render(request, 'question.html',
                  context={
                      "profile": profile,
                      "question": quest,
                      **pagination,
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                      "head": [quest.title, "List questions", "index"],
                      "form": form,
                  }
            )


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if not form.is_valid():
            return render(request,'login.html', {'form': form})
        user = auth.authenticate(request, **form.cleaned_data)
        if user:
            auth.login(request, user)
            return redirect(reverse('index'))
        else:
            form.add_error(field=None, error="User not found")
    else:
        form = LoginForm()

    return render(request, 'login.html',
                  context={
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                      "form": form,
                  }
            )


def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))


def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, 'signup.html', context={
                                "tags": Tag.objects.get_popular_tags(),
                                "nicks": Profile.objects.get_most_active(),
                                "form": form
                            }
                        )
        form.save()
        user = auth.authenticate(request, **form.cleaned_data)
        if user:
            auth.login(request, user)
            return redirect(reverse('index'))
        else:
            form.add_error(field=None, error="Error")
    else:
        form = RegisterForm()
    return render(request, 'signup.html', context={
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                      "form": form
                  }
            )

@login_required(login_url=reverse_lazy("login"))
def ask(request):
    profile = Profile.objects.get_current(request.user)
    print(request.method)
    if request.method == 'POST':
        form = AskForm(request.POST)
        if not form.is_valid():
            return render(request, 'index.html', context={
                              "profile": profile,
                              "tags": Tag.objects.get_popular_tags(),
                              "nicks": Profile.objects.get_most_active(),
                              "form": form,
                    }
                )
        print(form.cleaned_data)
        question = Question(title=form.cleaned_data['title'], text=form.cleaned_data['text'], profile=profile, posted=datetime.now())
        question.save()
        QuestionsTags.objects.bulk_create([
            QuestionsTags(question=question, tag=Tag.objects.get_or_create(title=el)[0])
            for el in form.cleaned_data['tags']
        ])
        question.save()
    else:
        form = AskForm()
    return render(request, 'ask.html',
                  context={
                      "profile": profile,
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                      "form": form,
                  }
            )


@login_required(login_url=reverse_lazy("login"))
def settings(request):
    profile = Profile.objects.get_current(request.user)
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request,'settings.html',
                  context={
                      "profile": profile,
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                      "form": form,
                  }
            )
        Profile.objects.updating(request.user, form.cleaned_data)
        return redirect(reverse('settings'))
    else:
        data = {
            "username": profile.user.username,
            "email": profile.user.email,
            "nickname": profile.nickname,
        }
        form = SettingsForm(data)

    return render(request, 'settings.html',
                  context={
                      "profile": profile,
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                      "form": form,
                  }
            )

@login_required
def questions_likes(request, question_id):
    data = json.loads(request.body)
    profile = Profile.objects.get_current(request.user)
    fase = QuestionsLikes.objects.add_react(profile.id if profile else -1, question_id, data.get("pos"))
    res = QuestionsLikes.objects.get_count(question_id)
    if res is None: return JsonResponse({"likes": 0, "dislikes": 0, "fase": fase})
    return JsonResponse({"likes": res["like"], "dislikes": res["dis"], "fase": fase})

@login_required
def answer_likes(request, answer_id):
    data = json.loads(request.body)
    profile = Profile.objects.get_current(request.user)
    fase = AnswersLikes.objects.add_react(profile.id if profile else -1, answer_id, data.get("pos"))
    res = AnswersLikes.objects.get_count(answer_id)
    if res is None: return JsonResponse({"likes": 0, "dislikes": 0, "fase": fase})
    return JsonResponse({"likes": res["like"], "dislikes": res["dis"], "fase": fase})


@login_required
def answer_correct(request, answer_id):
    data = json.loads(request.body)
    profile = Profile.objects.get_current(request.user)
    res = Answer.objects.get(id=answer_id).profile_id == profile.id
    if not res: JsonResponse({"cor": True})
    Answer.objects.set_correct(answer_id, not data.get("cor"))
    return JsonResponse({"cor": False})