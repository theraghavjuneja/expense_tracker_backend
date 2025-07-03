from django.apps import AppConfig


class ExpensesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expenses'
    def ready(self):
        from django.db.utils import ProgrammingError
        try:
            from .models import ExpenseCategory
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
        except ProgrammingError:
            # Database not ready yet
            pass
