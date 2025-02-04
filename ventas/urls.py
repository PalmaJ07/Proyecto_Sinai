from django.urls import path
from .views import *

urlpatterns = [

    #Api de factura de ventas
    path('ventasCreate/', RegisterVenta.as_view(), name='create-venta'),

    path('ventasDetalleCreate/', RegisterVentaDetalle.as_view(), name='create-venta'),

    path('indexVenta/', IndexVenta.as_view(), name='index-venta'),

    path('indexDetalleVenta/', IndexVentaDetalle.as_view(), name='index-ventaDetalle'),

]