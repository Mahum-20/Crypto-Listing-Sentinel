from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    TIER_CHOICES = [
        ('FREE', 'Free Starter'),
        ('PRO', 'Pro Trader'),
        ('INSTITUTIONAL', 'Institutional Edge'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    account_balance = models.FloatField(default=10000.0)
    risk_per_trade_pct = models.FloatField(default=2.0)
    trading_tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='PRO')
    avatar_symbol = models.CharField(max_length=10, default='⚡')

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.trading_tier})"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()


PATTERN_TAG_CHOICES = [
    ('Pump → Dump → Accumulate', 'Pump → Dump → Accumulate (Classic Retail Trap)'),
    ('Instant Dump → Range → Slow Recovery', 'Instant Dump → Range → Slow Recovery (VC Dump)'),
    ('Slow Bleed Downwards', 'Slow Bleed Downwards (Low Demand, High FDV)'),
    ('Pump → Hold High → Expand', 'Pump → Hold High → Expand (Institutional Support)'),
    ('Fake Pump → Sharp Dump → Dead Range', 'Fake Pump → Sharp Dump (Rug Risk)'),
    ('Sideways First → Breakout Later', 'Sideways First → Breakout Later (Stealth Accumulation)'),
    ('Pump → Fake Dump → V-Shaped Recovery', 'Pump → Fake Dump → V-Recovery (Liquidity Trap)'),
    ('Announcement Arb Pump → Quick Fade', 'Announcement Arb Pump → Quick Fade (Bot Frenzy)'),
    ('Futures-Led Cascade', 'Futures-Led Cascade (Perp Dominance)'),
    ('Exploit/Backlash Dump → Rebound', 'Exploit Dump → Rebound (Narrative Fix)'),
    ('Delisting Shadow', 'Delisting Shadow (Pre-delist Bleed)'),
    ('Narrative Rotation Surge', 'Narrative Rotation Surge (Chain Hop)'),
]

PSYCHOLOGY_CHOICES = [
    ('DISCIPLINED', '🎯 Disciplined Execution'),
    ('FOMO_ENTRY', '🔥 FOMO / Chasing Pump'),
    ('REVENGE_TRADE', '😡 Revenge Trade after Loss'),
    ('EARLY_EXIT', '😰 Early Exit / Fear of Loss'),
    ('GREED_OVERLEVERAGED', '🤑 Greed / Over-leveraged'),
    ('PANIC_CUT', '😱 Panic Cut at Lows'),
]

STATUS_CHOICES = [
    ('OPEN', 'Open'),
    ('CLOSED_WIN', 'Closed (Win)'),
    ('CLOSED_LOSS', 'Closed (Loss)'),
    ('CLOSED_BREAKEVEN', 'Closed (Breakeven)'),
    ('CANCELLED', 'Cancelled'),
]

TRADE_TYPE_CHOICES = [
    ('LONG', 'Long'),
    ('SHORT', 'Short'),
]

class TradeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades')
    symbol = models.CharField(max_length=20)
    trade_type = models.CharField(max_length=10, choices=TRADE_TYPE_CHOICES, default='LONG')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    entry_price = models.FloatField()
    exit_price = models.FloatField(null=True, blank=True)
    stop_loss = models.FloatField(null=True, blank=True)
    take_profit = models.FloatField(null=True, blank=True)
    
    position_size_usd = models.FloatField(default=1000.0)
    leverage = models.IntegerField(default=1)
    
    pnl_usd = models.FloatField(default=0.0)
    pnl_pct = models.FloatField(default=0.0)
    r_multiple = models.FloatField(default=0.0)
    
    pattern_tag = models.CharField(max_length=100, choices=PATTERN_TAG_CHOICES, blank=True, null=True)
    psychology_state = models.CharField(max_length=50, choices=PSYCHOLOGY_CHOICES, default='DISCIPLINED')
    
    notes = models.TextField(blank=True)
    chart_url = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} | {self.trade_type} {self.symbol} ({self.status})"

    @property
    def abs_pnl_usd(self):
        return round(abs(self.pnl_usd), 2)

    def calculate_metrics(self):
        """Auto-calculate PnL, ROI %, and R-Multiple based on entry, exit, position size, and stop loss."""
        if self.status != 'OPEN' and self.exit_price is not None and self.entry_price > 0:
            if self.trade_type == 'LONG':
                raw_diff = self.exit_price - self.entry_price
                pct = (raw_diff / self.entry_price) * 100 * self.leverage
            else:
                raw_diff = self.entry_price - self.exit_price
                pct = (raw_diff / self.entry_price) * 100 * self.leverage

            self.pnl_pct = round(pct, 2)
            self.pnl_usd = round((self.position_size_usd * (pct / 100)), 2)

            # R-Multiple calculation
            if self.stop_loss and self.stop_loss != self.entry_price:
                risk_per_unit = abs(self.entry_price - self.stop_loss)
                reward_per_unit = raw_diff
                if risk_per_unit > 0:
                    self.r_multiple = round(reward_per_unit / risk_per_unit, 2)
                else:
                    self.r_multiple = 0.0
            else:
                self.r_multiple = round(pct / 10.0, 2) # fallback estimate
        elif self.status == 'OPEN':
            self.pnl_usd = 0.0
            self.pnl_pct = 0.0
            self.r_multiple = 0.0

    def save(self, *args, **kwargs):
        self.calculate_metrics()
        super().save(*args, **kwargs)


class TradeChecklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coin_name = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coin_name} - {self.user.username}"

class ChecklistItem(models.Model):
    trade = models.ForeignKey(TradeChecklist, on_delete=models.CASCADE, related_name="items")
    step_name = models.CharField(max_length=100)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.step_name} - {self.trade.coin_name}"
