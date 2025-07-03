from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework import generics, status
from rest_framework.permissions import AllowAny,IsAdminUser,IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum,Count,QuerySet
from django.db.models.functions import (
    TruncDate,
    TruncWeek,
    TruncMonth
)
from django.utils.dateparse import parse_date
from datetime import date,timedelta
from .models import User,Expense,ExpenseCategory
from .serializers import(
    UserSerializer, LoginSerializer, ExpenseSerializer, 
    ExpenseCategorySerializer, ExpenseAnalyticsSerializer
    
)

logger=logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer=LoginSerializer(data=request.data)
    if serializer.is_valid():
        user=serializer.validated_data['user']
        refresh=RefreshToken.for_user(user)
        logger.info(f"Successful login for user :{user.email}")
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        },status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

