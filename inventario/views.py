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

        # Buscar un ProductoDetalle con todos los valores NULL
        producto_detalle_vacio = ProductoDetalle.objects.filter(
            producto_id=data['producto'],
            cantidad_por_presentacion__isnull=True,
            total_unidades__isnull=True,
            almacen__isnull=True,
            deleted_at__isnull=True,
            fecha_expiracion__isnull=True
        ).first()

        if producto_detalle_vacio and not producto_detalle_vacio.almacen and not producto_detalle_vacio.fecha_expiracion:
            # Actualizar los campos vacíos
            producto_detalle_vacio.cantidad_por_presentacion = int(data['cantidad_por_presentacion'])
            producto_detalle_vacio.total_unidades = int(data['unidades_por_presentacion'])
            producto_detalle_vacio.almacen_id = data['config_almacen']
            producto_detalle_vacio.fecha_expiracion = data['fecha_expiracion']
            producto_detalle_vacio.update_user = current_user
            producto_detalle_vacio.save()
            producto_detalle_id = producto_detalle_vacio.id
            message = "ProductoDetalle con valores nulos actualizado."
        else:
            # Verificar si existe un ProductoDetalle con la misma fecha de expiración y almacen
            producto_detalle_existente = ProductoDetalle.objects.filter(
                producto_id=data['producto'],
                almacen_id=data['config_almacen'],
                fecha_expiracion=data.get('fecha_expiracion'),
                deleted_at__isnull=True
            ).first()

            if producto_detalle_existente:
                # Si existe, sumar las cantidades
                producto_detalle_existente.cantidad_por_presentacion += int(data['cantidad_por_presentacion'])
                producto_detalle_existente.total_unidades += int(data['unidades_por_presentacion'])
                producto_detalle_existente.update_user = current_user
                producto_detalle_existente.save()
                producto_detalle_id = producto_detalle_existente.id
                message = "ProductoDetalle actualizado con las nuevas cantidades."
            else:
                # Crear un nuevo ProductoDetalle
                producto_detalle_base = ProductoDetalle.objects.filter(producto_id=data['producto']).first()
                if producto_detalle_base:
                    nuevo_producto_detalle = ProductoDetalle.objects.create(
                        producto_id=data['producto'],
                        config_unidad_medida_id=producto_detalle_base.config_unidad_medida.id,
                        peso=producto_detalle_base.peso,
                        config_presentacion_producto_id=producto_detalle_base.config_presentacion_producto.id,
                        cantidad_por_presentacion=int(data['cantidad_por_presentacion']),
                        unidades_por_presentacion=producto_detalle_base.unidades_por_presentacion,
                        total_unidades=int(data['unidades_por_presentacion']),
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

        # Crear el ProductoDetalleIngreso
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

    
class IndexProductoDetalleIngresoView(APIView):
    def get(self, request):
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        detalles_ingreso = ProductoDetalleIngreso.objects.filter(deleted_user__isnull=True)

        # Filtro de búsqueda por fecha de ingreso
        search_query = request.GET.get('search')
        if search_query:
            detalles_ingreso = detalles_ingreso.filter(fecha_ingreso__icontains=search_query)

        # Paginación
        paginator = CustomPagination()
        paginated_detalles = paginator.paginate_queryset(detalles_ingreso, request)
        
        serializer = ProductoDetalleIngresoSerializer(paginated_detalles, many=True)

        return paginator.get_paginated_response(serializer.data)

class UpdateProductoDetalleIngresoView(APIView):
    def patch(self, request, encrypted_id):
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        try:
            producto_ingreso_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            producto_ingreso = ProductoDetalleIngreso.objects.get(id=producto_ingreso_id)
        except ProductoDetalleIngreso.DoesNotExist:
            return Response({'error': 'ProductoDetalleIngreso not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar ProductoDetalleIngreso
        serializer = ProductoDetalleIngresoSerializer(producto_ingreso, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Ajustar ProductoDetalle según los cambios
        producto_detalle = producto_ingreso.producto_detalle
        previous_data = {
            'cantidad_por_presentacion': producto_ingreso.cantidad_por_presentacion,
            'unidades_por_presentacion': producto_ingreso.unidades_por_presentacion,
        }
        updated_data = request.data
        diff_cantidad = int(updated_data.get('cantidad_por_presentacion', previous_data['cantidad_por_presentacion'])) - previous_data['cantidad_por_presentacion']
        diff_unidades = int(updated_data.get('unidades_por_presentacion', previous_data['unidades_por_presentacion'])) - previous_data['unidades_por_presentacion']

        producto_detalle.cantidad_por_presentacion += diff_cantidad
        producto_detalle.total_unidades += diff_unidades
        producto_detalle.save()

        return Response({'message': 'ProductoDetalleIngreso and ProductoDetalle updated successfully.'}, status=status.HTTP_200_OK)


class DeleteProductoDetalleIngresoView(APIView):
    def delete(self, request, encrypted_id):
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        try:
            producto_ingreso_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            producto_ingreso = ProductoDetalleIngreso.objects.get(id=producto_ingreso_id)
        except ProductoDetalleIngreso.DoesNotExist:
            return Response({'error': 'ProductoDetalleIngreso not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Revertir las cantidades en ProductoDetalle
        producto_detalle = producto_ingreso.producto_detalle
        producto_detalle.cantidad_por_presentacion -= producto_ingreso.cantidad_por_presentacion
        producto_detalle.total_unidades -= producto_ingreso.unidades_por_presentacion
        producto_detalle.save()

        # Marcar ProductoDetalleIngreso como eliminado
        producto_ingreso.deleted_user = User.objects.get(id=payload['id'])
        producto_ingreso.deleted_at = timezone.now()
        producto_ingreso.save()

        return Response({'message': 'ProductoDetalleIngreso marked as deleted successfully.'}, status=status.HTTP_200_OK)

########################PRODUCTO-MOVIMIENTO########################

class ProductoMovimientoCreate(APIView):
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

        current_user = User.objects.get(id=payload['id'])
        data = request.data

        # Obtener producto_detalle_origen
        try:
            producto_detalle_origen = ProductoDetalle.objects.get(id=data['producto_detalle'])
        except ProductoDetalle.DoesNotExist:
            return Response({'error': 'ProductoDetalle no encontrado para el id proporcionado'}, status=status.HTTP_400_BAD_REQUEST)

        if producto_detalle_origen.cantidad_por_presentacion < int(data['unidades_por_presentacion']):
            return Response({'error': 'Cantidad insuficiente en el almacén de origen'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar cantidades disponibles en el origen
        if producto_detalle_origen.total_unidades < int(data['unidades_por_presentacion']):
            return Response({'error': 'Cantidad insuficiente en el almacén de origen'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener producto_detalle_destino o crearlo si no existe
        producto_detalle_destino = ProductoDetalle.objects.filter(
            producto_id=data['producto'],
            almacen_id=data['config_almacen'],
            fecha_expiracion=data.get('fecha_expiracion'),
            deleted_at__isnull=True
        ).first()

        if producto_detalle_destino is None:
            # Si no existe, crear un nuevo ProductoDetalle
            producto_detalle_destino = ProductoDetalle.objects.create(
                producto_id=data['producto'],
                almacen_id=data['config_almacen'],
                fecha_expiracion=data.get('fecha_expiracion'),
                config_unidad_medida_id=producto_detalle_origen.config_unidad_medida_id,
                peso=producto_detalle_origen.peso,
                config_presentacion_producto_id=producto_detalle_origen.config_presentacion_producto_id,
                cantidad_por_presentacion=data.get('cantidad_por_presentacion'),
                unidades_por_presentacion=producto_detalle_origen.unidades_por_presentacion,
                total_unidades=data.get('unidades_por_presentacion'),
                precio_venta_presentacion=producto_detalle_origen.precio_venta_presentacion,
                precio_venta_unidades=producto_detalle_origen.precio_venta_unidades,
                proveedor_id=producto_detalle_origen.proveedor_id,
                created_user=current_user
            )

            producto_detalle_origen.cantidad_por_presentacion -= int(data['cantidad_por_presentacion'])
            producto_detalle_origen.total_unidades -= int(data['unidades_por_presentacion'])
            producto_detalle_origen.update_user = current_user
            producto_detalle_origen.save()

        else:
            # Si existe, actualizarlo
            producto_detalle_destino.cantidad_por_presentacion += int(data['cantidad_por_presentacion'])
            producto_detalle_destino.total_unidades += int(data['unidades_por_presentacion'])
            producto_detalle_destino.update_user = current_user
            producto_detalle_destino.save()

            # Actualizar producto_detalle_origen
            producto_detalle_origen.cantidad_por_presentacion -= int(data['cantidad_por_presentacion'])
            producto_detalle_origen.total_unidades -= int(data['unidades_por_presentacion'])
            producto_detalle_origen.update_user = current_user
            producto_detalle_origen.save()

        # Registrar movimiento
        movimiento = ProductoMovimiento.objects.create(
            producto_detalle_origen=producto_detalle_origen.almacen,
            producto_detalle_destino=producto_detalle_destino.almacen,
            cantidad_por_presentacion=int(data['cantidad_por_presentacion']),
            unidades_por_presentacion=int(data['unidades_por_presentacion']),
            fecha=data['fecha_ingreso'],
            fecha_expiracion=data.get('fecha_expiracion'),
            created_user=current_user
        )

        # Registrar ingreso en producto_detalle_destino
        ProductoDetalleIngreso.objects.create(
            producto_id=data['producto'],
            producto_detalle_id=producto_detalle_destino.id,
            config_almacen_id=data['config_almacen'],
            producto_movimiento_id=movimiento.id,  # Asociar el ID del movimiento creado
            user=current_user,
            cantidad_por_presentacion=int(data['cantidad_por_presentacion']),
            unidades_por_presentacion=int(data['unidades_por_presentacion']),
            precio_compra_presentacion=float(data['precio_compra_presentacion']),
            precio_compra_unidades=float(data['precio_compra_unidades']),
            fecha_expiracion=data.get('fecha_expiracion'),
            fecha_ingreso=data['fecha_ingreso'],
            created_user=current_user
        )

        return Response({'message': 'ProductoDetalle actualizado y movimiento registrado con éxito.'}, status=status.HTTP_201_CREATED)


########################PRODUCTO-DEVOLUCION########################
class RegisterProductoDevolucion(APIView):
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

        # Obtener datos de entrada
        data = request.data.copy()
        producto_detalle_id = int(data.get('producto_detalle'))
        cantidad_por_presentacion = int(data.get('cantidad_por_presentacion', 0))
        unidades_por_presentacion = int(data.get('unidades_por_presentacion', 0))

        try:
            # Buscar el registro ProductoDetalle
            producto_detalle = ProductoDetalle.objects.get(id=producto_detalle_id)

            # Validar disponibilidad antes de realizar cambios
            if cantidad_por_presentacion > producto_detalle.cantidad_por_presentacion:
                return Response({"error": "La cantidad por presentación excede el inventario disponible."}, status=status.HTTP_400_BAD_REQUEST)
            if unidades_por_presentacion > producto_detalle.total_unidades:
                return Response({"error": "Las unidades por presentación exceden las unidades disponibles."}, status=status.HTTP_400_BAD_REQUEST)

            # Actualizar los valores en ProductoDetalle
            producto_detalle.cantidad_por_presentacion -= cantidad_por_presentacion
            producto_detalle.total_unidades -= unidades_por_presentacion
            producto_detalle.update_user = current_user  # Usar la instancia de User
            producto_detalle.save()

            # Preparar datos para la creación de ProductoDevolucion
            data['created_user'] = current_user.id
            data['update_user'] = None
            data['deleted_user'] = None

            # Crear el registro de devolución
            devolucion_serializer = ProductoDevolucionSerializer(data=data)
            devolucion_serializer.is_valid(raise_exception=True)
            devolucion_serializer.save()

            return Response(devolucion_serializer.data, status=status.HTTP_201_CREATED)

        except ProductoDetalle.DoesNotExist:
            return Response({"error": "ProductoDetalle no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
