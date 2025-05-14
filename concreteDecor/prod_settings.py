# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
from concreteDecor.settings import DEBUG

ALLOWED_HOSTS = ['*']
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": "concretedecor",
        "USER": "concrete_user",
        "PASSWORD": "concrete_decor",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

DJOSER = {
    "EMAIL_FRONTEND_DOMAIN": "concrete-decor.ru",
    "EMAIL_FRONTEND_SITE_NAME": "Concrete Decor",
    'USER_CREATE_PASSWORD_RETYPE': True,
    "PASSWORD_RESET_CONFIRM_RETYPE": True,
    "PASSWORD_RESET_CONFIRM_URL": 'auth/users/reset_password_confirm/{uid}/{token}',
    'SERIALIZERS': {
        'user_create': 'api.serializers.user.CustomUserCreateSerializer',
        'user_create_password_retype': 'api.serializers.user.CustomUserCreateSerializer',
        'user': 'api.serializers.CustomUserCreateSerializer',
        'token_create': 'api.serializers.user.CustomTokenCreateSerializer',
    },
}