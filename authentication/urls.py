from django.urls import path
from authentication.views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    ProjectsView, ProjectDetailView, DeleteAccountView
)

app_name = 'authentication'

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('profile/<str:profile_slug>/', ProfileView.as_view()),
    path('delete/', DeleteAccountView.as_view()),
    path('projects/', ProjectsView.as_view()),
    path('projects/<int:project_id>/', ProjectDetailView.as_view()),
]
