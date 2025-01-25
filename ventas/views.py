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

        # Validar existencia del producto
        producto_detalle_id = data.get('producto_detalle')
        producto_detalle = ProductoDetalle.objects.filter(id=producto_detalle_id).first()

        if not producto_detalle:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Validar cantidad y actualizar inventario
        cantidad = data.get('cantidad', 0)
        unidades = data.get('unidades', False)  # True si se vende en unidades, False si se vende por presentación

        if unidades:
            # Validar cantidad disponible por presentación
            if producto_detalle.cantidad_por_presentacion < cantidad:
                return Response({'error': 'Cantidad excede el inventario disponible por presentación.'}, status=status.HTTP_400_BAD_REQUEST)
            producto_detalle.cantidad_por_presentacion -= cantidad
        else:
            # Validar cantidad disponible en unidades
            if producto_detalle.total_unidades < cantidad:
                return Response({'error': 'Cantidad excede las unidades disponibles en inventario.'}, status=status.HTTP_400_BAD_REQUEST)
            producto_detalle.total_unidades -= cantidad

        # Lógica de descuentos
        descuento = data.get('descuento', 0)
        descuento_porcentual = data.get('descuento_porcentual', False)

        if descuento_porcentual:
            # Descuento porcentual
            if descuento < 0 or descuento > 100:
                return Response({'error': 'El descuento porcentual debe ser un valor entre 0 y 100.'}, status=status.HTTP_400_BAD_REQUEST)
            precio_base = producto_detalle.precio_venta_presentacion if unidades else producto_detalle.precio_venta_unidades
            precio_final = precio_base * (1 - descuento / 100)
        else:
            # Descuento monetario
            if descuento < 0:
                return Response({'error': 'El descuento monetario debe ser un valor positivo.'}, status=status.HTTP_400_BAD_REQUEST)
            precio_base = producto_detalle.precio_venta_presentacion if unidades else producto_detalle.precio_venta_unidades
            precio_final = max(precio_base - descuento, 0)  # Asegurarse de que no sea negativo

        data['precio_venta'] = precio_final

        # Serialización y validación
        serializer = VentaDetalleSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        venta_detalle = serializer.save()

        # Guardar cambios en el inventario
        producto_detalle.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class IndexVenta(APIView):
    pagination_class = CustomPagination

    def get(self, request):
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

        # Obtener usuario actual
        current_user = User.objects.filter(id=payload['id']).first()
        if not current_user:
            raise AuthenticationFailed('User not found!')

        # Obtener filtros de la solicitud
        cliente = request.GET.get('cliente')  # ID del cliente
        fecha_inicio = request.GET.get('fecha_inicio')  # Fecha mínima
        fecha_fin = request.GET.get('fecha_fin')  # Fecha máxima
        usuario = request.GET.get('usuario')  # ID del usuario
        identificador = request.GET.get('id')

        # Aplicar filtros dinámicamente
        ventas = Venta.objects.filter(deleted_user__isnull=True)  # Ignorar registros eliminados lógicamente

        if cliente:
            ventas = ventas.filter(cliente_id=cliente)
        if fecha_inicio:
            ventas = ventas.filter(fecha_venta__gte=fecha_inicio)
        if fecha_fin:
            ventas = ventas.filter(fecha_venta__lte=fecha_fin)
        if usuario:
            ventas = ventas.filter(user_id=usuario)
        if identificador:
            ventas = ventas.filter(identificador = id)

        # Aplicar paginación personalizada
        paginator = self.pagination_class()
        paginated_ventas = paginator.paginate_queryset(ventas, request, view=self)

        # Serializar los datos paginados
        serializer = VentaSerializer(paginated_ventas, many=True)

        # Devolver respuesta paginada
        return paginator.get_paginated_response(serializer.data)
