# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
from concreteDecor.settings import DEBUG

ALLOWED_HOSTS = ['*']
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": "concretedecor",
        "USER": "cduser",
        "PASSWORD": "concrete_decor",
        "HOST": "127.0.0.1",
        "PORT": "5433",
    }
}
