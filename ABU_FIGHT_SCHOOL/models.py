from datetime import date

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


# ---------------------------------------------------------------
# 1. FOYDALANUVCHI (login, parol, rol shu yerda)
# ---------------------------------------------------------------
class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        COACH = "coach", "Murabbiy"
        ATHLETE = "athlete", "Sportchi"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.ATHLETE)
    phone = models.CharField(max_length=40, blank=True)

    @property
    def is_coach(self):
        return self.role == self.Role.COACH

    @property
    def is_athlete(self):
        return self.role == self.Role.ATHLETE

    def __str__(self):
        return self.get_full_name() or self.username


# ---------------------------------------------------------------
# 2. KURSLAR
# ---------------------------------------------------------------
class Workouts(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=16, decimal_places=2)
    period = models.PositiveIntegerField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ---------------------------------------------------------------
# 3. MURABBIY PROFILI (CustomUser ga bog'langan)
# ---------------------------------------------------------------
class Coach(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coach_profile",
    )
    f_name = models.CharField(max_length=35)
    experience = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to="coach_photos/", blank=True, null=True)

    def __str__(self):
        return self.f_name


# ---------------------------------------------------------------
# 4. GURUH
# ---------------------------------------------------------------
class Group(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Workouts, on_delete=models.PROTECT, related_name="groups")
    coach = models.ForeignKey(Coach, on_delete=models.PROTECT, related_name="groups")
    started_time = models.TimeField()
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# ---------------------------------------------------------------
# 5. SPORTCHI PROFILI (CustomUser ga bog'langan)
# ---------------------------------------------------------------
class Athlete(models.Model):
    GENDER = [
        ("m", "Erkak"),
        ("f", "Ayol"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="athlete_profile",
    )
    f_name = models.CharField(max_length=25)
    gender = models.CharField(max_length=2, choices=GENDER)
    birth_date = models.DateField()
    comment = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    groups = models.ManyToManyField(Group, related_name="students", blank=True)

    @property
    def age(self):
        """Yosh tug'ilgan sanadan avtomatik hisoblanadi."""
        today = date.today()
        b = self.birth_date
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

    def __str__(self):
        return self.f_name


# ---------------------------------------------------------------
# 6. DAVOMAT
# ---------------------------------------------------------------
class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Keldi"),
        ("absent", "Kelmadi"),
        ("late", "Kech qolgan"),
        ("excused", "Sababli"),
    ]

    student = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="present")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "group", "date"], name="one_day_one_student"
            )
        ]

    @property
    def status_label(self):
        return self.get_status_display()

    def __str__(self):
        return f"{self.student.f_name} - {self.date} ({self.status_label})"


# ---------------------------------------------------------------
# 7. TO'LOV
# ---------------------------------------------------------------
class Payment(models.Model):
    METHODS = [
        ("cash", "Naqd"),
        ("card", "Plastik karta"),
        ("payme", "Payme"),
        ("click", "Click"),
    ]

    athlete = models.ForeignKey(Athlete, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=16, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=METHODS, default="cash")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.athlete.f_name} - {self.price}"


# ---------------------------------------------------------------
# 8. YANGILIKLAR
# ---------------------------------------------------------------
class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# ---------------------------------------------------------------
# 9. MAHSULOTLAR
# ---------------------------------------------------------------
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name