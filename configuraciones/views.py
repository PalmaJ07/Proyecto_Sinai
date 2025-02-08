from django.shortcuts import render, get_object_or_404
import base64
from io import BytesIO
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
from inventario.models import ProductoDetalleIngreso, Producto, ConfigUnidadMedida, ProductoMovimiento
from inventario.serializers import ProductoMovimientoSerializer # Ajusta según tus modelos
from usuarios.serializers import ClienteSerializer
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from ventas.models import Venta, VentaDetalle
from django.db.models import Sum, F
from decimal import Decimal
from django.utils.timezone import now
    
# Create your views here.
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

################CATEGORIAS###########################
class RegisterCategoria(APIView):
    def post(self, request):
        # Extraer el token JWT de la cookie
        #token = request.COOKIES.get('jwt')
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
        serializer = ConfigCategoriaSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateCategoria(APIView):
    def patch(self, request, encrypted_id):
        # Autenticación
        #token = request.COOKIES.get('jwt')
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
            categoria_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar la categoría por ID
        try:
            categoria = ConfigCategoria.objects.get(id=categoria_id)
        except ConfigCategoria.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar los campos que fueron enviados en el request
        serializer = ConfigCategoriaSerializer(categoria, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Category updated successfully.'}, status=status.HTTP_200_OK)

class IndexCategoriaView(APIView):
    # Método GET para listar las categorías con paginación
    def get(self, request):
        # Autenticación mediante JWT
        #token = request.COOKIES.get('jwt')
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener todas las categorías
        categorias = ConfigCategoria.objects.filter(deleted_user__isnull=True)

        # Filtro de búsqueda (opcional)
        search_query = request.GET.get('search')
        if search_query:
            categorias = categorias.filter(nombre__icontains=search_query)

        # Configurar paginación
        paginator = CustomPagination()
        paginated_categorias = paginator.paginate_queryset(categorias, request)

        # Serializar los resultados paginados
        serializer = ConfigCategoriaSerializer(paginated_categorias, many=True)

        # Devolver la respuesta paginada usando `get_paginated_response()`
        return paginator.get_paginated_response(serializer.data)

class DeleteCategoriaView(APIView):
    def delete(self, request, encrypted_id):
        # Autenticación
        #token = request.COOKIES.get('jwt')
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
            categoria_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar la categoría por ID
        try:
            categoria = ConfigCategoria.objects.get(id=categoria_id)
        except ConfigCategoria.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar los campos de eliminación lógica
        categoria.deleted_user = User.objects.get(id=payload['id'])
        categoria.deleted_at = timezone.now()

        # Guardar los cambios
        categoria.save()

        return Response({'message': 'Category marked as deleted successfully.'}, status=status.HTTP_200_OK)


################MARCAS###########################
class RegisterMarca(APIView):
    def post(self, request):
        #token = request.COOKIES.get('jwt')
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        current_user = User.objects.filter(id=payload['id']).first()
        if not current_user:
            raise AuthenticationFailed('User not found!')

        data = request.data.copy()
        data['created_user'] = current_user.id
        data['update_user'] = None
        data['deleted_user'] = None

        serializer = ConfigMarcaSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateMarca(APIView):
    def patch(self, request, encrypted_id):
        #token = request.COOKIES.get('jwt')
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
            marca_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            marca = ConfigMarca.objects.get(id=marca_id)
        except ConfigMarca.DoesNotExist:
            return Response({'error': 'Marca not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConfigMarcaSerializer(marca, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Marca updated successfully.'}, status=status.HTTP_200_OK)


class IndexMarcaView(APIView):
    def get(self, request):
        #token = request.COOKIES.get('jwt')
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        marcas = ConfigMarca.objects.filter(deleted_user__isnull=True)

        search_query = request.GET.get('search')
        if search_query:
            marcas = marcas.filter(nombre__icontains=search_query)

        paginator = CustomPagination()
        paginated_marcas = paginator.paginate_queryset(marcas, request)

        serializer = ConfigMarcaSerializer(paginated_marcas, many=True)

        return paginator.get_paginated_response(serializer.data)


class DeleteMarcaView(APIView):
    def delete(self, request, encrypted_id):
        #token = request.COOKIES.get('jwt')
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
            marca_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            marca = ConfigMarca.objects.get(id=marca_id)
        except ConfigMarca.DoesNotExist:
            return Response({'error': 'Marca not found.'}, status=status.HTTP_404_NOT_FOUND)

        marca.deleted_user = User.objects.get(id=payload['id'])
        marca.deleted_at = timezone.now()
        marca.save()

        return Response({'message': 'Marca marked as deleted successfully.'}, status=status.HTTP_200_OK)

################ALMACEN###########################
class RegisterAlmacen(APIView):
    def post(self, request):
        #token = request.COOKIES.get('jwt')
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        current_user = User.objects.filter(id=payload['id']).first()
        if not current_user:
            raise AuthenticationFailed('User not found!')

        data = request.data.copy()
        data['created_user'] = current_user.id
        data['update_user'] = None
        data['deleted_user'] = None

        serializer = ConfigAlmacenSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateAlmacen(APIView):
    def patch(self, request, encrypted_id):
        #token = request.COOKIES.get('jwt')
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
            almacen_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            almacen = ConfigAlmacen.objects.get(id=almacen_id)
        except ConfigAlmacen.DoesNotExist:
            return Response({'error': 'Almacen not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConfigAlmacenSerializer(almacen, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Almacen updated successfully.'}, status=status.HTTP_200_OK)

class IndexAlmacenView(APIView):
    def get(self, request):
        #token = request.COOKIES.get('jwt')
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        almacenes = ConfigAlmacen.objects.filter(deleted_user__isnull=True)

        search_query = request.GET.get('search')
        if search_query:
            almacenes = almacenes.filter(nombre__icontains=search_query)

        paginator = CustomPagination()
        paginated_almacenes = paginator.paginate_queryset(almacenes, request)

        serializer = ConfigAlmacenSerializer(paginated_almacenes, many=True)

        return paginator.get_paginated_response(serializer.data)

class DeleteAlmacenView(APIView):
    def delete(self, request, encrypted_id):
        #token = request.COOKIES.get('jwt')
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
            almacen_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            almacen = ConfigAlmacen.objects.get(id=almacen_id)
        except ConfigAlmacen.DoesNotExist:
            return Response({'error': 'Almacen not found.'}, status=status.HTTP_404_NOT_FOUND)

        almacen.deleted_user = User.objects.get(id=payload['id'])
        almacen.deleted_at = timezone.now()
        almacen.save()

        return Response({'message': 'Almacen marked as deleted successfully.'}, status=status.HTTP_200_OK)
    
################Presentaciones###########################

class RegisterPresentacionProducto(APIView):
    def post(self, request):
        #token = request.COOKIES.get('jwt')
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        current_user = User.objects.filter(id=payload['id']).first()
        if not current_user:
            raise AuthenticationFailed('User not found!')

        data = request.data.copy()
        data['created_user'] = current_user.id
        data['update_user'] = None
        data['deleted_user'] = None

        serializer = ConfigPresentacionProductoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdatePresentacionProducto(APIView):
    def patch(self, request, encrypted_id):
        #token = request.COOKIES.get('jwt')
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
            presentacion_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            presentacion = ConfigPresentacionProducto.objects.get(id=presentacion_id)
        except ConfigPresentacionProducto.DoesNotExist:
            return Response({'error': 'Presentacion not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConfigPresentacionProductoSerializer(presentacion, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Presentacion updated successfully.'}, status=status.HTTP_200_OK)

class IndexPresentacionProductoView(APIView):
    def get(self, request):
        #token = request.COOKIES.get('jwt')
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        presentaciones = ConfigPresentacionProducto.objects.filter(deleted_user__isnull=True)

        search_query = request.GET.get('search')
        if search_query:
            presentaciones = presentaciones.filter(nombre__icontains=search_query)

        paginator = CustomPagination()
        paginated_presentaciones = paginator.paginate_queryset(presentaciones, request)

        serializer = ConfigPresentacionProductoSerializer(paginated_presentaciones, many=True)

        return paginator.get_paginated_response(serializer.data)

class DeletePresentacionProductoView(APIView):
    def delete(self, request, encrypted_id):
        #token = request.COOKIES.get('jwt')
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
            presentacion_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            presentacion = ConfigPresentacionProducto.objects.get(id=presentacion_id)
        except ConfigPresentacionProducto.DoesNotExist:
            return Response({'error': 'Presentacion not found.'}, status=status.HTTP_404_NOT_FOUND)

        presentacion.deleted_user = User.objects.get(id=payload['id'])
        presentacion.deleted_at = timezone.now()
        presentacion.save()

        return Response({'message': 'Presentacion marked as deleted successfully.'}, status=status.HTTP_200_OK)

################UNIDAD DE MEDIDA###########################
class RegisterUnidadMedida(APIView):
    def post(self, request):
        #token = request.COOKIES.get('jwt')
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        current_user = User.objects.filter(id=payload['id']).first()
        if not current_user:
            raise AuthenticationFailed('User not found!')

        data = request.data.copy()
        data['created_user'] = current_user.id
        data['update_user'] = None
        data['deleted_user'] = None

        serializer = ConfigUnidadMedidaSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateUnidadMedida(APIView):
    def patch(self, request, encrypted_id):
        #token = request.COOKIES.get('jwt')
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
            unidad_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            unidad_medida = ConfigUnidadMedida.objects.get(id=unidad_id)
        except ConfigUnidadMedida.DoesNotExist:
            return Response({'error': 'Unidad de Medida not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConfigUnidadMedidaSerializer(unidad_medida, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Unidad de Medida updated successfully.'}, status=status.HTTP_200_OK)

class IndexUnidadMedidaView(APIView):
    def get(self, request):
        #token = request.COOKIES.get('jwt')
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        unidades = ConfigUnidadMedida.objects.filter(deleted_user__isnull=True)

        search_query = request.GET.get('search')
        if search_query:
            unidades = unidades.filter(nombre__icontains=search_query)

        paginator = CustomPagination()
        paginated_unidades = paginator.paginate_queryset(unidades, request)

        serializer = ConfigUnidadMedidaSerializer(paginated_unidades, many=True)

        return paginator.get_paginated_response(serializer.data)

class DeleteUnidadMedidaView(APIView):
    def delete(self, request, encrypted_id):
        #token = request.COOKIES.get('jwt')
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
            unidad_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            unidad_medida = ConfigUnidadMedida.objects.get(id=unidad_id)
        except ConfigUnidadMedida.DoesNotExist:
            return Response({'error': 'Unidad de Medida not found.'}, status=status.HTTP_404_NOT_FOUND)

        unidad_medida.deleted_user = User.objects.get(id=payload['id'])
        unidad_medida.deleted_at = timezone.now()
        unidad_medida.save()

        return Response({'message': 'Unidad de Medida marked as deleted successfully.'}, status=status.HTTP_200_OK)

################PROVEEDOR###########################

class RegisterProveedor(APIView):
    def post(self, request):
        #token = request.COOKIES.get('jwt')
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        current_user = User.objects.filter(id=payload['id']).first()
        if not current_user:
            raise AuthenticationFailed('User not found!')

        data = request.data.copy()
        data['created_user'] = current_user.id
        data['update_user'] = None
        data['deleted_user'] = None

        serializer = ConfigProveedorSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateProveedor(APIView):
    def patch(self, request, encrypted_id):
        #token = request.COOKIES.get('jwt')
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
            proveedor_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            proveedor = ConfigProveedor.objects.get(id=proveedor_id)
        except ConfigProveedor.DoesNotExist:
            return Response({'error': 'Proveedor not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConfigProveedorSerializer(proveedor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Proveedor updated successfully.'}, status=status.HTTP_200_OK)

class IndexProveedorView(APIView):
    def get(self, request):
        #token = request.COOKIES.get('jwt')
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        proveedores = ConfigProveedor.objects.filter(deleted_user__isnull=True)

        search_query = request.GET.get('search')
        if search_query:
            proveedores = proveedores.filter(nombre_proveedor__icontains=search_query)

        paginator = CustomPagination()
        paginated_proveedores = paginator.paginate_queryset(proveedores, request)

        serializer = ConfigProveedorSerializer(paginated_proveedores, many=True)

        return paginator.get_paginated_response(serializer.data)

class DeleteProveedorView(APIView):
    def delete(self, request, encrypted_id):
        #token = request.COOKIES.get('jwt')
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
            proveedor_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            proveedor = ConfigProveedor.objects.get(id=proveedor_id)
        except ConfigProveedor.DoesNotExist:
            return Response({'error': 'Proveedor not found.'}, status=status.HTTP_404_NOT_FOUND)

        proveedor.deleted_user = User.objects.get(id=payload['id'])
        proveedor.deleted_at = timezone.now()
        proveedor.save()

        return Response({'message': 'Proveedor marked as deleted successfully.'}, status=status.HTTP_200_OK)

#######Reportes#######

##########Reportes de ventas##############
class ReporteVentas(APIView):
    def get(self, request):
        # Obtener parámetros de fecha
        fecha_inicio = request.GET.get('fecha_inicio', None)  # Fecha de inicio para el rango
        fecha_fin = request.GET.get('fecha_fin', None)  # Fecha de fin para el rango
        fecha = request.GET.get('fecha', None)  # Fecha única (si se pasa solo una)

        # Filtrar las ventas por fecha
        ventas = Venta.objects.all()

        if fecha:
            # Si solo se pasa una fecha, filtrar por esa fecha
            ventas = ventas.filter(fecha_venta=fecha)
        elif fecha_inicio and fecha_fin:
            # Si se pasan ambas fechas, filtrar por el rango
            ventas = ventas.filter(fecha_venta__gte=fecha_inicio, fecha_venta__lte=fecha_fin)
        elif fecha_inicio:
            # Si solo se pasa la fecha de inicio
            ventas = ventas.filter(fecha_venta__gte=fecha_inicio)
        elif fecha_fin:
            # Si solo se pasa la fecha de fin
            ventas = ventas.filter(fecha_venta__lte=fecha_fin)

        # Calcular el total de ventas
        total_ventas = ventas.aggregate(total=Sum('total_venta'))

        # Si no hay ventas, devolver un mensaje apropiado
        if total_ventas['total'] is None:
            total_ventas['total'] = 0

        # Devolver el reporte
        return Response({
            'total_ventas': total_ventas['total'],
            'ventas': [{'id': venta.id, 'cliente': venta.cliente, 'total_venta': venta.total_venta, 'fecha_venta': venta.fecha_venta} for venta in ventas]
        }, status=status.HTTP_200_OK)
    
##########Reportes de ganancias##############

class ReporteGanancias(APIView):
    def get(self, request):
        # Obtener parámetros de fecha
        fecha_inicio = request.GET.get('fecha_inicio', None)  # Fecha de inicio para el rango
        fecha_fin = request.GET.get('fecha_fin', None)  # Fecha de fin para el rango
        fecha = request.GET.get('fecha', None)  # Fecha única (si se pasa solo una)

        # Filtrar las ventas por fecha
        ventas = Venta.objects.all()

        if fecha:
            ventas = ventas.filter(fecha_venta=fecha)
        elif fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha_venta__gte=fecha_inicio, fecha_venta__lte=fecha_fin)
        elif fecha_inicio:
            ventas = ventas.filter(fecha_venta__gte=fecha_inicio)
        elif fecha_fin:
            ventas = ventas.filter(fecha_venta__lte=fecha_fin)

        # Calcular el total de ventas
        total_ventas = ventas.aggregate(total=Sum('total_venta'))

        # Calcular el costo total de los productos vendidos, considerando unidades o presentaciones
        total_costos = Decimal(0)

        for venta in ventas:
            for detalle in venta.detalles.all():
                producto_detalle = detalle.producto_detalle

                # Obtener el ingreso de productos en base al producto_detalle
                producto_ingreso = ProductoDetalleIngreso.objects.filter(producto_detalle=producto_detalle).first()

                if producto_ingreso:
                    if detalle.unidades == 1:  # Si es por unidad
                        costo = producto_ingreso.precio_compra_unidades
                        cantidad = detalle.cantidad  # Usar la cantidad de unidades
                    elif detalle.unidades == 0:  # Si es por presentación
                        costo = producto_ingreso.precio_compra_presentacion
                        cantidad = detalle.cantidad  # En este caso usamos cantidad, pero se calcula con presentación

                    # Calculando el costo total
                    total_costos += costo * cantidad

        # Si no hay ventas o costos, establecer los valores como 0
        total_ventas_value = Decimal(total_ventas['total']) if total_ventas['total'] else Decimal(0)
        total_costos_value = total_costos if total_costos else Decimal(0)

        # Calcular las ganancias (ventas - costos)
        ganancias = total_ventas_value - total_costos_value

        # Devolver el reporte de ganancias
        return Response({
            'ganancias': float(ganancias),  # Convertir ganancias a float si es necesario
            'total_ventas': float(total_ventas_value),  # Convertir total_ventas a float
            'total_costos': float(total_costos_value),  # Convertir total_costos a float
            'ventas': [{
                'id': venta.id,
                'cliente': ClienteSerializer(venta.cliente).data,
                'total_venta': venta.total_venta,
                'fecha_venta': venta.fecha_venta
            } for venta in ventas]
        }, status=status.HTTP_200_OK)
    
##########Reportes de movimientos##############
class ReporteMovimientos(APIView):
    def get(self, request):
        # Filtrar por fechas, si se pasan como parámetros
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        fecha = request.query_params.get('fecha')

        # Convertir las fechas si se pasan como parámetros
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        if fecha:
            fecha = datetime.strptime(fecha, '%Y-%m-%d')

        # Filtrar ProductoDetalleIngreso que no estén eliminados y que tengan producto_movimiento no nulo
        queryset = ProductoDetalleIngreso.objects.filter(
            producto_movimiento__isnull=False,
            deleted_at__isnull=True
        )

        # Filtrar por fecha si se pasó un rango de fechas
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(fecha_ingreso__range=[fecha_inicio, fecha_fin])
        elif fecha_inicio:
            queryset = queryset.filter(fecha_ingreso__gte=fecha_inicio)
        elif fecha_fin:
            queryset = queryset.filter(fecha_ingreso__lte=fecha_fin)
        elif fecha:
            queryset = queryset.filter(fecha_ingreso=fecha)

        # Obtener los movimientos relacionados
        movimientos = []
        for detalle_ingreso in queryset:
            # Obtener los movimientos relacionados con el ProductoDetalleIngreso
            producto_movimiento = detalle_ingreso.producto_movimiento
            if producto_movimiento:
                movimiento_data = ProductoMovimientoSerializer(producto_movimiento).data
                movimientos.append({
                    'producto': detalle_ingreso.producto.descripcion,
                    'producto_detalle_origen': movimiento_data['producto_detalle_origen'],
                    'producto_detalle_destino': movimiento_data['producto_detalle_destino'],
                    'cantidad_por_presentacion': movimiento_data['cantidad_por_presentacion'],
                    'unidades_por_presentacion': movimiento_data['unidades_por_presentacion'],
                    'fecha': movimiento_data['fecha'],
                    'fecha_expiracion': movimiento_data['fecha_expiracion'],
                })

        return Response(movimientos, status=status.HTTP_200_OK)
    
class ProductosMasVendidos(APIView):
    def get(self, request):
        productos_vendidos = (
            VentaDetalle.objects.values("producto_detalle__id", "producto_detalle__producto__descripcion")
            .annotate(total_vendido=Sum("cantidad"))
            .order_by("-total_vendido")[:10]  # Obtener los 10 más vendidos
        )

        return Response(productos_vendidos)
    
class GananciasDelDia(APIView):
    def get(self, request):
        fecha_hoy = now().date()

        # Total de ventas del día
        total_ventas = Venta.objects.filter(fecha_venta=fecha_hoy).aggregate(total=Sum("total_venta"))["total"] or Decimal(0)

        # Cálculo de costos
        total_costos = Decimal(0)
        ventas_detalles = VentaDetalle.objects.filter(venta__fecha_venta=fecha_hoy)

        for detalle in ventas_detalles:
            producto_ingreso = ProductoDetalleIngreso.objects.filter(producto_detalle=detalle.producto_detalle).first()
            if producto_ingreso:
                costo = producto_ingreso.precio_compra_unidades if detalle.unidades == 1 else producto_ingreso.precio_compra_presentacion
                total_costos += costo * detalle.cantidad

        # Cálculo de ganancias
        ganancias = total_ventas - total_costos

        return Response({
            "fecha": str(fecha_hoy),
            "total_ventas": float(total_ventas),
            "total_costos": float(total_costos),
            "ganancias": float(ganancias)
        })

class VendedoresMasVentas(APIView):
    def get(self, request):
        vendedores = (
            Venta.objects.values("user__id", "user__name")  # 'user__name' según tu modelo
            .annotate(total_ventas=Sum("total_venta"))
            .order_by("-total_ventas")[:10]  # Top 10 vendedores
        )

        return Response(vendedores)