from rest_framework import serializers
from .models import Candidate

class CandidateSerializer(serializers.ModelSerializer):
    total_votes = serializers.ReadOnlyField()
    election_status = serializers.CharField(source='election.status', read_only=True)
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)
    constituency_region = serializers.CharField(source='constituency.region', read_only=True)

    class Meta:
        model = Candidate
        fields = ['candidate_id', 'full_name', 'party','election', 'election_status','constituency', 'constituency_name', 'constituency_region','total_votes', 'created_at', 'updated_at',]

        read_only_fields =['candidate_id', 'created_at', 'updated_at']


class CandidateCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = ['full_name', 'party', 'election', 'constituency']

    def validate_election(self, value):
        if value.status == 'closed':
            raise serializers.ValidationError(
                'Cannot add a candidate to a closed election.'
            )
        return value

    def validate(self, data):
        # Check if a candidate is registered twice in same election
        full_name = data.get('full_name')
        election  = data.get('election')

        if Candidate.objects.filter(
            full_name__iexact=full_name,
            election=election
        ).exists():
            raise serializers.ValidationError({
                'full_name': f'{full_name} is already registered in this election.'
            })
        return data
    

class CandidateDetailSerializer(serializers.ModelSerializer):

    total_votes = serializers.ReadOnlyField()

    election = serializers.SerializerMethodField()
    constituency = serializers.SerializerMethodField()

    class Meta:
        model  = Candidate
        fields = [
            'candidate_id', 'full_name', 'party',
            'election', 'constituency',
            'total_votes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['candidate_id', 'created_at', 'updated_at']

    def get_election(self, obj):
        return {
            'election_id': obj.election.election_id,
            'start_date': obj.election.start_date,
            'end_date': obj.election.end_date,
            'status': obj.election.status,
        }

    def get_constituency(self, obj):
        return {
            'constituency_id':obj.constituency.constituency_id,
            'name': obj.constituency.name,
            'region': obj.constituency.region,
            }
    

class CandidateResultSerializer(serializers.ModelSerializer):
    
    total_votes  = serializers.ReadOnlyField()
    percentage   = serializers.SerializerMethodField()
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)

    class Meta:
        model  = Candidate
        fields = ['candidate_id', 'full_name', 'party','constituency_name', 'total_votes', 'percentage',]

    def get_percentage(self, obj):
        total_election_votes = self.context.get('total_election_votes', 0)
        if not total_election_votes:
            return 0.0
        return round((obj.total_votes / total_election_votes) * 100, 2)