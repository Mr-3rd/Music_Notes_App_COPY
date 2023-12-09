""" Views related to creating and viewing Notes for shows. """

from django.forms import ValidationError
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import Note, Show
from ..forms import NewNoteForm 

from django.utils import timezone

from django.contrib import messages  # Message to display


@login_required
def new_note(request, show_pk):
    """ Create a new note for a show. """
    show = get_object_or_404(Show, pk=show_pk)

    # checks that a note for this show doesn't already exist
    if Note.objects.filter(user=request.user, show=show).exists():
        form = NewNoteForm()  # empty form
        # if yes then take them render the form and also an error message and hide the button
        # render the form with an error message and hide the button and show the update button 
        return render(request, 'lmn/notes/new_note.html', {
            'form': form, 'show': show, 
            'error': 'You can only create one note per show', 
            "hide_button": True
        })
        
    if request.method == 'POST':
        form = NewNoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.show = show
            try: 
                note.save()
                return redirect('note_detail', note_pk=note.pk)
            # if an error occurs, show the error message 
            except ValidationError as e:
                # Show error message if the show date is in the future
                return HttpResponseBadRequest(render(request, 'lmn/notes/new_note.html', {'error': e}))

    else:
        form = NewNoteForm()

    return render(request, 'lmn/notes/new_note.html', {'form': form, 'show': show})

@login_required
def edit_note(request, show_pk):
    """ Edit a note for a show. each show should be having only one note instance per user"""
    show = get_object_or_404(Show, pk=show_pk) # get the show
    note = get_object_or_404(Note, show=show, user=request.user) # get the note for the show and user
    
    if request.method == 'POST': # update post request
        form = NewNoteForm(request.POST, request.FILES, instance=note) # create a form with the data from the request
        if form.is_valid():
            try: 
                form.save() # save the form
                return redirect('note_detail', note_pk=note.pk) # redirect to the note detail page
            # if an error occurs, show the error message 
            except ValidationError as e:
                # Show error message if the show date is in the future
                return HttpResponseBadRequest(render(request, 'lmn/notes/new_note.html', { 'error': e}))

    else:
        form = NewNoteForm(instance=note) # create a form with the data from the note

    return render(request, 'lmn/notes/edit_note.html', {'form': form, 'show': show, 'note': note})

def latest_notes(request):
    """ Get the 20 most recent notes, ordered with most recent first. """
    notes = Note.objects.all().order_by('-posted_date')[:20]   # slice of the 20 most recent notes
    return render(request, 'lmn/notes/note_list.html', {'notes': notes, 'title': 'Latest Notes'})


def notes_for_show(request, show_pk): 
    """ Get notes for one show, most recent first. """
    show = get_object_or_404(Show, pk=show_pk)  
    notes = Note.objects.filter(show=show_pk).order_by('-posted_date')

    dt = timezone.now()
    
    if request.user.is_authenticated: # we only wanna shows this to user if logged 
         if Note.objects.filter(user=request.user, show=show).exists(): # if the user has already created a note for this show instead of showing '"Add your own notes for this show" show "edit note" button'
            return render(request, 'lmn/notes/notes_for_show.html', {'show': show, 'notes': notes, 'hide_button': True})
            
    if show.show_date > dt:
        # Show error message if the show date is in the future, we also wanna show the show details but just not the notes
        return HttpResponseForbidden(render(request, 'lmn/notes/notes_for_show.html', {'show': show, 'error': 'You cannot add a note for a show that has not happened yet.'}))
    return render(request, 'lmn/notes/notes_for_show.html', {'show': show, 'notes': notes})


def note_detail(request, note_pk):
    """ Display one note. """
    note = get_object_or_404(Note, pk=note_pk)

    return render(request, 'lmn/notes/note_detail.html', {'note': note})

# Delete feature will be displayed within that note details, and only for the owner of those notes
# When a non login users tries to delete, it will redirect them to the login section


@login_required
def delete_note(request, note_pk):
    note = get_object_or_404(Note, pk=note_pk)

    # If the request is not from the note user (owner of those notes), then redirect them back to the login page and give them a message error
    if request.method == 'POST':
        # Check if current user is the owner of those notes they are about to delete
        if request.user != note.user:

            # Error Message for unauthorized user
            messages.error(request, 'Unauthorized user! Please use the correct login for that note account!')

            # Redirect to the login page
            return redirect('login')

        # Else, delete that note
        note.delete()
        # Redirect them to the latest notes
        return redirect('latest_notes')

    # Any thing else redirect them to the latest notes
    return redirect('latest_notes')
