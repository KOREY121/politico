from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny

from .models import Candidate
from .serializers import CandidateSerializer,CandidateCreateSerializer,CandidateDetailSerializer,CandidateResultSerializer


class CandidateListCreateView(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CandidateCreateSerializer
        return CandidateSerializer

    def get_queryset(self):
        queryset = Candidate.objects.select_related('election', 'constituency').all()
        election_id = self.request.query_params.get('election')
        const_id = self.request.query_params.get('constituency')
        party = self.request.query_params.get('party')

        if election_id:
            queryset = queryset.filter(election__election_id=election_id)
        if const_id:
            queryset = queryset.filter(constituency__constituency_id=const_id)
        if party:
            queryset = queryset.filter(party__icontains=party)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = CandidateCreateSerializer(data=request.data)
        if serializer.is_valid():
            candidate = serializer.save()
            return Response({
                'message': 'candidate registered successfully.',
                'candidate': CandidateSerializer(candidate).data,
            }, status= status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    

class CandidateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.select_related('election', 'constituency').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CandidateDetailSerializer
        return CandidateCreateSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        candidate = self.get_object()
        serializer = CandidateCreateSerializer(
            candidate,
            data=request.data,
            partial=partial
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Candidate updated successfully.',
                'candidate': CandidateDetailSerializer(candidate).data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        candidate = self.get_object()

        # This will prevent removing a candidate from an active election that has votes
        if candidate.election.status == 'active' and candidate.total_votes > 0:
            return Response(
                {'error': 'Cannot remove a candidate who has already received votes.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        candidate.delete()
        return Response(
            {'message': f'{candidate.full_name} has been removed from Election #{candidate.election_id}.'},
            status=status.HTTP_200_OK
        )
    


class CandidatesByElectionView(generics.ListAPIView):
   
    serializer_class = CandidateSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        election_id = self.kwargs.get('election_id')
        constituency = self.request.query_params.get('constituency')

        queryset = Candidate.objects.select_related('election', 'constituency').filter(election__election_id=election_id)

        if constituency:
            queryset = queryset.filter(constituency__constituency_id=constituency)

        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {'message': 'No candidates found for this election.'},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'election_id': self.kwargs.get('election_id'),
            'count': queryset.count(),
            'candidates': serializer.data,
        }, status=status.HTTP_200_OK)
        


