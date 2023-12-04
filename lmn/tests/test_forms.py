from django.test import TestCase

from django.contrib.auth.models import User
from lmn.forms import NewNoteForm, UserRegistrationForm
import string
# Simple upload file library allows to create a "in memory file" that behaves like a regular upload. Can customize what type of upload it is (e.g name, content, content type)
# https://stackoverflow.com/questions/11170425/how-to-unit-test-file-upload-in-django
from django.core.files.uploadedfile import SimpleUploadedFile
# Using a simple generated image using pillow library
from PIL import Image
# Import IO for file manipulation
import io

from lmn.models import User, Show, Note

# Validation error for invalid media upload type
from django.core.exceptions import ValidationError

# Test that forms are validating correctly, and don't accept invalid data


class NewNoteFormTests(TestCase):
    fixtures = ['testing_users', 'testing_artists', 'testing_shows', 'testing_venues', 'testing_notes']

    def test_missing_title_is_invalid(self):
        form_data = {'text': 'blah blah'}
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())

        invalid_titles = list(string.whitespace) + ['   ', '\n\n\n', '\t\t\n\t']

        for invalid_title in invalid_titles:
            form_data = {'title': invalid_title, 'text': 'blah blah'}
            form = NewNoteForm(form_data)
            self.assertFalse(form.is_valid())

    def test_missing_text_is_invalid(self):
        form_data = {'title': 'blah blah'}
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())

        invalid_texts = list(string.whitespace) + ['   ', '\n\n\n', '\t\t\n\t']

        for invalid_text in invalid_texts:
            form_data = {'title': 'blah blah', 'text': invalid_text}
            form = NewNoteForm(form_data)
            self.assertFalse(form.is_valid())

    def test_title_too_long_is_invalid(self):
        # Max length is 200
        form_data = {'title': 'a' * 201}
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())

    def test_text_too_long_is_invalid(self):
        # Max length is 1000
        form_data = {'title': 'a' * 1001}
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())

    def test_ok_title_and_length_is_valid(self):
        form_data = {'title': 'blah blah', 'text': 'blah, blah, blah.'}
        form = NewNoteForm(form_data)
        self.assertTrue(form.is_valid())

    # Mock image generator using pillow
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

        # Returns a mimic mock image file upload (The buffer reads the content of the mock image file into the simple file uploaded)
        # https://stackoverflow.com/questions/11170425/how-to-unit-test-file-upload-in-django
        return SimpleUploadedFile(name, buffer_file.read(), content_type='image/jpeg')

    # Testing valid image file upload (happy path)
    def test_valid_image_uploaded_from_users(self):
        # Mock image provided by pillow image creation file
        mock_image = self.generate_testing_image_to_use()

        # Mock form data to send to NewNoteForm object
        # Mock Data taken from above tests, just added photo section as well
        form_data_with_photo_upload = {'title': 'blah blah', 'text': 'blah, blah, blah.'}

        # Attached files to the form data to send, I am not sure why we need to separate data and files, but before it would fail where files is not properly attached to the form data for the new note form object.
        files = {'photo': mock_image}

        # Creating NewNoteForm object with the valid form data with photo upload
        new_note_form = NewNoteForm(data=form_data_with_photo_upload, files=files)

        # Assert that the form is valid with valid photo uploaded
        self.assertTrue(new_note_form.is_valid())

        # Assert that uploaded photo is in notes_detail
        # First Instances for users and show models
        user = User.objects.first()  
        show = Show.objects.first()  

        # Check if form is valid, then save it 
        if new_note_form.is_valid():
            new_note = new_note_form.save(commit=False)
            new_note.user = user
            new_note.show = show
            new_note.save()

        # Retrieve the saved note with the latest ID (Recent note id that was just create)
        saved_note = Note.objects.latest('id')
        # Check if the photo's URL ends with .jpg, because mock image data created above is jpg.
        self.assertTrue(saved_note.photo.url.endswith('.jpg'))

    # Unhappy path, same as above test, but this time the photo upload will be invalid and we will assert that there is errors in photo field and assert the form.is_valid() is false
    def test_invalid_image_upload(self):
        mock_image = SimpleUploadedFile('Wishlist.txt', b'This is invalid content upload!', content_type='text/plain')

        data_mock = {'title': 'blah blah', 'text': 'blah, blah, blah.'}

        files = {'photo': mock_image}

        new_note_form = NewNoteForm(data=data_mock, files=files)

        # Checks if error is present for photo field
        self.assertIn('photo', new_note_form.errors)

        # This is not a valid form, since the image file is not an image, but a text file
        self.assertFalse(new_note_form.is_valid())


class RegistrationFormTests(TestCase):

    # check for missing fields

    def test_register_user_with_valid_data_is_valid(self):
        form_data = {
            'username': 'bob', 
            'email': 'bob@bob.com', 
            'first_name': 'bob', 
            'last_name': 'whatever', 
            'password1': 'q!w$er^ty6ui7op', 
            'password2': 'q!w$er^ty6ui7op'
        }

        form = UserRegistrationForm(form_data)
        self.assertTrue(form.is_valid())

    def test_register_user_with_missing_data_fails(self):
        form_data = {
            'username': 'bob', 
            'email': 'bob@bob.com', 
            'first_name': 'bob', 
            'last_name': 'whatever', 
            'password1': 'q!w$er^ty6ui7op', 
            'password2': 'q!w$er^ty6ui7op'
        }

        # Remove one key-value pair from a copy of the dictionary, assert form not valid
        for field in form_data.keys():
            copy_of_form_data = dict(form_data)
            del (copy_of_form_data[field])
            form = UserRegistrationForm(copy_of_form_data)
            self.assertFalse(form.is_valid())

    def test_register_user_with_password_mismatch_fails(self):
        form_data = {
            'username': 'another_bob', 
            'email': 'bob@bob.com', 
            'first_name': 'bob', 
            'last_name': 'whatever', 
            'password1': 'q!w$er^ty6ui7op', 
            'password2': 'dr%$ESwsdgdfh'
        }

        form = UserRegistrationForm(form_data)
        self.assertFalse(form.is_valid())

    def test_register_user_with_email_already_in_db_fails(self):
        # Create a user with email bob@bob.com
        bob = User(username='bob', email='bob@bob.com', first_name='bob', last_name='bob')
        bob.save()

        # attempt to create another user with same email
        form_data = {
            'username': 'another_bob', 
            'email': 'bob@bob.com', 
            'first_name': 'bob', 
            'last_name': 'whatever', 
            'password1': 'q!w$er^ty6ui7op', 
            'password2': 'q!w$er^ty6ui7op'
        }

        form = UserRegistrationForm(form_data)
        self.assertFalse(form.is_valid())

    def test_register_user_with_username_already_in_db_fails(self):

        # Create a user with username bob
        bob = User(username='bob', email='bob@bob.com')
        bob.save()

        # attempt to create another user with same username
        form_data = {
            'username': 'bob', 
            'email': 'another_bob@bob.com', 
            'first_name': 'bob', 
            'last_name': 'whatever', 
            'password1': 'q!w$er^ty6ui7op', 
            'password2': 'q!w$er^ty6ui7op'
        }

        form = UserRegistrationForm(form_data)
        self.assertFalse(form.is_valid())

    def test_register_user_with_username_already_in_db_case_insensitive_fails(self):
        # Create a user with username bob
        bob = User(username='bob', email='bob@bob.com')
        bob.save()

        invalid_username = ['BOB', 'BOb', 'Bob', 'bOB', 'bOb', 'boB']

        for invalid in invalid_username:
            # attempt to create another user with same username
            form_data = {
                'username': invalid, 
                'email': 'another_bob@bob.com', 
                'first_name': 'bob', 
                'last_name': 'whatever', 
                'password1': 'q!w$er^ty6ui7op', 
                'password2': 'q!w$er^ty6ui7opq!w$er^ty6ui7op'
            }

            form = UserRegistrationForm(form_data)
            self.assertFalse(form.is_valid())

    def test_register_user_with_email_already_in_db_case_insensitive_fails(self):
        # Create a user with username bob
        bob = User(username='bob', email='bob@bob.com')
        bob.save()

        invalid_email = ['BOB@bOb.com', 'BOb@bob.cOm', 'Bob@bob.coM', 'BOB@BOB.COM', 'bOb@bob.com', 'boB@bob.com']

        for invalid in invalid_email:
            # attempt to create another user with same username
            form_data = {
                'username': 'another_bob', 
                'email': invalid, 
                'first_name': 'bob', 
                'last_name': 'whatever', 
                'password1': 'q!w$er^ty6ui7op', 
                'password2': 'q!w$er^ty6ui7op'
            }
            form = UserRegistrationForm(form_data)
            self.assertFalse(form.is_valid())
