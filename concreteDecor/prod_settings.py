# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
from concreteDecor.settings import DEBUG

ALLOWED_HOSTS = ['*']
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": "concretedecor",
        "USER": "admin",
        "PASSWORD": "1234",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
