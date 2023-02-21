from django.urls import path

from .views import *

urlpatterns = [
    path('early-access', earlyAccessUserView, name='early-access'),
    path('signup', SignupView.as_view(), name='signup'),
    path('signin', signinView, name='signin'),
    path('signout', signoutView, name='signout'),
    path('profile', UserView.as_view(), name='profile'),
    path('profile-picture', ProfilePictureView.as_view(), name='profile-picture'),
    path('change-password', change_password_view),
    path('portfolio', PortfoliosView.as_view())
]
