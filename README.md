# hu-22-python-master

## Steps to run the example app on local environment:
1. Clone this repository: `git clone git@github.com:Deloitte/hu-22-python-master.git`

2. `cd hu-22-python-master`

3. Start a postgres container: `docker run --name hutemplatedb -e POSTGRES_PASSWORD=python -e POSTGRES_DB=python -e POSTGRES_USER=python -p 5432:5432 -d postgres:13.2`  

    (You can verify if container is running using `docker ps`)





4. In the root directory of project 'hu-22-python-master', create a new virtual environment: `python3 -m venv venv`

5. Activate the virtual environment: `source venv/bin/activate`

6. Install the project dependencies: `pip install -r requirements.txt`

7. Go to the app sub-directory: `cd app`

8. Create a **`local_settings.py`** file inside **`app/myproject`** directory and add the following:
  
    ```
    from myproject.settings import *

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'python',
            'USER': 'python',
            'PASSWORD': 'python',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```

    _(The values should be the same as the values given while starting  the docker container.)_
    


9. Run db migrations: `python manage.py migrate --settings=myproject.local_settings`.

    (In case User model needs to be customized, please create a User model before running first migration and before first merge to main branch.
    ```
    from django.contrib.auth.models import AbstractUser

    class User(AbstractUser):
        pass
    ```
    Please refer: https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#substituting-a-custom-user-model)

10. Create an admin user: `python manage.py createsuperuser --settings=myproject.local_settings`. Enter the requested details accordingly.

11. Start the development server: `python manage.py runserver --settings=myproject.local_settings` 

12. Login to the admin portal from: http://localhost:8000/admin/ (Use the superuser credentials to login)

13. APIs can be accessed from http://localhost:8000/api/persons/
14. To run test cases: `python manage.py test --settings=myproject.local_settings`
15. Before deploying to main branch: 
    -  Update the db details in settings.py with the db details of your production db server.
    -  Provide your username and password in the Docker file in the last line - 
    `CMD python manage.py migrate && python manage.py initadmin --username <provide your username --password <provide your password> --email <your email> && python manage.py runserver 0.0.0.0:8080`
16. #### For production:
    After the first deployment, go to "Actions" tab in github repo. -> Click on the Merge Request workflow pipeline. -> Click on "Setup, Build and Deploy" button. -> Expand "Deploy" sub-section. -> At the end you will find Service URL. This is the production URL where app will be hosted.

17. After the production url is generated, it needs to be added as part of `CSRF_TRUSTED_ORIGINS` and `ALLOWED_HOSTS` in settings.py.


## Useful material
1. **Python HU-22 course**

    - [Cura](https://becurious.edcast.eu/journey/hu-python-track-hu)

2. **Rest APIs**

    - [DRF official documentation](https://www.django-rest-framework.org/#)


3. **Writing unit tests**

    - [Django unit tests](https://docs.djangoproject.com/en/4.0/topics/testing/overview/#module-django.test)

    - [API tests](https://www.django-rest-framework.org/api-guide/testing/#testing)
