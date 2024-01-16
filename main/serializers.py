from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
import hashlib
from decimal import Decimal, InvalidOperation, ROUND_DOWN



class LimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Limit
        fields = '__all__'

class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        read_only_fields = ['username']

    def create(self, validated_data):
        email = validated_data['email']
        username = hashlib.sha256(email.encode('utf-8')).hexdigest()
        password = validated_data['password']

        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()

        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            return data
        else:
            raise serializers.ValidationError('Email and password are required fields.')


class ExpenseCategorySerializer(serializers.ModelSerializer):
    profile = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ExpenseCategory
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'profile', 'category', 'amount', 'description', 'reg_date']
        read_only_fields = ['id', 'reg_date']

    def validate_amount(self, value):       
        if value <= 0:
            raise serializers.ValidationError("Amount should be greater than zero.")
        return value
    
    
class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ExpenseCategoryTotalSerializer(serializers.Serializer):
    category_title = serializers.CharField()
    category_emoji = serializers.CharField()
    total_count = serializers.IntegerField()
    total_amount = serializers.IntegerField()
    total_category_amount = serializers.IntegerField()

   

class PasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()