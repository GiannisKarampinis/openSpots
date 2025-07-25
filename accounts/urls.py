from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views

urlpatterns = [
    path('login/',      auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('signup/',     views.signup_view, name='signup'),
    path('profile/',    views.profile_view, name='profile'),
    path('logout/',     auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/',  views.venue_dashboard_view, name='venue_dashboard'),
    path('reservation/<int:reservation_id>/update-status/', views.update_reservation_status, name='update_reservation_status'),
]