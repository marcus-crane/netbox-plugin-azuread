from django.urls import path

from . import views

urlpatterns = [
    path('complete/',views.authorize, name='azuread-complete'),
    path('login/', views.login, name='azuread-login'),
]
