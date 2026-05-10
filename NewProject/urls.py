from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('accounts/', include('accounts.urls')),
    path('appointments/', include('appointments.urls')),
    path('diet/', include('diet_compatibility.urls')),
    path('reminders/', include('medicine_reminders.urls')),

    path('api-auth/', include('rest_framework.urls')),
]

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
