from django.conf.urls import include, url

urlpatterns = [
    url('^sofort/', include('django_sofortueberweisung.urls', namespace='sofort', app_name='sofort')),
]
