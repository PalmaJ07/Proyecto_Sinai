from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserView.as_view(), name='user'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/filter/', UserFilterView.as_view(), name='user-filter'),
    path('users/filtertype/', UserTypeFilterView.as_view(), name='user-type-filter'),
    path('users/update/status/<int:user_id>/', UpdateUserStatusView.as_view(), name='update-user-status'),
    path('users/delete/', DeleteUserView.as_view(), name='user-delete'),

]

"""
user/empleados/index/
user/empleados/profile/
user/empleados/create/
user/empleados/edit/
user/empleados/update/ 
user/empleados/delete/
user/empleados/activate/
user/empleados/changePassword/
"""