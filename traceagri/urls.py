"""
URL configuration for traceagri project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.messages import api
from django.urls import path, include, re_path

from tracelan.views import HomePageView, ProducteurListView, ProducteurDetailView, ProducteurCreateView, \
    ParcelleListView, ParcelleDetailView, ParcelleCreateView, ParcelleUpdateView, ParcelleDeleteView, ProjectListView, \
    ProjectCreateView, ProjectUpdateView, ProjectDeleteView, TaskListView, TaskCreateView, TaskUpdateView, \
    TaskDeleteView, MilestoneListView, MilestoneCreateView, MilestoneUpdateView, MilestoneDeleteView, \
    ProjectDetailsView, EventListView, EventDetailView, get_invite_list, add_invites_to_event, \
    add_invites_and_send_emails, confirm_presence, CooperativeListView, CooperativeCreateView, CooperativeUpdateView, \
    CooperativeDeleteView, CooperativeDetailView, ParcelleExportView, ProducteurExportView, MobileDataListView, \
    MobileDataDetailView, MobileDataUpdateView, MobileDataDeleteView, LandingView, add_culture_activity, \
    ProducteurUpdateView, valider_mobiledata, ProducteurDeleteView, get_cultures

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('unicorn/', include('django_unicorn.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/', include('traceagri.api.urls')),
    # path('api-auth/', include('rest_framework.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/tablette/', include('djoser.urls.authtoken')),

    path('dashboard', HomePageView.as_view(), name='home'),
    path('', LandingView.as_view(), name='landing'),
    path('Producteurs', ProducteurListView.as_view(), name='producteurs-list'),
    path('Producteurs/create', ProducteurCreateView.as_view(), name='producteurs-create'),
    path('Producteurs/update/<int:pk>', ProducteurUpdateView.as_view(), name='producteurs-update'),
    path('Producteurs/details<int:pk>', ProducteurDetailView.as_view(), name='producteurs-details'),
    path('Producteurs/delete<int:pk>', ProducteurDeleteView.as_view(), name='producteurs-delete'),

    path('export/producteurs/', ProducteurExportView.as_view(), name='producteur_export'),

    path("parcelles/", ParcelleListView.as_view(), name="parcelle-list"),
    path('parcelle/<int:parcelle_id>/add_culture_activity/', add_culture_activity, name="add_culture_activity"),

    path("parcelles/<int:pk>/", ParcelleDetailView.as_view(), name="parcelle-detail"),
    path("look/cultures/", get_cultures, name="look_cultures"),

    path("parcelles/create/<int:producteur_id>", ParcelleCreateView.as_view(), name="parcelle-create"),
    path("parcelles/<int:pk>/update/", ParcelleUpdateView.as_view(), name="parcelle-update"),
    path("parcelles/<int:producteur_id>/delete/<int:pk>", ParcelleDeleteView.as_view(), name="parcelle-delete"),
    path('export/parcelles/', ParcelleExportView.as_view(), name='parcelle_export'),

    # Project URLs
    path("projects/", ProjectListView.as_view(), name="project_list"),
    path("projects/details/<int:pk>", ProjectDetailsView.as_view(), name="project_details"),
    path("projects/new/", ProjectCreateView.as_view(), name="project_create"),
    path("projects/<int:pk>/edit/", ProjectUpdateView.as_view(), name="project_update"),
    path("projects/<int:pk>/delete/", ProjectDeleteView.as_view(), name="project_delete"),

    path("event/list", EventListView.as_view(), name="event_list"),
    path("event/detail<int:pk>", EventDetailView.as_view(), name="event_details"),
    path('get-invite-list/', get_invite_list, name='get_invite_list'),
    path('event/<int:event_id>/add-invites/', add_invites_to_event, name='add_invites_to_event'),

    path('event/<int:event_id>/add-invites/', add_invites_and_send_emails,
         name='add_invites_and_send_emails'),
    path('event/<int:event_id>/confirm/<int:producer_id>/<str:token>/', confirm_presence,
         name='confirm_presence'),

    # Task URLs
    path("tasks/", TaskListView.as_view(), name="task_list"),
    path("tasks/new/", TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task_update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),

    # Milestone URLs
    path("milestones/", MilestoneListView.as_view(), name="milestone_list"),
    path("milestones/new/", MilestoneCreateView.as_view(), name="milestone_create"),
    path("milestones/<int:pk>/edit/", MilestoneUpdateView.as_view(), name="milestone_update"),
    path("milestones/<int:pk>/delete/", MilestoneDeleteView.as_view(), name="milestone_delete"),

    path('cooperatives/', CooperativeListView.as_view(), name='cooperative_list'),
    path('cooperatives/create/', CooperativeCreateView.as_view(), name='cooperative_create'),
    path('cooperatives/<int:pk>/update/', CooperativeUpdateView.as_view(), name='cooperative_update'),
    path('cooperatives/<int:pk>/delete/', CooperativeDeleteView.as_view(), name='cooperative_delete'),
    path('cooperatives/<int:pk>/', CooperativeDetailView.as_view(), name='cooperative_detail'),

    # Deliverable URLs
    # path("deliverables/", DeliverableListView.as_view(), name="deliverable_list"),
    # path("deliverables/new/", DeliverableCreateView.as_view(), name="deliverable_create"),
    # path("deliverables/<int:pk>/edit/", DeliverableUpdateView.as_view(), name="deliverable_update"),
    # path("deliverables/<int:pk>/delete/", DeliverableDeleteView.as_view(), name="deliverable_delete"),
    path('mobiledata/valider/<int:pk>/', valider_mobiledata, name='valider_mobiledata'),

    path('liste/donnee/mobile', MobileDataListView.as_view(), name='mobiledata_list'),  # Liste
    path('mobiledata<int:pk>/', MobileDataDetailView.as_view(), name='mobiledata_detail'),  # Détails
    path('mobiledata<int:pk>/update/', MobileDataUpdateView.as_view(), name='mobiledata_update'),  # Mise à jour
    path('mobiledata<int:pk>/delete/', MobileDataDeleteView.as_view(), name='mobiledata_delete'),  # Suppression

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
