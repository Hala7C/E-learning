
from pathlib import Path
import os
from datetime import timedelta
from decouple import config, Csv
from django.conf import global_settings
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(kry3o%mahw$e79k3tc4guo2cr(*sn+x=a!35l8c%-xwaxhe4u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "daphne",
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'newapp',
    'rest_framework.authtoken',
    'mainAuth',
    'djoser',
    'social_django',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'trainer',
    'axes',
    'parler',
    'qrcode',
    'storages',
    'django_filters',
    'minio_storage', 
    'payments',
    'rating',
    'AdminDashBoard',


]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'mainAuth.middleware.LanguageMiddleware',
]

ROOT_URLCONF = 'eLearning.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':[os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

# WSGI_APPLICATION = 'eLearning.wsgi.application'
ASGI_APPLICATION = 'eLearning.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':config('POSTGRES_NAME') ,
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST'),
        'PORT': config('POSTGRES_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en'


TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('en', ('English')),
    ('ar', ('Arabic')),
)

LOCALE_PATHS = [
    os.path.join(BASE_DIR,'locale')
    
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


DJOSER={
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE':True,
    'USERNAME_CHANGED_EMAIL_CONFIRMATION':True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION':True,
    'SEND_CONFIRMATION_EMAIL':True,
    'SET_USERNAME_RETYPE':True,
    'SET_PASSWORD_RETYPE':True,
    'PASSWORD_RESET_CONFIRM_URL':'password-reset/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL' :'email-reset/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL':True,
    # 'SOCIAL_AUTH_TOKEN_STRATEGY':'djoser.social.token.jwt.TokenStrategy',
    'TOKEN_MODEL':'rest_framework.authtoken.models.Token',
    'SOCIAL_AUTH_TOKEN_STRATEGY':'mainAuth.token.authToken.CustomTokenStrategy',
    'SOCIAL_AUTH_ALLOWED_REDIRECT_URIS':config('SOCIAL_AUTH_ALLOWED_REDIRECT_URIS', cast=Csv()),
    'EMAIL': {
        'activation': 'mainAuth.email.ActivationEmail',
        # Add other email actions and their corresponding template paths here
    },
    'SERIALIZERS':{
        'user_create': 'mainAuth.serializer.UserRegistrationSerializer',
        'user': 'mainAuth.serializers.UserRegistrationSerializer',
        'current_user':'mainAuth.serializers.UserRegistrationSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializers',
        'social_login': 'mainAuth.serializers.CustomSocialLoginSerializer',
    }
    
}
REST_FRAMEWORK = {
   'DEFAULT_AUTHENTICATION_CLASSES': (
       'rest_framework.authentication.TokenAuthentication',
    #    'rest_framework_simplejwt.authentication.JWTAuthentication',
   ),
   'DEFAULT_PERMISSION_CLASSES': ( 
       'rest_framework.permissions.IsAuthenticated',
    #    'mainAuth.permissions.IsAuthenticatedLoggin',
       ),

}
AUTHENTICATION_BACKENDS=(

    'social_core.backends.google.GoogleOAuth2',
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
)
SIMPLE_JWT={
    'AUTH_HEADER_TYPES':('JWT','Bearer',),
    'ACCESS_TOKEN_LIFETIME':timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME':timedelta(days=1),
    # 'AUTH_TOKEN_CLASSES':(
    #     'rest_framework_simplejwt.tokens.AccessToken',
    # ),
}
PARLER_LANGUAGES = {
    None: (
        {'code': 'en',},
        {'code': 'ar',},
    ),
    'default': {
        'fallbacks': ['en'],
        'hide_untranslated': False,   # Default
    }
}
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://localhost:3000"
]
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL='mainAuth.CustomUser'

EMAIL_BACKEND =config('EMAIL_BACKEND')

DEFAULT_FROM_EMAIL="halasaadeh04@gmail.com"
EMAIL_HOST =config('EMAIL_HOST')
EMAIL_HOST_USER =config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD =config('EMAIL_HOST_PASSWORD')
EMAIL_PORT =config('EMAIL_PORT')
EMAIL_USE_TLS=config('EMAIL_USE_TLS')


SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=config('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=config('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA=['first_name','last_name']


# state code : a39272499b435c9890406f85535f46fa

AUTH_PASSWORD_VALIDATORS = [
    
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8, }
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'mainAuth.validators.NumberValidator',
        'OPTIONS': {
            'min_digits': 1, }},
    {'NAME': 'mainAuth.validators.UppercaseValidator', },
    {'NAME': 'mainAuth.validators.LowercaseValidator', },
    {'NAME': 'mainAuth.validators.SymbolValidator', },
    
]
AXES_LOCK_OUT_AT_FAILURE = True  # Enable lockouts
AXES_USERNAME_FORM_FIELD = 'email'
AXES_FAILURE_LIMIT=5
AXES_COOLOFF_TIME = timedelta(minutes=5)# AXES_USERNAME_FORM_FIELD='email'
AXES_LOCKOUT_PARAMETERS=["username"]
AXES_LOCKOUT_CALLABLE='mainAuth.views.lockout'



# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': "channels.layers.InMemoryChannelLayer"
#     }
# }
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}
# CELERY_BROKER_URL = "redis://redis:6379"
# CELERY_BROKER_URL = "amqp://rabbitmq_server:5672"

CELERY_BROKER_URL ="amqp://guest:guest@rabbitmq_server:5672/"
CELERY_RESULT_BACKEND =  "redis://redis:6379/0"

STATIC_ROOT=os.path.join(BASE_DIR,'static')
STATIC_URL = '/static/'
STATICFILES_DIRS=[
    os.path.join(BASE_DIR,'eLearning/static')
]

# STATIC_URL = '/static/'
# STATIC_ROOT = './static_files/'
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATICFIELS_DIRS =[
#     os.path.join(BASE_DIR,'build/static')
# ]

DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
# STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"
MINIO_STORAGE_ENDPOINT = config("MINIO_STORAGE_ENDPOINT")
MINIO_STORAGE_ACCESS_KEY = config("MINIO_STORAGE_ACCESS_KEY")
MINIO_STORAGE_SECRET_KEY = config("MINIO_STORAGE_SECRET_KEY")
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_OBJECT_METADATA = {"Cache-Control": "max-age=1000"}
MINIO_STORAGE_MEDIA_BUCKET_NAME = config("MINIO_STORAGE_MEDIA_BUCKET_NAME")
MINIO_STORAGE_MEDIA_BACKUP_BUCKET =config("MINIO_STORAGE_MEDIA_BACKUP_BUCKET")
MINIO_STORAGE_MEDIA_BACKUP_FORMAT = '%c/'
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
# MINIO_STORAGE_STATIC_BUCKET_NAME = config("MINIO_STORAGE_STATIC_BUCKET_NAME")
# MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True







CLIENT_ID = config("ZOOM_CLIENT_ID")
CLIENT_SECRET = config("ZOOM_CLIENT_SECRET")
ACCOUNT_ID = config("ZOOM_ACCOUNT_ID")


STRIPE_PUBLISHABLE_KEY=config('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY=config('STRIPE_SECRET_KEY')
STRIPE_ENDPOINT_SECRET=config('STRIPE_ENDPOINT_SECRET')
STRIPE_CONNECT_CLIENT_ID=config('STRIPE_CONNECT_CLIENT_ID')
BASE_URL='http://127.0.0.1:8000/'

IS_DATA_LOADED=config('IS_DATA_LOADED')== 'True'
