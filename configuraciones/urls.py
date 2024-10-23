from django.urls import path
from .views import *

urlpatterns = [

    #Apis de categoria

    path('categoria/create', RegisterCategoria.as_view(), name='createCategoria'),
    path('categoria/update/<str:encrypted_id>/', UpdateCategoria.as_view(), name='updateCategoria'),
    path('categoria/index/', IndexCategoriaView.as_view(), name='index'),
    path('categoria/delete/<str:encrypted_id>/', DeleteCategoriaView.as_view(), name='deleteCategoria'),







    # #Apis de usuarios

    # path('cliente/create/', RegisterClient.as_view(), name='CCliente'),
    # path('cliente/update/<str:encrypted_id>/', UpdateClient.as_view(), name='update - cliente'),
    # path('cliente/index/', IndexClientView.as_view(), name='index'),
    # path('cliente/delete/<str:encrypted_id>/', DeleteClientView.as_view(), name='user-delete'),

]