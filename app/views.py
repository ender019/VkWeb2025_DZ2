from datetime import timezone, datetime

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse

from app.forms import LoginForm, SettingsForm, RegisterForm, AskForm, AnswerForm
from app.models import Question, Tag, Profile, Answer, QuestionsTags


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
    profile = Profile.objects.get_current(request.user)
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
    profile = Profile.objects.get_current(request.user)
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
    profile = Profile.objects.get_current(request.user)
    quest = Question.objects.get_by_id(question_id)
    pagination = paginate(Answer.objects.get_by_question_id(question_id), request, 5)
    pagination["page"].object_list = (Answer.objects.full_answers(pagination["page"]))
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
        form = RegisterForm(request.POST)
        if not form.is_valid():
            return render(request, 'signup.html', context={
                                "tags": Tag.objects.get_popular_tags(),
                                "nicks": Profile.objects.get_most_active(),
                                "form": form
                            }
                        )
        user = User(username=form.cleaned_data['username'], email=form.cleaned_data['email'], )
        user.set_password(form.cleaned_data['password'])
        profile = Profile(nickname=form.cleaned_data['nickname'], avatar=form.cleaned_data['avatar'], user=user)
        user.save()
        profile.save()
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
    print(profile.nickname)
    if request.method == 'POST':
        print(request.POST)
        form = SettingsForm(request.POST)
        if not form.is_valid():
            return render(request,'settings.html',
                  context={
                      "profile": profile,
                      "tags": Tag.objects.get_popular_tags(),
                      "nicks": Profile.objects.get_most_active(),
                      "form": form,
                  }
            )
        print(form.cleaned_data)
        Profile.objects.updating(request.user, form.cleaned_data)
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
