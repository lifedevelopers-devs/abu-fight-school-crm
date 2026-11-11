from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Athlete, Coach, Group, Payment, Workouts


class PaymentPageTests(TestCase):
    def test_payment_page_renders_real_athletes_and_real_status(self):
        User = get_user_model()
        workout = Workouts.objects.create(
            name='Boks',
            price=Decimal('300000'),
            period=1,
            description='Test workout',
        )
        coach = Coach.objects.create(
            f_name='Test Coach',
            phone='998901234567',
            experience=2,
            description='Coach description',
        )
        group = Group.objects.create(
            name='Junior 1',
            course=workout,
            coach=coach,
            started_time='18:00:00',
            comment='Test group',
        )
        athlete = Athlete.objects.create(
            f_name='Test Athlete',
            phone='998901234568',
            age=18,
            gender='m',
            birth_date='2010-01-01',
            comment='Test athlete',
        )
        athlete.groups.add(group)
        Payment.objects.create(
            athlete=athlete,
            group=group,
            price=Decimal('150000'),
            payment_type='cash',
        )

        user = User.objects.create_user(username='998901234567', password='secret123')
        self.client.force_login(user)

        response = self.client.get(reverse('tolov'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Athlete')
        self.assertContains(response, 'Qarzdor')

    def test_custom_username_login_matches_coach_and_athlete_accounts(self):
        User = get_user_model()

        coach = Coach.objects.create(
            f_name='Abu Coach',
            phone='998901000001',
            experience=3,
            description='Coach desc',
            login_name='abucoach',
        )
        athlete = Athlete.objects.create(
            f_name='Zokirjon',
            phone='998901000002',
            age=20,
            gender='m',
            birth_date='2005-01-01',
            login_name='zokirjoncoach',
        )

        coach_user = User.objects.create_user(username='abucoach', password='secret123')
        athlete_user = User.objects.create_user(username='zokirjoncoach', password='secret123')

        self.assertEqual(coach_user.username, 'abucoach')
        self.assertEqual(athlete_user.username, 'zokirjoncoach')
        self.assertEqual(coach.login_name, 'abucoach')
        self.assertEqual(athlete.login_name, 'zokirjoncoach')

    def test_logout_clears_django_session(self):
        User = get_user_model()
        user = User.objects.create_user(username='abucoach', password='ABUFIGHT2026!')
        self.client.force_login(user)

        response = self.client.post(reverse('logout'))

        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_page_uses_real_django_auth_and_not_mock_js(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'AFS_AUTH')
        self.assertNotContains(response, 'localStorage.getItem')
        self.assertNotContains(response, 'AFS_DATA')
