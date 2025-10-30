from django.urls import path

from . import views

urlpatterns = [
    path('', views.base, name = "welcome"),
    path('features', views.feature, name='features'),
    path('about', views.about, name='about'),
]
