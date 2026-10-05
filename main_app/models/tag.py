from django.db import models, IntegrityError

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True, db_index=True)

    def __str__(self):
        return self.name
