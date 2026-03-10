from django.urls import path
from . import views


urlpatterns = [
    path('candidates/',             views.CandidateListCreateView.as_view(),   name='candidate-list-create'),
    path('candidates/<int:pk>/',    views.CandidateDetailView.as_view(),       name='candidate-detail'),
    path('elections/<int:election_id>/candidates/',         views.CandidatesByElectionView.as_view(),   name='candidates-by-election'),

]