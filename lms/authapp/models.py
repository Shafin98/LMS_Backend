from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # role-specific example fields
    expertise = models.CharField(max_length=255, blank=True, null=True)  # instructor
    enrolled_date = models.DateTimeField(auto_now_add=True)  # student

    def __str__(self):
        return self.user.username
    
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 3600