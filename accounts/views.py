from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm
from venues.models import Booking, Venue
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            
            form.save()
            
            username    = form.cleaned_data.get('username')
            password    = form.cleaned_data.get('password1')
            user        = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                # Authentication failed for some reason
                form.add_error(None, 'Authentication failed after signup.')
            
            # If there was a pending booking, finalize it
            booking_data    = request.session.get('booking_data')
            venue_id        = request.session.get('booking_venue_id')

            if booking_data and venue_id:
                try:
                    venue = Venue.objects.get(id = venue_id)

                    # Convert booking_date back to a Python date object
                    booking_date_str = booking_data.get('booking_date')
                    booking_date = datetime.fromisoformat(booking_date_str).date() if booking_date_str else None

                    number_of_people = booking_data.get('number_of_people', 1)

                    # Create the booking
                    Booking.objects.create(
                        user=user,
                        venue=venue,
                        booking_date=booking_date,
                        number_of_people=number_of_people
                    )

                    # Reduce available tables if needed
                    venue.available_tables = max(0, venue.available_tables - 1)
                    venue.save()

                    # Clean up the session
                    del request.session['booking_data']
                    del request.session['booking_venue_id']

                except Venue.DoesNotExist:
                    pass  # Optionally handle missing venue
                except Exception as e:
                    print("Error during post-signup booking:", e)  # Log or handle error
            
            if user.user_type == 'venue_admin':
                return redirect('venue_dashboard')
            else:
                return redirect('profile')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user

    # Redirect venue admins to their dashboard
    if user.user_type == 'venue_admin':
        return redirect('venue_dashboard')  # Ensure this URL name exists

    # Only customers can access profile with reservations
    elif user.user_type == 'customer':
        # Fetch all reservations for the user
        all_reservations = user.reservation_set.all()

        now = timezone.now()
        # Split reservations into upcoming and past based on combined date & time
        upcoming_reservations = [r for r in all_reservations if datetime.combine(r.date, r.time) >= now]
        past_reservations     = [r for r in all_reservations if datetime.combine(r.date, r.time) < now]

        context = {
            'user': user,
            'upcoming_reservations': upcoming_reservations,
            'past_reservations': past_reservations,
        }
        return render(request, 'accounts/profile.html', context)

    # For any other user types, redirect to home (fallback)
    else:
        return redirect('home')


def is_venue_admin(user):
    return user.is_authenticated and user.user_type == 'venue_admin'


@login_required
@user_passes_test(is_venue_admin)
def venue_dashboard_view(request):
    user = request.user
    venues = user.owned_venues.all()

    bookings = []
    reservations = []

    for venue in venues:
        bookings += list(venue.booking_set.all())
        reservations += list(venue.reservations.all())

    # Filtering reservations by date (optional)
    filter_date_str = request.GET.get('reservation_date')
    if filter_date_str:
        filter_date = parse_date(filter_date_str)
        if filter_date:
            reservations = [r for r in reservations if r.date == filter_date]
        else:
            messages.warning(request, "Invalid date format for filtering reservations.")

    # Paginate bookings and reservations (10 per page)
    bookings_paginator = Paginator(bookings, 10)
    reservations_paginator = Paginator(reservations, 10)

    bookings_page_number = request.GET.get('bookings_page')
    reservations_page_number = request.GET.get('reservations_page')

    bookings_page_obj = bookings_paginator.get_page(bookings_page_number)
    reservations_page_obj = reservations_paginator.get_page(reservations_page_number)

    context = {
        'venues': venues,
        'bookings_page_obj': bookings_page_obj,
        'reservations_page_obj': reservations_page_obj,
        'filter_date': filter_date_str or '',
    }
    return render(request, 'accounts/venue_dashboard.html', context)



@login_required
@user_passes_test(is_venue_admin)
def update_reservation_status(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Check that the user owns the venue of this reservation
    if reservation.venue.owner != request.user:
        messages.error(request, "You do not have permission to update this reservation.")
        return redirect('venue_dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Reservation.STATUS_CHOICES):
            reservation.status = new_status
            reservation.save()
            messages.success(request, f"Reservation status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status selected.")
        return redirect('venue_dashboard')

    # GET request: render a simple status update form
    return render(request, 'accounts/update_reservation_status.html', {'reservation': reservation, 'status_choices': Reservation.STATUS_CHOICES})
