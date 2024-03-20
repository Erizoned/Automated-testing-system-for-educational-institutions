from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class Createuserform(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']


class TestForm(forms.ModelForm):
    start_time = forms.DateTimeField(label='Start Time (YYYY-MM-DD HH:MM)', required=False, widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M', attrs={'type': 'datetime-local'}))
    end_time = forms.DateTimeField(label='End Time (YYYY-MM-DD HH:MM)', required=False, widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M', attrs={'type': 'datetime-local'}))

    class Meta:
        model = Test
        fields = ['title', 'description', 'start_time', 'end_time', 'subject', 'group']

class QuesModelForm(forms.ModelForm):
    class Meta:
        model = QuesModel
        fields = ['question', 'question_type', 'op1', 'op2', 'op3', 'op4', 'ans']
        widgets = {
            'op1': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'op2': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'op3': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'op4': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'ans': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
        }

    def __init__(self, *args, **kwargs):
        super(QuesModelForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs and kwargs['initial'].get('question_type') == 'WA':
            del self.fields['op1']
            del self.fields['op2']
            del self.fields['op3']
            del self.fields['op4']
            del self.fields['ans']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'

class CustomGroupForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = CustomGroup
        fields = ['name', 'year', 'subjects']

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'user_type')

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'user_type')

