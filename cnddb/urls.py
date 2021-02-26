from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from cnddb.views.overlays import MVT_County, MVT_Quad
from cnddb.views.external_resource_data import ExternalResourceDataValidation, ExternalResourceDataCreation

urlpatterns = [
    url(r'^', include('arches.urls')),
    url(
        r"^mvt-county/(?P<zoom>[0-9]+|\{z\})/(?P<x>[0-9]+|\{x\})/(?P<y>[0-9]+|\{y\}).pbf$",
        MVT_County.as_view(), name="mvt-conuty",
    ),
    url(
        r"^mvt-quad/(?P<zoom>[0-9]+|\{z\})/(?P<x>[0-9]+|\{x\})/(?P<y>[0-9]+|\{y\}).pbf$",
        MVT_Quad.as_view(), name="mvt-quad",
    ),
    url(r"^resource-data-validation$", ExternalResourceDataValidation.as_view(), name="api_external_resource_data_validation"),
    url(r"^resource-data-creation/(?P<graphid>%s)$" % (settings.UUID_REGEX), ExternalResourceDataCreation.as_view(), name="api_external_resource_creation"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SHOW_LANGUAGE_SWITCH is True:
    urlpatterns = i18n_patterns(*urlpatterns)