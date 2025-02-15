from django.urls import path
from . import views
from .views import dashboard, get_dashboard_data

urlpatterns = [
    path('', views.home, name='home'),
    path("customer/register/", views.customer_register, name="customer_register"),
    path("customer/login/", views.customer_login, name="customer_login"),
    path("workplace/register/", views.workplace_register, name="workplace_register"),
    path("workplace/login/", views.workplace_login, name="workplace_login"),
    path("shop/", views.shop, name="shop"),  # Redirect for customers
    path('dashboard/', dashboard, name='dashboard'),
    path('get_dashboard_data/', get_dashboard_data, name='get_dashboard_data'),
]
