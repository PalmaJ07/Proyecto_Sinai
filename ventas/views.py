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
from django.db import transaction


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
        data['user'] = current_user.pk
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
        # 🔹 Autenticación con JWT
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # 🔹 Obtener el usuario actual
        current_user = User.objects.filter(id=payload['id']).first()
        if not current_user:
            raise AuthenticationFailed('User not found!')

        # 🔹 Preparar datos para la creación
        data = request.data.copy()
        data['created_user'] = current_user.id
        data['updated_user'] = current_user.id

        # 🔹 Validar existencia del producto
        producto_detalle_id = data.get('producto_detalle')
        producto_detalle = ProductoDetalle.objects.filter(id=producto_detalle_id).first()
        if not producto_detalle:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # 🔹 Validar y convertir cantidad
        try:
            cantidad = int(data.get('cantidad', '0'))  # Asegura que sea entero
        except ValueError:
            return Response({'error': 'Cantidad no válida'}, status=status.HTTP_400_BAD_REQUEST)

        if cantidad <= 0:
            return Response({'error': 'La cantidad debe ser mayor a cero'}, status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Validar y convertir unidades
        unidades = data.get('unidades', False)
        if isinstance(unidades, str):
            unidades = unidades.strip() in ['1', 'true', 'True']
        elif isinstance(unidades, int):
            unidades = unidades == 1
        else:
            unidades = bool(unidades)  # Asegurar que sea booleano en caso de ser None

        # 🔹 Obtener datos del producto
        total_unidades = producto_detalle.total_unidades
        cantidad_por_presentacion = producto_detalle.cantidad_por_presentacion
        unidades_por_presentacion = producto_detalle.unidades_por_presentacion  # Cantidad de unidades en cada presentación

        # 🔹 Si se venden unidades y no hay suficientes unidades sueltas
        if not unidades:
            if total_unidades < cantidad:
                unidades_faltantes = cantidad - total_unidades  # Cuántas unidades nos faltan
                presentaciones_necesarias = unidades_faltantes // unidades_por_presentacion
                if unidades_faltantes % unidades_por_presentacion > 0:
                    presentaciones_necesarias += 1  # Se toma una presentación adicional si hay residuo

                # 🔹 Verificar si hay suficientes presentaciones
                if cantidad_por_presentacion < presentaciones_necesarias:
                    return Response({'error': 'Cantidad excede el inventario disponible.'}, status=status.HTTP_400_BAD_REQUEST)

                # 🔹 Convertir presentaciones a unidades
                producto_detalle.cantidad_por_presentacion -= presentaciones_necesarias
                total_unidades += presentaciones_necesarias * unidades_por_presentacion

            # 🔹 Ahora verificamos si hay suficientes unidades después del desglose
            if total_unidades < cantidad:
                return Response({'error': 'Cantidad excede el inventario disponible en unidades.'}, status=status.HTTP_400_BAD_REQUEST)

            producto_detalle.total_unidades = total_unidades - cantidad  # Restar solo después de asegurarse de que hay suficientes

        else:
            # 🔹 Si se venden por presentación
            if cantidad_por_presentacion < cantidad:
                return Response({'error': 'Cantidad excede el inventario disponible por presentación.'}, status=status.HTTP_400_BAD_REQUEST)
            producto_detalle.cantidad_por_presentacion -= cantidad

        # 🔹 Guardar en la base de datos dentro de una transacción
        with transaction.atomic():
            producto_detalle.save()  # Guardar cambios en inventario

            serializer = VentaDetalleSerializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            venta_detalle = serializer.save()  # Guardar la venta detalle en la BD

        # 🔹 Retornar la respuesta con la instancia guardada
        return Response(VentaDetalleSerializer(venta_detalle).data, status=status.HTTP_201_CREATED)
        
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

class IndexVentaDetalle(APIView):
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
        
        identificador = request.GET.get('venta')

        # Aplicar filtros dinámicamente
        ventas = VentaDetalle.objects.filter(deleted_user__isnull=True)  # Ignorar registros eliminados lógicamente

        if identificador:
            ventas = ventas.filter(venta_id = identificador)

        # Aplicar paginación personalizada
        paginator = self.pagination_class()
        paginated_ventas = paginator.paginate_queryset(ventas, request, view=self)

        # Serializar los datos paginados
        serializer = VentaDetalleSerializer(paginated_ventas, many=True)

        # Devolver respuesta paginada
        return paginator.get_paginated_response(serializer.data)
