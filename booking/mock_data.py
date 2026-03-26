COURTS = [
    {
        "id": 1,
        "name": "Arena Paulista Futsal",
        "sport": "futsal",
        "distance_km": 2.4,
        "rating": 4.8,
        "location": "Bela Vista, São Paulo",
        "price_per_hour": 180,
        "available_for_rent": True,
        "description": "Quadra coberta com iluminação noturna e estrutura pronta para partidas competitivas.",
        "contact": "(11) 99999-1111",
        "slots": ["08:00", "09:00", "10:00", "18:00", "19:00", "20:00"],
        "image": "images/futsal.svg",
        "featured": True,
        "tags": ["Coberta", "Iluminação noturna", "Alta demanda"],
    },
    {
        "id": 2,
        "name": "Clube Tênis Jardins",
        "sport": "tenis",
        "distance_km": 4.1,
        "rating": 4.9,
        "location": "Jardins, São Paulo",
        "price_per_hour": 220,
        "available_for_rent": True,
        "description": "Quadra rápida com excelente manutenção e perfil ideal para treinos técnicos.",
        "contact": "(11) 99999-2222",
        "slots": ["07:00", "08:00", "17:00", "18:00"],
        "image": "images/tenis.svg",
        "featured": True,
        "tags": ["Piso rápido", "Premium", "Bem avaliada"],
    },
    {
        "id": 3,
        "name": "Vôlei Center Zona Sul",
        "sport": "volei",
        "distance_km": 6.8,
        "rating": 4.5,
        "location": "Santo Amaro, São Paulo",
        "price_per_hour": 150,
        "available_for_rent": False,
        "description": "Quadra indoor voltada para treinos, amistosos e locações em grupo.",
        "contact": "(11) 99999-3333",
        "slots": ["09:00", "10:00", "11:00", "19:00"],
        "image": "images/volei.svg",
        "featured": False,
        "tags": ["Indoor", "Treinos", "Grupos"],
    },
    {
        "id": 4,
        "name": "Beach Point",
        "sport": "beach_tennis",
        "distance_km": 3.2,
        "rating": 4.7,
        "location": "Moema, São Paulo",
        "price_per_hour": 200,
        "available_for_rent": True,
        "description": "Estrutura completa com areia premium e ambiente pensado para experiência esportiva.",
        "contact": "(11) 99999-4444",
        "slots": ["06:00", "07:00", "08:00", "18:00", "19:00"],
        "image": "images/beach.svg",
        "featured": True,
        "tags": ["Areia premium", "Ambiente moderno", "Beach Tennis"],
    },
]

TEMP_BLOCKS = {
    3: {
        "reason": "Manutenção do piso",
        "until": "2026-03-25",
    }
}


def get_all_courts():
    return COURTS


def get_available_courts():
    return [court for court in COURTS if court["available_for_rent"]]


def get_court_by_id(court_id):
    for court in COURTS:
        if court["id"] == court_id:
            return court
    return None


def filter_courts(
    sport=None,
    name=None,
    sort_by=None,
    availability=None,
    min_rating=None,
    max_rating=None,
):
    courts = get_all_courts()

    if sport:
        courts = [court for court in courts if court["sport"] == sport]

    if name:
        courts = [court for court in courts if name.lower() in court["name"].lower()]

    if availability == "available":
        courts = [court for court in courts if court["available_for_rent"]]
    elif availability == "unavailable":
        courts = [court for court in courts if not court["available_for_rent"]]

    if min_rating is not None:
        courts = [court for court in courts if court["rating"] >= min_rating]

    if max_rating is not None:
        courts = [court for court in courts if court["rating"] <= max_rating]

    if sort_by == "distance":
        courts = sorted(courts, key=lambda x: x["distance_km"])
    elif sort_by == "rating":
        courts = sorted(courts, key=lambda x: x["rating"], reverse=True)
    elif sort_by == "name":
        courts = sorted(courts, key=lambda x: x["name"])

    return courts


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

def get_featured_courts():
    return [court for court in COURTS if court.get("featured")]
