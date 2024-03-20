from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Quiz.views import *
from Quiz import views

app_name = 'Quiz'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home, name='home'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutPage, name='logout'),
    path('register/', registerPage, name='register'),
    path('create_test/', create_test, name='create_test'),
    path('addQuestion/<int:test_id>/', addQuestion, name='addQuestion'),
    path('tests/<int:test_id>/', take_test, name='take_test'),
    path('tests/<int:test_id>/results/<int:customuser_id>/', views.test_results, name='test_results'),
    path('tests/<int:test_id>/show_results/<int:customuser_id>/', views.show_test_results, name='show_test_results'),
    path('journal/', journal, name='journal'),
    path('tests/<int:test_id>/edit/', edit_test, name='edit_test'),
    path('start_test/<int:test_id>/', start_test, name='start_test'),
    path('tests/<int:test_id>/edit_question/<int:ques_id>/', edit_question, name='edit_question'),
    path('view_student_answers/<int:customuser_id>/<int:test_id>/', view_student_answers, name='view_student_answers'),
    path('add_subject/', add_subject, name='add_subject'),
    path('add_group/', add_group, name='add_group'),
    path('groups/', group_list, name='group_list'),
    path('', index, name='index'),
    path('publish_test/<int:test_id>/', views.publish_test, name='publish_test'),
    path('delete_question/<int:question_id>/', delete_question, name='delete_question'),
    path('delete_test/<int:test_id>/', delete_test, name='delete_test'),
    path('manage_group_users/<int:group_id>/', manage_group_users, name='manage_group_users'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)