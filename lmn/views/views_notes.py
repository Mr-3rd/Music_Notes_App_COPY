""" Views related to creating and viewing Notes for shows. """

from django.forms import ValidationError
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import Note, Show
from ..forms import NewNoteForm 
from django.utils import timezone



@login_required
def new_note(request, show_pk):
    """ Create a new note for a show. """
    show = get_object_or_404(Show, pk=show_pk)

    # if the request is a POST request, then validate the form and save the note
    if request.method == 'POST':
        form = NewNoteForm(request.POST)
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
                return HttpResponseBadRequest(render(request, 'lmn/notes/new_note.html', { 'error': e}))
    else:
        form = NewNoteForm()

    return render(request, 'lmn/notes/new_note.html', {'form': form, 'show': show})


def latest_notes(request):
    """ Get the 20 most recent notes, ordered with most recent first. """
    notes = Note.objects.all().order_by('-posted_date')[:20]   # slice of the 20 most recent notes
    return render(request, 'lmn/notes/note_list.html', {'notes': notes, 'title': 'Latest Notes'})


def notes_for_show(request, show_pk): 
    """ Get notes for one show, most recent first. """
    show = get_object_or_404(Show, pk=show_pk)  
    notes = Note.objects.filter(show=show_pk).order_by('-posted_date')
    
    dt = timezone.now()
    
    if show.show_date > dt:
        # Show error message if the show date is in the future, we also wanna show the show details but just not the notes
        return HttpResponseForbidden(render(request, 'lmn/notes/notes_for_show.html', {'show': show, 'error': 'You cannot add a note for a show that has not happened yet.'}))
    return render(request, 'lmn/notes/notes_for_show.html', {'show': show, 'notes': notes})


def note_detail(request, note_pk):
    """ Display one note. """
    note = get_object_or_404(Note, pk=note_pk)
    return render(request, 'lmn/notes/note_detail.html', {'note': note})