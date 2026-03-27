from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Voter
from .serializers import AdminRegisterSerializer, VoterRegisterSerializer,VoterLoginSerializer,VoterProfileSerializer,VoterAdminSerializer,ChangePasswordSerializer

def get_tokens_for_voter(voter):
    refresh = RefreshToken.for_user(voter)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


class AdminRegisterView(APIView):

    #Requires an existing admin token to create new admins. Only admins can create other admins.

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)
        if serializer.is_valid():
            admin    = serializer.save()
            tokens   = get_tokens_for_voter(admin)
            return Response({
                'message': 'Admin registered successfully.',
                'admin':   VoterProfileSerializer(admin).data,
                'tokens':  tokens,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VoterRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = VoterRegisterSerializer(data=request.data)
        if serializer.is_valid():
            voter = serializer.save()
            tokens =get_tokens_for_voter(voter)
            return Response({
                'message': 'Registration successful.',
                'voter': VoterProfileSerializer(voter).data,
                'tokens': tokens,
            }, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VoterLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = VoterLoginSerializer(data=request.data)
        if serializer.is_valid():
            voter = serializer.validated_data['voter']
            tokens = get_tokens_for_voter(voter)
            return Response({
                'message':'Login Successful',
                'voter': VoterLoginSerializer(voter).data,
                'tokens': tokens,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VoterLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required.'},
                    status= status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Logged out successfully.'},
                status = status.HTTP_205_RESET_CONTENT
            )
        except Exception:
            return Response(
                {'error': 'Invalid or expired token.'},
                status = status.HTTP_400_BAD_REQUEST
            )
        
class VoterProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = VoterProfileSerializer(request.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        serializer = VoterProfileSerializer(
            request.user,
            data=request.data,
            partial = True
        )
        if serializer.is_valid():
            serializer.dave()
            return Response({
                'message': 'Profile Updated',
                'voter': serializer.data,
            }, status= status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data = request.data,
            context = {'request': request}
        )
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response(
                {'message': 'Password changed successfully, Please log in again.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VoterListView(generics.ListAPIView):
    #this is for admin only - list all voters
    queryset = Voter.objects.all()
    serializer_class = VoterAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    
    def get_queryset(self):
        self.queryset = Voter.objects.all()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            return queryset
        

class VoterDetailView(generics.RetrieveUpdateDestroyAPIView):
    #admin - retireve, update or deactivate a user

    queryset = Voter.objects.all()
    serializer_class = VoterAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        voter = self.get_object()
        voter.status = 'inactive'
        voter.save()
        return Rwsponse(
            {'message': f'{voter.full_name} has been deactivated'},
            status = status.HTTP_200_OK
        )
    