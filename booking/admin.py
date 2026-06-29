from django.contrib import admin

from .models import (
    Club, Court, CourtSchedule, CourtBlock, SlotBlock, Reservation,
)


class CourtInline(admin.TabularInline):
    model = Court
    extra = 0
    show_change_link = True


class CourtScheduleInline(admin.TabularInline):
    model = CourtSchedule
    extra = 0


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "neighborhood", "rating", "featured")
    list_filter = ("featured", "city")
    search_fields = ("name", "neighborhood", "city")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CourtInline]


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ("name", "club", "sport", "size", "price_per_hour", "available_for_rent", "rating")
    list_filter = ("sport", "available_for_rent", "is_indoor", "club")
    search_fields = ("name",)
    inlines = [CourtScheduleInline]


@admin.register(CourtBlock)
class CourtBlockAdmin(admin.ModelAdmin):
    list_display = ("court", "reason", "until")


@admin.register(SlotBlock)
class SlotBlockAdmin(admin.ModelAdmin):
    list_display = ("court", "date", "start_time", "reason")
    list_filter = ("date", "court")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("user", "court", "date", "start_time", "status", "created_at")
    list_filter = ("status", "date", "court")
    date_hierarchy = "date"