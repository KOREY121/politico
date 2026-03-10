from django.urls import path
from . import views


urlpatterns = [
    path('votes/cast/', views.CastVoteView.as_view(), name='vote-cast'),
    path('votes/receipt/<int:pk>/', views.VoteReceiptView.as_view(), name='vote-receipt'),
    path('votes/results/<int:election_id>/', views.ElectionResultsView.as_view(), name='election-results'),
    path('votes/log/', views.VoteAuditLogView.as_view(), name='vote-audit-log'),
    path('votes/has-voted/<int:election_id>/', views.HasVotedView.as_view(), name='has-voted'),
    path('votes/results/<int:election_id>/constituency/<int:constituency_id>/', views.ConstituencyResultsView.as_view(), name='constituency-results'),
    path('votes/my-history/', views.VoterHistoryView.as_view(), name='voter-history'),
]