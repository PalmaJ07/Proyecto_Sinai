from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.exceptions import NotFound,AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from .models import User
import jwt, datetime

# Create your views here.

"""class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)"""
    
#Register
class RegisterView(APIView):
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

#Login
# class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('Username not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.now(datetime.UTC)
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response

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
        response.set_cookie(key='jwt', value=token, httponly=True)

        # Incluir el token JWT en la respuesta
        response.data = {
            'jwt': token
        }

        return response
    
# class UserView(APIView):

#     def get(self, request):
#         token = request.COOKIES.get('jwt')

#         if not token:
#             raise AuthenticationFailed('Unauthenticated!')

#         try:
#             payload = jwt.decode(token, 'secret', algorithms=['HS256'])
#         except jwt.ExpiredSignatureError:
#             raise AuthenticationFailed('Unauthenticated!')
#         except jwt.DecodeError:
#             raise AuthenticationFailed('Invalid token!')

#         user = User.objects.filter(id=payload['id']).first()

#         serializer = UserSerializer(user)
#         return Response(serializer.data)

#UserView
class UserView(APIView):

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
    
class UserPagination(PageNumberPagination):
    page_size = 5  # Valor por defecto
    page_size_query_param = 'page_size'  # Permite definir el tamaño de página a través de la URL
    max_page_size = 100  # Tamaño máximo que se puede solicitar

class UserListView(APIView):
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

        # Obtener todos los usuarios
        users = User.objects.all()

        # Obtener el tamaño de página desde los parámetros de consulta, o usar el valor por defecto
        page_size = request.GET.get('page_size', 5)
        paginator = UserPagination()
        paginator.page_size = int(page_size)  # Convertir a entero

        page = request.GET.get('page')  # Obtener el número de página
        paginated_users = paginator.paginate_queryset(users, request)

        # Serializar los usuarios
        serializer = UserSerializer(paginated_users, many=True)

        # Devolver la respuesta paginada
        return paginator.get_paginated_response(serializer.data)

class UserFilterView(APIView):
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

        # Obtener todos los usuarios
        users = User.objects.all()

        # Filtrar por estado si se proporciona en la consulta
        estado = request.GET.get('estado')
        if estado is not None:
            # Convertir a entero
            estado = int(estado)  # Se espera que sea 1 o 0
            users = users.filter(estado=estado)

        # Configurar paginación
        paginator = UserPagination()
        paginated_users = paginator.paginate_queryset(users, request)

        # Serializar los usuarios
        serializer = UserSerializer(paginated_users, many=True)

        # Devolver la respuesta paginada
        return paginator.get_paginated_response(serializer.data)

class UserTypeFilterView(APIView):
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

        # Obtener el tipo de usuario desde los parámetros de consulta (GET)
        user_type = request.GET.get('user_type')

        if not user_type:
            return Response({'error': 'user_type parameter is required'}, status=400)

        # Filtrar usuarios por `user_type`
        users = User.objects.filter(user_type__id=user_type)

        # Configurar paginación
        paginator = PageNumberPagination()
        paginator.page_size = request.GET.get('page_size', 5)  # Tamaño de página por defecto: 5

        # Paginación de los usuarios filtrados
        paginated_users = paginator.paginate_queryset(users, request)

        # Serializar los usuarios paginados
        serializer = UserSerializer(paginated_users, many=True)

        # Devolver la respuesta paginada
        return paginator.get_paginated_response(serializer.data)

class UpdateUserStatusView(APIView):
    def patch(self, request, user_id):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Buscar el usuario por ID
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound('User not found!')

        # Obtener el nuevo estado del request
        new_status = request.data.get('estado')

        # Validar que el nuevo estado sea 0 o 1
        if new_status is not None and new_status in [0, 1]:
            user.estado = new_status
            user.save()
            return Response({
                'message': 'User status updated successfully.',
                'user_id': user.id,
                'new_estado': user.estado
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid status value. Use 0 for Inactive or 1 for Active.'
            }, status=status.HTTP_400_BAD_REQUEST)

class DeleteUserView(APIView):
    def delete(self, request):
        # Extraer el token JWT de la cookie para obtener el usuario logueado
        token = request.COOKIES.get('jwt')

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

        # Obtener el ID del usuario que se va a eliminar desde el cuerpo de la solicitud
        user_id = request.data.get('id')

        if not user_id:
            return Response({'error': 'ID is required.'}, status=400)

        try:
            # Buscar el usuario por ID
            user_to_delete = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        # Actualizar los campos deleted_user y deleted_at
        user_to_delete.deleted_user = logged_in_user  # ID del usuario que está eliminando
        user_to_delete.deleted_at = timezone.now()  # Hora y fecha actuales

        # Guardar los cambios en la base de datos
        user_to_delete.save()

        return Response({'message': 'User marked as deleted successfully.'})

class DeleteUserView(APIView):
    def delete(self, request):
        # Extraer el token JWT de la cookie para obtener el usuario logueado
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            # Decodificar el token para obtener el payload
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        # Obtener el usuario logueado que realiza la acción de eliminación
        logged_in_user = User.objects.get(id=payload['id'])

        # Obtener el ID del usuario que se va a eliminar desde el cuerpo de la solicitud
        user_id = request.data.get('id')

        if not user_id:
            return Response({'error': 'User ID is required.'}, status=400)

        try:
            # Buscar el usuario por ID
            user_to_delete = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        # Actualizar los campos deleted_user y deleted_at
        user_to_delete.deleted_user = logged_in_user  # ID del usuario que está eliminando
        user_to_delete.deleted_at = datetime.datetime.now()  # Fecha y hora actuales

        # Guardar los cambios en la base de datos
        user_to_delete.save()

        return Response({'message': 'User marked as deleted successfully.'})

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response

