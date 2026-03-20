import json
from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Account, Transaction, Budget, Goal, PlaidItem
from . import plaid_service


def get_month_range(year, month):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


@login_required
def dashboard(request):
    user = request.user
    today = date.today()
    year, month = today.year, today.month
    start, end = get_month_range(year, month)

    accounts = Account.objects.filter(user=user)
    total_assets = accounts.filter(account_type__in=['checking', 'savings', 'investment']).aggregate(
        total=Sum('balance'))['total'] or Decimal('0')
    total_liabilities = accounts.filter(account_type__in=['credit', 'loan']).aggregate(
        total=Sum('balance'))['total'] or Decimal('0')
    net_worth = total_assets - total_liabilities

    monthly_txns = Transaction.objects.filter(user=user, date__gte=start, date__lte=end)
    monthly_income = monthly_txns.filter(amount__lt=0).aggregate(
        total=Sum('amount'))['total'] or Decimal('0')
    monthly_income = abs(monthly_income)
    monthly_spend = monthly_txns.filter(amount__gt=0).aggregate(
        total=Sum('amount'))['total'] or Decimal('0')

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_start, prev_end = get_month_range(prev_year, prev_month)
    prev_spend = Transaction.objects.filter(
        user=user, date__gte=prev_start, date__lte=prev_end, amount__gt=0
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    savings_this_month = monthly_income - monthly_spend
    savings_rate = (savings_this_month / monthly_income * 100) if monthly_income > 0 else Decimal('0')

    recent_transactions = Transaction.objects.filter(user=user).select_related('account')[:8]

    cash_flow_data = []
    for i in range(5, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        s, e = get_month_range(y, m)
        inc = abs(Transaction.objects.filter(user=user, date__gte=s, date__lte=e, amount__lt=0).aggregate(
            total=Sum('amount'))['total'] or 0)
        exp = abs(Transaction.objects.filter(user=user, date__gte=s, date__lte=e, amount__gt=0).aggregate(
            total=Sum('amount'))['total'] or 0)
        month_name = date(y, m, 1).strftime('%b')
        cash_flow_data.append({'month': month_name, 'income': float(inc), 'expenses': float(exp)})

    plaid_connected = PlaidItem.objects.filter(user=user).exists()
    account_count = accounts.count()

    greeting = f"Hello, {user.first_name or user.username}"

    context = {
        'greeting': greeting,
        'net_worth': net_worth,
        'monthly_income': monthly_income,
        'monthly_spend': monthly_spend,
        'savings_this_month': savings_this_month,
        'savings_rate': savings_rate,
        'prev_spend': prev_spend,
        'recent_transactions': recent_transactions,
        'accounts': accounts[:6],
        'cash_flow_data': json.dumps(cash_flow_data),
        'plaid_connected': plaid_connected,
        'account_count': account_count,
        'today': today,
        'active_page': 'dashboard',
    }
    return render(request, 'finance/dashboard.html', context)


@login_required
def transactions_view(request):
    user = request.user
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')

    txns = Transaction.objects.filter(user=user).select_related('account')
    if category_filter:
        txns = txns.filter(category=category_filter)
    if search:
        txns = txns.filter(Q(name__icontains=search) | Q(merchant_name__icontains=search))

    categories = Transaction.objects.filter(user=user).values_list('category', flat=True).distinct().order_by('category')

    context = {
        'transactions': txns[:200],
        'categories': categories,
        'category_filter': category_filter,
        'search': search,
        'active_page': 'transactions',
    }
    return render(request, 'finance/transactions.html', context)


@login_required
def accounts_view(request):
    user = request.user
    accounts = Account.objects.filter(user=user)
    total_assets = accounts.filter(account_type__in=['checking', 'savings', 'investment']).aggregate(
        total=Sum('balance'))['total'] or 0
    total_liabilities = accounts.filter(account_type__in=['credit', 'loan']).aggregate(
        total=Sum('balance'))['total'] or 0

    context = {
        'accounts': accounts,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'active_page': 'accounts',
    }
    return render(request, 'finance/accounts.html', context)


@login_required
def budgets_view(request):
    user = request.user
    today = date.today()
    year, month = today.year, today.month
    start, end = get_month_range(year, month)

    budgets = Budget.objects.filter(user=user, month=month, year=year)
    budget_data = []
    for budget in budgets:
        spent = Transaction.objects.filter(
            user=user, category=budget.category,
            date__gte=start, date__lte=end, amount__gt=0
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        pct = min(float(spent / budget.limit_amount * 100), 100) if budget.limit_amount > 0 else 0
        budget_data.append({
            'budget': budget,
            'spent': spent,
            'remaining': max(budget.limit_amount - spent, 0),
            'percent': pct,
            'over_budget': spent > budget.limit_amount,
        })

    context = {
        'budget_data': budget_data,
        'month_name': date(year, month, 1).strftime('%B %Y'),
        'active_page': 'budgets',
    }
    return render(request, 'finance/budgets.html', context)


@login_required
def goals_view(request):
    user = request.user
    goals = Goal.objects.filter(user=user)
    context = {
        'goals': goals,
        'active_page': 'goals',
    }
    return render(request, 'finance/goals.html', context)


@login_required
def net_worth_view(request):
    user = request.user
    accounts = Account.objects.filter(user=user)
    assets = accounts.filter(account_type__in=['checking', 'savings', 'investment'])
    liabilities = accounts.filter(account_type__in=['credit', 'loan'])
    total_assets = assets.aggregate(total=Sum('balance'))['total'] or Decimal('0')
    total_liabilities = liabilities.aggregate(total=Sum('balance'))['total'] or Decimal('0')
    net_worth = total_assets - total_liabilities

    context = {
        'assets': assets,
        'liabilities': liabilities,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'net_worth': net_worth,
        'active_page': 'net_worth',
    }
    return render(request, 'finance/net_worth.html', context)


@login_required
def analytics_view(request):
    user = request.user
    spending_by_category = Transaction.objects.filter(
        user=user, amount__gt=0
    ).values('category').annotate(
        total=Sum('amount'), count=Count('id')
    ).order_by('-total')[:10]

    chart_data = [{'category': s['category'] or 'Uncategorized', 'total': float(s['total'])} for s in spending_by_category]

    context = {
        'spending_by_category': spending_by_category,
        'chart_data': json.dumps(chart_data),
        'active_page': 'analytics',
    }
    return render(request, 'finance/analytics.html', context)


@login_required
def reports_view(request):
    user = request.user
    today = date.today()
    year, month = today.year, today.month
    start, end = get_month_range(year, month)

    monthly_income = abs(Transaction.objects.filter(
        user=user, date__gte=start, date__lte=end, amount__lt=0
    ).aggregate(total=Sum('amount'))['total'] or 0)
    monthly_spend = Transaction.objects.filter(
        user=user, date__gte=start, date__lte=end, amount__gt=0
    ).aggregate(total=Sum('amount'))['total'] or 0
    net = monthly_income - monthly_spend

    monthly_data = []
    for i in range(5, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        s, e = get_month_range(y, m)
        inc = abs(Transaction.objects.filter(user=user, date__gte=s, date__lte=e, amount__lt=0).aggregate(
            total=Sum('amount'))['total'] or 0)
        exp = Transaction.objects.filter(user=user, date__gte=s, date__lte=e, amount__gt=0).aggregate(
            total=Sum('amount'))['total'] or 0
        monthly_data.append({
            'month': date(y, m, 1).strftime('%b'),
            'income': float(inc),
            'expenses': float(exp),
        })

    context = {
        'monthly_income': monthly_income,
        'monthly_spend': monthly_spend,
        'net': net,
        'month_name': date(year, month, 1).strftime('%B %Y'),
        'chart_data': json.dumps(monthly_data),
        'active_page': 'reports',
    }
    return render(request, 'finance/reports.html', context)


@login_required
def settings_view(request):
    user = request.user
    plaid_items = PlaidItem.objects.filter(user=user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            messages.success(request, 'Profile updated successfully.')
        elif action == 'change_password':
            old_pw = request.POST.get('old_password', '')
            new_pw = request.POST.get('new_password', '')
            if user.check_password(old_pw):
                user.set_password(new_pw)
                user.save()
                messages.success(request, 'Password changed. Please log in again.')
                return redirect('login')
            else:
                messages.error(request, 'Incorrect current password.')
        return redirect('settings')

    context = {
        'plaid_items': plaid_items,
        'plaid_configured': bool(from_settings_plaid_client_id()),
        'active_page': 'settings',
    }
    return render(request, 'finance/settings.html', context)


def from_settings_plaid_client_id():
    from django.conf import settings
    return settings.PLAID_CLIENT_ID


@login_required
def get_link_token(request):
    from django.conf import settings as django_settings
    if not django_settings.PLAID_CLIENT_ID or not django_settings.PLAID_SECRET:
        return JsonResponse({'error': 'Plaid API keys not configured. Please add PLAID_CLIENT_ID and PLAID_SECRET in Settings.'}, status=400)
    try:
        link_token = plaid_service.create_link_token(request.user.id)
        return JsonResponse({'link_token': link_token})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def exchange_token(request):
    from django.conf import settings as django_settings
    if not django_settings.PLAID_CLIENT_ID:
        return JsonResponse({'error': 'Plaid not configured'}, status=400)
    try:
        data = json.loads(request.body)
        public_token = data.get('public_token')
        institution_name = data.get('institution_name', 'Unknown Bank')
        access_token, item_id = plaid_service.exchange_public_token(public_token)
        PlaidItem.objects.update_or_create(
            item_id=item_id,
            defaults={
                'user': request.user,
                'access_token': access_token,
                'institution_name': institution_name,
            }
        )
        return JsonResponse({'success': True, 'message': f'Connected to {institution_name}'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def sync_transactions(request):
    user = request.user
    items = PlaidItem.objects.filter(user=user)
    if not items.exists():
        messages.warning(request, 'No bank accounts connected. Please connect a bank first.')
        return redirect('dashboard')

    synced_count = 0
    try:
        for item in items:
            accounts_data = plaid_service.get_accounts(item.access_token)
            for acc_data in accounts_data:
                acc_type = acc_data.type.value if hasattr(acc_data.type, 'value') else str(acc_data.type)
                acc_subtype = acc_data.subtype.value if acc_data.subtype and hasattr(acc_data.subtype, 'value') else str(acc_data.subtype or '')
                type_map = {'depository': 'checking', 'credit': 'credit', 'investment': 'investment', 'loan': 'loan'}
                mapped_type = type_map.get(acc_type, 'other')
                if acc_subtype == 'savings':
                    mapped_type = 'savings'
                last_four = acc_data.mask or ''

                Account.objects.update_or_create(
                    plaid_account_id=acc_data.account_id,
                    defaults={
                        'user': user,
                        'plaid_item': item,
                        'name': acc_data.name,
                        'official_name': acc_data.official_name or '',
                        'account_type': mapped_type,
                        'balance': acc_data.balances.current or 0,
                        'available_balance': acc_data.balances.available,
                        'last_four': last_four,
                        'currency_code': acc_data.balances.iso_currency_code or 'USD',
                    }
                )

            added, modified, removed, _ = plaid_service.sync_transactions(item.access_token)
            for txn in added:
                try:
                    account = Account.objects.filter(user=user, plaid_account_id=txn.account_id).first()
                    category = ''
                    if hasattr(txn, 'personal_finance_category') and txn.personal_finance_category:
                        category = txn.personal_finance_category.primary or ''
                    elif hasattr(txn, 'category') and txn.category:
                        category = txn.category[0] if txn.category else ''
                    Transaction.objects.update_or_create(
                        plaid_transaction_id=txn.transaction_id,
                        defaults={
                            'user': user,
                            'account': account,
                            'name': txn.name,
                            'merchant_name': txn.merchant_name or '',
                            'amount': txn.amount,
                            'category': category,
                            'date': txn.date,
                            'pending': txn.pending,
                        }
                    )
                    synced_count += 1
                except Exception:
                    pass

            for txn in removed:
                Transaction.objects.filter(plaid_transaction_id=txn.transaction_id).delete()

        messages.success(request, f'Synced successfully! {synced_count} transactions updated.')
    except Exception as e:
        messages.error(request, f'Sync failed: {str(e)}')
    return redirect('dashboard')


@login_required
@require_POST
def add_transaction(request):
    user = request.user
    name = request.POST.get('name', '').strip()
    amount_raw = request.POST.get('amount', '0')
    category = request.POST.get('category', '')
    txn_date = request.POST.get('date', str(date.today()))
    txn_type = request.POST.get('type', 'debit')
    account_id = request.POST.get('account_id', '')

    try:
        amount = Decimal(amount_raw)
        if txn_type == 'credit':
            amount = -abs(amount)
        else:
            amount = abs(amount)

        account = None
        if account_id:
            account = Account.objects.filter(user=user, id=account_id).first()

        Transaction.objects.create(
            user=user,
            account=account,
            name=name,
            amount=amount,
            category=category,
            date=txn_date,
        )
        messages.success(request, 'Transaction added successfully.')
    except Exception as e:
        messages.error(request, f'Error adding transaction: {str(e)}')
    return redirect('transactions')


@login_required
@require_POST
def add_goal(request):
    user = request.user
    try:
        name = request.POST.get('name', '').strip()
        target = Decimal(request.POST.get('target_amount', '0'))
        saved = Decimal(request.POST.get('saved_amount', '0'))
        deadline_raw = request.POST.get('deadline', '')
        deadline = deadline_raw if deadline_raw else None
        Goal.objects.create(user=user, name=name, target_amount=target, saved_amount=saved, deadline=deadline)
        messages.success(request, 'Goal created successfully.')
    except Exception as e:
        messages.error(request, f'Error creating goal: {str(e)}')
    return redirect('goals')


@login_required
@require_POST
def add_budget(request):
    user = request.user
    try:
        category = request.POST.get('category', '').strip()
        limit = Decimal(request.POST.get('limit_amount', '0'))
        today = date.today()
        Budget.objects.update_or_create(
            user=user, category=category, month=today.month, year=today.year,
            defaults={'limit_amount': limit}
        )
        messages.success(request, 'Budget saved.')
    except Exception as e:
        messages.error(request, f'Error saving budget: {str(e)}')
    return redirect('budgets')


@login_required
def delete_account(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)
    account.delete()
    messages.success(request, 'Account removed.')
    return redirect('accounts')


def logout_view(request):
    logout(request)
    return redirect('login')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'finance/signup.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'finance/signup.html')
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('dashboard')
    return render(request, 'finance/signup.html')
