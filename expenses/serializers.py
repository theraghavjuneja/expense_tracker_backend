from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User,Expense,ExpenseCategory
import logging
logger=logging.getLogger(__name__)
class UserSerializer(serializers.ModelSerializer):
    """User serializer class"""
    class Meta:
        model=User
        fields=['id','email','first_name','last_name','created_at']
        read_only_fields=['id','created_at']
class LoginSerializer(serializers.Serializer):
    """Serializer class for the user login"""
    email=serializers.EmailField()
    password=serializers.CharField(write_only=True)
    def validate(self,data):
        email=data.get('email')
        password=data.get('password')
        if email and password:
            user=authenticate(username=email, password=password)
            if not user:
                logger.warning(f"Failed login attempt for email: {email}")
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                logger.warning(f"Inactive user login attempt: {email}")
                raise serializers.ValidationError("User account is disabled")
            data['user']=user
        else:
            raise serializers.ValidationError("Must include email and password")
        return data
class ExpenseCategorySerializer(serializers.ModelSerializer):
    category=serializers.CharField(source='category.name',read_only=True)
    class Meta:
        model=Expense
        fields=[
            'id', 'amount', 'category', 'category_name', 
            'description', 'date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    def create(self,validated_data):
        validated_data['user'] = self.context['request'].user
        logger.info(f"Creating expense for user: {validated_data['user'].email}")
        return super().create(validated_data)
    
class ExpenseAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for the expense analytics data
    """
    total_expenses=serializers.DecimalField(max_digits=12,decimal_places=2)
    expense_count=serializers.IntegerField()
    category_breakown=serializers.ListField(
        child=serializers.DictField()
    )
    daily_trends=serializers.ListField(
        child=serializers.DictField()
    )
    weekly_trends=serializers.ListField(
        child=serializers.DictField()
    )
    monthly_trends=serializers.ListField(
        child=serializers.DictField()
    )
    
    







