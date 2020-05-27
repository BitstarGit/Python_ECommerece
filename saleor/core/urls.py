from django.conf.urls import url
from impersonate.views import stop_impersonate

from . import views

urlpatterns = [
    url(r"^$", views.home, name="home"),
    url(r"^style-guide/", views.styleguide, name="styleguide"),
    url(r"^impersonate/(?P<uid>\d+)/", views.impersonate, name="impersonate-start"),
    url(r"^impersonate/stop/$", stop_impersonate, name="impersonate-stop"),
    url(r"^404", views.handle_404, name="handle-404"),
    url(r"^manifest\.json$", views.manifest, name="manifest"),

    url(r"^about/", views.about_us, name="about"),
    url(r"^partners/", views.for_partners, name="partners"),

    url(r"^facebook/", views.facebook, name="facebook"),
    url(r"^instagram/", views.instagram, name="instagram"),
]
