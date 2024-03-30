from rest_framework import serializers
from .models import UserDetail, Blog
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
    
class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'
        read_only_fields = ['user']

class DetailBlogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    summary_short = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = '__all__'

    def get_summary_short(self, obj):
        summary_words = obj.summary.split()
        summary_shortened = ' '.join(summary_words[:15])
        if len(summary_words) > 15:
            summary_shortened += ' ...'
        return summary_shortened

