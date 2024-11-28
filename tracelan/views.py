import csv
import json
import logging
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db import models
from django.db.models import Sum, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from openpyxl.workbook import Workbook

from tracelan.forms import ProducteurForm, ParcelleForm, ProjectForm, TaskForm, MilestoneForm, DepenseForm, \
    TaskProjectForm, AddMemberForm, AddInviteForm
from tracelan.models import Producteur, Parcelle, DistrictSanitaire, Region, Project, Task, Milestone, Event, \
    Cooperative, Ville, EventInvite, CooperativeMember
from tracelan.task import envoyer_email_invitation


# Create your views here.


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producteurs = Producteur.objects.all().count()
        parcelle = Parcelle.objects.all().count()
        top_parcelles = Parcelle.objects.order_by('-dimension_ha')[:10]
        # Ajouter une API pour les données du dashboard si nécessaire
        context['dashboard_data_url'] = reverse_lazy('dashboard-data-api')  # Assurez-vous de définir cette URL
        context['nombreproducteur'] = producteurs  # Assurez-vous de définir cette URL
        context['parcelle'] = parcelle  # Assurez-vous de définir cette URL
        context['top_parcelles'] = top_parcelles
        return context


class ProducteurListView(LoginRequiredMixin, ListView):
    model = Producteur
    template_name = "pages/producteur_list.html"
    context_object_name = "producteurs_liste"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producteurs = self.object_list.count()
        context['nombreproducteur'] = producteurs
        return context


class ProducteurDetailView(LoginRequiredMixin, DetailView):
    model = Producteur
    template_name = "pages/producteur_detail.html"
    context_object_name = "producteurdetails"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parcelle = Parcelle.objects.filter(producteur=self.object)
        context['parcelle'] = parcelle
        return context


logger = logging.getLogger(__name__)  # Configurer un logger


class ProducteurCreateView(LoginRequiredMixin, CreateView):
    model = Producteur
    template_name = "pages/producteur_create.html"
    form_class = ProducteurForm
    success_url = reverse_lazy("producteurs-list")

    def form_valid(self, form):
        # Récupération des données nettoyées
        nom = form.cleaned_data['nom'].upper()
        prenom = form.cleaned_data['prenom'].upper()
        date_naissance = form.cleaned_data['date_naissance']
        telephone = form.cleaned_data['telephone']

        # Vérification des doublons
        if Producteur.objects.filter(nom__iexact=nom, prenom__iexact=prenom, date_naissance=date_naissance).exists():
            logger.warning("Tentative de création d'un producteur existant.")
            messages.error(self.request, 'Ce Producteur existe déjà.')
            return self.form_invalid(form)

        if Producteur.objects.filter(telephone=telephone).exists():
            logger.warning("Numéro de téléphone déjà utilisé.")
            messages.error(self.request, 'Un Producteur avec ce contact existe déjà.')
            return self.form_invalid(form)

        # Sauvegarde du producteur
        producteur = form.save(commit=False)
        producteur.save()
        logger.info(f"Producteur {producteur.nom} créé avec succès.")

        messages.success(self.request, 'Producteur créé avec succès!')
        return redirect(self.success_url)

    def form_invalid(self, form):
        logger.error(f"Erreur dans le formulaire : {form.errors}")
        messages.error(self.request, 'Une erreur est survenue. Veuillez vérifier vos données.')
        return super().form_invalid(form)


class ProducteurUpdateView(LoginRequiredMixin, UpdateView):
    model = Producteur
    template_name = "pages/producteur_form.html"
    fields = ["nom", "prenom", "sexe", "telephone", "date_naissance", "lieu_naissance", "cooperative"]
    success_url = reverse_lazy("producteur_list")


class ProducteurExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Récupérer le format d'export (csv, excel)
        export_format = request.GET.get('format', 'csv')  # Par défaut, CSV
        producteurs = Producteur.objects.annotate(nbr_parcelles=Count('parcelles'))

        if export_format == 'csv':
            return self.export_csv(producteurs)
        elif export_format == 'excel':
            return self.export_excel(producteurs)
        else:
            return HttpResponse("Format non pris en charge.", status=400)

    def export_csv(self, producteurs):
        # Créer la réponse HTTP avec l'en-tête pour un fichier CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Producteurs.csv"'

        writer = csv.writer(response)
        # Ajouter les en-têtes des colonnes
        writer.writerow(['Nom', 'Prénom', 'Sexe', 'Téléphone', 'Nombre de Parcelles'])

        # Ajouter les données des producteurs
        for producteur in producteurs:
            writer.writerow([
                producteur.nom,
                producteur.prenom,
                producteur.sexe,
                producteur.telephone,
                producteur.nbr_parcelles
            ])

        return response

    def export_excel(self, producteurs):
        # Créer un fichier Excel
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Producteurs"

        # Ajouter les en-têtes des colonnes
        headers = ['Nom', 'Prénom', 'Sexe', 'Téléphone', 'Nombre de Parcelles']
        sheet.append(headers)

        # Ajouter les données des producteurs
        for producteur in producteurs:
            sheet.append([
                producteur.nom,
                producteur.prenom,
                producteur.sexe,
                producteur.telephone,
                producteur.nbr_parcelles
            ])

        # Créer la réponse HTTP avec l'en-tête pour un fichier Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Producteurs.xlsx"'
        workbook.save(response)
        return response


class ProducteurDeleteView(LoginRequiredMixin, DeleteView):
    model = Producteur
    template_name = "pages/producteur_confirm_delete.html"
    success_url = reverse_lazy("producteur_list")


class ParcelleExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Récupérer le format d'export (csv, excel)
        export_format = request.GET.get('format', 'csv')  # Par défaut, CSV
        parcelles = Parcelle.objects.select_related('producteur', 'localite').prefetch_related('culture_perenne',
                                                                                               'culture_saisonniere')

        if export_format == 'csv':
            return self.export_csv(parcelles)
        elif export_format == 'excel':
            return self.export_excel(parcelles)
        else:
            return HttpResponse("Format non pris en charge.", status=400)

    def export_csv(self, parcelles):
        # Créer la réponse HTTP avec l'en-tête pour un fichier CSV
        dates = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="Exportparcelles_{dates}.csv"'

        writer = csv.writer(response)
        # Ajouter les en-têtes des colonnes
        writer.writerow([
            'Nom Parcelle', 'Code', 'Localité', 'Dimension (ha)', 'Longitude', 'Latitude', 'Status',
            'Producteur', 'Cultures Pérènes', 'Cultures Saisonnières'
        ])

        # Ajouter les données des parcelles
        for parcelle in parcelles:
            producteur = f"{parcelle.producteur.nom} {parcelle.producteur.prenom}" if parcelle.producteur else "N/A"
            cultures_perennes = ", ".join(culture.nom for culture in parcelle.culture_perenne.all())
            cultures_saisonnieres = ", ".join(culture.nom for culture in parcelle.culture_saisonniere.all())

            writer.writerow([
                parcelle.nom,
                parcelle.code,
                parcelle.localite.name if parcelle.localite else '',
                parcelle.dimension_ha,
                parcelle.longitude,
                parcelle.latitude,
                parcelle.status,
                producteur,
                cultures_perennes,
                cultures_saisonnieres
            ])

        return response

    def export_excel(self, parcelles):
        # Créer un fichier Excel
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Parcelles"

        # Ajouter les en-têtes des colonnes
        headers = [
            'Nom Parcelle', 'Code', 'Localité', 'Dimension (ha)', 'Longitude', 'Latitude', 'Status',
            'Producteur', 'Cultures Pérènes', 'Cultures Saisonnières'
        ]
        sheet.append(headers)

        # Ajouter les données des parcelles
        for parcelle in parcelles:
            producteur = f"{parcelle.producteur.nom} {parcelle.producteur.prenom}" if parcelle.producteur else "N/A"
            cultures_perennes = ", ".join(culture.nom for culture in parcelle.culture_perenne.all())
            cultures_saisonnieres = ", ".join(culture.nom for culture in parcelle.culture_saisonniere.all())

            sheet.append([
                parcelle.nom,
                parcelle.code,
                parcelle.localite.nom if parcelle.localite else '',
                parcelle.dimension_ha,
                parcelle.longitude,
                parcelle.latitude,
                parcelle.status,
                producteur,
                cultures_perennes,
                cultures_saisonnieres
            ])

        # Créer la réponse HTTP avec l'en-tête pour un fichier Excel

        dates = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Format: YYYY-MM-DD_HH-MM-SS

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Exportparcelles_{dates}.xlsx"'

        workbook.save(response)
        return response


class ParcelleListView(LoginRequiredMixin, ListView):
    model = Parcelle
    template_name = "pages/parcelle_list.html"
    context_object_name = "parcelles"
    # paginate_by = 10  # Pagination, 10 éléments par page
    ordering = ["-created_at"]  # Trier par date de création

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parcelles = self.object_list.count()
        total_dimension = self.object_list.aggregate(total_dimension=Sum('dimension_ha'))['total_dimension'] or 0
        context['parcellesnbr'] = parcelles
        context['total_dimension'] = total_dimension
        return context


class ParcelleDetailView(LoginRequiredMixin, DetailView):
    model = Parcelle
    template_name = "pages/parcelle_detail.html"
    context_object_name = "parcelle"


class ParcelleCreateView(LoginRequiredMixin, CreateView):
    model = Parcelle
    template_name = "pages/parcelle_create.html"
    form_class = ParcelleForm

    # success_url = reverse_lazy("parcelle-list")  # Remplacez par le nom de votre URL

    def dispatch(self, request, *args, **kwargs):
        self.producteur = get_object_or_404(Producteur, id=self.kwargs['producteur_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Associer le producteur à la parcelle
        form.instance.producteur = self.producteur
        messages.success(self.request, 'Parcelle Ajoutee avec succes.')
        return super().form_valid(form)

    def get_success_url(self):
        # Retourner l'URL de la page de détail du producteur
        return reverse('producteurs-details', kwargs={'pk': self.producteur.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producteur'] = self.producteur
        return context


class ParcelleUpdateView(LoginRequiredMixin, UpdateView):
    model = Parcelle
    template_name = "pages/parcelle_update.html"
    form_class = ParcelleForm
    success_url = reverse_lazy("parcelle-list")  # Remplacez par le nom de votre URL


class ParcelleDeleteView(LoginRequiredMixin, DeleteView):
    model = Parcelle
    template_name = "pages/parcelle_confirm_delete.html"

    # success_url = reverse_lazy("parcelle-list")  # Remplacez par le nom de votre URL

    def dispatch(self, request, *args, **kwargs):
        # Récupérer le producteur associé à la parcelle
        self.producteur = get_object_or_404(Producteur, id=self.kwargs['producteur_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producteur'] = self.producteur  # Ajoutez le producteur au contexte
        context['parcelle'] = self.get_object()
        return context

    def get_success_url(self):
        # Assurez-vous que self.producteur a un ID valide
        if not self.producteur or not self.producteur.id:
            raise ValueError("Impossible de trouver l'ID du producteur.")
        # Retourner l'URL avec le bon pk
        messages.success(self.request, "La parcelle a été supprimée avec succès.")
        return reverse('producteurs-details', kwargs={'pk': self.producteur.id})


# Project Views
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "project/project_list.html"
    context_object_name = "projects"


class ProjectDetailsView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "project/project_details.html"
    context_object_name = "projects_details"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        context['depense_form'] = DepenseForm()
        context['depenses'] = project.depenses.all()  # Récupérer toutes les dépenses liées au projet
        context['latest_depenses'] = project.depenses.order_by('-date')[:5]

        context['task_form'] = TaskProjectForm()
        context['tasks'] = project.tasks.all()  # Tâches liées au projet
        context['latest_tasks'] = project.tasks.order_by('-created_at')[:5]

        context['add_member_form'] = AddMemberForm()  # Formulaire d'ajout de membres

        # Ajouter les heures cumulées à chaque membre
        # Préparer un dictionnaire des heures cumulées pour chaque employé
        # Récupérer les membres et leurs heures cumulées
        members_hours = project.members.annotate(
            total_hours=Sum('assigned_tasks__nbr_heure', filter=models.Q(assigned_tasks__project=project))
        )

        context['members_hours'] = members_hours

        # Compter le nombre de tâches par statut
        task_status_data = project.tasks.values('status').annotate(count=Count('status'))

        # Préparer les données pour le graphique
        context['task_status_data'] = list(task_status_data)

        # Ajouter les données pour le graphique d'évaluation budgétaire
        context['budget_data'] = {
            'previsionnel': project.previsionnel or 0,
            'estimatif': project.budget_estimatif,
            'depenses': project.get_total_expenses()
        }

        return context

    def post(self, request, *args, **kwargs):
        project = self.get_object()

        # Gérer l'ajout de dépense
        if 'add_depense' in request.POST:
            depense_form = DepenseForm(request.POST, request.FILES)
            if depense_form.is_valid():
                depense = depense_form.save(commit=False)
                depense.projet = project
                depense.save()
                messages.success(request, "La dépense a été enregistrée avec succès.")
                return redirect('project_details', pk=project.pk)
            else:
                messages.error(request, "Une erreur est survenue lors de l'enregistrement de la dépense.")

        # Gérer l'ajout de tâche
        if 'add_task' in request.POST:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.project = project
                task.assigned_by = request.user.employee
                task.save()
                messages.success(request, "La tâche a été ajoutée avec succès.")
                return redirect('project_details', pk=project.pk)
            else:
                messages.error(request, "Une erreur est survenue lors de l'ajout de la tâche.")

        # Gérer l'ajout de membre
        if 'add_member' in request.POST:
            add_member_form = AddMemberForm(request.POST)
            if add_member_form.is_valid():
                member = add_member_form.cleaned_data['member']
                if project.members.filter(id=member.id).exists():
                    # Vérifie si le membre est déjà dans le projet
                    messages.warning(request, f"{member} fait déjà partie de ce projet.")
                else:
                    project.members.add(member)  # Ajoute le membre au projet
                    messages.success(request, f"{member} a été ajouté au projet avec succès.")
                return redirect('project_details', pk=project.pk)
            else:
                messages.error(request, "Une erreur est survenue lors de l'ajout du membre.")

                return self.get(request, *args, **kwargs)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "project/project_form.html"
    success_url = reverse_lazy("project_list")

    def form_valid(self, form):
        # Associer le producteur à la parcelle
        # form.instance.producteur = self.producteur
        messages.success(self.request, 'Projet cree avec succes.')
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "project/project_form.html"
    success_url = reverse_lazy("project_list")


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "project/project_confirm_delete.html"
    success_url = reverse_lazy("project_list")


# Task Views
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "task/task_list.html"
    context_object_name = "tasks"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "task/task_form.html"
    success_url = reverse_lazy("task_list")


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "task/task_form.html"
    success_url = reverse_lazy("task_list")


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "task/task_confirm_delete.html"
    success_url = reverse_lazy("task_list")


# Milestone Views
class MilestoneListView(LoginRequiredMixin, ListView):
    model = Milestone
    template_name = "milestone/milestone_list.html"
    context_object_name = "milestones"


class MilestoneCreateView(LoginRequiredMixin, CreateView):
    model = Milestone
    form_class = MilestoneForm
    template_name = "milestone/milestone_form.html"
    success_url = reverse_lazy("milestone_list")


class MilestoneUpdateView(LoginRequiredMixin, UpdateView):
    model = Milestone
    form_class = MilestoneForm
    template_name = "milestone/milestone_form.html"
    success_url = reverse_lazy("milestone_list")


class MilestoneDeleteView(LoginRequiredMixin, DeleteView):
    model = Milestone
    template_name = "milestone/milestone_confirm_delete.html"
    success_url = reverse_lazy("milestone_list")


def ajouter_invites_et_programmer_rappel(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        form = AddInviteForm(request.POST)
        if form.is_valid():
            invite_type = form.cleaned_data['invite_type']
            invite_ids = form.cleaned_data['invite_ids'].split(',')

            # Appelle la fonction d'ajout d'invités et envoie un premier email
            envoyer_email_invitation.delay(event.id, "Invitation à l'événement", """
            Bonjour {name},

            Vous êtes invité à l'événement :
            - Événement : {event}
            - Date : {date}
            - Lieu : {location}

            Merci de confirmer votre présence.

            Cordialement,
            L'équipe
            """)

            # Programme un rappel après 2 jours
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=2,
                period=IntervalSchedule.DAYS,
            )

            PeriodicTask.objects.create(
                interval=schedule,
                name=f"Rappel pour l'événement {event.name} ({event.id})",
                task='events.tasks.envoyer_email_rappel',
                args=json.dumps([event.id]),
            )

            messages.success(request, "Invités ajoutés et rappel programmé.")
            return redirect('event_detail', pk=event.pk)
    else:
        form = AddInviteForm()

    return render(request, 'events/add_invites.html', {'form': form, 'event': event})


# def get_invite_list(request):
#     invite_type = request.GET.get('invite_type')
#     entities = []
#
#     if invite_type == 'producteur':
#         entities = list(Producteur.objects.values('id', 'nom', 'prenom'))
#     elif invite_type == 'cooperative':
#         entities = list(Cooperative.objects.values('id', 'nom'))
#     elif invite_type == 'ville':
#         entities = list(Ville.objects.values('id', 'name'))
#     elif invite_type == 'district':
#         entities = list(DistrictSanitaire.objects.values('id', 'nom'))
#     elif invite_type == 'region':
#         entities = list(Region.objects.values('id', 'name'))
#
#     return JsonResponse({'entities': entities})
def get_invite_list(request):
    invite_type = request.GET.get('invite_type')
    entities = []

    if invite_type == 'producteur':
        entities = list(Producteur.objects.values('id', 'nom', 'prenom'))
    elif invite_type == 'cooperative':
        entities = list(Cooperative.objects.values('id', 'nom'))
    elif invite_type == 'ville':
        entities = list(Ville.objects.values('id', 'name'))
    elif invite_type == 'district':
        entities = list(DistrictSanitaire.objects.values('id', 'nom'))
    elif invite_type == 'region':
        entities = list(Region.objects.values('id', 'name'))

    return JsonResponse({'entities': entities})


def add_invites_to_event(request, event_id):
    """
    Vue pour ajouter des invités à un événement.
    """
    event = get_object_or_404(Event, id=event_id)  # Récupérer l'événement

    if request.method == 'POST':
        # Extraire les données du formulaire
        invite_type = request.POST.get('invite_type')  # Type d'invité (ex: producteur)
        invite_ids = request.POST.get('invite_ids')  # IDs des invités (séparés par des virgules)

        if not invite_type or not invite_ids:
            messages.error(request, "Veuillez sélectionner un type d'invité et au moins un invité.")
            return redirect('event_detail', event_id=event_id)

        # Convertir les IDs en une liste
        invite_ids = invite_ids.split(',')

        # Enregistrer chaque invité
        for invite_id in invite_ids:
            try:
                # Vérifier si l'invité existe déjà pour cet événement
                if EventInvite.objects.filter(event=event, invite_type=invite_type, invite_id=invite_id).exists():
                    continue  # Passer si l'invité est déjà ajouté

                # Créer un nouvel invité
                EventInvite.objects.create(event=event, invite_type=invite_type, invite_id=invite_id)
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de l'invité ID {invite_id}: {str(e)}")
                continue

        messages.success(request, "Les invités ont été ajoutés avec succès.")
        return redirect('event_details', pk=event_id)

    return redirect('event_details', pk=event_id)


def add_invites_and_send_emails(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        invite_type = request.POST.get('invite_type')
        invite_ids = request.POST.get('invite_ids', '').split(',')

        if not invite_type or not invite_ids:
            messages.error(request, "Veuillez sélectionner un type et des invités.")
            return redirect('event_detail', event_id=event_id)

        # Liste des emails à envoyer
        emails_to_send = []

        # Gérer chaque ID sélectionné
        for invite_id in invite_ids:
            if EventInvite.objects.filter(event=event, invite_type=invite_type, invite_id=invite_id).exists():
                continue  # Ignorer les doublons

            # Ajouter l'invité
            EventInvite.objects.create(event=event, invite_type=invite_type, invite_id=invite_id)

            # Récupérer les producteurs associés à cet invité
            producers = get_producers_from_invite(invite_type, invite_id)

            for producer in producers:
                # Générer un lien unique de confirmation
                confirmation_link = request.build_absolute_uri(
                    reverse('confirm_presence', args=[event_id, producer.id, get_random_string(32)])
                )
                emails_to_send.append((producer, confirmation_link))

        # Envoyer les emails
        send_confirmation_emails(event, emails_to_send)

        messages.success(request, "Les invités ont été ajoutés et les emails ont été envoyés.")
        return redirect('event_detail', event_id=event_id)

    return redirect('event_detail', event_id=event_id)


def get_producers_from_invite(invite_type, invite_id):
    """
    Retourne les producteurs associés à un type et ID donné.
    """
    if invite_type == 'producteur':
        return Producteur.objects.filter(id=invite_id)
    elif invite_type == 'cooperative':
        return Producteur.objects.filter(cooperative_id=invite_id)
    elif invite_type == 'ville':
        return Producteur.objects.filter(cooperative__ville_id=invite_id)
    elif invite_type == 'district':
        return Producteur.objects.filter(cooperative__ville__district_id=invite_id)
    elif invite_type == 'region':
        return Producteur.objects.filter(cooperative__ville__district__region_id=invite_id)
    return Producteur.objects.none()


def send_confirmation_emails(event, emails_to_send):
    """
    Envoie un email de confirmation à chaque producteur.
    """
    for producer, confirmation_link in emails_to_send:
        subject = f"Invitation à l'événement : {event.name}"
        message = (
            f"Bonjour {producer.nom} {producer.prenom},\n\n"
            f"Vous êtes invité à l'événement '{event.name}' qui aura lieu le {event.start_date} à {event.location}.\n\n"
            f"Veuillez confirmer votre présence en cliquant sur le lien suivant :\n"
            f"{confirmation_link}\n\n"
            f"Merci.\n\n"
            f"L'équipe d'organisation"
        )
        send_mail(subject, message, 'no-reply@yourdomain.com', [producer.telephone or producer.email])


def confirm_presence(request, event_id, producer_id, token):
    """
    Vue pour confirmer la présence d'un invité.
    """
    try:
        # Rechercher l'invitation correspondante
        invite = EventInvite.objects.get(event_id=event_id, invite_id=producer_id, confirmation_token=token)

        # Marquer comme confirmé et ajouter la date de confirmation
        invite.confirmed = True
        invite.confirmation_date = now()
        invite.save()

        return HttpResponse("Votre présence a été confirmée. Merci !")
    except EventInvite.DoesNotExist:
        return HttpResponse("Lien invalide ou invitation non trouvée.")


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 10  # Pagination (facultatif)

    def get_queryset(self):
        return Event.objects.order_by('-created_at')  # Trier par date décroissante


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "events"
    paginate_by = 10  # Pagination (facultatif)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        context['invites'] = event.invites.all()  # Liste des invités
        context['invites_confirmes'] = event.invites.filter(confirmed=True)  # Liste des invités
        context['addinviteForm'] = AddInviteForm()  # ajout des invités
        return context


class CooperativeListView(LoginRequiredMixin, ListView):
    model = Cooperative
    template_name = "cooperatives/cooperative_list.html"
    context_object_name = "cooperatives"
    paginate_by = 10  # Pagination (facultatif)


class CooperativeCreateView(LoginRequiredMixin, CreateView):
    model = Cooperative
    template_name = "cooperatives/cooperative_form.html"
    fields = ['nom', 'code', 'ville', 'president']
    success_url = reverse_lazy('cooperative_list')  # Redirection après succès


class CooperativeUpdateView(LoginRequiredMixin, UpdateView):
    model = Cooperative
    template_name = "cooperatives/cooperative_form.html"
    fields = ['nom', 'code', 'ville', 'president']
    success_url = reverse_lazy('cooperative_list')


class CooperativeDeleteView(LoginRequiredMixin, DeleteView):
    model = Cooperative
    template_name = "cooperatives/cooperative_confirm_delete.html"
    success_url = reverse_lazy('cooperative_list')


class CooperativeDetailView(LoginRequiredMixin, DetailView):
    model = Cooperative
    template_name = "cooperatives/cooperative_detail.html"
    context_object_name = "cooperative"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cooperative = self.get_object()

        # Récupérer les membres de la coopérative
        members = CooperativeMember.objects.filter(cooperative=cooperative).first()
        context['members'] = members.producteurs.all() if members else []

        # Récupérer les événements liés à la coopérative
        events = Event.objects.filter(invites__invite_type="cooperative", invites__invite_id=cooperative.id).distinct()
        context['events'] = events

        return context
