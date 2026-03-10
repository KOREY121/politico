from rest_framework import serializers
from .models import Constituency




class ConstituencySerializer(serializers.ModelSerializer):
    total_candidates = serializers.ReadOnlyField()

    class Meta:
        model  = Constituency
        fields = ['constituency_id', 'name', 'region', 'total_candidates', 'created_at', 'updated_at',]
        read_only_fields = ['constituency_id', 'created_at', 'updated_at']

    def validate_name(self, value):
        # Case-insensitive duplicate check
        instance = self.instance
        qs = Constituency.objects.filter(name__iexact=value)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError(f"A constituency named '{value}' already exists.")
        return value
    

class ConstituencyDetailSerializer(serializers.ModelSerializer):
    # includes all candidates nested under this constituency.
    
    total_candidates = serializers.ReadOnlyField()
    candidates       = serializers.SerializerMethodField()

    class Meta:
        model  = Constituency
        fields = ['constituency_id', 'name', 'region', 'total_candidates', 'candidates','created_at', 'updated_at',]
        read_only_fields = ['constituency_id', 'created_at', 'updated_at']

    def get_candidates(self, obj):
        from candidates.serializers import CandidateSerializer
        candidates = obj.candidates.select_related('election').all()
        return CandidateSerializer(candidates, many=True).data
    

class ConstituencySimpleSerializer(serializers.ModelSerializer):
   
    class Meta:
        model  = Constituency
        fields = ['constituency_id', 'name', 'region']