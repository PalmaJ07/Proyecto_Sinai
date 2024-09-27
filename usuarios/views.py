from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.exceptions import AuthenticationFailed
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

class LoginView(APIView):
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
     
    
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response

