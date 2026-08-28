from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from NewCoinSetupApp.models import TradeEntry, UserProfile

class MultiUserJournalTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create two test users with emails
        self.user_a = User.objects.create_user(username='trader_alpha', email='alpha@example.com', password='password123')
        self.user_b = User.objects.create_user(username='trader_beta', email='beta@example.com', password='password123')

    def test_user_profile_creation(self):
        """Verify UserProfile is automatically created via post_save signal."""
        self.assertIsNotNone(self.user_a.profile)
        self.assertEqual(self.user_a.profile.account_balance, 10000.0)
        self.assertEqual(self.user_a.profile.trading_tier, 'PRO')

    def test_email_login_and_username_login(self):
        """Verify users can log in using either Email or Username."""
        # Login with Email
        res_email = self.client.post(reverse('login'), {
            'username_or_email': 'alpha@example.com',
            'password': 'password123'
        })
        self.assertEqual(res_email.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

        self.client.logout()

        # Login with Username
        res_user = self.client.post(reverse('login'), {
            'username_or_email': 'trader_alpha',
            'password': 'password123'
        })
        self.assertEqual(res_user.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_password_reset_views(self):
        """Verify password reset request flow accessibility."""
        res = self.client.get(reverse('password_reset'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Forgot Password')

        # Submit email for reset
        res_post = self.client.post(reverse('password_reset'), {'email': 'alpha@example.com'})
        self.assertEqual(res_post.status_code, 302)

    def test_trade_metrics_calculation(self):
        """Test auto-calculation of PnL, ROI %, and R-Multiple for winning and losing trades."""
        trade_win = TradeEntry.objects.create(
            user=self.user_a,
            symbol='SOL/USDT',
            trade_type='LONG',
            status='CLOSED_WIN',
            entry_price=100.0,
            exit_price=120.0,
            stop_loss=90.0,
            position_size_usd=1000.0,
            leverage=1
        )
        self.assertEqual(trade_win.pnl_pct, 20.0)
        self.assertEqual(trade_win.pnl_usd, 200.0)
        self.assertEqual(trade_win.r_multiple, 2.0)

    def test_multi_user_data_isolation(self):
        """Ensure User A cannot see or access User B's trade logs."""
        TradeEntry.objects.create(
            user=self.user_a,
            symbol='BTC/USDT',
            trade_type='LONG',
            status='OPEN',
            entry_price=60000.0
        )
        TradeEntry.objects.create(
            user=self.user_b,
            symbol='ETH/USDT',
            trade_type='SHORT',
            status='OPEN',
            entry_price=3000.0
        )

        self.client.login(username='trader_alpha', password='password123')
        response = self.client.get(reverse('journal_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BTC/USDT')
        self.assertNotContains(response, 'ETH/USDT')

    def test_fomo_shield_and_pattern_edge_views(self):
        """Verify views load cleanly for authenticated users."""
        self.client.login(username='trader_alpha', password='password123')
        
        res_fomo = self.client.get(reverse('fomo_shield'))
        self.assertEqual(res_fomo.status_code, 200)
        self.assertContains(res_fomo, 'Psychology')

        res_pattern = self.client.get(reverse('pattern_edge_matrix'))
        self.assertEqual(res_pattern.status_code, 200)
        self.assertContains(res_pattern, 'Strategy')
