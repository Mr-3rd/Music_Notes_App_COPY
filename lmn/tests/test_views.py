from django.test import TestCase

from django.urls import reverse
from django.contrib import auth
from django.contrib.auth import authenticate

import re
import datetime
from datetime import timezone

from lmn.models import Note
from django.contrib.auth.models import User

# Simple upload file library allows to create a "in memory file" that behaves like a file type that would be uploaded. Can customize what type of upload it is (e.g name, content, content type)
# https://stackoverflow.com/questions/11170425/how-to-unit-test-file-upload-in-django
from django.core.files.uploadedfile import SimpleUploadedFile
# Using a simple generated image using pillow library
from PIL import Image
# Import IO for file manipulation
import io


class TestHomePage(TestCase):

    def test_home_page_message(self):
        home_page_url = reverse('homepage')
        response = self.client.get(home_page_url)
        self.assertContains(response, 'Welcome to Live Music Notes, LMN')


class TestEmptyViews(TestCase):
    """ Main views - the ones in the navigation menu """

    def test_with_no_artists_returns_empty_list(self):
        response = self.client.get(reverse('artist_list'))
        self.assertFalse(response.context['artists'])  # An empty list is false

    def test_with_no_venues_returns_empty_list(self):
        response = self.client.get(reverse('venue_list'))
        self.assertFalse(response.context['venues'])  # An empty list is false

    def test_with_no_notes_returns_empty_list(self):
        response = self.client.get(reverse('latest_notes'))
        self.assertFalse(response.context['notes'])  # An empty list is false


class TestArtistViews(TestCase):
    fixtures = ['testing_artists', 'testing_venues', 'testing_shows']

    def test_all_artists_displays_all_alphabetically(self):
        response = self.client.get(reverse('artist_list'))

        # .* matches 0 or more of any character. Test to see if
        # these names are present, in the right order

        regex = '.*ACDC.*REM.*Yes.*'
        response_text = str(response.content)

        self.assertTrue(re.match(regex, response_text))
        self.assertEqual(len(response.context['artists']), 3)

    def test_artists_search_clear_link(self):
        response = self.client.get(reverse('artist_list'), {'search_name': 'ACDC'})

        # There is a 'clear' link on the page and, its url is the main venue page
        all_artists_url = reverse('artist_list')
        self.assertContains(response, all_artists_url)

    def test_artist_search_no_search_results(self):
        response = self.client.get(reverse('artist_list'), {'search_name': 'Queen'})
        self.assertNotContains(response, 'Yes')
        self.assertNotContains(response, 'REM')
        self.assertNotContains(response, 'ACDC')
        # Check the length of artists list is 0
        self.assertEqual(len(response.context['artists']), 0)

    def test_artist_search_partial_match_search_results(self):
        response = self.client.get(reverse('artist_list'), {'search_name': 'e'})
        # Should be two responses, Yes and REM
        self.assertContains(response, 'Yes')
        self.assertContains(response, 'REM')
        self.assertNotContains(response, 'ACDC')
        # Check the length of artists list is 2
        self.assertEqual(len(response.context['artists']), 2)

    def test_artist_search_one_search_result(self):
        response = self.client.get(reverse('artist_list'), {'search_name': 'ACDC'})
        self.assertNotContains(response, 'REM')
        self.assertNotContains(response, 'Yes')
        self.assertContains(response, 'ACDC')
        # Check the length of artists list is 1
        self.assertEqual(len(response.context['artists']), 1)

    def test_correct_template_used_for_artists(self):
        # Show all
        response = self.client.get(reverse('artist_list'))
        self.assertTemplateUsed(response, 'lmn/artists/artist_list.html')

        # Search with matches
        response = self.client.get(reverse('artist_list'), {'search_name': 'ACDC'})
        self.assertTemplateUsed(response, 'lmn/artists/artist_list.html')
        # Search no matches
        response = self.client.get(reverse('artist_list'), {'search_name': 'Non Existant Band'})
        self.assertTemplateUsed(response, 'lmn/artists/artist_list.html')

        # Artist detail
        response = self.client.get(reverse('artist_detail', kwargs={'artist_pk': 1}))
        self.assertTemplateUsed(response, 'lmn/artists/artist_detail.html')

        # Artist list for venue
        response = self.client.get(reverse('artists_at_venue', kwargs={'venue_pk': 1}))
        self.assertTemplateUsed(response, 'lmn/artists/artist_list_for_venue.html')

    def test_artist_detail(self):
        """ Artist 1 details displayed in correct template """
        # kwargs to fill in parts of url. Not get or post params

        response = self.client.get(reverse('artist_detail', kwargs={'artist_pk': 1}))
        self.assertContains(response, 'REM')
        self.assertEqual(response.context['artist'].name, 'REM')
        self.assertEqual(response.context['artist'].pk, 1)

    def test_get_artist_that_does_not_exist_returns_404(self):
        response = self.client.get(reverse('artist_detail', kwargs={'artist_pk': 10}))
        self.assertEqual(response.status_code, 404)

    def test_venues_played_at_most_recent_shows_first(self):
        # For each artist, display a list of venues they have played shows at.
        # Artist 1 (REM) has played at venue 2 (Turf Club) on two dates

        url = reverse('venues_for_artist', kwargs={'artist_pk': 1})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        show1, show2 = shows[0], shows[1]
        self.assertEqual(2, len(shows))

        self.assertEqual(show1.artist.name, 'REM')
        self.assertEqual(show1.venue.name, 'The Turf Club')

        # From the fixture, show 2's "show_date": "2017-02-02T19:30:00-06:00"
        expected_date = datetime.datetime(2017, 2, 2, 19, 30, 0, tzinfo=timezone.utc)
        self.assertEqual(show1.show_date, expected_date)

        # from the fixture, show 1's "show_date": "2017-01-02T17:30:00-00:00",
        self.assertEqual(show2.artist.name, 'REM')
        self.assertEqual(show2.venue.name, 'The Turf Club')
        expected_date = datetime.datetime(2017, 1, 2, 17, 30, 0, tzinfo=timezone.utc)
        self.assertEqual(show2.show_date, expected_date)

        # Artist 2 (ACDC) has played at venue 1 (First Ave)

        url = reverse('venues_for_artist', kwargs={'artist_pk': 2})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        show1 = shows[0]
        self.assertEqual(1, len(shows))

        # This show has "show_date": "2017-01-21T21:45:00-00:00",
        self.assertEqual(show1.artist.name, 'ACDC')
        self.assertEqual(show1.venue.name, 'First Avenue')
        expected_date = datetime.datetime(2017, 1, 21, 21, 45, 0, tzinfo=timezone.utc)
        self.assertEqual(show1.show_date, expected_date)

        # Artist 3, no shows

        url = reverse('venues_for_artist', kwargs={'artist_pk': 3})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        self.assertEqual(0, len(shows))


class TestVenues(TestCase):
    fixtures = ['testing_venues', 'testing_artists', 'testing_shows']

    def test_with_venues_displays_all_alphabetically(self):
        response = self.client.get(reverse('venue_list'))

        # .* matches 0 or more of any character. Test to see if
        # these names are present, in the right order

        regex = '.*First Avenue.*Target Center.*The Turf Club.*'
        response_text = str(response.content)

        self.assertTrue(re.match(regex, response_text))

        self.assertEqual(len(response.context['venues']), 3)
        self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')

    def test_venue_search_clear_link(self):
        response = self.client.get(reverse('venue_list'), {'search_name': 'Fine Line'})

        # There is a clear link, it's url is the main venue page
        all_venues_url = reverse('venue_list')
        self.assertContains(response, all_venues_url)

    def test_venue_search_no_search_results(self):
        response = self.client.get(reverse('venue_list'), {'search_name': 'Fine Line'})
        self.assertNotContains(response, 'First Avenue')
        self.assertNotContains(response, 'Turf Club')
        self.assertNotContains(response, 'Target Center')
        # Check the length of venues list is 0
        self.assertEqual(len(response.context['venues']), 0)
        self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')

    def test_venue_search_partial_match_search_results(self):
        response = self.client.get(reverse('venue_list'), {'search_name': 'c'})
        # Should be two responses, Yes and REM
        self.assertNotContains(response, 'First Avenue')
        self.assertContains(response, 'Turf Club')
        self.assertContains(response, 'Target Center')
        # Check the length of venues list is 2
        self.assertEqual(len(response.context['venues']), 2)
        self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')

    def test_venue_search_one_search_result(self):
        response = self.client.get(reverse('venue_list'), {'search_name': 'Target'})
        self.assertNotContains(response, 'First Avenue')
        self.assertNotContains(response, 'Turf Club')
        self.assertContains(response, 'Target Center')
        # Check the length of venues list is 1
        self.assertEqual(len(response.context['venues']), 1)
        self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')

    def test_venue_detail(self):
        # venue 1 details displayed in correct template
        # kwargs to fill in parts of url. Not get or post params
        response = self.client.get(reverse('venue_detail', kwargs={'venue_pk': 1}))
        self.assertContains(response, 'First Avenue')
        self.assertEqual(response.context['venue'].name, 'First Avenue')
        self.assertEqual(response.context['venue'].pk, 1)
        self.assertTemplateUsed(response, 'lmn/venues/venue_detail.html')

    def test_get_venue_that_does_not_exist_returns_404(self):
        response = self.client.get(reverse('venue_detail', kwargs={'venue_pk': 10}))
        self.assertEqual(response.status_code, 404)

    def test_artists_played_at_venue_most_recent_first(self):
        # Artist 1 (REM) has played at venue 2 (Turf Club) on two dates

        url = reverse('artists_at_venue', kwargs={'venue_pk': 2})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        show1, show2 = shows[0], shows[1]
        self.assertEqual(2, len(shows))

        self.assertEqual(show1.artist.name, 'REM')
        self.assertEqual(show1.venue.name, 'The Turf Club')

        expected_date = datetime.datetime(2017, 2, 2, 19, 30, 0, tzinfo=timezone.utc)
        self.assertEqual(show1.show_date, expected_date)

        self.assertEqual(show2.artist.name, 'REM')
        self.assertEqual(show2.venue.name, 'The Turf Club')
        expected_date = datetime.datetime(2017, 1, 2, 17, 30, 0, tzinfo=timezone.utc)
        self.assertEqual(show2.show_date, expected_date)

        # Artist 2 (ACDC) has played at venue 1 (First Ave)

        url = reverse('artists_at_venue', kwargs={'venue_pk': 1})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        show1 = shows[0]
        self.assertEqual(1, len(shows))

        self.assertEqual(show1.artist.name, 'ACDC')
        self.assertEqual(show1.venue.name, 'First Avenue')
        expected_date = datetime.datetime(2017, 1, 21, 21, 45, 0, tzinfo=timezone.utc)
        self.assertEqual(show1.show_date, expected_date)

        # Venue 3 has not had any shows

        url = reverse('artists_at_venue', kwargs={'venue_pk': 3})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        self.assertEqual(0, len(shows))

    def test_correct_template_used_for_venues(self):
        # Show all
        response = self.client.get(reverse('venue_list'))
        self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')

        # Search with matches
        response = self.client.get(reverse('venue_list'), {'search_name': 'First'})
        self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')

        # Search no matches
        response = self.client.get(reverse('venue_list'), {'search_name': 'Non Existant Venue'})
        self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')

        # Venue detail
        response = self.client.get(reverse('venue_detail', kwargs={'venue_pk': 1}))
        self.assertTemplateUsed(response, 'lmn/venues/venue_detail.html')

        response = self.client.get(reverse('artists_at_venue', kwargs={'venue_pk': 1}))
        self.assertTemplateUsed(response, 'lmn/artists/artist_list_for_venue.html')


class TestAddNoteUnauthentictedUser(TestCase):
    # Have to add artists and venues because of foreign key constrains in show
    fixtures = ['testing_artists', 'testing_venues', 'testing_shows']

    def test_add_note_unauthenticated_user_redirects_to_login(self):
        response = self.client.get('/notes/add/1/', follow=True)  # Use reverse() if you can, but not required.
        # Should redirect to login; which will then redirect to the notes/add/1 page on success.
        self.assertRedirects(response, '/accounts/login/?next=/notes/add/1/')


class TestAddNotesWhenUserLoggedIn(TestCase):
    fixtures = ['testing_users', 'testing_artists', 'testing_shows', 'testing_venues', 'testing_notes']

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)

    def test_save_note_for_non_existent_show_is_error(self):
        new_note_url = reverse('new_note', kwargs={'show_pk': 100})
        response = self.client.post(new_note_url)
        self.assertEqual(response.status_code, 404)

    def test_can_save_new_note_for_show_blank_data_is_error(self):
        initial_note_count = Note.objects.count()

        new_note_url = reverse('new_note', kwargs={'show_pk': 1})

        # No post params
        response = self.client.post(new_note_url, follow=True)
        # No note saved, should show same page
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # no title
        response = self.client.post(new_note_url, {'text': 'blah blah'}, follow=True)
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # no text
        response = self.client.post(new_note_url, {'title': 'blah blah'}, follow=True)
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # nothing added to database
        # 2 test notes provided in fixture, should still be 2
        self.assertEqual(Note.objects.count(), initial_note_count)

    def test_add_note_database_updated_correctly(self):
        initial_note_count = Note.objects.count()

        new_note_url = reverse('new_note', kwargs={'show_pk': 1})

        response = self.client.post(
            new_note_url,
            {'text': 'ok', 'title': 'blah blah'},
            follow=True)

        # Verify note is in database
        new_note_query = Note.objects.filter(text='ok', title='blah blah')
        self.assertEqual(new_note_query.count(), 1)

        # And one more note in DB than before
        self.assertEqual(Note.objects.count(), initial_note_count + 1)

        # Date correct?
        now = datetime.datetime.today()
        posted_date = new_note_query.first().posted_date
        self.assertEqual(now.date(), posted_date.date())  # TODO check time too

    def test_redirect_to_note_detail_after_save(self):
        new_note_url = reverse('new_note', kwargs={'show_pk': 1})
        response = self.client.post(
            new_note_url,
            {'text': 'ok', 'title': 'blah blah'},
            follow=True)

        new_note = Note.objects.filter(text='ok', title='blah blah').first()

        self.assertRedirects(response, reverse('note_detail', kwargs={'note_pk': new_note.pk}))


class TestUserProfile(TestCase):
    # Have to add artists and venues because of foreign key constrains in show
    fixtures = ['testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes']

    # verify correct list of reviews for a user
    def test_user_profile_show_list_of_their_notes(self):
        # get user profile for user 2. Should have 2 reviews for show 1 and 2.
        response = self.client.get(reverse('user_profile', kwargs={'user_pk': 2}))
        notes_expected = list(Note.objects.filter(user=2).order_by('-posted_date'))
        notes_provided = list(response.context['notes'])
        self.assertTemplateUsed('lmn/users/user_profile.html')
        self.assertEqual(notes_expected, notes_provided)

        # test notes are in date order, most recent first.
        # Note PK 3 should be first, then PK 2
        first_note = response.context['notes'][0]
        self.assertEqual(first_note.pk, 3)

        second_note = response.context['notes'][1]
        self.assertEqual(second_note.pk, 2)

    def test_user_with_no_notes(self):
        response = self.client.get(reverse('user_profile', kwargs={'user_pk': 3}))
        self.assertFalse(response.context['notes'])

    def test_username_shown_on_profile_page(self):
        # A string "username's notes" is visible
        response = self.client.get(reverse('user_profile', kwargs={'user_pk': 1}))
        self.assertContains(response, 'alice\'s notes')

        response = self.client.get(reverse('user_profile', kwargs={'user_pk': 2}))
        self.assertContains(response, 'bob\'s notes')

    def test_correct_user_name_shown_different_profiles(self):
        logged_in_user = User.objects.get(pk=2)
        self.client.force_login(logged_in_user)  # bob
        response = self.client.get(reverse('user_profile', kwargs={'user_pk': 2}))
        self.assertContains(response, 'You are logged in, <a href="/user/profile/2/">bob</a>.')

        # Same message on another user's profile. Should still see logged in message 
        # for currently logged in user, in this case, bob
        response = self.client.get(reverse('user_profile', kwargs={'user_pk': 3}))
        self.assertContains(response, 'You are logged in, <a href="/user/profile/2/">bob</a>.')


class TestNotes(TestCase):
    # Have to add Notes and Users and Show, and also artists and venues because of foreign key constrains in Show
    fixtures = ['testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes']

    def test_latest_notes(self):
        response = self.client.get(reverse('latest_notes'))
        # Should be note 3, then 2, then 1
        context = response.context['notes']
        first, second, third = context[0], context[1], context[2]
        self.assertEqual(first.pk, 3)
        self.assertEqual(second.pk, 2)
        self.assertEqual(third.pk, 1)

    def test_notes_for_show_view(self):
        # Verify correct list of notes shown for a Show, most recent first
        # Show 1 has 2 notes with PK = 2 (most recent) and PK = 1
        response = self.client.get(reverse('notes_for_show', kwargs={'show_pk': 1}))
        context = response.context['notes']
        first, second = context[0], context[1]
        self.assertEqual(first.pk, 2)
        self.assertEqual(second.pk, 1)

    def test_notes_for_show_when_show_not_found(self):
        response = self.client.get(reverse('notes_for_show', kwargs={'show_pk': 10000}))
        self.assertEqual(404, response.status_code)

    def test_correct_templates_uses_for_notes(self):
        response = self.client.get(reverse('latest_notes'))
        self.assertTemplateUsed(response, 'lmn/notes/note_list.html')

        response = self.client.get(reverse('note_detail', kwargs={'note_pk': 1}))
        self.assertTemplateUsed(response, 'lmn/notes/note_detail.html')

        response = self.client.get(reverse('notes_for_show', kwargs={'show_pk': 1}))
        self.assertTemplateUsed(response, 'lmn/notes/notes_for_show.html')

        # Log someone in
        self.client.force_login(User.objects.first())
        response = self.client.get(reverse('new_note', kwargs={'show_pk': 1}))
        self.assertTemplateUsed(response, 'lmn/notes/new_note.html')


class TestUserAuthentication(TestCase):
    """ Some aspects of registration (e.g. missing data, duplicate username) covered in test_forms """
    """ Currently using much of Django's built-in login and registration system """

    def test_user_registration_logs_user_in(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'sam12345',
                'email': 'sam@sam.com',
                'password1': 'feRpj4w4pso3az',
                'password2': 'feRpj4w4pso3az',
                'first_name': 'sam',
                'last_name': 'sam'
            },
            follow=True)

        # Assert user is logged in - one way to do it...
        user = auth.get_user(self.client)
        self.assertEqual(user.username, 'sam12345')

        # This works too. Don't need both tests, added this one for reference.
        # sam12345 = User.objects.filter(username='sam12345').first()
        # auth_user_id = int(self.client.session['_auth_user_id'])
        # self.assertEqual(auth_user_id, sam12345.pk)

    def test_user_registration_redirects_to_correct_page(self):
        # TODO If user is browsing site, then registers, once they have registered, they should
        # be redirected to the last page they were at, not the homepage.
        response = self.client.post(
            reverse('register'),
            {
                'username': 'sam12345',
                'email': 'sam@sam.com',
                'password1': 'feRpj4w4pso3az@1!2',
                'password2': 'feRpj4w4pso3az@1!2',
                'first_name': 'sam',
                'last_name': 'sam'
            },
            follow=True)
        new_user = authenticate(username='sam12345', password='feRpj4w4pso3az@1!2')
        self.assertRedirects(response, reverse('user_profile', kwargs={"user_pk": new_user.pk}))
        self.assertContains(response, 'sam12345')  # page has user's username on it


class TestErrorViews(TestCase):

    def test_404_view(self):
        response = self.client.get('this isnt a url on the site')
        self.assertEqual(404, response.status_code)
        self.assertTemplateUsed('404.html')

    def test_404_view_note(self):
        # example view that uses the database, get note with ID 10000
        response = self.client.get(reverse('note_detail', kwargs={'note_pk': 1}))
        self.assertEqual(404, response.status_code)
        self.assertTemplateUsed('404.html')

    def test_403_view(self):
        # there are no current views that return 403. When users can edit notes, or edit 
        # their profiles, or do other activities when it must be verified that the 
        # correct user is signed in (else 403) then this test can be written.
        pass

# Testing photo upload and redirecting feature after users upload a photo successfully 


class TestPhotoUpload(TestCase):
    # Need to create testing shows, artists,and venues to be able to create note and have a note id key.
    # Fixtures used the same from above tests
    fixtures = ['testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes'] 

    # SetUp method used from previous tests above
    # This gets the first user from User model, and then bypasses a request to login into that user without the need to know the password of that user. 
    def setUp(self):
        # Log someone in first
        user = User.objects.first()
        self.client.force_login(user)

    # This is to mimic a real file type to upload and the app only has a imagefield from the models where it only validates real image data that are accepted. So a random string or random binary data as a file will not pass the validation.
    # Static methods: https://www.toppr.com/guides/python-guide/references/methods-and-functions/methods/built-in/staticmethod/python-staticmethod/#:~:text=Methods%20and%20Functions-,Python%20staticmethod(),the%20Python%20staticmethod()%20function. - Doesn't need self, just a helper function
    @staticmethod
    def generate_testing_image_to_use(name='test_image.jpg'):
        # Understanding BytesIO()- My understanding, creates a file like data from string data. You can use it to manipulate binary data (images, audio,vids, etc) without making a physical file in system, instead just uses RAM.
        # https://levelup.gitconnected.com/python-stringio-and-bytesio-compared-with-open-c0e99b9def31#:~:text=StringIO%20and%20BytesIO%20are%20methods,to%20mimic%20a%20normal%20file. 
        # https://www.reddit.com/r/learnpython/comments/z9lfa7/class_bytes_vs_class_iobytesio/
        buffer_file = io.BytesIO()

        mock_image_creation = Image.new('RGB', (200, 200), color='grey')

        # Saving the image into the file buffer as a JPEG
        mock_image_creation.save(buffer_file, 'JPEG')

        # Move cursor before reading the file to the first (start) of the buffer
        buffer_file.seek(0)

        # Returns a mimic mock image file type (The buffer reads the content of the mock image file into the simple file uploaded)
        # https://stackoverflow.com/questions/11170425/how-to-unit-test-file-upload-in-django
        return SimpleUploadedFile(name, buffer_file.read(), content_type='image/jpeg')

    # Test a valid photo upload to ensure the page redirects as expected when the upload and save is done.
    def test_successful_photo_upload_and_redirects_to_note_detail_page(self):
        # Mock image uses simple upload file library method and pillow image creation. Calling this function would create a real mock image data to send for the mock post request
        mock_image = self.generate_testing_image_to_use()

        # Mock form data to send to create a new note 
        # Previous text and title used from above tests above but added photo for data to send as well with mock image created using pillow
        mock_form_data = {'text': 'ok', 'title': 'blah blah', 'photo': mock_image}

        new_note_url = reverse('new_note', kwargs={'show_pk': 1})

        # Response would redirect to the note_detail.html page after successful save and upload
        response = self.client.post(
            new_note_url, mock_form_data, follow=True
        )

        # Print the contents body of the response, should expect contents from note details 
        # print('Response', response.content)

        # Get first new note that was created
        new_note = Note.objects.filter(text='ok', title='blah blah').first()

        # Assert that the response redirected to note detail page:
        self.assertRedirects(response, reverse('note_detail', kwargs={
                             'note_pk': new_note.pk}))

        # Check if the response note_detail html page template was used
        self.assertTemplateUsed(response, 'lmn/notes/note_detail.html')

    # Test that the expected photo is returned when a page is loaded with notes
    def test_expected_photo_is_returned_when_note_detail_page_is_loaded(self):
        mock_image = self.generate_testing_image_to_use()

        # Mock form data to send to create a new note 
        # Previous text and title used from above tests above but added photo for data to send as well with mock image created using pillow
        mock_form_data = {'text': 'ok', 'title': 'blah blah', 'photo': mock_image}

        new_note_url = reverse('new_note', kwargs={'show_pk': 1})

        # Post req to send notes with uploaded photo to the new note url
        upload_mock_image_response = self.client.post(
            new_note_url, mock_form_data, follow=True
        )

        # First note retrieved
        new_note = Note.objects.filter(text='ok', title='blah blah').first()

        # Fetch note detail page of that new note created
        note_detail_url = reverse('note_detail', kwargs={'note_pk': new_note.pk})

        # Check if the upload post requests responses with a redirect to new note created
        self.assertRedirects(upload_mock_image_response, note_detail_url)

        # A get request response of the note detail page directly
        response_from_note_detail_url = self.client.get(note_detail_url)

        # Simple check if note detail page was used
        self.assertTemplateUsed(response_from_note_detail_url, 'lmn/notes/note_detail.html')

        # Expect photo from note detail page is returned when a page is loaded with notes
        # Checking to see if the note detail page response contains the photo url
        self.assertContains(response_from_note_detail_url, new_note.photo.url)

        # Checking the response
        # print(response_from_note_detail_url.content)


class TestLogoutPage(TestCase):

    def test_logout_page_message(self):
        logout_page_url = reverse('logout')
        response = self.client.get(logout_page_url)
        self.assertContains(response, 'Goodbye, see you next time.')

    def test_redirect_to_logout_page_when_user_logs_out(self):
        logout_page_url = reverse('logout')
        response = self.client.get(logout_page_url)
        self.assertEqual(200, response.status_code)
