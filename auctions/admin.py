from django.contrib import admin
from .models import User, Listings, Bids, Comments
# Register your models here.
admin.site.register(User)
admin.site.register(Listings)
admin.site.register(Bids)
admin.site.register(Comments)