from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, ConsentLog


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration (Tourist and Local)
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'user_type', 'country', 'mauritius_location',
            'data_consent', 'marketing_consent', 'cookie_consent'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        
        # DPA Compliance: Data consent is required
        if not attrs.get('data_consent'):
            raise serializers.ValidationError({
                "data_consent": "You must consent to data collection to register."
            })
        
        # Validate location based on user type
        if attrs['user_type'] == 'tourist':
            if not attrs.get('country'):
                raise serializers.ValidationError({
                    "country": "Country is required for tourists."
                })
        elif attrs['user_type'] == 'local':
            if not attrs.get('mauritius_location'):
                raise serializers.ValidationError({
                    "mauritius_location": "Location is required for local residents."
                })
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.give_consent()  # Record consent timestamp
        user.save()
        
        # Create consent log
        ConsentLog.objects.create(
            user=user,
            consent_type='data',
            granted=True
        )
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile display
    """
    location = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'user_type',
            'location', 'profile_picture', 'phone_number',
            'created_at', 'data_consent', 'marketing_consent'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_location(self, obj):
        return obj.get_location()


class ConsentUpdateSerializer(serializers.Serializer):
    """
    DPA Compliance: Update user consent preferences
    """
    data_consent = serializers.BooleanField(required=False)
    marketing_consent = serializers.BooleanField(required=False)
    cookie_consent = serializers.BooleanField(required=False)


class AccountDeletionSerializer(serializers.Serializer):
    """
    DPA Compliance: Request account deletion
    """
    confirm = serializers.BooleanField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError(
                "You must confirm account deletion."
            )
        return value