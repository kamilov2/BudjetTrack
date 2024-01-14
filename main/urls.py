from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

app_name = "main"

urlpatterns = [
    path('limit/', LimitAPIView.as_view(), name='limit'),
    path('register/', RegisterAPIView.as_view(), name='register'),  
    path('category/', CategoryAPIView.as_view(), name='category'),
    path('expense/', ExpenseAPIView.as_view(), name="expense"),
    path('update_password/', UpdatePasswordAPIView.as_view(), name="update_password"),
    path('total_category/', ExpenseCategoryTotalAPIView.as_view(), name='expense_category'),
    path('all_expense/', AllExpenseAPIView.as_view(), name="all_expense"),   
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('login/', LoginAPIView.as_view(), name="login"),
]
