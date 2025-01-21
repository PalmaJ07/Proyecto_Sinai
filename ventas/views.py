from django.shortcuts import render
import base64
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status
from rest_framework.exceptions import NotFound,AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from .models import *
from usuarios.models import  User
import jwt, datetime
from django.utils import timezone


# Funcion encargada de pagination.
class CustomPagination(PageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        # Tamaño de página por defecto es 10 si no se especifica
        page_size = request.GET.get('page_size', 10)
        self.page_size = int(page_size)
        return super().paginate_queryset(queryset, request)
                                                
    def get_paginated_response(self, data):
        return Response({
            'config': data,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page_size,
            'total_config': self.page.paginator.count,
        })

class RegisterVenta(APIView):
    def post(self, request):
        # Autenticación con JWT
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener el usuario actual
        current_user = User.objects.filter(id=payload['id']).first()
        if not current_user:
            raise AuthenticationFailed('User not found!')

        # Preparar datos para la creación
        data = request.data.copy()
        data['created_user'] = current_user.id
        data['updated_user'] = None
        data['deleted_user'] = None
        data['fecha_venta'] = data.get('fecha_venta', '2025-01-01T00:00:00Z')  # Default fecha, si no se pasa

        # Serialización y validación
        serializer = VentaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class RegisterVentaDetalle(APIView):
    def post(self, request):
        # Autenticación con JWT
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener el usuario actual
        current_user = User.objects.filter(id=payload['id']).first()
        if not current_user:
            raise AuthenticationFailed('User not found!')

        # Preparar datos para la creación
        data = request.data.copy()
        data['created_user'] = current_user.id
        data['updated_user'] = current_user.id
        data['deleted_user'] = None  # En caso de que no haya eliminación

        # Obtener el ProductoDetalle
        producto_detalle_id = data.get('producto_detalle')
        producto_detalle = ProductoDetalle.objects.filter(id=producto_detalle_id).first()

        if not producto_detalle:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Lógica de cantidad
        cantidad = data.get('cantidad')
        unidades = data.get('unidades')
        descuento = data.get('descuento')
        descuento_porcentual = data.get('descuento_porcentual')

        if unidades:  # Si unidades es True, actualizar cantidad_por_presentacion
            if producto_detalle.cantidad_por_presentacion < cantidad:
                return Response({'error': 'La cantidad excede la cantidad disponible por presentación.'}, status=status.HTTP_400_BAD_REQUEST)
            producto_detalle.cantidad_por_presentacion -= cantidad
        else:  # Si unidades es False, actualizar total_unidades
            if producto_detalle.total_unidades < cantidad:
                return Response({'error': 'La cantidad excede las unidades disponibles.'}, status=status.HTTP_400_BAD_REQUEST)
            producto_detalle.total_unidades -= cantidad

        # Lógica de descuento
        if descuento_porcentual:  # Descuento porcentual
            if descuento is None or descuento < 0 or descuento > 100:
                return Response({'error': 'El descuento porcentual debe ser un valor entre 0 y 100.'}, status=status.HTTP_400_BAD_REQUEST)
            if unidades:
                precio_venta = producto_detalle.precio_venta_presentacion
            else:
                precio_venta = producto_detalle.precio_venta_unidades

            # Aplicamos el descuento porcentual
            precio_venta = precio_venta * (1 - descuento / 100)
            data['precio_venta'] = precio_venta
        else:  # Descuento monetario
            if descuento is None or descuento < 0:
                return Response({'error': 'El descuento monetario debe ser un valor positivo.'}, status=status.HTTP_400_BAD_REQUEST)
            if unidades:
                precio_venta = producto_detalle.precio_venta_presentacion
            else:
                precio_venta = producto_detalle.precio_venta_unidades

            # Restamos el descuento monetario
            data['precio_venta'] = precio_venta - descuento

        # Serialización y validación
        serializer = VentaDetalleSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        venta_detalle = serializer.save()

        # Guardamos los cambios en ProductoDetalle
        producto_detalle.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    
