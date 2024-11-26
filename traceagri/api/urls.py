from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from traceagri.api.views import ParcellesProducteurAPIView, DashboardDataAPIView, ProducteurMobileViewSet, \
    ParcelleMobileViewSet, UserViewSet

router = DefaultRouter()
router.register(r'producteursmobile', ProducteurMobileViewSet, basename='producteurmobile')
router.register(r'parcellesmobile', ParcelleMobileViewSet, basename='parcellemobile')
router.register(r'users', UserViewSet)

urlpatterns = [
                  path('mobile/', include(router.urls)),

                  # path('api-auth/', include('rest_framework.urls')),

                  path('parcelles/<int:producteur_id>/', ParcellesProducteurAPIView.as_view(),name='parcelles-producteur-api'),
                  path('dashboard-data/', DashboardDataAPIView.as_view(), name='dashboard-data-api'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

