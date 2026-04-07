from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sobre/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
    path("contato/", views.contact, name="contact"),
    path("cadastro/", views.signup_view, name="signup"),
    path("clubes/", views.club_list, name="club_list"),
    path("clubes/<int:club_id>/", views.club_detail, name="club_detail"),
    path("clubes/<int:club_id>/esportes/<str:sport>/quadras/", views.club_sport_courts, name="club_sport_courts"),
    path("quadras/<int:court_id>/reservar/", views.reserve_court, name="reserve_court"),
    path("minhas-reservas/", views.my_reservations, name="my_reservations"),
    path("painel-admin/", views.admin_dashboard, name="admin_dashboard"),
]
