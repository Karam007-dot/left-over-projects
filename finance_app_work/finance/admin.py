from django.contrib import admin
from .models import Account, Transaction, Budget, Goal, PlaidItem

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'account_type', 'balance', 'last_four']
    list_filter = ['account_type']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'amount', 'category', 'date']
    list_filter = ['category', 'date']

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'user', 'limit_amount', 'month', 'year']

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'target_amount', 'saved_amount', 'deadline']

@admin.register(PlaidItem)
class PlaidItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'institution_name', 'item_id', 'created_at']
