from django import forms
from .models import Note

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError
from PIL import Image  # Used to open image and validate image format
from io import BytesIO


class VenueSearchForm(forms.Form):
    search_name = forms.CharField(label='Venue Name', max_length=200)


class ArtistSearchForm(forms.Form):
    search_name = forms.CharField(label='Artist Name', max_length=200)


class NewNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('title', 'text', 'photo', 'rating')

    # Check if the photo uploaded is valid
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')

        # print('photo:', photo) # Debug print will show photo name and extension or it will say 'None'

        # If there is a photo uploaded then check if the file is a valid image media upload  from users
        if photo:

            if not photo.content_type.startswith('image/'):
                raise ValidationError('Invalid Photo Upload! This upload was not a image upload!')
            try:
                # Open photo file
                users_image = Image.open(photo)

                # verify if image loads properly
                # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.verify
                users_image.verify()

            except Exception:
                raise ValidationError('Invalid Photo Upload! This upload was not a image upload!')

        return photo

class ShowSearchForm(forms.Form):
    # This is the search form which is used in show_list.html
    search_artist = forms.CharField(label='Artist Name', max_length=200, required=False)
    search_venue = forms.CharField(label='Venue Name', max_length=200, required=False)


class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data['username']

        if not username:
            raise ValidationError('Please enter a username')

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('A user with that username already exists')

        return username

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise ValidationError('Please enter your first name')

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name:
            raise ValidationError('Please enter your last name')

        return last_name

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError('Please enter an email address')

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('A user with that email address already exists')

        return email

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user
