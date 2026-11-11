from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.shortcuts import redirect, render

from .models import Athlete, Attendance, Coach, Group, News, Payment, Product, Workouts


def _normalize_identity(value):
    if value is None:
        return ''
    return str(value).strip().lower()


def get_logged_in_coach(user):
    if not user or not user.is_authenticated:
        return None

    if hasattr(user, 'coach_profile'):
        profile = getattr(user, 'coach_profile', None)
        if profile:
            return profile

    username = _normalize_identity(user.username)
    phone = _normalize_identity(getattr(user, 'phone', ''))
    if not username and not phone:
        return None

    queryset = Coach.objects.select_related('user')
    if username:
        coach = queryset.filter(user__username__iexact=username).first()
        if coach:
            return coach
    if phone:
        coach = queryset.filter(user__phone__iexact=phone).first()
        if coach:
            return coach
    return None


def get_logged_in_athlete(user):
    if not user or not user.is_authenticated:
        return None

    if hasattr(user, 'athlete_profile'):
        profile = getattr(user, 'athlete_profile', None)
        if profile:
            return profile

    username = _normalize_identity(user.username)
    phone = _normalize_identity(getattr(user, 'phone', ''))
    if not username and not phone:
        return None

    queryset = Athlete.objects.select_related('user')
    if username:
        athlete = queryset.filter(user__username__iexact=username).first()
        if athlete:
            return athlete
    if phone:
        athlete = queryset.filter(user__phone__iexact=phone).first()
        if athlete:
            return athlete
    return None


@login_required(login_url='login')
def home(request):
    coach = get_logged_in_coach(request.user)
    athlete = get_logged_in_athlete(request.user)
    if athlete and not coach:
        return redirect('profil')

    athletes_count = Athlete.objects.count()
    groups_count = Group.objects.count()
    today = date.today()
    today_attendance_count = Attendance.objects.filter(date=today).count()
    groups = Group.objects.select_related('course', 'coach').prefetch_related('students').all()
    recent_news = News.objects.order_by('-created_at')[:5]
    user_name = coach.f_name if coach else (request.user.get_full_name() or request.user.username)

    context = {
        'athletes_count': athletes_count,
        'groups_count': groups_count,
        'today_attendance_count': today_attendance_count,
        'groups': groups,
        'recent_news': recent_news,
        'user_name': user_name,
        'coach': coach,
    }
    return render(request, 'index.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
        messages.error(request, 'Login yoki parol xato!')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required(login_url='login')
def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')


@login_required(login_url='login')
def davomat(request):
    athlete = get_logged_in_athlete(request.user)
    coach = get_logged_in_coach(request.user)
    if athlete and not coach:
        return redirect('profil')

    groups = Group.objects.select_related('course', 'coach').prefetch_related('students').all()
    return render(request, 'davomat.html', {'groups': groups})


@login_required(login_url='login')
def davomat_guruh(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        student_id = request.POST.get('student_id')
        attendance_date = request.POST.get('date')
        status = request.POST.get('status')
        if group_id and student_id and attendance_date and status:
            group = Group.objects.filter(id=group_id).first()
            student = Athlete.objects.filter(id=student_id).first()
            if group and student and status in {'present', 'absent', 'late'}:
                Attendance.objects.update_or_create(
                    student=student,
                    group=group,
                    date=attendance_date,
                    defaults={'status': status},
                )
            elif group and student and status == 'empty':
                Attendance.objects.filter(student=student, group=group, date=attendance_date).delete()
        return redirect(f"{request.path}?group={group_id or ''}&month={request.POST.get('month') or date.today().strftime('%Y-%m')}")

    groups = Group.objects.select_related('course', 'coach').prefetch_related('students').all()
    group_id = request.GET.get('group')
    selected_group = groups.filter(id=group_id).first() if group_id else groups.first()
    students = selected_group.students.all().order_by('f_name') if selected_group else Athlete.objects.none()

    month = request.GET.get('month') or date.today().strftime('%Y-%m')
    year, month_num = map(int, month.split('-'))
    days_in_month = []
    for day_num in range(1, 32):
        try:
            current_date = date(year, month_num, day_num)
        except ValueError:
            break
        if current_date.month != month_num:
            continue
        if current_date.weekday() == 6:
            continue
        days_in_month.append({
            'day': day_num,
            'iso': current_date.isoformat(),
            'label': current_date.strftime('%d.%m'),
        })

    attendance_rows = []
    if selected_group:
        status_by_student_date = {
            (attendance.student_id, attendance.date.isoformat()): attendance.status
            for attendance in Attendance.objects.filter(group=selected_group, date__year=year, date__month=month_num)
        }

        for student in students:
            daily_statuses = []
            for day in days_in_month:
                status = status_by_student_date.get((student.id, day['iso']), 'empty')
                daily_statuses.append({'iso': day['iso'], 'day': day['day'], 'status': status})
            attendance_rows.append({'student': student, 'daily_statuses': daily_statuses})

    context = {
        'groups': groups,
        'selected_group': selected_group,
        'students': students,
        'attendance_rows': attendance_rows,
        'days': days_in_month,
        'month': month,
        'month_label': date(year, month_num, 1).strftime('%B %Y'),
    }
    return render(request, 'davomat-guruh.html', context)


@login_required(login_url='login')
def azolar(request):
    athlete = get_logged_in_athlete(request.user)
    coach = get_logged_in_coach(request.user)
    if athlete and not coach:
        return redirect('profil')

    athletes = Athlete.objects.prefetch_related('groups').all()
    groups = Group.objects.select_related('course', 'coach').all()
    return render(request, 'azolar.html', {'athletes': athletes, 'groups': groups})


@login_required(login_url='login')
def tolov(request):
    athlete = get_logged_in_athlete(request.user)
    coach = get_logged_in_coach(request.user)
    if athlete and not coach:
        return redirect('profil')

    groups = Group.objects.select_related('course', 'coach').prefetch_related('students').all()
    if coach:
        groups = groups.filter(coach=coach)

    payment_rows = []
    for group in groups:
        for athlete in group.students.all().order_by('f_name'):
            total_paid = Payment.objects.filter(athlete=athlete, group=group).aggregate(total=Sum('price'))['total'] or Decimal('0')
            fee = Decimal(str(group.course.price)) if group.course else Decimal('0')
            if total_paid >= fee:
                status = 'paid'
                status_label = "To'langan"
            elif total_paid > 0:
                status = 'partial'
                status_label = 'Qisman'
            else:
                status = 'unpaid'
                status_label = 'Qarzdor'

            payment_rows.append({
                'athlete': athlete,
                'group': group,
                'fee': fee,
                'paid': total_paid,
                'debt': max(fee - total_paid, Decimal('0')),
                'status': status,
                'status_label': status_label,
            })

    total_expected = sum((row['fee'] for row in payment_rows), Decimal('0'))
    total_collected = sum((row['paid'] for row in payment_rows), Decimal('0'))
    total_debt = total_expected - total_collected
    latest_payments = Payment.objects.select_related('athlete', 'group').order_by('-added_at')[:12]

    context = {
        'payment_rows': payment_rows,
        'total_expected': total_expected,
        'total_collected': total_collected,
        'total_debt': total_debt,
        'latest_payments': latest_payments,
        'coach': coach,
    }
    return render(request, 'tolov.html', context)


@login_required(login_url='login')
def yangiliklar(request):
    coach = get_logged_in_coach(request.user)
    athlete = get_logged_in_athlete(request.user)
    news = News.objects.order_by('-created_at')
    return render(request, 'yangiliklar.html', {
        'news': news,
        'coach': coach,
        'athlete': athlete,
        'can_manage_news': bool(coach and not athlete),
    })


@login_required(login_url='login')
def dokon(request):
    products = Product.objects.order_by('category', 'name')
    return render(request, 'dokon.html', {'products': products})


@login_required(login_url='login')
def profil(request):
    user = request.user
    coach = get_logged_in_coach(user)
    athlete = get_logged_in_athlete(user)
    user_name = coach.f_name if coach else (athlete.f_name if athlete else (user.get_full_name() or user.username))

    attendance_list = []
    payment_list = []

    if athlete and not coach:
        attendance_list = Attendance.objects.filter(student=athlete).order_by('-date')[:10]
        payment_list = Payment.objects.filter(athlete=athlete).select_related('group').order_by('-added_at')[:10]

    if request.method == 'POST':
        if coach:
            full_name = request.POST.get('f_name', '').strip() or request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            experience = request.POST.get('experience', '').strip()
            description = request.POST.get('description', '').strip()
            password = request.POST.get('password', '').strip()
            email = request.POST.get('email', user.email or '').strip()
            uploaded_image = request.FILES.get('image')

            if full_name:
                coach.f_name = full_name
            if phone:
                coach.phone = phone
            if experience:
                coach.experience = int(experience)
            coach.description = description or coach.description
            if uploaded_image:
                coach.image = uploaded_image
            coach.save()

            if full_name:
                user.first_name = full_name
            if email:
                user.email = email
            user.save()

            if password:
                user.set_password(password)
                user.save()

            return redirect('profil')

        if athlete and not coach:
            return redirect('profil')

    context = {
        'user': user,
        'athlete': athlete,
        'coach': coach,
        'user_name': user_name,
        'attendance_list': attendance_list,
        'payment_list': payment_list,
    }
    return render(request, 'profil.html', context)


def maxfiylik(request):
    return render(request, 'maxfiylik.html')


def ota_ona(request):
    return render(request, 'ota-ona-login.html')


def ota_ona_portal(request):
    return render(request, 'ota-ona.html')


def ota_ona_1(request):
    return render(request, 'ota-ona-1.html')


def ota_ona_2(request):
    return render(request, 'ota-ona-2.html')


def ota_ona_3(request):
    return render(request, 'ota-ona-3.html')


def ota_ona_4(request):
    return render(request, 'ota-ona-4.html')


def ota_ona_5(request):
    return render(request, 'ota-ona-5.html')


def ota_ona_6(request):
    return render(request, 'ota-ona-6.html')


@login_required(login_url='login')
def dev_console(request):
    return render(request, 'dev-console.html', {
        'athletes_count': Athlete.objects.count(),
        'groups_count': Group.objects.count(),
        'payments_count': Payment.objects.count(),
        'news_count': News.objects.count(),
    })
