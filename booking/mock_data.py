CLUBS = [
    {
        "id": 1,
        "name": "Clube Paulista Sports",
        "location": "Bela Vista, São Paulo",
        "rating": 4.8,
        "description": "Complexo esportivo com foco em locação de quadras para treinos e partidas.",
        "image": "images/default-court.svg",
        "sports": ["futsal", "tenis"],
        "featured": True,
    },
    {
        "id": 2,
        "name": "Arena Zona Sul",
        "location": "Santo Amaro, São Paulo",
        "rating": 4.6,
        "description": "Clube com múltiplas modalidades e estrutura para campeonatos amadores.",
        "image": "images/default-court.svg",
        "sports": ["volei", "beach_tennis", "futsal"],
        "featured": True,
    },
    {
        "id": 3,
        "name": "Centro Esportivo Moema",
        "location": "Moema, São Paulo",
        "rating": 4.7,
        "description": "Espaço premium para esportes de quadra com agendamento rápido.",
        "image": "images/default-court.svg",
        "sports": ["tenis", "beach_tennis"],
        "featured": False,
    },
]

COURTS = [
    {
        "id": 101,
        "club_id": 1,
        "name": "Quadra Futsal A",
        "sport": "futsal",
        "distance_km": 2.4,
        "rating": 4.8,
        "price_per_hour": 180,
        "available_for_rent": True,
        "description": "Quadra coberta com iluminação noturna e estrutura pronta para partidas competitivas.",
        "contact": "(11) 99999-1111",
        "slots": ["08:00", "09:00", "10:00", "18:00", "19:00", "20:00"],
        "image": "images/futsal.svg",
        "tags": ["Coberta", "Iluminação noturna", "Alta demanda"],
    },
    {
        "id": 102,
        "club_id": 1,
        "name": "Quadra Tênis 1",
        "sport": "tenis",
        "distance_km": 2.4,
        "rating": 4.9,
        "price_per_hour": 220,
        "available_for_rent": True,
        "description": "Quadra rápida com excelente manutenção e perfil ideal para treinos técnicos.",
        "contact": "(11) 99999-2222",
        "slots": ["07:00", "08:00", "17:00", "18:00"],
        "image": "images/tenis.svg",
        "tags": ["Piso rápido", "Premium", "Bem avaliada"],
    },
    {
        "id": 201,
        "club_id": 2,
        "name": "Quadra Vôlei Indoor",
        "sport": "volei",
        "distance_km": 6.8,
        "rating": 4.5,
        "price_per_hour": 150,
        "available_for_rent": False,
        "description": "Quadra indoor voltada para treinos, amistosos e locações em grupo.",
        "contact": "(11) 99999-3333",
        "slots": ["09:00", "10:00", "11:00", "19:00"],
        "image": "images/volei.svg",
        "tags": ["Indoor", "Treinos", "Grupos"],
    },
    {
        "id": 202,
        "club_id": 2,
        "name": "Areia Beach 1",
        "sport": "beach_tennis",
        "distance_km": 6.8,
        "rating": 4.7,
        "price_per_hour": 200,
        "available_for_rent": True,
        "description": "Estrutura completa com areia premium e ambiente pensado para experiência esportiva.",
        "contact": "(11) 99999-4444",
        "slots": ["06:00", "07:00", "08:00", "18:00", "19:00"],
        "image": "images/beach.svg",
        "tags": ["Areia premium", "Ambiente moderno", "Beach Tennis"],
    },
    {
        "id": 301,
        "club_id": 3,
        "name": "Quadra Tênis Pro",
        "sport": "tenis",
        "distance_km": 3.2,
        "rating": 4.8,
        "price_per_hour": 230,
        "available_for_rent": True,
        "description": "Quadra de tênis com piso profissional e iluminação de alta performance.",
        "contact": "(11) 99999-5555",
        "slots": ["06:00", "07:00", "19:00", "20:00"],
        "image": "images/tenis.svg",
        "tags": ["Premium", "Profissional"],
    },
]

TEMP_BLOCKS = {
    201: {
        "reason": "Manutenção do piso",
        "until": "2026-04-20",
    }
}
SLOT_BLOCKS = {}


def _get_sports_for_club(club_id):
    return sorted({court["sport"] for court in COURTS if court["club_id"] == club_id})


def _enrich_club(club):
    club_copy = club.copy()
    club_copy["sports"] = _get_sports_for_club(club["id"])
    return club_copy


def get_all_clubs():
    return [_enrich_club(club) for club in CLUBS]


def get_featured_clubs():
    return [_enrich_club(club) for club in CLUBS if club.get("featured")]


def get_club_by_id(club_id):
    for club in CLUBS:
        if club["id"] == club_id:
            return _enrich_club(club)
    return None


def filter_clubs(sport=None, name=None, min_rating=None, max_rating=None, sort_by=None):
    clubs = CLUBS

    if sport:
        clubs = [club for club in clubs if sport in club.get("sports", [])]

    if name:
        clubs = [club for club in clubs if name.lower() in club["name"].lower()]

    if min_rating is not None:
        clubs = [club for club in clubs if club["rating"] >= min_rating]

    if max_rating is not None:
        clubs = [club for club in clubs if club["rating"] <= max_rating]

    if sort_by == "rating":
        clubs = sorted(clubs, key=lambda x: x["rating"], reverse=True)
    elif sort_by == "name":
        clubs = sorted(clubs, key=lambda x: x["name"])

    return clubs


def get_courts_by_club(club_id):
    return [court for court in COURTS if court["club_id"] == club_id]


def get_courts_by_club_and_sport(club_id, sport=None):
    courts = get_courts_by_club(club_id)

    if sport:
        courts = [court for court in courts if court["sport"] == sport]

    return courts


def get_available_courts_by_club(club_id):
    return [court for court in get_courts_by_club(club_id) if court["available_for_rent"]]


def get_court_by_id(court_id):
    for court in COURTS:
        if court["id"] == court_id:
            return court
    return None


def get_reserved_slots(court_id, reservations):
    return {
        reservation["slot"]
        for reservation in reservations
        if reservation.get("court_id") == court_id
    }


def get_blocked_slots(court_id):
    return set(SLOT_BLOCKS.get(court_id, set()))


def get_timetable(court_id, reservations=None):
    court = get_court_by_id(court_id)
    if not court:
        return []

    reserved_slots = get_reserved_slots(court_id, reservations or [])
    blocked_slots = get_blocked_slots(court_id)

    timetable = []
    for slot in court["slots"]:
        if slot in reserved_slots:
            status = "booked"
        elif slot in blocked_slots:
            status = "blocked"
        else:
            status = "available"
        timetable.append({"time": slot, "status": status})

    return timetable


def set_slot_block(court_id, slot, blocked=True):
    court = get_court_by_id(court_id)
    if not court or slot not in court["slots"]:
        return False

    if blocked:
        SLOT_BLOCKS.setdefault(court_id, set()).add(slot)
    else:
        court_blocks = SLOT_BLOCKS.get(court_id, set())
        court_blocks.discard(slot)
        if not court_blocks and court_id in SLOT_BLOCKS:
            SLOT_BLOCKS.pop(court_id)
    return True


def set_court_availability(court_id, is_available, reason="", until=""):
    court = get_court_by_id(court_id)
    if not court:
        return False

    court["available_for_rent"] = is_available

    if is_available:
        TEMP_BLOCKS.pop(court_id, None)
    else:
        TEMP_BLOCKS[court_id] = {
            "reason": reason or "Indisponível temporariamente",
            "until": until or "Sem data definida",
        }

    return True
