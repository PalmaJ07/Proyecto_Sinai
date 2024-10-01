from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/empleado/profile/', UserView.as_view(), name='profile'),
    path('user/empleado/create/', RegisterView.as_view(), name='create'),
    path('user/empleado/index/', IndexView.as_view(), name='index'),

    path('users/update/status/<int:user_id>/', UpdateUserStatusView.as_view(), name='update-user-status'),
    path('users/delete/', DeleteUserView.as_view(), name='user-delete'),

]
