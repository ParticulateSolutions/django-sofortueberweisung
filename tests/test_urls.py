from django.conf.urls import include, url

app_name = 'sofort'
urlpatterns = [
    url('^sofort/', include('django_sofortueberweisung.urls')),
]
