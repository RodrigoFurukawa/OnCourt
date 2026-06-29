"""Popula o banco com dados de exemplo (clubes, quadras, janelas de horário).

Uso:
    python manage.py seed_data
    python manage.py seed_data --flush   # zera os dados de booking antes

Não depende de fixtures externas — os dados de exemplo vivem aqui.
"""

from datetime import time

from django.core.management.base import BaseCommand
from django.db import transaction

from booking.models import (
    Club, Court, CourtSchedule, CourtBlock, SlotBlock, Reservation, Weekday,
)

# Janela padrão de funcionamento por dia da semana (abre, fecha).
DEFAULT_HOURS = {
    Weekday.MONDAY: (time(7, 0), time(23, 0)),
    Weekday.TUESDAY: (time(7, 0), time(23, 0)),
    Weekday.WEDNESDAY: (time(7, 0), time(23, 0)),
    Weekday.THURSDAY: (time(7, 0), time(23, 0)),
    Weekday.FRIDAY: (time(7, 0), time(23, 0)),
    Weekday.SATURDAY: (time(8, 0), time(20, 0)),
    Weekday.SUNDAY: (time(8, 0), time(18, 0)),
}

CLUBS = [
    {
        "name": "Clube Paulista Sports",
        "description": "Complexo esportivo com foco em locação de quadras para treinos e partidas.",
        "image": "images/default-court.svg",
        "rating": 4.8,
        "featured": True,
        "address": "Rua das Quadras, 100",
        "neighborhood": "Bela Vista",
        "city": "São Paulo",
        "state": "SP",
        "phone": "(11) 3000-1000",
        "email": "contato@paulistasports.com.br",
        "courts": [
            {
                "name": "Quadra Futsal A", "sport": "futsal", "size": "Society 25×15",
                "surface": "Sintético", "is_indoor": True, "price_per_hour": 180, "rating": 4.8,
                "contact": "(11) 99999-1111",
                "tags": ["Coberta", "Iluminação noturna", "Alta demanda"],
                "description": "Quadra coberta com iluminação noturna e estrutura pronta para partidas competitivas.",
            },
            {
                "name": "Quadra Tênis 1", "sport": "tenis", "size": "Oficial 23,77×10,97",
                "surface": "Piso rápido (hard)", "is_indoor": False, "price_per_hour": 220, "rating": 4.9,
                "contact": "(11) 99999-2222",
                "tags": ["Piso rápido", "Premium", "Bem avaliada"],
                "description": "Quadra rápida com excelente manutenção e perfil ideal para treinos técnicos.",
            },
            {
                "name": "Quadra Futsal B", "sport": "futsal", "size": "Society 25×15",
                "surface": "Sintético", "is_indoor": False, "price_per_hour": 170, "rating": 4.6,
                "contact": "(11) 99999-1212",
                "tags": ["Boa iluminação", "Custo-benefício", "Fácil acesso"],
                "description": "Quadra de futsal com piso em ótimo estado, ideal para jogos recreativos e treinos.",
            },
        ],
    },
    {
        "name": "Arena Zona Sul",
        "description": "Clube com múltiplas modalidades e estrutura para campeonatos amadores.",
        "image": "images/default-court.svg",
        "rating": 4.6,
        "featured": True,
        "address": "Av. Santo Amaro, 2500",
        "neighborhood": "Santo Amaro",
        "city": "São Paulo",
        "state": "SP",
        "phone": "(11) 3000-2000",
        "email": "contato@arenazonasul.com.br",
        "courts": [
            {
                "name": "Quadra Vôlei Indoor", "sport": "volei", "size": "Oficial 18×9",
                "surface": "Madeira", "is_indoor": True, "price_per_hour": 150, "rating": 4.5,
                "contact": "(11) 99999-3333", "available_for_rent": False,
                "tags": ["Indoor", "Treinos", "Grupos"],
                "description": "Quadra indoor voltada para treinos, amistosos e locações em grupo.",
            },
            {
                "name": "Areia Beach 1", "sport": "beach_tennis", "size": "Oficial 16×8",
                "surface": "Areia premium", "is_indoor": False, "price_per_hour": 200, "rating": 4.7,
                "contact": "(11) 99999-4444",
                "tags": ["Areia premium", "Ambiente moderno", "Beach Tennis"],
                "description": "Estrutura completa com areia premium e ambiente pensado para experiência esportiva.",
            },
        ],
    },
    {
        "name": "Centro Esportivo Moema",
        "description": "Espaço premium para esportes de quadra com agendamento rápido.",
        "image": "images/default-court.svg",
        "rating": 4.7,
        "featured": False,
        "address": "Alameda dos Esportes, 45",
        "neighborhood": "Moema",
        "city": "São Paulo",
        "state": "SP",
        "phone": "(11) 3000-3000",
        "email": "contato@cemoema.com.br",
        "courts": [
            {
                "name": "Quadra Tênis Pro", "sport": "tenis", "size": "Oficial 23,77×10,97",
                "surface": "Saibro", "is_indoor": False, "price_per_hour": 230, "rating": 4.8,
                "contact": "(11) 99999-5555",
                "tags": ["Premium", "Profissional"],
                "description": "Quadra de tênis com piso profissional e iluminação de alta performance.",
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Popula clubes, quadras e janelas de horário com dados de exemplo."

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Zera os dados de booking antes.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            Reservation.objects.all().delete()
            SlotBlock.objects.all().delete()
            CourtBlock.objects.all().delete()
            CourtSchedule.objects.all().delete()
            Court.objects.all().delete()
            Club.objects.all().delete()
            self.stdout.write(self.style.WARNING("Dados de booking apagados."))

        clubs = courts = schedules = 0
        for c in CLUBS:
            club, _ = Club.objects.update_or_create(
                name=c["name"],
                defaults={k: c[k] for k in (
                    "description", "image", "rating", "featured",
                    "address", "neighborhood", "city", "state", "phone", "email",
                )},
            )
            clubs += 1

            for ct in c["courts"]:
                court, _ = Court.objects.update_or_create(
                    club=club, name=ct["name"],
                    defaults={
                        "sport": ct["sport"],
                        "size": ct.get("size", ""),
                        "surface": ct.get("surface", ""),
                        "is_indoor": ct.get("is_indoor", False),
                        "price_per_hour": ct["price_per_hour"],
                        "rating": ct.get("rating", 0),
                        "tags": ct.get("tags", []),
                        "available_for_rent": ct.get("available_for_rent", True),
                        "description": ct.get("description", ""),
                        "contact": ct.get("contact", ""),
                        "image": ct.get("image", c["image"]),
                    },
                )
                courts += 1

                # (Re)cria as janelas de horário por dia da semana.
                court.schedules.all().delete()
                for weekday, (opening, closing) in DEFAULT_HOURS.items():
                    CourtSchedule.objects.create(
                        court=court, weekday=weekday, opening_time=opening, closing_time=closing,
                    )
                    schedules += 1

                # Exemplo de bloqueio de quadra (espelha o cenário antigo).
                if not ct.get("available_for_rent", True):
                    CourtBlock.objects.update_or_create(
                        court=court,
                        defaults={"reason": "Manutenção do piso", "until": "2026-07-20"},
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Seed concluído: {clubs} clubes, {courts} quadras, {schedules} janelas de horário."
        ))