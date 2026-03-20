from django.db import models
from django.contrib.auth.models import User


class PlaidItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plaid_items')
    access_token = models.TextField()
    item_id = models.CharField(max_length=200, unique=True)
    institution_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.institution_name}"


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('credit', 'Credit'),
        ('investment', 'Investment'),
        ('loan', 'Loan'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    plaid_item = models.ForeignKey(PlaidItem, on_delete=models.SET_NULL, null=True, blank=True)
    plaid_account_id = models.CharField(max_length=200, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200)
    official_name = models.CharField(max_length=200, blank=True)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES, default='checking')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    last_four = models.CharField(max_length=4, blank=True)
    currency_code = models.CharField(max_length=10, default='USD')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-balance']

    def __str__(self):
        return f"{self.name} (****{self.last_four})"

    @property
    def is_liability(self):
        return self.account_type in ('credit', 'loan')

    @property
    def net_balance(self):
        if self.is_liability:
            return -abs(self.balance)
        return self.balance


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    plaid_transaction_id = models.CharField(max_length=200, unique=True, null=True, blank=True)
    name = models.CharField(max_length=300)
    merchant_name = models.CharField(max_length=300, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    category = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    pending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.name} - ${self.amount}"

    @property
    def is_debit(self):
        return self.amount > 0

    @property
    def display_amount(self):
        if self.amount > 0:
            return f"-${abs(self.amount):,.2f}"
        return f"+${abs(self.amount):,.2f}"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=200)
    limit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        unique_together = ('user', 'category', 'month', 'year')
        ordering = ['category']

    def __str__(self):
        return f"{self.category} - ${self.limit_amount} ({self.month}/{self.year})"


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - ${self.target_amount}"

    @property
    def progress_percent(self):
        if self.target_amount <= 0:
            return 0
        pct = (self.saved_amount / self.target_amount) * 100
        return min(float(pct), 100)

    @property
    def remaining(self):
        return max(self.target_amount - self.saved_amount, 0)
