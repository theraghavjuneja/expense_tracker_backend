from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import ExpenseCategory

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    default_categories = [
        ('Food & Dining', 'Restaurants, groceries, and food delivery'),
        ('Transportation', 'Gas, public transport, rideshare, parking'),
        ('Shopping', 'Clothing, electronics, household items'),
        ('Entertainment', 'Movies, games, subscriptions, hobbies'),
        ('Bills & Utilities', 'Rent, electricity, water, internet, phone'),
        ('Healthcare', 'Medical expenses, insurance, medications'),
        ('Travel', 'Flights, hotels, vacation expenses'),
        ('Education', 'Books, courses, tuition, training'),
        ('Personal Care', 'Haircuts, cosmetics, gym membership'),
        ('Others', 'Miscellaneous expenses'),
    ]

    for name, description in default_categories:
        ExpenseCategory.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
