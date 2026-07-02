from django.db import models
from django.contrib.auth.models import User

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
