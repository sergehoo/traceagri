import json
from datetime import datetime

from django import forms
from django.forms import Select, NumberInput, Textarea, CheckboxInput, DateInput

from tracelan.models import Producteur, Parcelle, Status_choices, Project, Task, Milestone, Deliverable, Depense, \
    Employee, EventInvite, CultureDetail, MobileData


class ProducteurForm(forms.ModelForm):
    class Meta:
        model = Producteur
        fields = [
            "nom",
            "prenom",
            "sexe",
            "telephone",
            "date_naissance",
            "lieu_naissance",
            "cooperative",

        ]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez le nom"}),
            "prenom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez le prénom"}),
            "sexe": forms.Select(attrs={"class": "form-control"}),
            "telephone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Entrez le téléphone"}),
            "date_naissance": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "lieu_naissance": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Entrez le lieu de naissance"}),
            "cooperative": forms.Select(attrs={"class": "form-control"}),
            # "photo": forms.ClearableFileInput(attrs={"class": "form-control-file"})
        }


class ParcelleForm(forms.ModelForm):
    class Meta:
        model = Parcelle
        fields = [
            "localite", "nom", "dimension_ha",
            "polygone_kmz", "culture", "images", "status"
        ]
        widgets = {
            # "producteur": forms.Select(attrs={"class": "form-control"}),
            # "code": forms.TextInput(attrs={"class": "form-control"}),
            "localite": forms.Select(attrs={"class": "form-control select2", 'id': 'kt_select2_1', 'name': 'param'}),
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "dimension_ha": forms.NumberInput(attrs={"class": "form-control"}),
            "polygone_kmz": forms.FileInput(attrs={"class": "form-control"}),
            # "geojson": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            # "longitude": forms.NumberInput(attrs={"class": "form-control"}),
            # "latitude": forms.NumberInput(attrs={"class": "form-control"}),
            # "geom": forms.TextInput(attrs={"class": "form-control"}),
            # "carracteristic": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "status": forms.Select(choices=Status_choices,
                                   attrs={"class": "form-control select2", 'id': 'kt_select2_1_2', 'name': 'param'}),
            "culture": forms.TextInput(
                attrs={"class": "form-control tagify", 'id': 'kt_tagify_1', 'name': 'tags'}),
            "images": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        }

        def clean_culture(self):
            """Valider que le champ culture contient un JSON valide et extraire la première valeur."""
            culture_data = self.cleaned_data['culture']
            try:
                # Convertit la chaîne en liste d'objets JSON
                cultures = json.loads(culture_data)

                # Vérifie que chaque élément est un dictionnaire contenant une clé "value"
                if all(isinstance(item, dict) and "value" in item for item in cultures):
                    # Retourne uniquement la première valeur
                    return cultures[0]["value"] if cultures else ""
                else:
                    raise forms.ValidationError("Chaque élément doit contenir une clé 'value'.")
            except ValueError:
                raise forms.ValidationError("Le champ Culture doit contenir un JSON valide.")


class ParcelleUpdateForm(forms.ModelForm):
    class Meta:
        model = Parcelle
        fields = [
            'producteur', 'code', 'localite', 'nom', 'dimension_ha',
            'polygone_kmz', 'geojson', 'longitude', 'latitude', 'geom',
            'status', 'carracteristic', 'culture', 'affectations',
            'images',
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'producteur': forms.Select(attrs={'class': 'form-control'}),
            'localite': forms.Select(attrs={'class': 'form-control'}),
            # 'projet': forms.Select(attrs={'class': 'form-control'}),
            'carracteristic': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'culture': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'affectations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dimension_ha': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'polygone_kmz': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'images': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_polygone_kmz(self):
        file = self.cleaned_data.get('polygone_kmz')
        if file and not file.name.endswith('.kmz'):
            raise forms.ValidationError("Le fichier doit être au format KMZ.")
        return file


class CaracteristiqueForm(forms.ModelForm):
    class Meta:
        model = Parcelle
        fields = ['nom', 'dimension_ha', 'carracteristic']
        widgets = {
            'carracteristic': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
        }
        labels = {
            'nom': 'Nom de la parcelle',
            'dimension_ha': 'Dimension (ha)',
            'carracteristic': 'Caractéristiques (format JSON)',
        }

    def clean_carracteristic(self):
        data = self.cleaned_data['carracteristic']
        try:
            # Vérifie si le champ est un JSON valide
            return json.loads(data)
        except ValueError:
            raise forms.ValidationError("Les caractéristiques doivent être un JSON valide.")


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "manager", "members", "start_date", "end_date", "status", "previsionnel",
                  "marge_previsionnel"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "manager": forms.Select(attrs={"class": "form-control"}),
            "members": forms.SelectMultiple(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "previsionnel": forms.NumberInput(attrs={"class": "form-control"}),
            "marge_previsionnel": forms.NumberInput(attrs={"class": "form-control"}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description", "project", "assigned_to", "priority", "status", "start_date", "nbr_heure"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "project": forms.Select(attrs={"class": "form-control"}),
            "assigned_to": forms.Select(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(attrs={"class": "form-control datetimepicker-input", "type": "date",
                                                 'data-target': "#kt_datetimepicker_1"}),
            "nbr_heure": forms.DateInput(attrs={"class": "form-control"}),
        }


class TaskProjectForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'start_date', 'nbr_heure', 'priority', 'status', 'assigned_to']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'nbr_heure': forms.NumberInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ["name", "description", "project", "due_date", "is_completed"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "project": forms.Select(attrs={"class": "form-control"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class DeliverableForm(forms.ModelForm):
    class Meta:
        model = Deliverable
        fields = ["name", "description", "project", "file", "is_approved"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "project": forms.Select(attrs={"class": "form-control"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        }


class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depense
        fields = ['categorie', 'description', 'montant', 'date', 'responsable', 'justificatif']
        widgets = {
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'responsable': forms.Select(attrs={'class': 'form-control'}),
            'justificatif': forms.FileInput(attrs={'class': 'form-control'}),
        }


class AddMemberForm(forms.Form):
    member = forms.ModelChoiceField(queryset=Employee.objects.all(), label="Ajouter un membre", widget=forms.Select(
        attrs={'class': 'form-control select2', 'id': "kt_select2_1", 'name': "param"}))


class AddInviteForm(forms.Form):
    invite_type = forms.ChoiceField(
        choices=EventInvite.INVITE_TYPE_CHOICES,
        label="Type d'invité",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    invite_ids = forms.CharField(
        label="IDs des invités",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Entrez les IDs séparés par des virgules'}),
        help_text="IDs des invités, séparés par des virgules (ex: 1,2,3)"
    )


class CultureActivityForm(forms.ModelForm):
    YEARS = [(year, year) for year in range(1900, datetime.now().year + 1)]

    annee_mise_en_place = forms.ChoiceField(
        choices=YEARS,
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': "kt_select2_1", 'name': "param"}),
        label="Année de mise en place"
    )

    class Meta:
        model = CultureDetail
        fields = [
            'culture',
            'type_culture',
            'annee_mise_en_place',
            'dernier_rendement_kg_ha',
            'pratiques_culturales',
            'annee_mise_en_place',
            'date_recolte',
            'date_derniere_recolte',
            'utilise_fertilisants',
            'type_fertilisants',
            'analyse_sol',

        ]
        widgets = {
            'culture': Select(attrs={'class': 'form-control select2', 'id': "kt_select2_2", 'name': "param",
                                     'placeholder': 'Sélectionnez une culture'}),
            'type_culture': Select(attrs={'class': 'form-control ', 'placeholder': 'Type de culture'}),
            'dernier_rendement_kg_ha': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Rendement (kg/ha)'}),
            'pratiques_culturales': Textarea(attrs={'class': 'form-control', 'placeholder': 'Pratiques culturales'}),
            'date_recolte': DateInput(
                attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Date de récolte'}),
            'date_derniere_recolte': DateInput(
                attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Date de dernière récolte'}),
            'utilise_fertilisants': CheckboxInput(attrs={'class': 'form-check-input'}),
            'type_fertilisants': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Type de fertilisants'}),
            'analyse_sol': CheckboxInput(attrs={'class': 'form-check-input'}),
        }



class MobileDataForm(forms.ModelForm):
    class Meta:
        model = MobileData
        fields = [
            'uid',
            'nom',
            'prenom',
            'sexe',
            'telephone',
            'date_naissance',
            'lieu_naissance',
            'fonction',
            'ville_enquette',
            'nbre_personne_foyer',
            'nbre_personne_charge',
            'revenue_derniere_recolte',
            'handicap',
            'cultureType',
            'nom_culture',
            'annee_mise_en_place',
            'date_derniere_recolte',
            'rendement_approximatif',
            'Culture_intercalaire',
            'dimension_ha',
            'cultures_precedentes',
            'annee_cultures_precedentes',
            'evenements_climatiques',
            'commentaires',
            'nom_parcelle',
            'localite_parcelle',
            'annee_premiere_recole',
            'utilise_fertilisants',
            'fertilizerType',
            'analyse_sol',
            'autre_culture',
            'autre_culture_nom',
            'autre_culture_volume_ha',
            'photo',
            'nom_cooperative',
            'ville',
            'createdDate',


        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 1}),
            # 'pratiques_culturales': forms.Textarea(attrs={'rows': 1}),
            'commentaires': forms.Textarea(attrs={'rows': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Appliquer 'form-control' à tous les champs
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_dimension_ha(self):
        """Validation personnalisée pour la dimension."""
        dimension = self.cleaned_data.get('dimension_ha')
        if dimension and dimension <= 0:
            raise forms.ValidationError("La dimension doit être supérieure à 0.")
        return dimension

    def clean_nom(self):
        """Validation personnalisée pour le nom."""
        nom = self.cleaned_data.get('nom')
        if not nom:
            raise forms.ValidationError("Le champ Nom est obligatoire.")
        return nom
