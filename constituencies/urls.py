from django.urls import path
from . import views


urlpatterns = [
    path('constituencies/',             views.ConstituencyListCreateView.as_view(),  name='constituency-list-create'),
    path('constituencies/<int:pk>/',    views.ConstituencyDetailView.as_view(),      name='constituency-detail'),
    path('constituencies/region/<str:region>/',     views.ConstituencyByRegionView.as_view(),    name='constituency-by-region'),
]