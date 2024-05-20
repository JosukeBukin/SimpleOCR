from django.db import models

# Create your models here.
class UploadedFiles(models.Model):
    file = models.FileField(upload_to = 'saved_files/')