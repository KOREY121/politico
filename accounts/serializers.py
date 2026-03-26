from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Voter


class AdminRegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, label='Confirm Password')

    class Meta:
        model  = Voter
        fields = [
            'national_id', 'full_name', 'email',
            'dob', 'password', 'password2'
        ]

    def validate_national_id(self, value):
        
        if not value.startswith('ADMIN-'):
            raise serializers.ValidationError(
                'Admin ID must start with ADMIN- (e.g. ADMIN-001)'
            )
        if Voter.objects.filter(national_id=value).exists():
            raise serializers.ValidationError('This Admin ID is already registered.')
        return value

    def validate_email(self, value):
        if Voter.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already in use.')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        voter = Voter.objects.create_user(
            national_id = validated_data['national_id'],
            full_name   = validated_data['full_name'],
            email       = validated_data['email'],
            dob         = validated_data['dob'],
            password    = password,
        )
        # Automatically set admin flags
        voter.is_staff     = True
        voter.is_superuser = False  #just staff
        voter.save()
        return voter

class VoterRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, min_length = 6)
    password2 = serializers.CharField(write_only = True, label = 'confirm Password')

    
    class Meta:
        model = Voter
        fields = [ 'national_id', 'full_name', 'email', 'dob', 'password', 'password2']

    def validate_national_id(self, value):
        if Voter.objects.filter(national_id=value).exists():
            raise serializers.ValidationError('This NIN is already registered.')
        return value
    
    def validate_email(self, value):
        if Voter.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email i salready in use.')
        return value
        
    def validate(self, data):
        if data['password'] !=data['password2']:
            raise serializers.ValidationError({'password2':'passwords do not match'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        voter = Voter.objects.create_user(
            national_id = validated_data['national_id'],
            full_name   = validated_data['full_name'],
            email       = validated_data['email'],
            dob         = validated_data['dob'],
            password    = password,
        )
        return voter
    

class VoterLoginSerializer(serializers.Serializer):
    national_id = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        national_id = data.get('national_id')
        password = data.get('password')

        # Try national_id first, then email
        from django.contrib.auth import authenticate
        voter = authenticate(username=national_id, password=password)

        if not voter:
            # Try finding by email
            from .models import Voter
            try:
                voter_obj = Voter.objects.get(email=national_id)
                voter = authenticate(username=voter_obj.national_id, password=password)
            except Voter.DoesNotExist:
                pass

        if not voter:
            raise serializers.ValidationError('Invalid credentials.')
        if voter.status != 'active':
            raise serializers.ValidationError('Your account is inactive.')

        data['voter'] = voter
        return data    

class VoterProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Voter
        fields = ['voter_id', 'national_id', 'full_name', 'email','dob', 'status', 'date_joined' ]
        read_only_fields = ['voter_id', 'national_id', 'status','date_joined']


class VoterAdminSerializer(serializers.ModelSerializer):
    #used by admin to list and manage all voters ----  Remember to make the models admin so i dont firget 
    votes_cast = serializers.SerializerMethodField()

    class Meta:
        fields = ['voter_id', 'national_id', 'full_name', 'email', 'dob', 'status', 'is_admin', 'date_joined', 'votes_cast']
        read_only_fields = ['voter_id', 'national_id', 'date_joined']

    def get_votes_cast(self,obj):
        return obj.votes.count()
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only = True)
    new_password = serializers.CharField(write_only = True, min_length = 6)
    new_password2 = serializers.CharField(write_only = True, label = 'Confirm New Password')

    def validate(self,data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': 'New Passwords do not match'})
        return data
    
    def validate_old_password(self,value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
    

