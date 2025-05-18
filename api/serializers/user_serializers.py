from rest_framework import serializers
from accounts.models import CustomUser, LandlordVerification
from listings.models import RoommateProfile

class LandlordVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandlordVerification
        fields = ['id', 'user', 'verification_document', 'is_verified', 'verified_at', 'verification_notes']
        read_only_fields = ['is_verified', 'verified_at', 'verification_notes']

class RoommateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoommateProfile
        fields = ['id', 'user', 'age', 'gender', 'occupation', 'smoker', 'pet_owner', 'about_me', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number', 'profile_picture', 'bio', 'date_joined']
        read_only_fields = ['date_joined']

class UserDetailSerializer(serializers.ModelSerializer):
    landlord_verification = LandlordVerificationSerializer(read_only=True)
    roommate_profile = RoommateProfileSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 
                  'phone_number', 'profile_picture', 'bio', 'date_joined',
                  'landlord_verification', 'roommate_profile']
        read_only_fields = ['date_joined']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'user_type', 'phone_number']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user 