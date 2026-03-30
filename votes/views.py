from django.shortcuts import render
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny

from .models import Vote
from . serializers import VoteCastSerializer, VoteAuditSerializer, VoteReceiptSerializer
from elections.models import Election
from candidates.models import Candidate


class CastVoteView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        # the voter must be active
        if request.user.status != 'active':
            return Response(
                {'error': 'Your account is inactive. Contact the administrator.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = VoteCastSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                election  = serializer.validated_data['election']
                candidate = serializer.validated_data['candidate']
                voter     = serializer.validated_data['voter']

                Vote.objects.select_for_update().filter(
                    voter=voter,
                    election=election
                )

                # Final integrity check inside the transaction
                if Vote.objects.filter(voter=voter, election=election).exists():
                    return Response(
                        {'error': 'You have already cast your vote in this election.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                vote = Vote.objects.create(
                    voter     = voter,
                    candidate = candidate,
                    election  = election,
                )
            return Response({
                'message': 'Your vote has been cast successfully.',
                'receipt': VoteReceiptSerializer(vote).data,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class VoteReceiptView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            vote = Vote.objects.select_related(
                'voter', 'candidate', 'candidate__constituency', 'election'
            ).get(pk=pk)
        except Vote.DoesNotExist:
            return Response(
                {'error': 'Vote receipt not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Voter can only see their own receipt
        if vote.voter != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to view this receipt.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(
            VoteReceiptSerializer(vote).data,
            status=status.HTTP_200_OK
        )
    

class HasVotedView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, election_id):
        election = get_object_or_404(Election, pk=election_id)

        has_voted = Vote.objects.filter(
            voter    = request.user,
            election = election
        ).exists()

        return Response({
            'election_id': election_id,
            'has_voted':   has_voted,
        }, status=status.HTTP_200_OK)
    

class ElectionResultsView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, election_id):
        election = get_object_or_404(Election, pk=election_id)

        total_votes = Vote.objects.filter(election=election).count()

        # Aggregate votes per candidate using ORM annotations
        raw_results = (
            Vote.objects
            .filter(election=election)
            .values(
                'candidate__candidate_id',
                'candidate__full_name',
                'candidate__party',
                'candidate__constituency__name',
            )
            .annotate(vote_count=Count('vote_id'))
            .order_by('-vote_count')
        )
        
        results = []
        for row in raw_results:
            percentage = round((row['vote_count'] / total_votes * 100), 2) if total_votes else 0.0
            results.append({
                'candidate_id':       row['candidate__candidate_id'],
                'full_name':          row['candidate__full_name'],
                'party':              row['candidate__party'],
                'constituency_name':  row['candidate__constituency__name'],
                'vote_count':         row['vote_count'],
                'percentage':         percentage,
            })

        # Include candidates with zero votes
        all_candidates = Candidate.objects.filter(
            election=election
        ).select_related('constituency')

        voted_ids = {r['candidate_id'] for r in results}

        for candidate in all_candidates:
            if candidate.candidate_id not in voted_ids:
                results.append({
                    'candidate_id':      candidate.candidate_id,
                    'full_name':         candidate.full_name,
                    'party':             candidate.party,
                    'constituency_name': candidate.constituency.name,
                    'vote_count':        0,
                    'percentage':        0.0,
                })

        results.sort(key=lambda x: x['vote_count'], reverse=True)

        # Determine winner
        winner = results[0] if results and total_votes > 0 else None

        return Response({
            'election_id':      election.election_id,
            'election_status':  election.status,
            'start_date':       election.start_date,
            'end_date':         election.end_date,
            'total_votes':      total_votes,
            'total_candidates': len(results),
            'winner':           winner,
            'results':          results,
        }, status=status.HTTP_200_OK)
    



class ConstituencyResultsView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, election_id, constituency_id):
        from constituencies.models import Constituency

        election     = get_object_or_404(Election, pk=election_id)
        constituency = get_object_or_404(Constituency, pk=constituency_id)

        total_votes = Vote.objects.filter(
            election=election,
            candidate__constituency=constituency
        ).count()

        raw_results = (
            Vote.objects
            .filter(election=election, candidate__constituency=constituency)
            .values(
                'candidate__candidate_id',
                'candidate__full_name',
                'candidate__party',
            )
            .annotate(vote_count=Count('vote_id'))
            .order_by('-vote_count')
        )

        results = []
        for row in raw_results:
            percentage = round((row['vote_count'] / total_votes * 100), 2) if total_votes else 0.0
            results.append({
                'candidate_id': row['candidate__candidate_id'],
                'full_name':    row['candidate__full_name'],
                'party':        row['candidate__party'],
                'vote_count':   row['vote_count'],
                'percentage':   percentage,
            })

        return Response({
            'election_id':       election.election_id,
            'constituency_id':   constituency.constituency_id,
            'constituency_name': constituency.name,
            'region':            constituency.region,
            'total_votes':       total_votes,
            'results':           results,
        }, status=status.HTTP_200_OK)
    


class VoteAuditLogView(APIView):

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        queryset = Vote.objects.select_related(
            'voter',
            'candidate',
            'candidate__constituency',
            'election'
        ).all()

        election_id = request.query_params.get('election')
        if election_id:
            queryset = queryset.filter(election__election_id=election_id)

        serializer = VoteAuditSerializer(queryset, many=True)

        return Response({
            'total': queryset.count(),
            'votes': serializer.data,
        }, status=status.HTTP_200_OK)




class VoterHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        votes = Vote.objects.select_related(
            'candidate',
            'candidate__constituency',
            'election'
        ).filter(voter=request.user)

        serializer = VoteReceiptSerializer(votes, many=True)

        return Response({
            'total': votes.count(),
            'votes': serializer.data,
        }, status=status.HTTP_200_OK)

