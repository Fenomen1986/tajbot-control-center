from django.contrib import admin
from django.urls import path, include
# --- ИЗМЕНЕНИЕ ---
from controlcenter.main.admin import site as main_admin_site

urlpatterns = [
    # Заменяем стандартный admin.site на наш
    path('admin/', main_admin_site.urls),
    path('api/', include('controlcenter.main.urls')),
]