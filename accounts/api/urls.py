from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import (CustomRegisterView,
                    UserLoginView,
                    UserLogoutView, ACMMemberRegisterView, GuestView, form_pass,
                    CheckEmail,
                    )

urlpatterns = [
     path('register/user/', CustomRegisterView.as_view(),name='register_user'),  # don't create user from admin
     path('pass/<guest_id>/<randomstring>/', form_pass,name='set_password'),  # verification link
     path('login/', UserLoginView.as_view(),name='member_login'),  # generate token
     path('logout/', UserLogoutView.as_view(), name='user_logout'),
     path('registration/', ACMMemberRegisterView.as_view(),name='add'),  # acm registation endpoint
     path('guest/', GuestView.as_view(), name='guest_view'),
     path('check/', CheckEmail.as_view()),  # check email endpoint
]
