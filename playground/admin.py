from django.contrib import admin

from .models import RSLeaderboardEntry
from .models import Weeklys
from .models import RaidsLeaderboard
from .models import GainsLeaderboard
from .models import PollResults
admin.site.register(GainsLeaderboard)
admin.site.register(RaidsLeaderboard)
admin.site.register(RSLeaderboardEntry)
admin.site.register(Weeklys)
admin.site.register(PollResults)