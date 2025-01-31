from django.urls import path
from .views import *

urlpatterns = [

    #Api de factura de ventas
    path('ventasCreate/', RegisterVenta.as_view(), name='create-venta'),

    path('ventasDetalleCreate/', RegisterVentaDetalle.as_view(), name='create-venta'),

]