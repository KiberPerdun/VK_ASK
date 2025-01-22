"""
URL configuration for VK_WEB project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from app import views
from app import views_ajax

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.QuestionsList, name='QuestionsList'),
                  path('settings/', views.Settings, name='Settings'),
    path('ask', views.Ask, name='Ask'),
                  path('login/', views.Login, name='Login'),
                  path('reg/', views.Register, name='Register'),
    path('tag/perdun', views.ListByTag, name='ListBytag'),
    path('question/<int:question_id>/', views.SingleQuestion, name='SingleQuestion'),
                  path('logout', views.Logout, name='Logout'),

                  path('ajax/toggle_like/', views_ajax.toggle_like, name='toggle_like'),
                  path('ajax/mark_correct/', views_ajax.mark_correct, name='mark_correct'),
                  path('question/<int:question_id>/post_answer/', views_ajax.post_answer, name='post_answer'),
                  path("question/<int:question_id>/get_likes_data/", views_ajax.get_likes_data, name="get_likes_data"),
                  path("get_tags/", views_ajax.get_tags, name="get_tags"),
                  path("add_tag/", views_ajax.add_tag, name="add_tag"),
                  path("submit_question/", views_ajax.submit_question, name="submit_question"),
                  path('question/<int:question_id>/select_correct/<int:answer_id>/', views_ajax.select_correct_answer,
                       name='select_correct_answer'),
                  path('answer/<int:answer_id>/toggle_like/', views_ajax.toggle_answer_like, name='toggle_answer_like'),
                  path('question/<int:question_id>/get_likes_data_answers/', views_ajax.get_likes_data_answers, name='get_likes_data_answers'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
