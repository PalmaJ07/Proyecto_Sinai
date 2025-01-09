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


########################PRODUCTO########################

class RegisterProducto(APIView):
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
        data['update_user'] = None
        data['deleted_user'] = None

        # Serialización y validación
        serializer = ProductoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateProducto(APIView):
    def patch(self, request, encrypted_id):
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

        # Decodificar el ID encriptado
        try:
            producto_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar el producto
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar el producto con los datos del request
        serializer = ProductoSerializer(producto, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Product updated successfully.'}, status=status.HTTP_200_OK)


class IndexProductoView(APIView):
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

        # Obtener productos
        productos = Producto.objects.filter(deleted_user__isnull=True)

        # Filtro de búsqueda (opcional)
        search_query = request.GET.get('search')
        if search_query:
            productos = productos.filter(descripcion__icontains=search_query)
        
        # Filtro por categoría
        categoria_id = request.GET.get('categoria')
        if categoria_id:
            productos = productos.filter(config_categoria__id=categoria_id)

        # Filtro por marca
        marca_id = request.GET.get('marca')
        if marca_id:
            productos = productos.filter(config_marca__id=marca_id)

        # Paginación
        paginator = CustomPagination()
        paginated_productos = paginator.paginate_queryset(productos, request)

        # Serializar los resultados
        serializer = ProductoSerializer(paginated_productos, many=True)

        # Devolver respuesta paginada
        return paginator.get_paginated_response(serializer.data)


class DeleteProductoView(APIView):
    def delete(self, request, encrypted_id):
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

        # Decodificar el ID encriptado
        try:
            producto_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar el producto
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Realizar la eliminación lógica
        producto.deleted_user = User.objects.get(id=payload['id'])
        producto.deleted_at = timezone.now()
        producto.save()

        return Response({'message': 'Product marked as deleted successfully.'}, status=status.HTTP_200_OK)

########################PRODUCTO-DETALLE########################
class CreateProductoDetalle(APIView):
    def post(self, request):
        # Autenticación mediante JWT
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener el usuario que está realizando la solicitud
        current_user = User.objects.filter(id=payload['id']).first()
        if not current_user:
            raise AuthenticationFailed('User not found!')

        # Crear un diccionario con los datos enviados en la solicitud
        data = request.data.copy()
        data['created_user'] = current_user.id
        data['update_user'] = None
        data['deleted_user'] = None

        # Serializar y validar los datos
        serializer = ProductoDetalleSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateProductoDetalle(APIView):
    def patch(self, request, encrypted_id):
        # Autenticación mediante JWT
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Decodificar el `encrypted_id` para obtener el ID real
        try:
            producto_detalle_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar el ProductoDetalle por ID
        try:
            producto_detalle = ProductoDetalle.objects.get(id=producto_detalle_id)
        except ProductoDetalle.DoesNotExist:
            return Response({'error': 'ProductoDetalle not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar los campos que fueron enviados en el request
        serializer = ProductoDetalleSerializer(producto_detalle, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'ProductoDetalle updated successfully.'}, status=status.HTTP_200_OK)

class IndexProductoDetalleView(APIView):
    # Método GET para listar los productos detalles con paginación y filtros
    def get(self, request):
        # Autenticación mediante JWT
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener todos los detalles de productos que no han sido eliminados
        producto_detalles = ProductoDetalle.objects.filter(deleted_user__isnull=True)

        # Filtro por almacen
        almacen_id = request.GET.get('almacen')
        if almacen_id:
            producto_detalles = producto_detalles.filter(almacen_id=almacen_id)

        # Filtro por proveedor
        proveedor_id = request.GET.get('proveedor')
        if proveedor_id:
            producto_detalles = producto_detalles.filter(proveedor_id=proveedor_id)

        # Filtro de búsqueda (opcional)
        search_query = request.GET.get('search')
        if search_query:
            producto_detalles = producto_detalles.filter(producto__descripcion__icontains=search_query)

        # Configurar paginación
        paginator = CustomPagination()
        paginated_producto_detalles = paginator.paginate_queryset(producto_detalles, request)

        # Serializar los resultados paginados
        serializer = ProductoDetalleSerializer(paginated_producto_detalles, many=True)

        # Devolver la respuesta paginada usando `get_paginated_response()`
        return paginator.get_paginated_response(serializer.data)

class DeleteProductoDetalle(APIView):
    def delete(self, request, encrypted_id):
        # Autenticación mediante JWT
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Decodificar el `encrypted_id` para obtener el ID real
        try:
            producto_detalle_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar el ProductoDetalle por ID
        try:
            producto_detalle = ProductoDetalle.objects.get(id=producto_detalle_id)
        except ProductoDetalle.DoesNotExist:
            return Response({'error': 'ProductoDetalle not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar los campos de eliminación lógica
        producto_detalle.deleted_user = User.objects.get(id=payload['id'])
        producto_detalle.deleted_at = timezone.now()

        # Guardar los cambios
        producto_detalle.save()

        return Response({'message': 'ProductoDetalle marked as deleted successfully.'}, status=status.HTTP_200_OK)

########################PRODUCTO-DETALLE-INGRESO########################

class ProductoDetalleIngresoCreate(APIView):
    def post(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return Response({'error': 'Token no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token expirado'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

        # Obtener el usuario actual
        current_user = User.objects.get(id=payload['id'])

        # Obtener los datos del request
        data = request.data

        # Verificar si existe un ProductoDetalle con la misma fecha de expiración y almacen
        producto_detalle_existente = ProductoDetalle.objects.filter(
            producto_id=data['producto'],
            almacen_id=data['config_almacen'],
            fecha_expiracion=data.get('fecha_expiracion')
        ).first()

        if producto_detalle_existente:
            # Si existe, sumar las cantidades
            producto_detalle_existente.cantidad_por_presentacion += int(data['cantidad_por_presentacion'])
            producto_detalle_existente.unidades_por_presentacion += int(data['unidades_por_presentacion'])
            producto_detalle_existente.total_unidades += int(data['unidades_por_presentacion'])  # O la cantidad correspondiente
            producto_detalle_existente.update_user = current_user
            producto_detalle_existente.save()

            # Usar el ID del ProductoDetalle existente
            producto_detalle_id = producto_detalle_existente.id
            message = "ProductoDetalle actualizado con las nuevas cantidades."
        else:
            # Si no existe, obtener los datos del ProductoDetalle base (del mismo producto)
            producto_detalle_base = ProductoDetalle.objects.filter(producto_id=data['producto']).first()

            if producto_detalle_base:
                # Crear un nuevo ProductoDetalle con los datos base, pero con la nueva fecha de expiración o almacén
                nuevo_producto_detalle = ProductoDetalle.objects.create(
                    producto_id=data['producto'],
                    config_unidad_medida_id=producto_detalle_base.config_unidad_medida.id,
                    peso=producto_detalle_base.peso,
                    config_presentacion_producto_id=producto_detalle_base.config_presentacion_producto.id,
                    cantidad_por_presentacion=int(data['cantidad_por_presentacion']),
                    unidades_por_presentacion=int(data['unidades_por_presentacion']),
                    total_unidades=int(data['unidades_por_presentacion']),  # Total inicial igual a las unidades por presentación
                    almacen_id=data['config_almacen'],
                    precio_venta_presentacion=producto_detalle_base.precio_venta_presentacion,
                    precio_venta_unidades=producto_detalle_base.precio_venta_unidades,
                    proveedor_id=producto_detalle_base.proveedor.id,
                    fecha_expiracion=data['fecha_expiracion'],
                    created_user=current_user
                )

                producto_detalle_id = nuevo_producto_detalle.id
                message = "Nuevo ProductoDetalle creado."
            else:
                return Response({'error': 'ProductoDetalle base no encontrado para el producto'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el ProductoDetalleIngreso con los valores del request
        ProductoDetalleIngreso.objects.create(
            producto_id=data['producto'],
            producto_detalle_id=producto_detalle_id,
            config_almacen_id=data['config_almacen'],
            producto_movimiento_id=data.get('producto_movimiento'),
            user=current_user,
            cantidad_por_presentacion=int(data['cantidad_por_presentacion']),
            unidades_por_presentacion=int(data['unidades_por_presentacion']),
            precio_compra_presentacion=float(data['precio_compra_presentacion']),
            precio_compra_unidades=float(data['precio_compra_unidades']),
            fecha_expiracion=data.get('fecha_expiracion'),
            fecha_ingreso=data['fecha_ingreso'],
            created_user=current_user
        )

        return Response({'message': message}, status=status.HTTP_201_CREATED)