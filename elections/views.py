from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny

from .models import Election
from .serializers import ElectionSerializer, ElectionDetailSerializer, ElectionStatusSerializer


class ElectionListCreateView(generics.ListCreateAPIView):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny]
    
    def get_queryset(self):
        queryset = Election.objects.all()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset
    
    def create(self,request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            election = serializer.save()
            return Response({
                'message': 'Election created successfully.',
                'elections' : ElectionSerializer(election).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    

class ElectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Election.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ElectionDetailSerializer
        return ElectionSerializer
    
    def get_permisions(self):
        if self.request.method == 'GET':
            return [ AllowAny]
        return [IsAuthenticated(), IsAdminUser()]
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        election = self.get_object()
        serializer = self.get_serializer(election, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Election updated successfully.',
                'election' : serializer.data,
            }, status = status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        election = self.get_object()
        if election.status == 'active':
            return Response(
                {'error': ' delete an active election. Close it first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        election.delete()
        return Response(
            {'message': f'Election #{election.election_id} has been deleted.'},
            status = status.HTTP_201_CREATED
        )
    

class ActiveElectionListView(generics.ListAPIView):
    serializer_class = ElectionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Election.objects.filter(status='active')
    

class ElectionStatusUpdateView(APIView):
    permission_classes =[IsAuthenticated, IsAdminUser]

    def patch(self, request, pk):
        try:
            election = Election.objects.get(pk=pk)
        except Election.DoesNotExist:
            return Response(
                {'error': 'Election not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ElectionStatusSerializer(
            election,data= request.data,partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': f'Election status updated to {election.status}.',
                'election': ElectionSerializer(election).data,
            },status = status.HTTP_200_OK)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
    
class ElectionSummaryView(APIView):
    permission_classes = [AllowAny]

    def get(self,request,pk):
        try:
            election = Election.objects.get(pk=pk)
        except Election.DoesNotExist:
            return Response(
                {'error': 'Election not found.'},
                status = status.HTTP_404_NOT_FOUND
            )
        return Response({
            'election_id': election.election_id,
            'status': election.status,
            'start_date': election.start_date,
            'end_date': election.end_date,
            'total_votes': election.total_votes,
            'total_candidates': election.total_candidates,
        }, status=status.HTTP_200_OK)
