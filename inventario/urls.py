from django.urls import path
from .views import *

urlpatterns = [

    #Apis de producto

    path('producto/create/', RegisterProducto.as_view(), name='createProducto'),
    path('producto/update/<str:encrypted_id>/', UpdateProducto.as_view(), name='updateProducto'),
    path('producto/index/', IndexProductoView.as_view(), name='index'),
    path('producto/delete/<str:encrypted_id>/', DeleteProductoView.as_view(), name='deleteProducto'),


    #Apis de productoDetalle

    path('productoDetalle/create/', CreateProductoDetalle.as_view(), name='createProducto'),
    path('productoDetalle/update/<str:encrypted_id>/', UpdateProductoDetalle.as_view(), name='updateProducto'),
    path('productoDetalle/index/', IndexProductoDetalleView.as_view(), name='index'),
    path('productoDetalle/delete/<str:encrypted_id>/', DeleteProductoDetalle.as_view(), name='deleteProducto'),

    #Apis de productoDetalleIngreso
    
    path('productoIngreso/create/', ProductoDetalleIngresoCreate.as_view(), name='createProducto'),
]

