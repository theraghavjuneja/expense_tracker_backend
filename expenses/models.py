from django.db import models
from django.constrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
logger=logging.getLogger(__name__)
# Create your models here.
class User(AbstractUser):
    """
    Our custom user model with some fields for tracking expenses
    """
    email=models.EmailField(unique=True)
    first_name=models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    def __str__(self):
        return f"{self.first_name}- {self.last_name} ({self.email})"
    class Meta:
        db_table='auth_user'


class ExpenseCategory(models.Model):
    """
    Model for expense categories
    """
    name=models.CharField(max_length=50,unique=True)
    description=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural="Expense Categories"
        ordering=['name']
        
class Expense(models.Model):
    """This will contain what all expenses user has done"""
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='expenses')
    amount=models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category=models.ForeignKey(ExpenseCategory,on_delete=models.CASCADE)
    description=models.TextField(blank=True)
    date=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.user.email}-{self.amount}-{self.category.name}-{self.date}"
    
    def save(self,*args,**kwargs):
        logger.info(f"Creating/updating expense {self.amount} for user {self.user.email}")
        super().save(*args,**kwargs)
    class Meta:
        verbose_name_plural="Expenses"
        ordering=['-date','-created_at']
        indexes=[
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['date']),
        ]