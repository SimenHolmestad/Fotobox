from django.db import models

# Create your models here.

class CameraStatus (models.Model):
    occupied = models.BooleanField(default=False)

    #make sure only one cameraStatus can exist
    def save(self, *args, **kwargs):
        if CameraStatus.objects.exists() and not self.pk:
            # if you'll not check for self.pk
            # then error will also raised in update of exists model
            raise ValidationError("There can only be one cameraStatus instance")
        return super(CameraStatus, self).save(*args, **kwargs)
            
        
