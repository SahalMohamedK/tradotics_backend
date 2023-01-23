from django.urls import path

from .views import *

urlpatterns = [
    path('early-access', earlyAccessUserView, name='early-access'),
    path('signup', SignupView.as_view(), name='signup'),
    path('signin', signinView, name='signin'),
    path('signout', signoutView, name='signout'),
    path('profile', ProfileView.as_view(), name='profile'),
]
