"""Lógica central de disponibilidade: gera os horários reserváveis de uma quadra
em uma data (a partir das janelas por dia da semana) e calcula o status de cada um
(disponível / reservado / bloqueado).
"""

from datetime import date as date_cls

from .models import Reservation, SlotBlock


def generate_slot_times(court, on_date):
    """Horários de início ofertados pela quadra na data (ordenados, sem duplicar)."""
    weekday = on_date.weekday()
    times = set()
    for schedule in court.schedules.all():
        if schedule.weekday == weekday:
            times.update(schedule.slot_start_times(court.slot_minutes))
    return sorted(times)


def get_timetable(court, on_date):
    """Lista [{time: 'HH:MM', start_time, status}] para a quadra na data.

    status: available | booked | blocked
    """
    times = generate_slot_times(court, on_date)

    reserved = {
        r.start_time
        for r in Reservation.objects.filter(
            court=court, date=on_date, status="confirmed"
        )
    }
    blocked = {
        b.start_time for b in SlotBlock.objects.filter(court=court, date=on_date)
    }
    court_unavailable = not court.available_for_rent

    timetable = []
    for t in times:
        if t in reserved:
            status = "booked"
        elif court_unavailable or t in blocked:
            status = "blocked"
        else:
            status = "available"
        timetable.append({"time": t.strftime("%H:%M"), "start_time": t, "status": status})
    return timetable


def is_slot_available(court, on_date, start_time):
    for slot in get_timetable(court, on_date):
        if slot["start_time"] == start_time and slot["status"] == "available":
            return True
    return False


def parse_date(value, default=None):
    """Converte 'YYYY-MM-DD' em date; cai no default (ou hoje) se inválido."""
    if value:
        try:
            return date_cls.fromisoformat(value)
        except (ValueError, TypeError):
            pass
    return default or date_cls.today()


def parse_time(value):
    """Converte 'HH:MM' em time; retorna None se inválido."""
    from datetime import time

    if not value:
        return None
    try:
        hour, minute = value.split(":")
        return time(int(hour), int(minute))
    except (ValueError, AttributeError):
        return None