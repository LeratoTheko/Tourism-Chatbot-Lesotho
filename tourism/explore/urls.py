from django.urls import path

from . import views

urlpatterns = [
    path('', views.base, name = "welcome"),
    path('features', views.feature, name='features'),
    path('about', views.about, name='about'),
    path('api/chat/', views.chat_api, name='chatbot_api'),
]
