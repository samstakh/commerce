from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from collections import defaultdict

from .models import User, Listings, Bids, Comments


def index(request):

    listings = Listings.objects.all
    return render(request, "auctions/index.html", {
        "listings": listings
        })


def activeList(request):
    listings = Listings.objects.all
    return render(request, "auctions/activeList.html", {
        "listings": listings
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

def addListing(request):

    if request.method == "POST":
        title = request.POST["title"]
        price = request.POST["price"]
        image = request.POST["image"]
        description = request.POST["Content"]
        category = request.POST["category"]

        # ensure user enters a number price
        try:
            price = float(price)
        except ValueError:
            return render(request, "auctions/create.html", {
                "error": "Invalid price entered."
            })
        
        # enter it into database
        Listings.objects.create(
            title=title,
            price=price,
            image=image,
            description=description, 
            category=category,
            owner=request.user,
            
        )

        return redirect("index")

        



    return render(request, "auctions/create.html")



def listing_detail(request, listing_id):

    isHighest=False

    listing = get_object_or_404(Listings, id=listing_id)
    allBids = Bids.objects.filter(listing=listing).order_by('-amount')
    comments = Comments.objects.filter(listing=listing).order_by('-timestamp')




    if allBids.exists():
        highestBidObject = allBids.first()
        highestBid = highestBidObject.amount

        # check if user is the highest bidder
        if highestBidObject.user == request.user:
            isHighest = True
    else:
        highestBid = listing.price


    # handles form submission
    if request.method == "POST":
        amount = request.POST.get("amount")
        content = request.POST.get("comment")

        if content.strip():
            Comments.objects.create(user=request.user, listing=listing, content=content)
            messages.success(request, "Your comment has been posted.")
            return redirect("listing_detail", listing_id=listing.id)



        # check amount
        try:
            bidAmount = float(amount)
        except (TypeError, ValueError):
            messages.error(request, "please enter a valid number.")
            return redirect("isting_detail", listing_id=listing.id)
        
        if bidAmount < 0:
            messages.error(request, "bid cannot be negative.")

        elif bidAmount <= highestBid:
            messages.error(request, f"Your bid must be higher than ${highestBid}.")

        else:

            if Bids.objects.filter(listing=listing, user=request.user).exists():
                messages.error(request, "You have already placed the highest bid.")

            else: 

                isHighest = True
                Bids.objects.create (
                    listing=listing,
                    user=request.user,
                    amount=bidAmount
                )

                messages.success(request, "Your bid has been placed.")
                return redirect("listing_detail", listing_id=listing.id)
            

    return render(request, "auctions/listing.html", {
        "listing": listing, 
        "bids": allBids,
        "highestBid": highestBid,
        "count": len(allBids),
        "isHighest": isHighest,
        "comments": comments,
    })


@login_required
def close_auction(request, listing_id):

    # get the listing
    listing = get_object_or_404(Listings, pk=listing_id)


    if request.user != listing.owner:
        messages.error(request, "Unauthorized to close this listing")
        return redirect("listing_detail", listing_id=listing.id)
    
    highestBid = Bids.objects.filter(listing=listing).order_by('-amount').first()

    if highestBid and (highestBid != listing.price):
        listing.winner = highestBid.user
        listing.closed = True
        listing.save()

    return redirect("listing_detail", listing_id=listing.id)


@login_required
def add_watchlist(request, listing_id):

    listing = get_object_or_404(Listings, pk=listing_id)
    request.user.watchlist.add(listing)
    return redirect("listing_detail", listing_id=listing.id)


@login_required
def remove_watchlist(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)
    request.user.watchlist.remove(listing)
    return redirect("listing_detail", listing_id=listing.id)


@login_required
def watchlist_view(request):
    
    listings = request.user.watchlist.all()
    return render(request, "auctions/watchList.html", {
        "listings": listings
    })


# shows all categories as lists
def category_view(request):

    categories = Listings.CATEGORY_CHOICES
    print(categories)

    return render(request, "auctions/categoryView.html", {
        "categories": categories
    })


# show all listings for a selected category
def category_listings(request, category_key):


    listings= Listings.objects.filter(category=category_key, closed=False)

    return render(request, "auctions/categoryListings.html", {
        "listings": listings,
        "category": category_key
    })

    