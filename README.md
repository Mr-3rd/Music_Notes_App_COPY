# LMNOP

## Live Music Notes, Opinions, Photographs


### To install

1. Create and activate a virtual environment. Use Python3 as the interpreter. Suggest locating the venv/ directory outside of the code directory.
2. Once you have your environment set, add the `TICKETMASTER` key. The value for this key can be found in the project's Slack channel.

```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py ticketmaster
python manage.py runserver
```

Site at

http://127.0.0.1:8000


### Create superuser

```
python manage.py createsuperuser
```

enter username and password

Then you will be able to use these to log into admin console at

127.0.0.1:8000/admin/

Create some example Artists, Venues, and Shows for the app to use. A user will create Notes using the app. 

### Run tests


```
python manage.py test
```

Or just some of the tests,

```
python manage.py test lmn.tests.test_views
python manage.py test lmn.tests.test_views.TestUserAuthentication
python manage.py test lmn.tests.test_views.TestUserAuthentication.test_user_registration_logs_user_in
```


### Functional Tests with Selenium

Make sure you have the latest version of Chrome or Firefox, and the most recent chromedriver or geckodriver, and latest Selenium.

chromedriver/geckodriver needs to be in path or you need to tell Selenium where it is. Pick an approach: http://stackoverflow.com/questions/40208051/selenium-using-python-geckodriver-executable-needs-to-be-in-path

If your DB is hosted at Elephant, your tests might time out, and you might need to use longer waits http://selenium-python.readthedocs.io/waits.html

Run tests with

```
python manage.py test lmn.tests.functional_tests.functional_tests
```

Or select tests, for example,
```
python manage.py test lmn.functional_tests.functional_tests.HomePageTest
python manage.py test lmn.functional_tests.functional_tests.BrowseArtists.test_searching_artists
```


### Test coverage

From directory with manage.py in it,

```
coverage run --source='.' manage.py test lmn.tests
coverage report
```

### Linting

Ensure requirements are installed, then run,

```
flake8 .
```

Configure linting rules if desired in the .flake8 file. 

### Databases

You will likely want to configure the app to use SQLite locally, and PaaS database when deployed.  
