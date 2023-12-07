from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

# Django's storage manager library that helps with retrieving, storing, deleting related media files. This helps with  the details on where to store it
from django.core.files.storage import default_storage

# Remember that every model gets a primary key field by default.

# The User model is provided by Django. The email field is not unique by
# default, so add this to prevent more than one user with the same email.
User._meta.get_field('email')._unique = True

# And, require email, first name, and last name for each user
User._meta.get_field('email')._blank = False
User._meta.get_field('last_name')._blank = False
User._meta.get_field('first_name')._blank = False


class Artist(models.Model):
    """ Represents a musician or a band - a music artist """
    name = models.CharField(max_length=200, blank=False)

    def __str__(self):
        return f'Name: {self.name}'


class Venue(models.Model):
    """ Represents a place that Shows take place at. """
    name = models.CharField(max_length=200, blank=False, unique=True)
    city = models.CharField(max_length=200, blank=False)
    state = models.CharField(max_length=2, blank=False)

    def __str__(self):
        return f'Name: {self.name} Location: {self.city}, {self.state}'


class Show(models.Model):
    """ One Artist playing at one Venue at a particular date and time. """
    show_date = models.DateTimeField(blank=False)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)

    def __str__(self):
        return f'Artist: {self.artist} At: {self.venue} On: {self.show_date}'


class Note(models.Model):
    """ One User's opinion of one Show. """

    STARS = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars')
    )

    # show = models.ForeignKey(Show, blank=False, on_delete=models.CASCADE, limit_choices_to={'show_date__lt': timezone.now()})

    show = models.ForeignKey(Show, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', blank=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False)
    text = models.TextField(max_length=1000, blank=False)
    rating = models.IntegerField(default=3, choices=STARS, validators=[MinValueValidator(1), MaxValueValidator(5)])
    posted_date = models.DateTimeField(auto_now_add=True, blank=False)

    # Image field to upload photos in the notes section from the main branch
    # Image upload is optional and can be null
    photo = models.ImageField(upload_to='user_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        """Create only one note for each user and show"""
        if Note.objects.filter(user=self.user, show=self.show).exists():
            raise ValidationError('You can only create one note per show')
        if self.show.show_date > timezone.now():
            raise ValidationError("Cannot add notes to future shows.")
        super(Note, self).save(*args, **kwargs)

    def __str__(self):
        # Photo Url will be generated if there is a photo uploaded, else it will display no photo
        photo_str = 'No photo uploaded yet!'
        if self.photo:
            # If there is a photo, get the photo url
            photo_str = self.photo.url

        return (f'User: {self.user} Show: {self.show} Note title: {self.title} \ '
                f'Text: {self.text} Posted on: {self.posted_date} Rating: {self.rating} Photo: {photo_str}')
