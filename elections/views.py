from rest_framework                 import generics
from rest_framework                 import status as http_status  # ← renamed to avoid conflict
from rest_framework.views           import APIView
from rest_framework.response        import Response
from rest_framework.permissions     import IsAuthenticated, IsAdminUser, AllowAny

from .models       import Election
from .serializers  import ElectionSerializer, ElectionDetailSerializer, ElectionStatusSerializer


class ElectionListCreateView(generics.ListCreateAPIView):
    queryset         = Election.objects.all()
    serializer_class = ElectionSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]   # ← fixed parentheses

    def get_queryset(self):
        queryset       = Election.objects.all()
        election_status = self.request.query_params.get('status')  # ← renamed variable
        if election_status:
            queryset = queryset.filter(status=election_status)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            election = serializer.save()
            return Response({
                'message':  'Election created successfully.',
                'election': ElectionSerializer(election).data,
            }, status=http_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)


class ElectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Election.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ElectionDetailSerializer
        return ElectionSerializer

    def get_permissions(self):   # ← fixed typo (was get_permisions)
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def update(self, request, *args, **kwargs):
        partial    = kwargs.pop('partial', False)
        election   = self.get_object()
        serializer = self.get_serializer(election, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message':  'Election updated successfully.',
                'election': serializer.data,
            }, status=http_status.HTTP_200_OK)
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        election = self.get_object()
        if election.status == 'active':
            return Response(
                {'error': 'Cannot delete an active election. Close it first.'},
                status=http_status.HTTP_400_BAD_REQUEST
            )
        election.delete()
        return Response(
            {'message': f'Election #{election.election_id} has been deleted.'},
            status=http_status.HTTP_200_OK  # ← fixed from 201 to 200
        )


class ActiveElectionListView(generics.ListAPIView):
    serializer_class   = ElectionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Election.objects.filter(status='active')


class ElectionStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, pk):
        try:
            election = Election.objects.get(pk=pk)
        except Election.DoesNotExist:
            return Response(
                {'error': 'Election not found.'},
                status=http_status.HTTP_404_NOT_FOUND
            )
        serializer = ElectionStatusSerializer(election, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message':  f'Election status updated to {election.status}.',
                'election': ElectionSerializer(election).data,
            }, status=http_status.HTTP_200_OK)
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)


class ElectionSummaryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            election = Election.objects.get(pk=pk)
        except Election.DoesNotExist:
            return Response(
                {'error': 'Election not found.'},
                status=http_status.HTTP_404_NOT_FOUND
            )
        return Response({
            'election_id':    election.election_id,
            'status':         election.status,
            'start_date':     election.start_date,
            'end_date':       election.end_date,
            'total_votes':    election.total_votes,
            'total_candidates': election.total_candidates,
        }, status=http_status.HTTP_200_OK)