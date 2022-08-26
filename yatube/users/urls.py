from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(
        extra_context={"var": "Зарегистрироваться"}), name='signup'),
    path('logout/', LogoutView.as_view(
        template_name='users/logged_out.html'), name='logout'),
    path('login/',
         LoginView.as_view(
             extra_context={"var": "Войти", "eto_login": "eto_login"},
             template_name='users/login.html'), name='login'),
    path('password_change/',
         PasswordChangeView.as_view(
             extra_context={"var": "Изменить пароль"},
             template_name='users/password_change_form.html'),
         name='password_change'
         ),
    path('password_change/done/',
         PasswordChangeView.as_view(
             template_name='users/password_change_done.html'),
         name='password_change_done'
         ),
    path('password_reset/',
         PasswordResetView.as_view(
             extra_context={"var": "Восстановить пароль"},
             template_name='users/password_reset_form.html'),
         name='password_reset'
         ),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'
         ),
    path('password_reset/done/',
         PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'),
         name='password_reset_done'
         ),
    path('reset/done/',
         PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'),
         name='password_reset_complete'
         ),
]
