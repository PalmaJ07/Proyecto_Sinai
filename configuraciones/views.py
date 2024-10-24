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
    
# Create your views here.


################CATEGORIAS###########################
class RegisterCategoria(APIView):
    def post(self, request):
        # Extraer el token JWT de la cookie
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
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
    def get(self, request):
        # Autenticación mediante JWT
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener todas las categorías
        categorias = ConfigCategoria.objects.all()

        # Filtro de búsqueda (opcional)
        search_query = request.GET.get('search')
        if search_query:
            categorias = categorias.filter(nombre__icontains=search_query)

        # Configurar paginación
        paginator = PageNumberPagination()
        paginated_categorias = paginator.paginate_queryset(categorias, request)

        # Serializar los resultados paginados
        serializer = ConfigCategoriaSerializer(paginated_categorias, many=True)

        return paginator.get_paginated_response(serializer.data)

class DeleteCategoriaView(APIView):
    def delete(self, request, encrypted_id):
        # Autenticación
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        marcas = ConfigMarca.objects.all()

        search_query = request.GET.get('search')
        if search_query:
            marcas = marcas.filter(nombre__icontains=search_query)

        paginator = PageNumberPagination()
        paginated_marcas = paginator.paginate_queryset(marcas, request)

        serializer = ConfigMarcaSerializer(paginated_marcas, many=True)

        return paginator.get_paginated_response(serializer.data)


class DeleteMarcaView(APIView):
    def delete(self, request, encrypted_id):
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        almacenes = ConfigAlmacen.objects.all()

        search_query = request.GET.get('search')
        if search_query:
            almacenes = almacenes.filter(nombre__icontains=search_query)

        paginator = PageNumberPagination()
        paginated_almacenes = paginator.paginate_queryset(almacenes, request)

        serializer = ConfigAlmacenSerializer(paginated_almacenes, many=True)

        return paginator.get_paginated_response(serializer.data)

class DeleteAlmacenView(APIView):
    def delete(self, request, encrypted_id):
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        presentaciones = ConfigPresentacionProducto.objects.all()

        search_query = request.GET.get('search')
        if search_query:
            presentaciones = presentaciones.filter(nombre__icontains=search_query)

        paginator = PageNumberPagination()
        paginated_presentaciones = paginator.paginate_queryset(presentaciones, request)

        serializer = ConfigPresentacionProductoSerializer(paginated_presentaciones, many=True)

        return paginator.get_paginated_response(serializer.data)

class DeletePresentacionProductoView(APIView):
    def delete(self, request, encrypted_id):
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        unidades = ConfigUnidadMedida.objects.all()

        search_query = request.GET.get('search')
        if search_query:
            unidades = unidades.filter(nombre__icontains=search_query)

        paginator = PageNumberPagination()
        paginated_unidades = paginator.paginate_queryset(unidades, request)

        serializer = ConfigUnidadMedidaSerializer(paginated_unidades, many=True)

        return paginator.get_paginated_response(serializer.data)

class DeleteUnidadMedidaView(APIView):
    def delete(self, request, encrypted_id):
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
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
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        proveedores = ConfigProveedor.objects.all()

        search_query = request.GET.get('search')
        if search_query:
            proveedores = proveedores.filter(nombre_proveedor__icontains=search_query)

        paginator = PageNumberPagination()
        paginated_proveedores = paginator.paginate_queryset(proveedores, request)

        serializer = ConfigProveedorSerializer(paginated_proveedores, many=True)

        return paginator.get_paginated_response(serializer.data)

class DeleteProveedorView(APIView):
    def delete(self, request, encrypted_id):
        token = request.COOKIES.get('jwt')
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
