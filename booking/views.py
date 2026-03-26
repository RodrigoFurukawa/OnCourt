from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import CourtFilterForm, SignUpForm
from .mock_data import (
    TEMP_BLOCKS,
    filter_courts,
    get_all_courts,
    get_available_courts,
    get_court_by_id,
    get_featured_courts,
    set_court_availability,
)


def home(request):
    featured_courts = get_featured_courts()

    stats = {
        "courts": len(get_all_courts()),
        "available": len(get_available_courts()),
        "sports": len(set(court["sport"] for court in get_all_courts())),
        "avg_rating": round(
            sum(court["rating"] for court in get_all_courts()) / len(get_all_courts()), 1
        ) if get_all_courts() else 0,
    }

    return render(request, "booking/home.html", {
        "featured_courts": featured_courts,
        "stats": stats,
    })


def about(request):
    return render(request, "booking/about.html")


def faq(request):
    return render(request, "booking/faq.html")


def contact(request):
    return render(request, "booking/contact.html")


def court_list(request):
    form = CourtFilterForm(request.GET or None)
    courts = get_all_courts()

    if form.is_valid():
        sport = form.cleaned_data.get("sport")
        name = form.cleaned_data.get("name")
        sort_by = form.cleaned_data.get("sort_by")
        availability = form.cleaned_data.get("availability")
        min_rating = form.cleaned_data.get("min_rating")
        max_rating = form.cleaned_data.get("max_rating")

        if min_rating is None:
            min_rating = 0

        if max_rating is None:
            max_rating = 5

        courts = filter_courts(
            sport=sport,
            name=name,
            sort_by=sort_by,
            availability=availability,
            min_rating=min_rating,
            max_rating=max_rating,
        )

    return render(request, "booking/court_list.html", {
        "form": form,
        "courts": courts,
    })


def court_detail(request, court_id):
    court = get_court_by_id(court_id)
    if not court:
        return redirect("court_list")

    return render(request, "booking/court_detail.html", {
        "court": court
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
        return redirect("court_list")

    if not court["available_for_rent"]:
        return redirect("court_detail", court_id=court_id)

    if request.method == "POST":
        slot = request.POST.get("slot")

        if not slot or slot not in court["slots"]:
            return render(request, "booking/reserve_court.html", {
                "court": court,
                "error": "Selecione um horário válido."
            })

        reservations = request.session.get("reservations", [])

        reservations.append({
            "court_id": court["id"],
            "court_name": court["name"],
            "location": court["location"],
            "slot": slot,
            "price_per_hour": court["price_per_hour"],
        })

        request.session["reservations"] = reservations
        return redirect("my_reservations")

    return render(request, "booking/reserve_court.html", {
        "court": court
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
        reason = request.POST.get("reason", "")
        until = request.POST.get("until", "")

        if action == "disable":
            set_court_availability(court_id, False, reason=reason, until=until)
        elif action == "enable":
            set_court_availability(court_id, True)

        return redirect("admin_dashboard")

    courts = get_all_courts()
    available_courts = get_available_courts()

    enriched_courts = []
    for court in courts:
        court_copy = court.copy()
        court_copy["temp_block"] = TEMP_BLOCKS.get(court["id"])
        enriched_courts.append(court_copy)

    return render(request, "booking/admin_dashboard.html", {
        "courts": enriched_courts,
        "available_courts": available_courts,
    })