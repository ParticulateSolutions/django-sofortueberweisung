from django.conf.urls import url

from .views import NotifySofortView

urlpatterns = [
    url(r'^notify/$', NotifySofortView.as_view(), name='notifiy'),
]
