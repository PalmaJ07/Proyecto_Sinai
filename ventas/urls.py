from django.urls import path
from .views import *

urlpatterns = [

    #Api de ventas
    path('ventasCreate/', RegisterVentaDetalle.as_view(), name='create-venta'),

]