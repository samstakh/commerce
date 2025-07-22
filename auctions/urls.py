from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("activeList", views.activeList, name="activeList"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("addListing", views.addListing, name="addListing"),
    path("listing/<int:listing_id>/", views.listing_detail, name="listing_detail"),
    path("close/<int:listing_id>/", views.close_auction, name="close_auction"),
    path("watchlist/add/<int:listing_id>/", views.add_watchlist, name="add_watchlist"),
    path("watchlist/remove/<int:listing_id>/", views.remove_watchlist, name="remove_watchlist"),
    path("watchlist/", views.watchlist_view, name="watchlist"),
    path("categories/", views.category_view, name="category_view"),
    path("categories/<str:category_key>/", views.category_listings, name="category_listings")
]
