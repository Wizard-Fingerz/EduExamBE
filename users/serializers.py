from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

import uuid
from django.utils.text import slugify

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'user_type')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'username': {'read_only': True},  # Prevent user from manually submitting it
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def generate_unique_username(self, first_name, last_name):
        base_username = slugify(f"{first_name}.{last_name}")
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        return username

    def create(self, validated_data):
        validated_data.pop('password2')
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        validated_data['username'] = self.generate_unique_username(first_name, last_name)
        user = User.objects.create_user(**validated_data)
        return user

class ExaminationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User._meta.get_field('examination_type').related_model
        fields = ('id', 'name')

class UserProfileSerializer(serializers.ModelSerializer):
    examination_type = ExaminationTypeSerializer(read_only=True)
    examination_type_id = serializers.PrimaryKeyRelatedField(
        queryset=User._meta.get_field('examination_type').related_model.objects.all(),
        source='examination_type',
        write_only=True,
        required=False
    )
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'user_type',
                 'profile_picture', 'bio', 'date_of_birth', 'phone_number', 'address',
                 'institution_name', 'examination_type', 'examination_type_id', 'grade')
        read_only_fields = ('id', 'username', 'user_type') 