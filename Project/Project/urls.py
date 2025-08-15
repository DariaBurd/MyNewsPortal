from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.urls import path, include
from allauth.account.views import LoginView, SignupView
from .views import ProfileUpdateView
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', include('news.urls')),
    path('', RedirectView.as_view(url='/news/')),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('accounts/yandex/login/', include('allauth.socialaccount.providers.yandex.urls')),
    path('accounts/profile/', login_required(TemplateView.as_view(template_name='account/profile.html')), name='profile'),
]
