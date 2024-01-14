from django.urls import re_path , path
from .views import *
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView

app_name = "main"

urlpatterns = [
    re_path(r'^limit/$', LimitAPIView.as_view(), name='limit'),
    re_path(r'^register/$', RegisterAPIView.as_view(), name='register'),  
    re_path(r'^category/$', CategoryAPIView.as_view(), name='category'),
    re_path(r'^expense/$', ExpenseAPIView.as_view(), name="expense"),
    re_path(r'^update_password/$', UpdatePasswordAPIView.as_view(), name="update_password"),
    re_path(r'^total_category/$' , ExpenseCategoryTotalAPIView.as_view() , name='expense_category'),
    re_path(r'^all_expense', AllExpenseAPIView.as_view() , name="all_expense"),   
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    re_path(r'^login/$', LoginAPIView.as_view(), name="login"),

]
