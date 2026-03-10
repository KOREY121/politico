from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
     path('register/',       views.VoterRegisterView.as_view(),  name='voter-register'),
    path('login/',          views.VoterLoginView.as_view(),     name='voter-login'),
    path('logout/',         views.VoterLogoutView.as_view(),    name='voter-logout'),
    path('token/refresh/',  TokenRefreshView.as_view(),         name='token-refresh'),
    path('profile/',        views.VoterProfileView.as_view(),   name='voter-profile'),
]