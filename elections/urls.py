from django.urls import path 
from . import views



urlpatterns = [
    path('elections/',              views.ElectionListCreateView.as_view(),    name='election-list-create'),
    path('elections/active/',       views.ActiveElectionListView.as_view(),    name='election-active'),
    path('elections/<int:pk>/',     views.ElectionDetailView.as_view(),        name='election-detail'),
    path('elections/<int:pk>/status/',      views.ElectionStatusUpdateView.as_view(), name='election-status'),
    path('elections/<int:pk>/summary/',     views.ElectionSummaryView.as_view(),      name='election-summary'),
]