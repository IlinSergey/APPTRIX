from django.urls import path
from .views import ClientRegistrationView, ClientLoginView, ClientLogoutView, ClientMatchView


urlpatterns = [
    path("clients/create/", ClientRegistrationView.as_view()),
    path("clients/login/", ClientLoginView.as_view()),
    path("clients/logout/", ClientLogoutView.as_view()),
    path("clients/<int:id>/match/", ClientMatchView.as_view())
]
