from django.db import models

class Vote(models.Model):
    vote_id = models.AutoField(primary_key=True)
    voter = models.ForeignKey('accounts.Voter', 
            on_delete =models.CASCADE, related_name= 'votes')
    candidate = models.ForeignKey('candidates.Candidate',
                on_delete= models.CASCADE, related_name='votes')
    election = models.ForeignKey('elections.Election',
                on_delete=models.CASCADE, related_name='votes')
    time = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table        = 'votes'
        ordering        = ['-time']
        unique_together = ('voter', 'election') #this should be for one vote per election per voter

    def __str__(self):
        return f"Vote #{self.vote_id} — {self.voter.full_name} → {self.candidate.full_name}"
    