from datetime import date as date_cls

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .availability import get_timetable, is_slot_available, parse_date, parse_time
from .forms import ClubFilterForm, SignUpForm
from .models import Club, Court, CourtBlock, Reservation, SlotBlock


def home(request):
    clubs = Club.objects.prefetch_related("courts")
    featured_clubs = [c for c in clubs if c.featured]

    courts_qs = Court.objects.all()
    stats = {
        "clubs": clubs.count(),
        "courts": courts_qs.count(),
        "available": courts_qs.filter(available_for_rent=True).count(),
        "sports": courts_qs.values("sport").distinct().count(),
        "avg_rating": round(clubs.aggregate(avg=Avg("rating"))["avg"] or 0, 1),
    }

    return render(request, "booking/home.html", {
        "featured_clubs": featured_clubs,
        "stats": stats,
    })


def about(request):
    return render(request, "booking/about.html")


def faq(request):
    return render(request, "booking/faq.html")


def contact(request):
    return render(request, "booking/contact.html")


def club_list(request):
    form = ClubFilterForm(request.GET or None)
    clubs = list(Club.objects.prefetch_related("courts"))

    if form.is_valid():
        sport = form.cleaned_data.get("sport")
        name = form.cleaned_data.get("name")
        sort_by = form.cleaned_data.get("sort_by")
        min_rating = form.cleaned_data.get("min_rating") or 0
        max_rating = form.cleaned_data.get("max_rating")
        if max_rating is None:
            max_rating = 5

        if sport:
            clubs = [c for c in clubs if sport in c.sports]
        if name:
            clubs = [c for c in clubs if name.lower() in c.name.lower()]
        clubs = [c for c in clubs if min_rating <= c.rating <= max_rating]

        if sort_by == "rating":
            clubs.sort(key=lambda c: c.rating, reverse=True)
        elif sort_by == "name":
            clubs.sort(key=lambda c: c.name)

    return render(request, "booking/club_list.html", {
        "form": form,
        "clubs": clubs,
    })


def club_detail(request, club_id):
    club = Club.objects.filter(id=club_id).prefetch_related("courts").first()
    if not club:
        return redirect("club_list")

    courts = list(club.courts.all())
    available_courts = [c for c in courts if c.available_for_rent]

    return render(request, "booking/club_detail.html", {
        "club": club,
        "courts": courts,
        "available_courts": available_courts,
    })


def club_sport_courts(request, club_id, sport):
    club = Club.objects.filter(id=club_id).first()
    if not club:
        return redirect("club_list")

    courts = list(
        club.courts.filter(sport=sport).prefetch_related("schedules")
    )
    selected_date = parse_date(request.GET.get("date") or request.POST.get("date"))

    if request.method == "POST":
        if not request.user.is_authenticated:
            next_url = reverse("club_sport_courts", args=[club_id, sport])
            return redirect(f"{reverse('login')}?next={next_url}")

        court = next((c for c in courts if str(c.id) == request.POST.get("court_id")), None)
        start_time = parse_time(request.POST.get("slot"))

        error = None
        if not court or start_time is None or not is_slot_available(court, selected_date, start_time):
            error = "Horário indisponível para reserva. Escolha outro horário."
        else:
            try:
                Reservation.objects.create(user=request.user, court=court, date=selected_date, start_time=start_time)
                return redirect("my_reservations")
            except IntegrityError:
                error = "Esse horário acabou de ser reservado. Tente outro."

        return render(request, "booking/club_sport_courts.html", _schedule_context(
            club, sport, courts, selected_date, error=error,
        ))

    return render(request, "booking/club_sport_courts.html", _schedule_context(
        club, sport, courts, selected_date,
    ))


def _schedule_context(club, sport, courts, selected_date, error=None):
    """Monta o grid (linhas = horários, colunas = quadras) para a data escolhida."""
    court_timetables = {
        court.id: {slot["time"]: slot["status"] for slot in get_timetable(court, selected_date)}
        for court in courts
    }

    all_times = sorted({time for tt in court_timetables.values() for time in tt})
    timetable_rows = []
    for time in all_times:
        row = {"time": time, "cells": []}
        for court in courts:
            status = court_timetables[court.id].get(time, "unavailable")
            row["cells"].append({"court_id": court.id, "time": time, "status": status})
        timetable_rows.append(row)

    return {
        "club": club,
        "sport": sport,
        "courts": courts,
        "timetable_rows": timetable_rows,
        "selected_date": selected_date,
        "error": error,
    }


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")

    return render(request, "booking/signup.html", {"form": form})


@login_required
def reserve_court(request, court_id):
    court = Court.objects.filter(id=court_id).select_related("club").first()
    if not court:
        return redirect("club_list")

    club = court.club
    if not court.available_for_rent:
        return redirect("club_detail", club_id=club.id)

    selected_date = parse_date(request.GET.get("date") or request.POST.get("date"))
    timetable = get_timetable(court, selected_date)

    if request.method == "POST":
        start_time = parse_time(request.POST.get("slot"))
        error = None
        if start_time is None or not is_slot_available(court, selected_date, start_time):
            error = "Selecione um horário válido."
        else:
            try:
                Reservation.objects.create(user=request.user, court=court, date=selected_date, start_time=start_time)
                return redirect("my_reservations")
            except IntegrityError:
                error = "Esse horário acabou de ser reservado. Tente outro."

        return render(request, "booking/reserve_court.html", {
            "club": club, "court": court, "timetable": timetable,
            "selected_date": selected_date, "error": error,
        })

    return render(request, "booking/reserve_court.html", {
        "club": club, "court": court, "timetable": timetable,
        "selected_date": selected_date,
    })


@login_required
def my_reservations(request):
    reservations = (
        Reservation.objects.filter(user=request.user)
        .select_related("court", "court__club")
    )
    return render(request, "booking/my_reservations.html", {"reservations": reservations})


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def admin_dashboard(request):
    selected_date = parse_date(request.GET.get("date") or request.POST.get("date"))

    if request.method == "POST":
        court = Court.objects.filter(id=request.POST.get("court_id")).first()
        action = request.POST.get("action")
        if court and action == "toggle_slot":
            start_time = parse_time(request.POST.get("slot"))
            if start_time is not None:
                existing = SlotBlock.objects.filter(court=court, date=selected_date, start_time=start_time)
                if existing.exists():
                    existing.delete()
                else:
                    SlotBlock.objects.create(court=court, date=selected_date, start_time=start_time)
        elif court and action == "disable":
            CourtBlock.objects.update_or_create(court=court, defaults={
                "reason": request.POST.get("reason") or "Indisponível temporariamente",
                "until": request.POST.get("until") or "Sem data definida",
            })
            court.available_for_rent = False
            court.save(update_fields=["available_for_rent"])
        elif court and action == "enable":
            CourtBlock.objects.filter(court=court).delete()
            court.available_for_rent = True
            court.save(update_fields=["available_for_rent"])

        return redirect(f"{reverse('admin_dashboard')}?date={selected_date:%Y-%m-%d}")

    courts = list(
        Court.objects.select_related("club").prefetch_related("schedules", "block")
    )
    for court in courts:
        court.timetable = get_timetable(court, selected_date)
        court.temp_block = court.block if court.has_active_block else None
        court.club_name = court.club.name
        court.location = court.club.location

    available_courts = [c for c in courts if c.available_for_rent]

    return render(request, "booking/admin_dashboard.html", {
        "courts": courts,
        "available_courts": available_courts,
        "selected_date": selected_date,
    })