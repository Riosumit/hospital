from rest_framework import serializers
from .models import UserDetail
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email']

class UserDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserDetail
        fields = ['profile_picture', 'line', 'city', 'state', 'pincode', 'user']
        read_only_fields = ['user_type']

    def create(self, validated_data):
        user = self.context.get('user')
        user_type = self.context.get('user_type')
        user_detail = UserDetail.objects.create(user=user, user_type=user_type, **validated_data)
        return user_detail