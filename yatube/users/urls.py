from django.contrib.auth.views import LogoutView, LoginView, PasswordChangeView
from django.contrib.auth.views import PasswordResetView, PasswordResetCompleteView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path('password_change/',
         PasswordChangeView.as_view(template_name="users/password_change_form.html"),
         name='password_change_form'),
    path('password_change/done/',
         PasswordChangeView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),
    path('password_reset/',
         PasswordResetView.as_view(template_name='users/password_reset_form.html'),
         name='password_reset_form'),
    path('password_reset/done/',
         PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_resent_confirm'),
    path('reset_confirm/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_resent_confirm'),
]
