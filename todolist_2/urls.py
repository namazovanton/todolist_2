from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include(('core.urls', 'core'))),
    path('goals/', include('goals.urls', namespace='goals')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('bot/', include('bot.urls')),
]
