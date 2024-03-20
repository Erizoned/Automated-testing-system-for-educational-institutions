from datetime import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    custom_groups = models.ManyToManyField(
        'CustomGroup',
        verbose_name=_('custom groups'),
        blank=True,
        help_text=_('The custom groups this user belongs to.'),
        related_name="custom_user_groups",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_permissions",
        related_query_name="user",
    )
    USER_TYPE_CHOICES = (
        (1, 'student'),
        (2, 'teacher'),
        (3, 'admin'),
    )
    subjects = models.ManyToManyField('Subject', related_name='users', blank=True)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=3)

class Test(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=200, null=True)
    description = models.TextField()
    time_create = models.DateTimeField(default=timezone.now, editable=False)
    time_start = models.DateTimeField(null=True, blank=True)
    time_update = models.DateTimeField(default=timezone.now)
    is_completed = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name='tests')
    group = models.ForeignKey('CustomGroup', on_delete=models.CASCADE, related_name='tests')
    is_published = models.BooleanField(default=False)

    def is_available(self):
        # Проверка доступности теста
        current_datetime = timezone.localtime(timezone.now())
        if self.start_time and self.end_time:
            return self.start_time <= current_datetime <= self.end_time
        return False  # Если времена не установлены, считаем тест недоступным

    def has_started(self):
        # Тест начинается сразу после публикации в указанное время
        if self.is_published and self.start_time:
            start_datetime = timezone.make_aware(datetime.combine(timezone.localdate(), self.start_time))
            return timezone.localtime(timezone.now()) >= start_datetime
        return False

    def is_expired(self):
        # Проверка времени окончания теста
        if self.end_time:
            end_datetime = timezone.make_aware(datetime.combine(timezone.localdate(), self.end_time))
            return timezone.localtime(timezone.now()) > end_datetime
        return False

    def start_test(self):
        if not self.has_started() and not self.is_expired():
            self.time_start = timezone.localtime(timezone.now())
            self.save()

    def remaining(self):
        if self.start_time and self.end_time:
            current_time = timezone.localtime(timezone.now()).time()
            remaining_time = (self.end_time.hour, self.end_time.minute) - (current_time.hour, current_time.minute)
            return max(remaining_time[0] * 3600 + remaining_time[1] * 60, 0)

    def get_user_result(self, user):
        user_result = UserResult.objects.filter(user=user, test=self).order_by('-date_taken').first()
        return user_result

class UserResult(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.IntegerField()
    time_taken = models.IntegerField(default=0)
    date_taken = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.user.username} - {self.test.title}'

    def get_answer_for_question(self, question):
        answer = StudentAnswer.objects.filter(user_result=self, question=question).first()
        if answer:
            if question.question_type == 'WA':
                return answer.answer_text
            else:
                return answer.selected_option
        return "Ответ не найден"

class QuesModel(models.Model):
    id = models.AutoField(primary_key=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True)
    question = models.CharField(max_length=200, null=True)
    op1 = models.CharField(max_length=200, null=True)
    op2 = models.CharField(max_length=200, null=True)
    op3 = models.CharField(max_length=200, null=True)
    op4 = models.CharField(max_length=200, null=True)
    ans = models.CharField(max_length=200, null=True)
    QUESTION_TYPE_CHOICES = [
        ('MC', 'Multiple Choice'),
        ('WA', 'Written Answer')
    ]
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPE_CHOICES, default='MC')

    def __str__(self):
        return self.question

class StudentAnswer(models.Model):
    user_result = models.ForeignKey(UserResult, on_delete=models.CASCADE)
    question = models.ForeignKey(QuesModel, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)  # для написанных ответов (WC)
    selected_option = models.CharField(max_length=200, blank=True, null=True)  # для множественного выбора (WA)

    def __str__(self):
        return f"{self.user_result.user.username} ответ на {self.question.question}"

class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class CustomGroup(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField()
    subjects = models.ManyToManyField('Subject', related_name='custom_groups')

    def __str__(self):
        return f"{self.name} - {self.year} year"