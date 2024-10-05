from django.urls import path
from .views import *

urlpatterns = [

    # #APIs de usuario - empleado 
    # path('empleado/profile/', UserView.as_view(), name='profile'),
    # path('empleado/create/', RegisterView.as_view(), name='create'),
    # path('empleado/update/<str:encrypted_id>/', UpdateUserView.as_view(), name='update - user'),
    # path('empleado/index/', IndexView.as_view(), name='index'),
    # path('empleado/activate/<str:encrypted_id>/', UpdateUserStatusView.as_view(), name='update-user-status'),
    # path('empleado/delete/<str:encrypted_id>/', DeleteUserView.as_view(), name='user-delete'),
    # path('empleado/changePassword/<str:encrypted_id>/', ChangePasswordView.as_view(), name='update-password'),

    # #Apis de usuarios - Clientes

    # path('cliente/create/', RegisterClient.as_view(), name='CCliente'),
    # path('cliente/update/<str:encrypted_id>/', UpdateClient.as_view(), name='update - cliente'),
    # path('cliente/index/', IndexClientView.as_view(), name='index'),
    # path('cliente/delete/<str:encrypted_id>/', DeleteClientView.as_view(), name='user-delete'),

]