from django.db import models

class Constituency(models.Model):
    constituency_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length= 255)
    region = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'constituencies'
        ordering  = ['name']
        verbose_name_plural = 'Constituencies'

    def __str__(self):
        return f"{self.name} — {self.region}"

    @property
    def total_candidates(self):
        return self.candidates.count()

    @property
    def total_voters(self):
        return self.candidates.values('election').distinct().count()