from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('usuarios.urls')),
    path('api/config/', include('configuraciones.urls')),
    path('api/inv/', include('inventario.urls')),
]