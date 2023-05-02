from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Watchlist


def index(request):
    # Returns all active listsings
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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


def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        price = request.POST["price"]
        image = request.POST["image"]
        description = request.POST["description"]
        category = request.POST["category"]

        # Create new listing
        listing = Listing(title=title, price=price, image=image, description=description, category=category, creator=request.user)
        listing.save()
 
        return HttpResponseRedirect(reverse("index"))
    
    else:
        return render(request, "auctions/create.html")


def listing(request, title):
    listing = Listing.objects.get(title=title)

    # Signify if listing is auction is closed and alert winner
    if listing.closed == True:
        all_bids = Bid.objects.filter(item=listing)
        if all_bids.exists():
            winner = all_bids.order_by("-bid_amount").first()
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "winner": winner
            })
        
    if  not request.user.is_authenticated:
        return render(request, "auctions/listing.html", {
            "listing": listing,
        })
        
    else:
        watchlist = Watchlist.objects.filter(user=request.user, item=listing)
        bids = Bid.objects.filter(item=listing)
        comments = Comment.objects.filter(item=listing)
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "watchlist": watchlist,
            "bids": bids,
            "comments": comments
        })
    

@login_required
def watchlist(request):
    if request.method == "POST":
        title = request.POST["add"]
        listing = Listing.objects.get(title=title)

        # Save item to user's watchlist
        watchlist = Watchlist(user=request.user, item=listing)
        watchlist.save()

        # Display watchlist page
        watchlist_items = Watchlist.objects.filter(user=request.user)
        return render(request, "auctions/watchlist.html", {
            "watchlists": watchlist_items
        })

    else:
        watchlist_items = Watchlist.objects.filter(user=request.user)
        return render(request, "auctions/watchlist.html", {
            "watchlists": watchlist_items
        })
    

def remove_watchlist(request):
    if request.method == "POST":
        title = request.POST["remove"]
        listing = Listing.objects.get(title=title)

        # Get the Watchlist instance to be deleted
        watchlist = Watchlist.objects.filter(user=request.user, item=listing).first()
        if watchlist:
            watchlist.delete()
        return render(request, "auctions/watchlist.html", {
            "watchlists": Watchlist.objects.filter(user=request.user)
        })
    
    else:
        return render(request, "auctions/watchlist.html", {
            "watchlists": Watchlist.objects.filter(user=request.user)
        })

@login_required
def bid(request):
    if request.method == "POST":
        title = request.POST["listing"]
        listing = Listing.objects.get(title=title)
        bid = float(request.POST["bid"])
        all_bids = Bid.objects.filter(item=listing)

        # If any bid has been made on item
        if all_bids.exists():
            highest_bid = all_bids.order_by("-bid_amount").first().bid_amount
            if bid <= highest_bid:
                return HttpResponse("Bid must be greater than current highest bid!")
        else:
            # No bid has been made on item
            highest_bid = 0

        if bid < listing.price:
            return HttpResponse("Bid cannot be less than starting price")

        # Save user's bid
        new_bid = Bid(item=listing, bid_amount=bid, bidder=request.user)
        new_bid.save()
        
        return HttpResponseRedirect(reverse("listing", args=(title,)))
    
   
def close_auction(request):
    if request.method == "POST":
        listing = Listing.objects.get(title=request.POST["listing"])
        listing.closed = True
        listing.save()

        return HttpResponseRedirect(reverse("listing", args=(listing.title,)))


@login_required
def comment(request):
    if request.method == "POST":
        listing = Listing.objects.get(title=request.POST["listing"])
        comment = request.POST["comment"]
        user = request.user
        new_comment = Comment(item=listing, comment=comment, user=user)
        new_comment.save()

        return HttpResponseRedirect(reverse("listing", args=(listing.title,)))


# Displays a page containing all categories
def categories(request):
    listings = Listing.objects.all()
    return render(request, "auctions/categories.html", {
        "listings": listings
    })


# Displays a page containing listings in a selected category
def category(request, category):
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        "listings": listings
    })