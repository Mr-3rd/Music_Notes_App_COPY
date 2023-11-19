from django.shortcuts import render, get_object_or_404

from ..models import Venue, Show
from ..forms import ShowSearchForm



from lmn.models import Show


def show_list(request ):
    """ gets the list of shows or searches and renders them"""
    
    # get the search form
    form = ShowSearchForm()
    
    # get the search parameter
    search_artist = request.GET.get('search_artist')
    search_venue = request.GET.get('search_venue')
    
    # filter the shows by date
    shows = Show.objects.all().order_by('-show_date') 
    # - meaning descending order and without means ascending order
     
     
    if search_artist:
        # filter the shows by artist name if it's searched by artist
        shows = shows.filter(artist__name__icontains=search_artist)
    
    if search_venue:
        shows = shows.filter(venue__name__icontains=search_venue)
        
    
    return render(request, 'lmn/shows/show_list.html', {'shows': shows, 'form': form})


def show_detail(request, show_pk):
    """ gets the show details and renders them, also renders the venue details, so we can use the location to give a but more detailed"""
    show = get_object_or_404(Show, pk=show_pk) # get the show details
    venue = get_object_or_404(Venue, pk=show.venue.pk) # get the venue details 
    return render(request, 'lmn/shows/show_detail.html', {'show': show, 'venue': venue})
        
    
