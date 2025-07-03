from django.urls import path
from . import views
urlpatterns=[
    path('login/', views.login_view, name='login'),
    path('expenses/', views.ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('expenses/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense-detail'),
    path('expenses/analytics/', views.expense_analytics_view, name='expense-analytics'),
    path('categories/', views.ExpenseCategoryListView.as_view(), name='category-list'),
]