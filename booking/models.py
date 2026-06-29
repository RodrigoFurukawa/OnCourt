from datetime import date as date_cls, datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Sport(models.TextChoices):
    FUTSAL = "futsal", "Futsal"
    TENIS = "tenis", "Tênis"
    VOLEI = "volei", "Vôlei"
    BEACH_TENNIS = "beach_tennis", "Beach Tennis"
    BASQUETE = "basquete", "Basquete"


class Weekday(models.IntegerChoices):
    # Compatível com date.weekday(): segunda=0 ... domingo=6.
    MONDAY = 0, "Segunda"
    TUESDAY = 1, "Terça"
    WEDNESDAY = 2, "Quarta"
    THURSDAY = 3, "Quinta"
    FRIDAY = 4, "Sexta"
    SATURDAY = 5, "Sábado"
    SUNDAY = 6, "Domingo"


class Club(models.Model):
    """Clube — agrupa quadras e concentra as informações de local/contato."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=200, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    featured = models.BooleanField(default=False)

    # Localização estruturada
    address = models.CharField("Endereço", max_length=200, blank=True)
    neighborhood = models.CharField("Bairro", max_length=100, blank=True)
    city = models.CharField("Cidade", max_length=100, blank=True)
    state = models.CharField("UF", max_length=2, blank=True)
    postal_code = models.CharField("CEP", max_length=12, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Contato
    phone = models.CharField("Telefone", max_length=40, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    @property
    def location(self):
        """Resumo legível do local (ex.: 'Bela Vista, São Paulo - SP')."""
        parts = [p for p in (self.neighborhood, self.city) if p]
        label = ", ".join(parts)
        if self.state:
            label = f"{label} - {self.state}" if label else self.state
        return label

    @property
    def sports(self):
        """Esportes distintos ofertados pelas quadras do clube."""
        return sorted({court.sport for court in self.courts.all()})


class Court(models.Model):
    """Quadra — pertence a um clube e tem suas próprias especificidades."""

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="courts")
    name = models.CharField(max_length=120)
    sport = models.CharField(max_length=20, choices=Sport.choices)

    # Especificidades
    size = models.CharField("Tamanho/dimensões", max_length=60, blank=True)
    surface = models.CharField("Piso", max_length=60, blank=True)
    is_indoor = models.BooleanField("Coberta", default=False)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    tags = models.JSONField(default=list, blank=True)

    # Duração de cada horário reservável (minutos). Base da geração de slots.
    slot_minutes = models.PositiveIntegerField(default=60)

    available_for_rent = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    contact = models.CharField(max_length=40, blank=True)
    image = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["club_id", "name"]

    def __str__(self):
        return f"{self.name} ({self.club.name})"

    @property
    def has_active_block(self):
        return hasattr(self, "block")


class CourtSchedule(models.Model):
    """Janela de funcionamento de uma quadra em um dia da semana.

    Pode haver mais de uma janela por dia (ex.: manhã e noite). Os horários
    reserváveis são GERADOS a partir destas janelas + Court.slot_minutes.
    """

    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name="schedules")
    weekday = models.IntegerField(choices=Weekday.choices)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        ordering = ["court_id", "weekday", "opening_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["court", "weekday", "opening_time"],
                name="uniq_schedule_window",
            ),
        ]

    def __str__(self):
        return f"{self.court.name} {self.get_weekday_display()} {self.opening_time:%H:%M}-{self.closing_time:%H:%M}"

    def slot_start_times(self, slot_minutes):
        """Gera os horários de início dentro desta janela."""
        cursor = self.opening_time
        while True:
            end = (datetime.combine(date_cls.min, cursor) + timedelta(minutes=slot_minutes)).time()
            if end > self.closing_time:
                break
            yield cursor
            cursor = end
            if cursor >= self.closing_time:
                break


class ReservationStatus(models.TextChoices):
    CONFIRMED = "confirmed", "Confirmada"
    CANCELLED = "cancelled", "Cancelada"


class Reservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations"
    )
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name="reservations")
    date = models.DateField()
    start_time = models.TimeField()
    status = models.CharField(
        max_length=12, choices=ReservationStatus.choices, default=ReservationStatus.CONFIRMED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["court", "date", "start_time"], name="uniq_reservation_slot"
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.court.name} {self.date} {self.start_time:%H:%M}"

    @property
    def end_time(self):
        base = datetime.combine(self.date, self.start_time) + timedelta(minutes=self.court.slot_minutes)
        return base.time()

    # --- Conveniências para os templates ---
    @property
    def club_name(self):
        return self.court.club.name

    @property
    def court_name(self):
        return self.court.name

    @property
    def sport(self):
        return self.court.sport

    @property
    def location(self):
        return self.court.club.location

    @property
    def price_per_hour(self):
        return self.court.price_per_hour

    @property
    def slot(self):
        return f"{self.date:%d/%m} às {self.start_time:%H:%M}"


class CourtBlock(models.Model):
    """Bloqueio no nível da quadra (indisponível por completo, com motivo/prazo)."""

    court = models.OneToOneField(Court, on_delete=models.CASCADE, related_name="block")
    reason = models.CharField(max_length=200, default="Indisponível temporariamente")
    until = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bloqueio: {self.court.name} ({self.reason})"


class SlotBlock(models.Model):
    """Bloqueio de um horário específico de uma quadra em uma data."""

    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name="slot_blocks")
    date = models.DateField()
    start_time = models.TimeField()
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["court_id", "date", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["court", "date", "start_time"], name="uniq_slot_block"
            ),
        ]

    def __str__(self):
        return f"Bloqueio {self.court.name} {self.date} {self.start_time:%H:%M}"