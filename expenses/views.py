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
import logging
from django.utils.dateparse import parse_date
from datetime import date,timedelta
from .models import User,Expense,ExpenseCategory
from .serializers import(
    UserSerializer, LoginSerializer, 
    ExpenseCategorySerializer, ExpenseAnalyticsSerializer
    ,ExpenseSerializer
    
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

class ExpenseListCreateView(generics.ListCreateAPIView):
    """
    With this view, a user can see his expenses or create them
    """
    serializer_class=ExpenseSerializer
    permission_classes=[IsAuthenticated]
    def get_query(self):
        # Stel1 Getting the Expenses of requested user
        queryset=Expense.objects.filter(user=self.request.user)
        
        # We can see analytics too, so maybe we can have some start & end date
        # in which we need to filter
        start_date=self.request.query_params.get('start_date')
        end_date=self.request.query_params.get('end_date')
        if start_date:
            start_date=parse_date(start_date)
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
        
        # User may also want to see a particular category ex
        category=self.request.query_params.get('category')
        if category:
            queryset=queryset.filter(category__name__icontains=category)
        
        logger.info(f"Fetching expenses for user: {self.request.user.email}, "
                   f"filters: start_date={start_date}, end_date={end_date}, category={category}")
        
        return queryset.select_related('category')


class ExpenseDetailView(generics.RetrieveDestroyAPIView):
    """
    With this, a user should be able to retrieve, update or delete some expense
    """
    serializer_class=ExpenseSerializer
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)
class ExpenseCategoryListView(generics.ListAPIView):
    """
    To list all the expense categories
    """
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_analytics_view(request):
    """
    Wth this view a logged in user should be able to get his expense
    analytics
    """
    user=request.user
    start_date=request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # if query params doesnt have date then we willconsider last 30 days
    if not start_date or not end_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = parse_date(start_date) or date.today() - timedelta(days=30)
        end_date = parse_date(end_date) or date.today()
    
    expenses = Expense.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=end_date
    )
    total_data = expenses.aggregate(
        total=Sum('amount'),
        count=Count('id')
    )
    category_breakdown = expenses.values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    daily_trends = expenses.annotate(
        day=TruncDate('date')
    ).values('day').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('day')
    weekly_trends = expenses.annotate(
        week=TruncWeek('date')
    ).values('week').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('week')
    monthly_trends = expenses.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('month')
    analytics_data = {
        'total_expenses': total_data['total'] or 0,
        'expense_count': total_data['count'] or 0,
        'category_breakdown': [
            {
                'category': item['category__name'],
                'total': item['total'],
                'count': item['count']
            }
            for item in category_breakdown
        ],
        'daily_trends': [
            {
                'date': item['day'].strftime('%Y-%m-%d'),
                'total': item['total'],
                'count': item['count']
            }
            for item in daily_trends
        ],
        'weekly_trends': [
            {
                'week': item['week'].strftime('%Y-%m-%d'),
                'total': item['total'],
                'count': item['count']
            }
            for item in weekly_trends
        ],
        'monthly_trends': [
            {
                'month': item['month'].strftime('%Y-%m-%d'),
                'total': item['total'],
                'count': item['count']
            }
            for item in monthly_trends
        ]
    }
    
    logger.info(f"Generated analytics for user: {user.email}, "
               f"period: {start_date} to {end_date}")
    
    serializer = ExpenseAnalyticsSerializer(analytics_data)
    return Response(serializer.data)