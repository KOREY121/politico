from django.db import models

class Election(models.Model):
    STATUS = [('pending', 'Pending'), ('active', 'Active'), ('closed', 'Closed')]
    election_id = models.AutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(choices=STATUS, default='pendong', max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'elections'
        ordering = ['-created_at']

    def __str__(self):
        return f'Election #{self.election_id} ({self.status})'
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def total_value(self):
        return self.votes.count()
    
    @property
    def total_candidates(self):
        return self.candidates.count()
    
    