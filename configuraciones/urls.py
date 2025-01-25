from django.urls import path
from .views import *

urlpatterns = [

    #Apis de categoria

    path('categoria/create/', RegisterCategoria.as_view(), name='createCategoria'),
    path('categoria/update/<str:encrypted_id>/', UpdateCategoria.as_view(), name='updateCategoria'),
    path('categoria/index/', IndexCategoriaView.as_view(), name='index'),
    path('categoria/delete/<str:encrypted_id>/', DeleteCategoriaView.as_view(), name='deleteCategoria'),

    # Apis de Marca
    path('marca/create/', RegisterMarca.as_view(), name='createMarca'),
    path('marca/update/<str:encrypted_id>/', UpdateMarca.as_view(), name='updateMarca'),
    path('marca/index/', IndexMarcaView.as_view(), name='indexMarca'),
    path('marca/delete/<str:encrypted_id>/', DeleteMarcaView.as_view(), name='deleteMarca'),


    # Apis de Almacen
    path('almacen/create/', RegisterAlmacen.as_view(), name='createAlmacen'),
    path('almacen/update/<str:encrypted_id>/', UpdateAlmacen.as_view(), name='updateAlmacen'),
    path('almacen/index/', IndexAlmacenView.as_view(), name='indexAlmacen'),
    path('almacen/delete/<str:encrypted_id>/', DeleteAlmacenView.as_view(), name='deleteAlmacen'),

    # Apis de Presentación de Producto
    path('presentacion/create/', RegisterPresentacionProducto.as_view(), name='createPresentacionProducto'),
    path('presentacion/update/<str:encrypted_id>/', UpdatePresentacionProducto.as_view(), name='updatePresentacionProducto'),
    path('presentacion/index/', IndexPresentacionProductoView.as_view(), name='indexPresentacionProducto'),
    path('presentacion/delete/<str:encrypted_id>/', DeletePresentacionProductoView.as_view(), name='deletePresentacionProducto'),

    # Apis de Unidad de Medida
    path('unidad-medida/create/', RegisterUnidadMedida.as_view(), name='createUnidadMedida'),
    path('unidad-medida/update/<str:encrypted_id>/', UpdateUnidadMedida.as_view(), name='updateUnidadMedida'),
    path('unidad-medida/index/', IndexUnidadMedidaView.as_view(), name='indexUnidadMedida'),
    path('unidad-medida/delete/<str:encrypted_id>/', DeleteUnidadMedidaView.as_view(), name='deleteUnidadMedida'),

    # Apis de Proveedor
    path('proveedor/create/', RegisterProveedor.as_view(), name='createProveedor'),
    path('proveedor/update/<str:encrypted_id>/', UpdateProveedor.as_view(), name='updateProveedor'),
    path('proveedor/index/', IndexProveedorView.as_view(), name='indexProveedor'),
    path('proveedor/delete/<str:encrypted_id>/', DeleteProveedorView.as_view(), name='deleteProveedor'),

    #Api para reportes 
    #path('reporteMovimiento/', CreateReporteMovimiento.as_view(), name='createReporte')

    #Reporte de ventas 
    path('reporteVentas/', ReporteVentas.as_view(), name='createReporte'),

    #Reporte de ganancias
    path('reporteGanancias/', ReporteGanancias.as_view(), name='createReporte')

]