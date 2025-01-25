from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from traceagri.api.views import ParcellesProducteurAPIView, DashboardDataAPIView, ProducteurMobileViewSet, \
    ParcelleMobileViewSet, UserViewSet, DynamicFormViewSet, ProjectViewSet, CooperativeViewSet, \
    CooperativeMemberViewSet, ParcelleDetailAPIView, MobileDataViewSet, MobileDataStatsAPIView

router = DefaultRouter()
router.register(r'producteursmobile', ProducteurMobileViewSet, basename='producteurmobile')
router.register(r'parcellesmobile', ParcelleMobileViewSet, basename='parcellemobile')
router.register(r'users', UserViewSet)
# router.register(r'forms', DynamicFormViewSet, basename='dynamicform')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'cooperatives', CooperativeViewSet, basename='cooperative')
router.register(r'cooperative-members', CooperativeMemberViewSet, basename='cooperative-member')
router.register(r'mobiledata', MobileDataViewSet, basename='mobiledata')

urlpatterns = ([
                   path('mobile/', include((router.urls, 'mobile'), namespace='mobile')),
                   path('api/mobiledata/stats/', MobileDataStatsAPIView.as_view(), name='mobiledata-stats'),
                   path('djoser/auth/', include('djoser.urls')),  # Endpoints Djoser par défaut
                   # path('djoser/auth/token', include('djoser.urls.authtoken')),  # Si vous utilisez TokenAuthentication
                   path('auth/', include('djoser.urls.jwt')),  # Endpoints JWT pour tokens

                   # path('auth/', include('djoser.urls.jwt')),

                   # path('api-auth/', include('rest_framework.urls')),

                   path('parcelles/<int:producteur_id>/', ParcellesProducteurAPIView.as_view(),
                        name='parcelles-producteur-api'),
                   path('parcelles/detail<int:parcelle_id>/', ParcelleDetailAPIView.as_view(),
                        name='parcelles-detail-api'),
                   path('dashboard-data/', DashboardDataAPIView.as_view(), name='dashboard-data-api'),

                   # path('enquete/mobiledata/', MobileDataViewSet.as_view(), name='mobiledata_api'),

               ] + router.urls
               + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
