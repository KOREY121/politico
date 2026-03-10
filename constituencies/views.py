from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.views import APIView 
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from rest_framework.response import Response
from .models import Constituency
from .serializers import ConstituencySerializer,ConstituencyDetailSerializer



class ConstituencyListCreateView(generics.ListCreateAPIView):


    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ConstituencySerializer
        return ConstituencySerializer

    def get_queryset(self):
        queryset = Constituency.objects.all()
        region   = self.request.query_params.get('region')
        search   = self.request.query_params.get('search')

        if region:
            queryset = queryset.filter(region__icontains=region)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = ConstituencySerializer(data=request.data)
        if serializer.is_valid():
            constituency = serializer.save()
            return Response({
                'message':      'Constituency created successfully.',
                'constituency': ConstituencySerializer(constituency).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class ConstituencyDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Constituency.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ConstituencyDetailSerializer
        return ConstituencySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def update(self, request, *args, **kwargs):
        partial      = kwargs.pop('partial', False)
        constituency = self.get_object()
        serializer   = ConstituencySerializer(
            constituency,
            data=request.data,
            partial=partial
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message':      'Constituency updated successfully.',
                'constituency': serializer.data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        constituency = self.get_object()

        # Prevent deleting a constituency that has candidates assigned
        if constituency.total_candidates > 0:
            return Response(
                {
                    'error': (
                        f'Cannot delete {constituency.name}. '
                        f'It has {constituency.total_candidates} candidate(s) assigned. '
                        f'Remove or reassign them first.')
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        constituency.delete()
        return Response(
            {'message': f'{constituency.name} has been deleted.'},
            status=status.HTTP_200_OK
        )
    

class ConstituencyByRegionView(generics.ListAPIView):

    serializer_class   = ConstituencySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        region = self.kwargs.get('region')
        return Constituency.objects.filter(region__icontains=region)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {'message': f"No constituencies found in region '{self.kwargs.get('region')}'."},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'region': self.kwargs.get('region'),
            'count':  queryset.count(),
            'constituencies': serializer.data,
        }, status=status.HTTP_200_OK)