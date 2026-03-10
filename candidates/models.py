from django.db import models

class Candidate(models.Model):
    candidate_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=200)
    party = models.CharField(max_length=250)
    election = models.ForeignKey('elections.Election', 
                on_delete=models.CASCADE, related_name='candidates')
    constituency = models.ForeignKey('constituencies.Constituency',
                    on_delete=models.CASCADE, related_name='candidates')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'candidates'
        ordering        = ['full_name']
        # Prevent same candidate from being registered twice in same election
        unique_together = ('full_name', 'election')

    def __str__(self):
        return f"{self.full_name} ({self.party}) — Election #{self.election_id}"

    @property
    def total_votes(self):
        return self.votes.count()
    
