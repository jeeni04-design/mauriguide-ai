from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('tourist', 'Tourist'),
        ('local', 'Local Resident'),
    ]
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='tourist'
    )
    
    # For Tourists - Country (using CharField instead of CountryField)
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Country of origin (for tourists)'
    )
    
    # For Locals - Mauritius location
    mauritius_location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Location in Mauritius (for locals)'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # DPA 2017 Compliance
    data_consent = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)
    cookie_consent = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    account_deletion_requested = models.BooleanField(default=False)
    deletion_request_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.username} ({self.get_user_type_display()})'
    
    def give_consent(self):
        self.data_consent = True
        self.consent_date = timezone.now()
        self.save()
    
    def request_account_deletion(self):
        self.account_deletion_requested = True
        self.deletion_request_date = timezone.now()
        self.is_active = False
        self.save()
    
    def get_location(self):
        if self.user_type == 'tourist':
            return self.country or 'Not specified'
        return self.mauritius_location or 'Not specified'


class ConsentLog(models.Model):
    CONSENT_TYPES = [
        ('data', 'Data Collection'),
        ('marketing', 'Marketing'),
        ('cookies', 'Cookies'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='consent_logs')
    consent_type = models.CharField(max_length=20, choices=CONSENT_TYPES)
    granted = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        status = 'Granted' if self.granted else 'Revoked'
        return f'{self.user.username} - {self.get_consent_type_display()} - {status}'


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.user.username} - {self.activity_type}'
