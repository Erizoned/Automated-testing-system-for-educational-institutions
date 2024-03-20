import logging
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.views.decorators.cache import never_cache
from .forms import *
from .models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

def index(request):
    return render(request,'Quiz/index.html')

def home(request):
    selected_subject_id = request.GET.get('subject_id')
    if request.user.is_authenticated:
        group_ids = request.user.custom_groups.values_list('id', flat=True)
        if request.user.is_staff:
            tests = Test.objects.filter(group__id__in=group_ids)
        else:
            tests = Test.objects.filter(group__id__in=group_ids, is_published=True)
        # Фильтрация тестов по выбранному предмету
        if selected_subject_id:
            tests = tests.filter(subject_id=selected_subject_id)
    else:
        tests = Test.objects.none()
    # Получение списка всех предметов для фильтра
    subjects = Subject.objects.all()
    return render(request, 'Quiz/home.html', {'tests': tests, 'subjects': subjects})

def create_test(request):
    # Если пользователь учитель, то открывается форма
    if request.user.is_staff:
        if request.method == 'POST':
            test_form = TestForm(request.POST)
            if test_form.is_valid():
                new_test = test_form.save(commit=False)
                max_id = Test.objects.aggregate(models.Max('id'))['id__max']
                new_test_id = 1 if max_id is None else max_id + 1
                new_test.id = new_test_id
                new_test.subject = test_form.cleaned_data.get('subject')
                new_test.group = test_form.cleaned_data.get('group')
                new_test.save()

                return redirect('take_test', test_id=new_test.id)
        else:
            test_form = TestForm()
        return render(request, 'Quiz/create_test.html',{'test_form': test_form})
    # Если у пользователя нет доступа, то его вернёт на страницу с тестами
    else:
        return redirect('home')

def addQuestion(request, test_id):
    if request.user.is_staff:
        test = get_object_or_404(Test, pk=test_id)
        # Тип вопросов с множественным выбором
        question_type = request.POST.get('question_type', 'MC')
        if request.method == 'POST':
            form = QuesModelForm(request.POST, initial={'question_type': question_type})
            if form.is_valid():
                question = form.save(commit=False)
                question.test = test
                question.save()
                return redirect('take_test', test_id=test.id)
        else:
            form = QuesModelForm(initial={'question_type': question_type})
        context = {'form': form, 'test': test}
        return render(request, 'Quiz/addQuestion.html', context)
    else:
        return redirect('home')


@login_required
def test_results(request, test_id, customuser_id):
    test = get_object_or_404(Test, pk=test_id)
    customuser = get_object_or_404(CustomUser, pk=customuser_id)
    # Получение записи UserResult для данного пользователя и теста
    user_result = UserResult.objects.filter(user=customuser, test=test).first()
    # Если ученик ещё не проходил тест и у него отсутсвуют результаты:
    if not user_result:
        return HttpResponse("Ошибка: результат теста не найден", status=404)
    if request.method == 'POST':
        # Заполнение модели user_result
        try:
            user_result.end_time = timezone.now()
            # Расчёт затраченного учеником времени:
            user_result.time_taken = max(int((user_result.end_time - user_result.start_time).total_seconds()), 0)
            score = 0
            correct = 0
            wrong = 0
            total = 0
            questions = QuesModel.objects.filter(test=test)
            for q in questions:
                total += 1
                submitted_answer = request.POST.get(q.question)
                # Обработка ответов пользователя
                if q.question_type == 'WA':
                    submitted_answer = request.POST.get(q.question)
                    StudentAnswer.objects.create(
                        user_result=user_result,
                        question=q,
                        answer_text=submitted_answer
                    )
                else:
                    StudentAnswer.objects.create(user_result=user_result, question=q, selected_option=submitted_answer)
                # Подсчет баллов
                if submitted_answer == q.ans:
                    score += 10
                    correct += 1
                else:
                    wrong += 1
            percent = (score / (total * 10)) * 100 if total > 0 else 0
            user_result.score = score
            user_result.is_completed = True
            user_result.save()
            context = {
                'test': test,
                'questions': questions,
                'user_result': user_result,
                'score': score,
                'time_taken': user_result.time_taken,
                'correct': correct,
                'wrong': wrong,
                'percent': percent,
                'total': total
            }
            return render(request, 'Quiz/result.html', context)
        except Exception as e:
            # Обработка исключений
            return HttpResponse("Внутренняя ошибка сервера", status=500)
    return HttpResponse("Неверный запрос", status=400)



@login_required
def show_test_results(request, test_id, customuser_id):
    test = get_object_or_404(Test, pk=test_id)
    customuser = get_object_or_404(CustomUser, pk=customuser_id)
    user_result = UserResult.objects.filter(user=customuser, test=test).order_by('-date_taken').first()
    if not user_result:
        return HttpResponse("Результаты для данного пользователя и теста не найдены", status=404)
    questions = QuesModel.objects.filter(test=test)
    student_answers = StudentAnswer.objects.filter(user_result=user_result)
    correct = 0
    wrong = 0
    for answer in student_answers:
        if answer.question.ans == (answer.answer_text or answer.selected_option):
            correct += 1
        else:
            wrong += 1
    total = len(questions)
    percent = (correct / total) * 100 if total > 0 else 0
    context = {
        'test': test,
        'questions': questions,
        'user_result': user_result,
        'correct': correct,
        'wrong': wrong,
        'total': total,
        'percent': percent
    }
    return render(request, 'Quiz/show_test_results.html', context)

logger = logging.getLogger(__name__)

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    register_form = Createuserform(request.POST or None)
    login_form = AuthenticationForm(request, request.POST or None)
    if request.method == 'POST':
        if 'register' in request.POST:
            if register_form.is_valid():
                register_form.save()
                username = register_form.cleaned_data.get('username')
                raw_password = register_form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('home')
            else:
                logger.error(f"Register Form Errors: {register_form.errors}")
        elif 'login' in request.POST:
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home')

    return render(request, 'Quiz/register.html', {'register_form': register_form, 'login_form': login_form})

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
        context = {}
        return render(request, 'Quiz/login.html', context)


def logoutPage(request):
    logout(request)
    return redirect('/')


@never_cache
@login_required
def take_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    # Проверка, является ли пользователь администратором (персоналом)
    if request.user.is_staff:
        questions = QuesModel.objects.filter(test=test)
        return render(request, 'Quiz/tests.html', {'test': test, 'questions': questions})
    # Проверка, опубликован ли тест
    if not test.is_published:
        return HttpResponse("Тест ещё не опубликован")
    current_datetime = timezone.localtime()
    # Проверка интервала
    if test.start_time and test.end_time:
        if not (test.start_time <= current_datetime <= test.end_time):
            return HttpResponse("Тест недоступен в данный момент.")
    # Проверка принадлежности пользователя к группе теста
    if not request.user.custom_groups.filter(id=test.group.id).exists():
        return redirect('home')
    # Поиск существующей записи UserResult
    user_result = UserResult.objects.filter(user=request.user, test=test).first()
    # Проверка прошёл ли пользователь тест:
    if user_result and user_result.is_completed:
        return HttpResponse("Вы уже прошли этот тест. Повторное прохождение не допускается.")
    if not user_result:
        UserResult.objects.create(
            user=request.user,
            test=test,
            start_time=timezone.now(),
            score=0
        )

    questions = QuesModel.objects.filter(test=test)
    return render(request, 'Quiz/tests.html', {'test': test, 'questions': questions})



def journal(request):
    all_users = CustomUser.objects.all()
    selected_username = request.GET.get('username', '')

    if selected_username:
        user = get_object_or_404(CustomUser, username=selected_username)
        user_results = UserResult.objects.filter(user=user).select_related('test').prefetch_related('test__group', 'test__subject')
    else:
        user_results = []

    context = {
        'all_users': all_users,
        'selected_username': selected_username,
        'user_results': user_results,
    }
    return render(request, 'Quiz/journal.html', context)


def edit_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            return redirect('take_test', test_id=test.id)
    else:
        form = TestForm(instance=test)

    return render(request, 'Quiz/edit_test.html', {'form': form, 'test': test})

def edit_question(request, test_id, ques_id):
    ques = get_object_or_404(QuesModel, pk=ques_id)
    if request.method == 'POST':
        form = QuesModelForm(request.POST, instance=ques)
        if form.is_valid():
            form.save()
            return redirect('take_test', test_id=test_id)
    else:
        form = QuesModelForm(instance=ques)
        return render(request, 'Quiz/edit_question.html', {'form': form, 'ques': ques})


@login_required
def start_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    user_result = UserResult.objects.filter(user=request.user, test=test).exists()

    context = {
        'test': test,
        'has_taken_test': user_result  # Эта переменная указывает, прошел ли пользователь тест
    }
    return render(request, 'Quiz/start_test.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def view_student_answers(request,  customuser_id, test_id):
    student = get_object_or_404(CustomUser, pk= customuser_id)
    test = get_object_or_404(Test, pk=test_id)
    questions = QuesModel.objects.filter(test=test)
    user_results = UserResult.objects.filter(user=student, test=test)
    print(f"CustomUser ID: {customuser_id}")

    context = {
        'student': student,
        'test': test,
        'questions': questions,
        'user_results': user_results,
    }
    return render(request, 'Quiz/view_student_answers.html', context)

def is_teacher_or_admin(user):
    return user.user_type in [2, 3]

@login_required
@user_passes_test(is_teacher_or_admin)
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Изменено на 'home'
    else:
        form = SubjectForm()
    return render(request, 'Quiz/add_subject.html', {'form': form})

@login_required
@user_passes_test(is_teacher_or_admin)
def add_group(request):
    if request.method == 'POST':
        form = CustomGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Or wherever you want to redirect
    else:
        form = CustomGroupForm()

    return render(request, 'Quiz/add_group.html', {'custom_group_form': form})


@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_group_users(request, group_id):
    group = get_object_or_404(CustomGroup, id=group_id)
    if request.method == 'POST':
        selected_user_ids = request.POST.getlist('users')
        selected_users = CustomUser.objects.filter(id__in=selected_user_ids)

        # Update group memberships
        group.custom_user_groups.clear()
        for user in selected_users:
            user.custom_groups.add(group)

        return redirect('home')

    users = CustomUser.objects.all()
    return render(request, 'Quiz/manage_group_users.html', {'group': group, 'users': users})

@login_required
@user_passes_test(lambda u: u.is_staff)
def group_list(request):
    groups = CustomGroup.objects.all()
    return render(request, 'Quiz/group_list.html', {'groups': groups})

@login_required
@user_passes_test(lambda u: u.is_staff)
def publish_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    test.is_published = True
    test.time_start = timezone.localtime(timezone.now())
    test.save()
    return redirect('home')

def delete_question(request, question_id):
    if request.user.is_staff and request.method == 'POST':
        question = get_object_or_404(QuesModel, pk=question_id)
        test_id = question.test.id
        question.delete()
        return HttpResponseRedirect(reverse('take_test', args=[test_id]))
    else:
        return HttpResponseRedirect(reverse('home'))

def delete_test(request, test_id):
    if request.user.is_staff and request.method == 'POST':
        test = get_object_or_404(Test, pk=test_id)
        test.delete()
        return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse('home'))