from rest_framework import serializers
from .models import Election
from candidates.serializers import CandidateSerializer



class ElectionSerializer(serializers.ModelSerializer):

    total_votes = serializers.ReadOnlyField()
    total_candidates = serializers.ReadOnlyField()

    class Meta:
        model = Election
        fields = [
            'election_id', 'start_date', 'end_date', 'status', 'total_votes', 'total_candidates', 'created_at', 'updated_at']
        
        read_only_fields = ['electiom_id', 'created_at', 'updated_at']

    
    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date') 
        if start and end and end <= start:
            raise serializers. ValidationError(
                {'end_date': 'End date must be after start date'})
        return data
    

class ElectionDetailSerializer(serializers.ModelSerializer):

    candidates = CandidateSerializer(many=True, read_only=True)
    total_votes = serializers.ReadOnlyField()
    total_candidates = serializers.ReadOnlyField()


    class Meta:
        model = Election
        fields = ['election_id', 'start_date', 'end_date', 'status', 'total_votes', 'total_candidates', 'candidates', 'created_at', 'updated_at']
        read_only_fields = ['election_id', 'created_at', 'updated_at']



class ElectionStatusSerializer(serializers.ModelSerializer):
    #let this be for updating election status only

    class Meta:
        model = Election
        fields = ['status']

    def validate_status(self,value):
        instance = self.instance

        transitions = {
            'pending' : ['active'],
            'active' : ['closed'],
            'closed' : [],
        }

        if instance and value not in transitions[instance.status]:
            raise serializers.ValidationError(
                f"Cannot transition from '{instance.status}' to '{value}'."
                f"Allowed transitions: {transitions[instance.status] or 'none'}"
            )
        return value
