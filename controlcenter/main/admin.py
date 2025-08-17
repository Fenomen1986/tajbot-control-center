from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from datetime import date, timedelta
from .models import Client, Bot, Lead

class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.dashboard_view), name='index'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        today = date.today()
        seven_days_later = today + timedelta(days=7)

        # Собираем статистику
        context = {
            'new_leads_today': Lead.objects.filter(created_at__date=today).count(),
            'leads_in_progress': Lead.objects.filter(status='В работе').count(),
            'total_clients': Client.objects.count(),
            'active_subscriptions': Client.objects.exclude(subscription_plan='Не активна').count(),
            'recent_leads': Lead.objects.order_by('-created_at')[:5],
            'expiring_clients': Client.objects.filter(
                subscription_end_date__gte=today,
                subscription_end_date__lte=seven_days_later
            ).order_by('subscription_end_date'),
        }
        return render(request, 'admin/dashboard.html', context)

# Заменяем стандартный admin.site на наш кастомный
site = CustomAdminSite()

@admin.register(Client, site=site)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_person', 'phone', 'subscription_plan', 'subscription_end_date')
    list_filter = ('subscription_plan',)
    search_fields = ('company_name', 'contact_person')
    ordering = ('company_name',)

@admin.register(Bot, site=site)
class BotAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'platform')
    list_filter = ('platform', 'client')
    search_fields = ('name', 'client__company_name')
    readonly_fields = ('api_auth_token',) 

@admin.register(Lead, site=site)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'bot', 'status', 'created_at') # Убрали colored_status для простоты
    list_filter = ('status', 'bot')
    search_fields = ('customer_name', 'customer_data')
    ordering = ('-created_at',)
    readonly_fields = ('bot', 'customer_name', 'customer_data', 'created_at') 
    list_editable = ('status',)