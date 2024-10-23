import base64
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, ClienteSerializer
from rest_framework import status
from rest_framework.exceptions import NotFound,AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from .models import User, Cliente
import jwt, datetime
from django.utils import timezone
    
#Controlador de login - api/login/

"""
class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        # Buscar el usuario por su username
        user = User.objects.filter(username=username).first()

        # Verificar si el usuario existe
        if user is None:
            raise AuthenticationFailed('Username not found!')

        # Verificar si el usuario está inactivo (estado = 0)
        if user.estado == 0:
            raise AuthenticationFailed('Your account is disabled. Please contact support.')

        # Verificar si la contraseña es correcta
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        # Crear el payload para el token JWT
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        # Generar el token JWT
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        # Preparar la respuesta
        response = Response()

        # Establecer la cookie con el token JWT
        response.set_cookie(key='jwt', value=token, httponly=True, samesite='Lax', secure=False)

        #
        response['Authorization'] = token
        # Incluir el token JWT en la respuesta
        response.data = {
            'jwt': token
        }

        return response
"""


class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        # Buscar el usuario por su username
        user = User.objects.filter(username=username).first()

        # Verificar si el usuario existe
        if user is None:
            raise AuthenticationFailed('Username not found!')

        # Verificar si el usuario está inactivo (estado = 0)
        if user.estado == 0:
            raise AuthenticationFailed('Your account is disabled. Please contact support.')

        # Verificar si la contraseña es correcta
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        # Crear el payload para el token JWT
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        # Generar el token JWT
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        # Preparar la respuesta
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)

        # Incluir el token JWT en la respuesta
        response.data = {
            'jwt': token
        }

        return response
    
#Controlador de logout - api/logout/
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response
    
#Controlador de index - user/empleados/index/
class CustomPagination(PageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        # Tamaño de página por defecto es 10 si no se especifica
        page_size = request.GET.get('page_size', 10)
        self.page_size = int(page_size)
        return super().paginate_queryset(queryset, request)

    def get_paginated_response(self, data):
        return Response({
            'users': data,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page_size,
            'total_users': self.page.paginator.count,
        })

class IndexView(APIView):
    def get(self, request):
        # Autenticación mediante JWT
        token = request.COOKIES.get('jwt')
        #token = request.headers.get('Authorization')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener todos los usuarios
        users = User.objects.all()

        # Filtro por user_type (0 o 1)
        user_type = request.GET.get('user_type')
        if user_type is not None:
            users = users.filter(user_type__id=user_type)

        # Filtro por estado (0 o 1)
        estado = request.GET.get('estado')
        if estado is not None:
            users = users.filter(estado=estado)

        # Filtro por búsqueda parcial (nombre, username, phone o id_personal)
        search_query = request.GET.get('search')
        if search_query:
            users = users.filter(
                Q(name__icontains=search_query) |
                Q(username__icontains=search_query) |
                Q(phone__icontains=search_query) |  # Para números como 88357378
                Q(id_personal__icontains=search_query)  # Para formatos como 281-250503-3425M
            )

        # Configurar paginación
        paginator = CustomPagination()
        paginated_users = paginator.paginate_queryset(users, request)

        # Serializar los usuarios paginados
        serializer = UserSerializer(paginated_users, many=True)

        # Devolver la respuesta paginada
        return paginator.get_paginated_response(serializer.data)


#Controlador de usuario logueado - user/empleados/profile/
class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')
        #token = request.headers.get('Authorization')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener el usuario correspondiente al id del payload
        user = User.objects.filter(id=payload['id']).first()

        # Verifica que el usuario existe
        if not user:
            raise AuthenticationFailed('User not found!')

        # Preparar la respuesta con la información requerida
        response_data = {
            'nombre': user.name,
            'username': user.username,
            'telefono': user.phone,
            'id_personal': user.id_personal,
            'user_type': user.user_type.description  # Obtener la descripción del tipo de usuario
        }

        return Response(response_data)
    
#Controlador de register - /api/user/empleado/create/
class RegisterView(APIView):
    def post(self, request):
        # Extraer el token JWT de la cookie
        token = request.COOKIES.get('jwt')
        #token = request.headers.get('Authorization')

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

        # Asignar el id del usuario actual como el que creó el registro
        data['created_user'] = current_user.id
        # Asignar null a update_user y deleted_user
        data['update_user'] = None
        data['deleted_user'] = None

        # Serializar los datos
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Devolver la respuesta con los datos creados
        return Response(serializer.data)

#Controlador de modificar - /api/user/empleado/update/
class UpdateUserView(APIView):
    def patch(self, request, encrypted_id):
        # Extraer el token JWT de la cookie para obtener el usuario logueado
        token = request.COOKIES.get('jwt')
        #token = request.headers.get('Authorization')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Decodificar el encrypted_id para obtener el ID real
        try:
            user_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception as e:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar el usuario por ID
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Obtener los datos a actualizar desde la solicitud
        name = request.data.get('name')
        id_personal = request.data.get('id_personal')
        phone = request.data.get('phone')
        username = request.data.get('username')
        user_type = request.data.get('user_type')

        # Actualizar solo los campos que se han pasado
        if name is not None:
            user.name = name
        if id_personal is not None:
            user.id_personal = id_personal
        if phone is not None:
            user.phone = phone
        if username is not None:
            user.username = username
        if user_type is not None:
            user.user_type = user_type

        # Guardar los cambios en la base de datos
        user.save()

        return Response({'message': 'User updated successfully.', 'user': user.id}, status=status.HTTP_200_OK)



#Controlador para modificar el estado  - /api/user/empleado/activate/ 
class UpdateUserStatusView(APIView):
    def patch(self, request, encrypted_id):
        token = request.COOKIES.get('jwt')
        #token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Decodificar el encrypted_id para obtener el id real
        decoded_id = base64.urlsafe_b64decode(encrypted_id).decode()

        # Buscar el usuario por ID
        try:
            user = User.objects.get(id=decoded_id)
        except User.DoesNotExist:
            raise NotFound('User not found!')

        # Cambiar el estado del usuario
        user.estado = 1 if user.estado == 0 else 0
        user.save()

        return Response({
            'message': 'User status updated successfully.',
            'encrypted_id': encrypted_id,
            'new_estado': user.estado
        }, status=status.HTTP_200_OK)

#Controlador para eliminar usuario - /api/user/empleado/delete/ 
class DeleteUserView(APIView):
    def delete(self, request, encrypted_id):
        # Extraer el token JWT de la cookie para obtener el usuario logueado
        token = request.COOKIES.get('jwt')
        #token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener el ID del usuario logueado que está eliminando
        logged_in_user = User.objects.get(id=payload['id'])

        # Decodificar el encrypted_id para obtener el ID real
        try:
            user_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception as e:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar el usuario por ID
            user_to_delete = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar los campos deleted_user y deleted_at
        user_to_delete.deleted_user = logged_in_user  # ID del usuario que está eliminando
        user_to_delete.deleted_at = timezone.now()  # Hora y fecha actuales

        # Guardar los cambios en la base de datos
        user_to_delete.save()

        return Response({'message': 'User marked as deleted successfully.'}, status=status.HTTP_200_OK)

#Controlador para cambiar password - user/empleado/changePassword/
class ChangePasswordView(APIView):
    def patch(self, request, encrypted_id):
        # Extraer el token JWT de la cookie para obtener el usuario logueado
        token = request.COOKIES.get('jwt')
        #token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Decodificar el encrypted_id para obtener el ID real
        try:
            user_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception as e:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar el usuario por ID
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Obtener la nueva contraseña desde el cuerpo de la solicitud
        password = request.data.get('password')

        if not password:
            return Response({'error': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Establecer la nueva contraseña
        user.set_password(password)
        user.save()

        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)

#Controlador de register - /api/user/cliente/create/
class RegisterClient(APIView):
    def post(self, request):
        # Extraer el token JWT de la cookie
        token = request.COOKIES.get('jwt')
        #token = request.headers.get('Authorization')
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

        # Asignar el id del usuario actual como el que creó el registro
        data['created_user'] = current_user.id
        # Asignar null a update_user y deleted_user
        data['update_user'] = None
        data['deleted_user'] = None

        # Serializar los datos
        serializer = ClienteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Devolver la respuesta con los datos creados
        return Response(serializer.data)

#Controlador de modificar - /api/user/cliente/update/
class UpdateClient(APIView):
    def patch(self, request, encrypted_id):
        # Extraer el token JWT de la cookie para obtener el usuario logueado
        token = request.COOKIES.get('jwt')
        #token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Decodificar el encrypted_id para obtener el ID real
        try:
            user_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception as e:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar el usuario por ID
            user = Cliente.objects.get(id=user_id)
        except Cliente.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Obtener los datos a actualizar desde la solicitud
        nombre = request.data.get('nombre')
        id_personal = request.data.get('id_personal')
        telefono = request.data.get('telefono')
        direccion = request.data.get('direccion')

        # Actualizar solo los campos que se han pasado
        if nombre is not None:
            user.nombre = nombre
        if id_personal is not None:
            user.id_personal = id_personal
        if telefono is not None:
            user.telefono = telefono
        if direccion is not None:
            user.direccion = direccion
            
        # Guardar los cambios en la base de datos
        user.save()

        return Response({'message': 'Cliente updated successfully.', 'user': user_id}, status=status.HTTP_200_OK)

#Controlador de index - user/cliente/index/
class IndexClientView(APIView):
    def get(self, request):
        # Autenticación mediante JWT
        token = request.COOKIES.get('jwt')
        #token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener todos los usuarios
        clientes = Cliente.objects.all()

        # Filtro por búsqueda parcial (nombre, telefono, id_personal)
        search_query = request.GET.get('search')
        if search_query:
            clientes = clientes.filter(
                Q(nombre__icontains=search_query) |
                Q(telefono__icontains=search_query) |  # Para números como 88357378
                Q(id_personal__icontains=search_query)  # Para formatos como 281-250503-3425M
            )

        # Configurar paginación
        paginator = CustomPagination()
        paginated_users = paginator.paginate_queryset(clientes, request)

        # Serializar los usuarios paginados
        serializer = ClienteSerializer(paginated_users, many=True)

        # Devolver la respuesta paginada
        return paginator.get_paginated_response(serializer.data)
    
#Controlador para eliminar usuario - /api/user/cliente/delete/ 
class DeleteClientView(APIView):
    def delete(self, request, encrypted_id):
        # Extraer el token JWT de la cookie para obtener el usuario logueado
        token = request.COOKIES.get('jwt')
        #token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener el ID del usuario logueado que está eliminando
        logged_in_user = User.objects.get(id=payload['id'])

        # Decodificar el encrypted_id para obtener el ID real
        try:
            user_id = base64.urlsafe_b64decode(encrypted_id).decode()
        except Exception as e:
            return Response({'error': 'Invalid encrypted ID.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar el usuario por ID
            user_to_delete = Cliente.objects.get(id=user_id)
        except Cliente.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar los campos deleted_user y deleted_at
        user_to_delete.deleted_user = logged_in_user  # ID del usuario que está eliminando
        user_to_delete.deleted_at = timezone.now()  # Hora y fecha actuales

        # Guardar los cambios en la base de datos
        user_to_delete.save()

        return Response({'message': 'User marked as deleted successfully.'}, status=status.HTTP_200_OK)
