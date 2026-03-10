from rest_framework import serializers
from .models import Vote

class VoteCastSerializer(serializers.Serializer):
    election_id  = serializers.IntegerField()
    candidate_id = serializers.IntegerField()

    def validate(self, data):
        from elections.models  import Election
        from candidates.models import Candidate

        election_id  = data.get('election_id')
        candidate_id = data.get('candidate_id')
        voter        = self.context['request'].user

        # Election must exist
        try:
            election = Election.objects.get(pk=election_id)
        except Election.DoesNotExist:
            raise serializers.ValidationError({
                'election_id': 'Election not found.'
            })

        # Election must be active
        if election.status != 'active':
            raise serializers.ValidationError({
                'election_id': f"This election is '{election.status}' and is not accepting votes."
            })
        
         # Candidate must exist 
        try:
            candidate = Candidate.objects.get(pk=candidate_id)
        except Candidate.DoesNotExist:
            raise serializers.ValidationError({
                'candidate_id': 'Candidate not found.'
            })

        # Candidate must belong to this election 
        if candidate.election_id != election.election_id:
            raise serializers.ValidationError({
                'candidate_id': 'This candidate is not registered in the specified election.'
            })

        # Voter must not have already voted in this election
        if Vote.objects.filter(voter=voter, election=election).exists():
            raise serializers.ValidationError(
                'You have already cast your vote in this election.'
            )

        # Attach objects so we don't re-query in the view
        data['election']  = election
        data['candidate'] = candidate
        data['voter']     = voter

        return data
    

class VoteReceiptSerializer(serializers.ModelSerializer):

    receipt_id        = serializers.SerializerMethodField()
    candidate_name    = serializers.CharField(source='candidate.full_name',         read_only=True)
    candidate_party   = serializers.CharField(source='candidate.party',             read_only=True)
    constituency_name = serializers.CharField(source='candidate.constituency.name', read_only=True)
    election_id       = serializers.IntegerField(source='election.election_id',     read_only=True)
    voter_name        = serializers.CharField(source='voter.full_name',             read_only=True)
    voter_national_id = serializers.CharField(source='voter.national_id',           read_only=True)

    class Meta:
        model  = Vote
        fields = [
            'receipt_id', 'voter_name', 'voter_national_id',
            'election_id', 'candidate_name', 'candidate_party',
            'constituency_name', 'time',
        ]

    def get_receipt_id(self, obj):
        # Format vote ID as a padded receipt number
        return f"VT-{str(obj.vote_id).zfill(6)}"
    


class VoteAuditSerializer(serializers.ModelSerializer):
#this should be for admin only
    receipt_id        = serializers.SerializerMethodField()
    voter_name        = serializers.CharField(source='voter.full_name',             read_only=True)
    voter_national_id = serializers.CharField(source='voter.national_id',           read_only=True)
    candidate_name    = serializers.CharField(source='candidate.full_name',         read_only=True)
    candidate_party   = serializers.CharField(source='candidate.party',             read_only=True)
    constituency_name = serializers.CharField(source='candidate.constituency.name', read_only=True)
    election_id       = serializers.IntegerField(source='election.election_id',     read_only=True)
    election_status   = serializers.CharField(source='election.status',             read_only=True)

    class Meta:
        model  = Vote
        fields = [
            'receipt_id', 'vote_id',
            'voter_name', 'voter_national_id',
            'election_id', 'election_status',
            'candidate_name', 'candidate_party',
            'constituency_name', 'time',
        ]

    def get_receipt_id(self, obj):
        return f"VT-{str(obj.vote_id).zfill(6)}"


class ElectionResultSerializer(serializers.Serializer):
# should return aggregated results for an election.

    election_id      = serializers.IntegerField()
    election_status  = serializers.CharField()
    start_date       = serializers.DateField()
    end_date         = serializers.DateField()
    total_votes      = serializers.IntegerField()
    total_candidates = serializers.IntegerField()
    winner           = serializers.SerializerMethodField()
    results          = serializers.ListField()

    def get_winner(self, obj):
        results = obj.get('results', [])
        if not results or obj.get('total_votes', 0) == 0:
            return None
        # First result is the winner (sorted by vote_count descending)
        top = results[0]
        return {
            'candidate_id':   top['candidate_id'],
            'full_name':      top['full_name'],
            'party':          top['party'],
            'total_votes':    top['vote_count'],
            'percentage':     top['percentage'],
        }
