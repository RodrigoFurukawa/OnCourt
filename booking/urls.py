from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sobre/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
    path("contato/", views.contact, name="contact"),
    path("cadastro/", views.signup_view, name="signup"),
    path("quadras/", views.court_list, name="court_list"),
    path("quadras/<int:court_id>/", views.court_detail, name="court_detail"),
    path("quadras/<int:court_id>/reservar/", views.reserve_court, name="reserve_court"),
    path("minhas-reservas/", views.my_reservations, name="my_reservations"),
    path("painel-admin/", views.admin_dashboard, name="admin_dashboard"),
]