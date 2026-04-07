from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from .forms import ClubFilterForm, SignUpForm
from .mock_data import (
    TEMP_BLOCKS,
    filter_clubs,
    get_all_clubs,
    get_available_courts_by_club,
    get_club_by_id,
    get_court_by_id,
    get_courts_by_club,
    get_courts_by_club_and_sport,
    get_featured_clubs,
    get_timetable,
    get_blocked_slots,
    set_slot_block,
    set_court_availability,
)


def home(request):
    featured_clubs = get_featured_clubs()
    all_clubs = get_all_clubs()

    total_courts = sum(len(get_courts_by_club(club["id"])) for club in all_clubs)
    total_available = sum(len(get_available_courts_by_club(club["id"])) for club in all_clubs)

    stats = {
        "clubs": len(all_clubs),
        "courts": total_courts,
        "available": total_available,
        "sports": len(set(sport for club in all_clubs for sport in club.get("sports", []))),
        "avg_rating": round(sum(club["rating"] for club in all_clubs) / len(all_clubs), 1)
        if all_clubs else 0,
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
    clubs = get_all_clubs()

    if form.is_valid():
        sport = form.cleaned_data.get("sport")
        name = form.cleaned_data.get("name")
        sort_by = form.cleaned_data.get("sort_by")
        min_rating = form.cleaned_data.get("min_rating")
        max_rating = form.cleaned_data.get("max_rating")

        if min_rating is None:
            min_rating = 0

        if max_rating is None:
            max_rating = 5

        clubs = filter_clubs(
            sport=sport,
            name=name,
            sort_by=sort_by,
            min_rating=min_rating,
            max_rating=max_rating,
        )

    return render(request, "booking/club_list.html", {
        "form": form,
        "clubs": clubs,
    })


def club_detail(request, club_id):
    club = get_club_by_id(club_id)
    if not club:
        return redirect("club_list")

    courts = get_courts_by_club(club_id)
    available_courts = [court for court in courts if court["available_for_rent"]]

    return render(request, "booking/club_detail.html", {
        "club": club,
        "courts": courts,
        "available_courts": available_courts,
    })


def club_sport_courts(request, club_id, sport):
    club = get_club_by_id(club_id)
    if not club:
        return redirect("club_list")

    courts = get_courts_by_club_and_sport(club_id, sport)

    return render(request, "booking/club_sport_courts.html", {
        "club": club,
        "sport": sport,
        "courts": courts,
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")

    return render(request, "booking/signup.html", {
        "form": form
    })


@login_required
def reserve_court(request, court_id):
    court = get_court_by_id(court_id)
    if not court:
        return redirect("club_list")

    club = get_club_by_id(court["club_id"])

    if not court["available_for_rent"]:
        return redirect("club_detail", club_id=court["club_id"])

    reservations = request.session.get("reservations", [])
    timetable = get_timetable(court_id, reservations=reservations)
    available_slots = {slot["time"] for slot in timetable if slot["status"] == "available"}

    if request.method == "POST":
        slot = request.POST.get("slot")

        if not slot or slot not in available_slots:
            return render(request, "booking/reserve_court.html", {
                "club": club,
                "court": court,
                "timetable": timetable,
                "error": "Selecione um horário válido."
            })

        reservations.append({
            "club_id": club["id"],
            "club_name": club["name"],
            "court_id": court["id"],
            "court_name": court["name"],
            "sport": court["sport"],
            "location": club["location"],
            "slot": slot,
            "price_per_hour": court["price_per_hour"],
        })

        request.session["reservations"] = reservations
        return redirect("my_reservations")

    return render(request, "booking/reserve_court.html", {
        "club": club,
        "court": court,
        "timetable": timetable,
    })


@login_required
def my_reservations(request):
    reservations = request.session.get("reservations", [])
    return render(request, "booking/my_reservations.html", {
        "reservations": reservations
    })


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def admin_dashboard(request):
    if request.method == "POST":
        court_id = int(request.POST.get("court_id"))
        action = request.POST.get("action")
        if action == "toggle_slot":
            slot = request.POST.get("slot")
            blocked = request.POST.get("blocked") == "true"
            set_slot_block(court_id, slot, blocked=blocked)
        elif action == "disable":
            reason = request.POST.get("reason", "")
            until = request.POST.get("until", "")
            set_court_availability(court_id, False, reason=reason, until=until)
        elif action == "enable":
            set_court_availability(court_id, True)

        return redirect("admin_dashboard")

    clubs = get_all_clubs()
    enriched_courts = []

    for club in clubs:
        for court in get_courts_by_club(club["id"]):
            court_copy = court.copy()
            court_copy["club_name"] = club["name"]
            court_copy["location"] = club["location"]
            court_copy["temp_block"] = TEMP_BLOCKS.get(court["id"])
            court_copy["blocked_slots"] = sorted(get_blocked_slots(court["id"]))
            court_copy["timetable"] = get_timetable(court["id"])
            enriched_courts.append(court_copy)

    available_courts = [court for court in enriched_courts if court["available_for_rent"]]

    return render(request, "booking/admin_dashboard.html", {
        "courts": enriched_courts,
        "available_courts": available_courts,
    })
