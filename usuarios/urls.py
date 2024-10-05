from django.urls import path
from .views import *

urlpatterns = [

    #APIs de sesion 
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    #APIs de usuario - empleado 
    path('user/empleado/profile/', UserView.as_view(), name='profile'),
    path('user/empleado/create/', RegisterView.as_view(), name='create'),
    path('user/empleado/update/<str:encrypted_id>/', UpdateUserView.as_view(), name='update - user'),
    path('user/empleado/index/', IndexView.as_view(), name='index'),
    path('user/empleado/activate/<str:encrypted_id>/', UpdateUserStatusView.as_view(), name='update-user-status'),
    path('user/empleado/delete/<str:encrypted_id>/', DeleteUserView.as_view(), name='user-delete'),
    path('user/empleado/changePassword/<str:encrypted_id>/', ChangePasswordView.as_view(), name='update-password'),

    #Apis de usuarios - Clientes

    # path('user/cliente/create/', RegisterView.as_view(), name='create'),
    # path('user/cliente/update/<str:encrypted_id>/', UpdateUserView.as_view(), name='update - user'),
    # path('user/cliente/index/', IndexView.as_view(), name='index'),
    # path('user/cliente/delete/<str:encrypted_id>/', DeleteUserView.as_view(), name='user-delete'),

]

