from django.contrib.auth.models import User, Group
from rules.models import ClassType
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ClassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassType
        fields = "__all__"
