from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ABU_FIGHT_SCHOOL.models import (
    Athlete,
    Attendance,
    Coach,
    CustomUser,
    Group,
    News,
    Payment,
    Product,
    Workouts,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "role", "phone", "is_active")
    list_filter = ("role", "is_active")

    # Mavjud foydalanuvchini tahrirlash sahifasi
    fieldsets = UserAdmin.fieldsets + (
        ("Qo'shimcha ma'lumot", {"fields": ("role", "phone")}),
    )
    # Yangi foydalanuvchi qo'shish sahifasi
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Qo'shimcha ma'lumot", {"fields": ("role", "phone")}),
    )


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ("f_name", "user", "experience")


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ("f_name", "user", "gender", "birth_date")


admin.site.register(Workouts)
admin.site.register(Group)
admin.site.register(Attendance)
admin.site.register(Payment)
admin.site.register(News)
admin.site.register(Product)