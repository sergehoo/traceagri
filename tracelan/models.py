import datetime
import json
import random
import uuid
import zipfile
from io import BytesIO

from django.contrib.auth.models import User
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.geos import Point, GEOSGeometry
from django.db import models
from django.contrib.gis.db import models
from django.db.models import Sum
from django.utils.timezone import now
from fastkml import kml
from shapely.geometry import mapping, shape
from django.utils.translation import gettext_lazy as _
from shapely.ops import unary_union
from simple_history.models import HistoricalRecords

Status_choices = [
    ('En projet', 'En projet'),
    ('Délimitée', 'Délimitée'),
    # ('En attente de validation', 'En attente de validation'),
    ('Défrichage', 'En cours de défrichage'),
    ('Prête', 'Prête pour la culture'),
    ('Aménagement', 'En cours d\'aménagement'),
    ('Ensemencée', 'Ensemencée'),
    ('En croissance', 'En croissance'),
    ('En floraison', 'En floraison'),
    ('En fructification', 'En fructification'),
    ('Récolte', 'Prête pour la récolte'),
    ('En récolte', 'En cours de récolte'),
    ('En jachère', 'En jachère'),
    ('Reconvertie', 'Reconvertie'),
    ('En reboisement', 'En reboisement'),
    ('En pause', 'En pause'),
    ('Observation', 'Sous observation'),
    ('En traitement', 'En traitement'),
    ('Abandonnée', 'Abandonnée'),
    ('En expérimentation', 'En expérimentation'),
    ('Protégée', 'En zone protégée'),
    ('Réservée', 'Réservée'),
]
Sexe_choices = [
    ('Homme', 'Homme'),
    ('Femme', 'Femme'),

]
nationalite_choices = [
    ('Afghane', 'Afghane'),
    ('Albanaise', 'Albanaise'),
    ('Algérienne', 'Algérienne'),
    ('Allemande', 'Allemande'),
    ('Américaine', 'Américaine'),
    ('Andorrane', 'Andorrane'),
    ('Angolaise', 'Angolaise'),
    ('Antiguaise-et-Barbudienne', 'Antiguaise-et-Barbudienne'),
    ('Argentine', 'Argentine'),
    ('Arménienne', 'Arménienne'),
    ('Australienne', 'Australienne'),
    ('Autrichienne', 'Autrichienne'),
    ('Azerbaïdjanaise', 'Azerbaïdjanaise'),
    ('Bahamienne', 'Bahamienne'),
    ('Bahreïnienne', 'Bahreïnienne'),
    ('Bangladaise', 'Bangladaise'),
    ('Barbadiènne', 'Barbadiènne'),
    ('Bélarusse', 'Bélarusse'),
    ('Belge', 'Belge'),
    ('Bélizienne', 'Bélizienne'),
    ('Béninoise', 'Béninoise'),
    ('Bhoutanaise', 'Bhoutanaise'),
    ('Birmane', 'Birmane'),
    ('Bolivienne', 'Bolivienne'),
    ('Bosniaque', 'Bosniaque'),
    ('Botswanéenne', 'Botswanéenne'),
    ('Brésilienne', 'Brésilienne'),
    ('Britannique', 'Britannique'),
    ('Brunéienne', 'Brunéienne'),
    ('Bulgare', 'Bulgare'),
    ('Burkinabè', 'Burkinabè'),
    ('Burundaise', 'Burundaise'),
    ('Cambodgienne', 'Cambodgienne'),
    ('Camerounaise', 'Camerounaise'),
    ('Canadienne', 'Canadienne'),
    ('Cap-Verdienne', 'Cap-Verdienne'),
    ('Centrafricaine', 'Centrafricaine'),
    ('Chilienne', 'Chilienne'),
    ('Chinoise', 'Chinoise'),
    ('Chypriote', 'Chypriote'),
    ('Colombienne', 'Colombienne'),
    ('Comorienne', 'Comorienne'),
    ('Congolaise (Congo-Brazzaville)', 'Congolaise (Congo-Brazzaville)'),
    ('Congolaise (Congo-Kinshasa)', 'Congolaise (Congo-Kinshasa)'),
    ('Costaricaine', 'Costaricaine'),
    ('Croate', 'Croate'),
    ('Cubaine', 'Cubaine'),
    ('Danoise', 'Danoise'),
    ('Djiboutienne', 'Djiboutienne'),
    ('Dominicaine', 'Dominicaine'),
    ('Dominicain(e)', 'Dominicain(e)'),
    ('Égyptienne', 'Égyptienne'),
    ('Émirienne', 'Émirienne'),
    ('Équatorienne', 'Équatorienne'),
    ('Érythréenne', 'Érythréenne'),
    ('Espagnole', 'Espagnole'),
    ('Estonienne', 'Estonienne'),
    ('Éthiopienne', 'Éthiopienne'),
    ('Fidjienne', 'Fidjienne'),
    ('Finlandaise', 'Finlandaise'),
    ('Française', 'Française'),
    ('Gabonaise', 'Gabonaise'),
    ('Gambienne', 'Gambienne'),
    ('Géorgienne', 'Géorgienne'),
    ('Ghanéenne', 'Ghanéenne'),
    ('Grenadienne', 'Grenadienne'),
    ('Guatémaltèque', 'Guatémaltèque'),
    ('Guinéenne', 'Guinéenne'),
    ('Guinéenne (Guinée-Bissau)', 'Guinéenne (Guinée-Bissau)'),
    ('Guyanienne', 'Guyanienne'),
    ('Haïtienne', 'Haïtienne'),
    ('Hellénique (Greque)', 'Hellénique (Greque)'),
    ('Hondurienne', 'Hondurienne'),
    ('Hongroise', 'Hongroise'),
    ('Indienne', 'Indienne'),
    ('Indonésienne', 'Indonésienne'),
    ('Irakienne', 'Irakienne'),
    ('Iranienne', 'Iranienne'),
    ('Irlandaise', 'Irlandaise'),
    ('Islandaise', 'Islandaise'),
    ('Israélienne', 'Israélienne'),
    ('Italienne', 'Italienne'),
    ('Ivoirienne', 'Ivoirienne'),
    ('Jamaïcaine', 'Jamaïcaine'),
    ('Japonaise', 'Japonaise'),
    ('Jordanienne', 'Jordanienne'),
    ('Kazakhe', 'Kazakhe'),
    ('Kényane', 'Kényane'),
    ('Kirghize', 'Kirghize'),
    ('Kiribatienne', 'Kiribatienne'),
    ('Koweïtienne', 'Koweïtienne'),
    ('Laotienne', 'Laotienne'),
    ('Lettone', 'Lettone'),
    ('Libanaise', 'Libanaise'),
    ('Libérienne', 'Libérienne'),
    ('Libyenne', 'Libyenne'),
    ('Liechtensteinoise', 'Liechtensteinoise'),
    ('Lituanienne', 'Lituanienne'),
    ('Luxembourgeoise', 'Luxembourgeoise'),
    ('Macédonienne', 'Macédonienne'),
    ('Malaisienne', 'Malaisienne'),
    ('Malawienne', 'Malawienne'),
    ('Maldivienne', 'Maldivienne'),
    ('Malgache', 'Malgache'),
    ('Malienne', 'Malienne'),
    ('Maltaise', 'Maltaise'),
    ('Marocaine', 'Marocaine'),
    ('Maréchalienne', 'Maréchalienne'),
    ('Mauricienne', 'Mauricienne'),
    ('Mauritanienne', 'Mauritanienne'),
    ('Mexicaine', 'Mexicaine'),
    ('Micronésienne', 'Micronésienne'),
    ('Moldave', 'Moldave'),
    ('Monégasque', 'Monégasque'),
    ('Mongole', 'Mongole'),
    ('Monténégrine', 'Monténégrine'),
    ('Mozambicaine', 'Mozambicaine'),
    ('Namibienne', 'Namibienne'),
    ('Nauruane', 'Nauruane'),
    ('Népalaise', 'Népalaise'),
    ('Nicaraguayenne', 'Nicaraguayenne'),
    ('Nigérienne', 'Nigérienne'),
    ('Nigériane', 'Nigériane'),
    ('Norvégienne', 'Norvégienne'),
    ('Néo-Zélandaise', 'Néo-Zélandaise'),
    ('Omanaise', 'Omanaise'),
    ('Ougandaise', 'Ougandaise'),
    ('Ouzbèke', 'Ouzbèke'),
    ('Pakistanaise', 'Pakistanaise'),
    ('Palaosienne', 'Palaosienne'),
    ('Palestinienne', 'Palestinienne'),
    ('Panaméenne', 'Panaméenne'),
    ('Papouane-Néo-Guinéenne', 'Papouane-Néo-Guinéenne'),
    ('Paraguayenne', 'Paraguayenne'),
    ('Néerlandaise', 'Néerlandaise'),
    ('Péruvienne', 'Péruvienne'),
    ('Philippine', 'Philippine'),
    ('Polonaise', 'Polonaise'),
    ('Portugaise', 'Portugaise'),
    ('Qatarienne', 'Qatarienne'),
    ('Roumaine', 'Roumaine'),
    ('Russe', 'Russe'),
    ('Rwandaise', 'Rwandaise'),
    ('Saint-Christophoro-Névicienne', 'Saint-Christophoro-Névicienne'),
    ('Saint-Lucienne', 'Saint-Lucienne'),
    ('Saint-Marinaise', 'Saint-Marinaise'),
    ('Saint-Vincentaise-et-Grenadine', 'Saint-Vincentaise-et-Grenadine'),
    ('Salomonaise', 'Salomonaise'),
    ('Salvadorienne', 'Salvadorienne'),
    ('Samoane', 'Samoane'),
    ('Santoméenne', 'Santoméenne'),
    ('Saoudienne', 'Saoudienne'),
    ('Sénégalaise', 'Sénégalaise'),
    ('Serbe', 'Serbe'),
    ('Seychelloise', 'Seychelloise'),
    ('Sierra-Léonaise', 'Sierra-Léonaise'),
    ('Singapourienne', 'Singapourienne'),
    ('Slovaque', 'Slovaque'),
    ('Slovène', 'Slovène'),
    ('Somalienne', 'Somalienne'),
    ('Soudanaise', 'Soudanaise'),
    ('Sud-Africaine', 'Sud-Africaine'),
    ('Sud-Soudanaise', 'Sud-Soudanaise'),
    ('Sri-Lankaise', 'Sri-Lankaise'),
    ('Suédoise', 'Suédoise'),
    ('Suisse', 'Suisse'),
    ('Surinamaise', 'Surinamaise'),
    ('Swazie', 'Swazie'),
    ('Syrienne', 'Syrienne'),
    ('Tadjike', 'Tadjike'),
    ('Tanzanienne', 'Tanzanienne'),
    ('Tchadienne', 'Tchadienne'),
    ('Tchèque', 'Tchèque'),
    ('Thaïlandaise', 'Thaïlandaise'),
    ('Timoraise', 'Timoraise'),
    ('Togolaise', 'Togolaise'),
    ('Tonguienne', 'Tonguienne'),
    ('Trinidadienne', 'Trinidadienne'),
    ('Tunisienne', 'Tunisienne'),
    ('Turkmène', 'Turkmène'),
    ('Turque', 'Turque'),
    ('Tuvaluane', 'Tuvaluane'),
    ('Ukrainienne', 'Ukrainienne'),
    ('Uruguayenne', 'Uruguayenne'),
    ('Vanuatuane', 'Vanuatuane'),
    ('Vénézuélienne', 'Vénézuélienne'),
    ('Vietnamienne', 'Vietnamienne'),
    ('Yéménite', 'Yéménite'),
    ('Zambienne', 'Zambienne'),
    ('Zimbabwéenne', 'Zimbabwéenne')
]
communes_et_quartiers_choices = [
    ('Abobo', 'Abobo'),
    ('Adjamé', 'Adjamé'),
    ('Aboisso', 'Aboisso'),
    ('Abengourou', 'Abengourou'),
    ('Adzopé', 'Adzopé'),
    ('Agboville', 'Agboville'),
    ('Agboville', 'Agboville'),
    ('Anyama', 'Anyama'),
    ('Attécoubé', 'Attécoubé'),
    ('Bongouanou', 'Bongouanou'),
    ('Bondoukou', 'Bondoukou'),
    ('Bouaflé', 'Bouaflé'),
    ('Bouaké', 'Bouaké'),
    ('Bouna', 'Bouna'),
    ('Bonoua', 'Bonoua'),
    ('Cocody', 'Cocody'),
    ('Daloa', 'Daloa'),
    ('Divo', 'Divo'),
    ('Grand-Bassam', 'Grand-Bassam'),
    ('Grand-Lahou', 'Grand-Lahou'),
    ('Guiglo', 'Guiglo'),
    ('Korhogo', 'Korhogo'),
    ('Man', 'Man'),
    ('San Pedro', 'San Pedro'),
    ('San Pédro', 'San Pédro'),
    ('Séguéla', 'Séguéla'),
    ('Sinfra', 'Sinfra'),
    ('Soubré', 'Soubré'),
    ('Tanda', 'Tanda'),
    ('Tabou', 'Tabou'),
    ('Tingrela', 'Tingrela'),
    ('Yamoussoukro', 'Yamoussoukro'),
    ('Yopougon', 'Yopougon'),
    ('Bingerville', 'Bingerville'),
    ('Daloa', 'Daloa'),
    ('Tiassalé', 'Tiassalé'),
    ('Akan', 'Akan'),
    ('Dimbokro', 'Dimbokro'),
    ('Gagnoa', 'Gagnoa'),
    ('Dabou', 'Dabou'),
    ('Lakota', 'Lakota'),
    ('Katiola', 'Katiola'),
    ('Mankono', 'Mankono'),
    ('Niakara', 'Niakara'),
    ('Ouangolodougou', 'Ouangolodougou'),
    ('Oumé', 'Oumé'),
    ('Tiebissou', 'Tiebissou'),
    ('Danané', 'Danané'),
    ('Odienné', 'Odienné'),
    ('Tiapoum', 'Tiapoum'),
    ('Bounoua', 'Bounoua'),
    ('Bouaflé', 'Bouaflé'),
    ('Bingerville', 'Bingerville'),
    ('Kouassi-Datékro', 'Kouassi-Datékro'),
    ('Zuenoula', 'Zuenoula'),
    ('Ferkessedougou', 'Ferkessedougou'),
    ('Dabakala', 'Dabakala'),
    ('Tiebissou', 'Tiebissou'),
    ('Bingerville', 'Bingerville'),
    ('Moussoukoro', 'Moussoukoro'),
    ('Zouan-Hounien', 'Zouan-Hounien'),
    ('Vavoua', 'Vavoua'),
    ('Sikensi', 'Sikensi'),
    ('Bouna', 'Bouna'),
    ('Oberlin', 'Oberlin'),
    ('Bongouanou', 'Bongouanou'),
    ('Bocanda', 'Bocanda'),
    ('Kani', 'Kani'),
    ('Brobo', 'Brobo'),
    ('Prikro', 'Prikro'),
    ('Niakara', 'Niakara'),
    ('Dabou', 'Dabou'),
    ('Katiola', 'Katiola'),
    ('Kouibly', 'Kouibly'),
    ('Sakassou', 'Sakassou'),
    ('Tengrela', 'Tengrela'),
    ('Bouaflé', 'Bouaflé'),
    ('Gagnoa', 'Gagnoa'),
    ('Mankono', 'Mankono'),
    ('Oumé', 'Oumé'),
    ('Grand Lahou', 'Grand Lahou'),
    ('Ouangolodougou', 'Ouangolodougou'),
    ('Kouassi-Kouassikro', 'Kouassi-Kouassikro'),
    ('Sassandra', 'Sassandra'),
    ('Autre', 'Autre'),
]
situation_matrimoniales_choices = [
    ('Celibataire', 'Celibataire'),
    ('Concubinage', 'Concubinage'),
    ('Marie', 'Marié'),
    ('Divorce', 'Divorcé'),
    ('Veuf', 'Veuf'),
    ('Autre', 'Autre'),
]


def get_random_code() -> str:
    return str(datetime.date.today().year)[2:] + str(random.randint(0000, 999999))


def qlook():
    qlook = ("QL" + str(random.randrange(0, 999999999, 1)) + "URAP")
    return qlook


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee", )
    qlook_id = models.CharField(default=qlook, unique=True, editable=False, max_length=100)
    gender = models.CharField(choices=Sexe_choices, max_length=100, null=True, blank=True, )
    situation_matrimoniale = models.CharField(choices=situation_matrimoniales_choices, max_length=100, null=True,
                                              blank=True, )

    persone_ref_noms = models.CharField(null=True, blank=True, max_length=100, default='Jean Kouame')
    persone_ref_contact = models.CharField(null=True, blank=True, max_length=100, default='05 00 05 00 05')
    num_cnps = models.CharField(null=True, blank=True, max_length=100, default='CNPS00000000')
    phone = models.CharField(null=True, blank=True, max_length=20, default='+22507070707')

    nationalite = models.CharField(null=True, blank=True, default='00000000', max_length=70, )
    personal_mail = models.CharField(null=True, blank=True, default='email@sah.com', max_length=70)
    birthdate = models.DateField(null=True, blank=True)
    date_embauche = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    salary = models.FloatField(blank=True, max_length=100, null=True)
    majoration = models.IntegerField(blank=True, null=True)

    job_title = models.CharField(null=True, blank=True, max_length=50, verbose_name="Titre du poste")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numéro de téléphone")
    photo = models.ImageField(null=True, blank=True, default='urap/users/5.png', upload_to='urap/users')
    sortie = models.SmallIntegerField(null=True, blank=True, default=0)
    slug = models.SlugField(null=True, blank=True, help_text="slug field", verbose_name="slug ", unique=True,
                            editable=False)
    created_at = models.DateTimeField(auto_now_add=now, )
    history = HistoricalRecords()

    @property
    def daily_cost(self):
        """
        Calculate the daily cost and hourly cost based on the monthly salary.
        Results are rounded to the nearest integer.
        """
        if self.salary is not None:
            monthly_salary = self.salary
            daily_cost = int(monthly_salary / 22)  # Convert to integer
            hourly_cost = int(daily_cost / 8)  # Convert to integer
            return {
                "daily_cost": daily_cost,
                "hourly_cost": hourly_cost,
            }
        return {
            "daily_cost": 0,
            "hourly_cost": 0,
        }

    @property
    def selling_price(self):
        """
        Calculate the selling price based on daily cost and markup.
        Results are rounded to the nearest integer.
        """
        costs = self.daily_cost  # Access the daily_cost property (no parentheses)
        daily_cost = costs["daily_cost"]
        hourly_cost = costs["hourly_cost"]

        if daily_cost > 0 and self.majoration is not None:
            markup = self.majoration / 100
            selling_price_daily = int(daily_cost * (1 + markup))
            selling_price_hourly = int(hourly_cost * (1 + markup))
            return {
                "selling_price_daily": selling_price_daily,
                "selling_price_hourly": selling_price_hourly,
            }

        return {
            "selling_price_daily": 0,
            "selling_price_hourly": 0,
        }

    def __str__(self):
        return f"{self.user.username}- {self.user.first_name} {self.user.last_name}"

    class Meta:
        permissions = (
            ("can_edit_employee", "Can edit employee"),
            ("can_create_employee", "Can create employee"),
            ("can_view_salary", "can view salary"),
            ("can_view_employee", "can view employee"),
        )


# Create your models here.
class Region(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class DistrictSanitaire(models.Model):
    nom = models.CharField(max_length=100, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    geom = models.PointField(null=True, blank=True, )
    geojson = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.nom}"


class Ville(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)
    place = models.CharField(max_length=100, null=True, blank=True)
    population = models.CharField(max_length=100, null=True, blank=True)
    is_in = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    osm_id = models.BigIntegerField(null=True, blank=True)
    osm_type = models.CharField(max_length=50, null=True, blank=True)
    district = models.ForeignKey(DistrictSanitaire, on_delete=models.CASCADE, null=True, blank=True)
    geom = models.PointField(null=True, blank=True, )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name}"


class Cooperative(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=100, default=uuid.uuid4, unique=True)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, null=True, blank=True)
    president = models.ForeignKey('Producteur', on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='president')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ("can_edit", "Can edit "),
            ("can_create", "Can create "),
            ("can_view", "can view "),
            ("can_members", "can view "),
        )
        verbose_name = "Coopérative"
        verbose_name_plural = "Coopératives"

    def __str__(self):
        return self.nom


class CooperativeMember(models.Model):
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, null=True, blank=True)
    producteurs = models.ManyToManyField('Producteur', related_name='members', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.cooperative} - {self.producteurs}"


class Producteur(models.Model):
    nom = models.CharField(max_length=100, null=True, blank=True)
    prenom = models.CharField(max_length=500, null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    telephone = models.CharField(max_length=20, blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    lieu_naissance = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(null=True, blank=True, upload_to="products/%Y/%m/%d/")
    cooperative = models.ForeignKey(Cooperative, on_delete=models.CASCADE, related_name="producteurs", null=True,
                                    blank=True)
    fonction = models.CharField(max_length=100, null=True, blank=True)
    projet = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ("can_edit", "Can edit "),
            ("can_create", "Can create "),
            ("can_update", "Can update "),
            ("can_view", "can view "),
        )
        verbose_name = "Producteur"
        verbose_name_plural = "Producteurs"

    def fonction(self):
        if self.cooperative and self.cooperative.president == self:
            return "Président de coopérative"
        elif self.cooperative:
            return "Membre de coopérative"
        return "Aucune Coopérative"

    def __str__(self):
        return f"{self.nom} {self.prenom}" if self.nom and self.prenom else self.nom or "Producteur anonyme"


class Parcelle(models.Model):
    producteur = models.ForeignKey(Producteur, on_delete=models.CASCADE, related_name="parcelles")
    code = models.CharField(max_length=100, null=True, blank=True)
    localite = models.ForeignKey(Ville, on_delete=models.CASCADE, null=True, blank=True)

    nom = models.CharField(max_length=100, null=True, blank=True)
    dimension_ha = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    polygone_kmz = models.FileField(upload_to="parcelles/", blank=True, null=True)
    geojson = models.JSONField(null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    geom = models.PointField(null=True, blank=True, srid=4326)
    status = models.CharField(choices=Status_choices, null=True, blank=True, max_length=100)
    carracteristic = models.JSONField(null=True, blank=True)
    culture = models.JSONField(null=True, blank=True)
    culture_perenne = models.ManyToManyField('CulturePerennial', related_name="cultureperenne", blank=True)
    culture_saisonniere = models.ManyToManyField('CultureSeasonal', related_name="culturesaison", blank=True)
    affectations = models.TextField(null=True, blank=True)  # Pour les événements affectant la parcelle

    images = models.ImageField(upload_to="parcelles/", blank=True, null=True)
    projet = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ("can_edit", "Can edit "),
            ("can_create", "Can create "),
            ("can_view", "can view "),
        )
        verbose_name = "Parcelle"
        verbose_name_plural = "Parcelles"

    def save(self, *args, **kwargs):
        # Vérifier si le fichier KMZ a changé
        kmz_changed = self.pk is None or self.polygone_kmz != type(self).objects.get(pk=self.pk).polygone_kmz

        # Si le fichier KMZ a changé, convertir en GeoJSON et recalculer les champs
        if kmz_changed and self.polygone_kmz:
            self.geojson = self.kmz_to_geojson()

        # Calculer la surface et les coordonnées si un GeoJSON valide est disponible
        if self.geojson:
            try:
                # Combiner les géométries pour obtenir une surface unique
                geometries = [shape(feature["geometry"]) for feature in self.geojson["features"]]
                combined_geometry = unary_union(geometries)

                # Vérifier si la géométrie combinée est valide
                if combined_geometry.is_valid:
                    # Reprojection pour calcul précis (EPSG:4326 vers EPSG:3857)
                    srid_target = SpatialReference(3857)  # Système métrique
                    srid_source = SpatialReference(4326)  # Système source (KMZ)
                    transform = CoordTransform(srid_source, srid_target)

                    # Convertir la géométrie en EPSG:3857
                    gdal_geometry = GEOSGeometry(json.dumps(mapping(combined_geometry)), srid=4326)
                    gdal_geometry.transform(transform)

                    # Calculer la surface en hectares
                    self.dimension_ha = round(gdal_geometry.area / 10000, 4)

                    # Centroid pour la localisation
                    centroid = combined_geometry.centroid
                    self.longitude = round(centroid.x, 6)
                    self.latitude = round(centroid.y, 6)
                    self.geom = Point(centroid.x, centroid.y, srid=4326)
                else:
                    print("Géométrie invalide détectée dans le fichier KMZ.")
            except Exception as e:
                print(f"Erreur lors du calcul de la dimension ou des coordonnées : {e}")

        super().save(*args, **kwargs)

    def extract_features(self, features, geojson_features):
        """Parcours récursif des fonctionnalités pour extraire les géométries"""
        for feature in features:
            if hasattr(feature, "geometry") and feature.geometry:
                geojson_features.append({
                    "type": "Feature",
                    "geometry": mapping(feature.geometry),
                    "properties": {"name": feature.name}
                })
            if hasattr(feature, "features"):  # Si le feature a des enfants
                self.extract_features(feature.features(), geojson_features)

    def kmz_to_geojson(self):
        """Convertit un fichier KMZ en GeoJSON"""
        try:
            with zipfile.ZipFile(BytesIO(self.polygone_kmz.read())) as kmz:
                # Rechercher le fichier KML dans l'archive
                kml_file = [f for f in kmz.namelist() if f.endswith(".kml")][0]
                with kmz.open(kml_file, "r") as kml_content:
                    k = kml.KML()
                    k.from_string(kml_content.read().decode("utf-8"))

                    geojson_features = []
                    self.extract_features(k.features(), geojson_features)

                    if not geojson_features:
                        print("Aucune fonctionnalité valide trouvée dans le fichier KML.")
                        return None

                    return {
                        "type": "FeatureCollection",
                        "features": geojson_features
                    }
        except Exception as e:
            print(f"Erreur lors de la conversion du fichier KMZ : {e}")
            return None

    def __str__(self):
        return f"{self.nom} ({self.dimension_ha} ha)" if self.nom else f"Parcelle sans nom ({self.dimension_ha} ha)"


class CulturePerennial(models.Model):
    parcelle = models.ForeignKey('Parcelle', on_delete=models.CASCADE, related_name="cultures_perennial")
    type_culture = models.CharField(max_length=100)
    annee_mise_en_place = models.PositiveIntegerField()
    date_derniere_recolte = models.DateField(null=True, blank=True)
    dernier_rendement_kg_ha = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pratiques_culturales = models.TextField(null=True, blank=True)
    utilise_fertilisants = models.BooleanField(default=False)
    type_fertilisants = models.TextField(null=True, blank=True)
    analyse_sol = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type_culture} ({self.parcelle.nom})"


class CultureSeasonal(models.Model):
    parcelle = models.ForeignKey('Parcelle', on_delete=models.CASCADE, related_name="cultures_seasonal")
    type_culture = models.CharField(max_length=100)
    annee_mise_en_place = models.PositiveIntegerField()
    date_recolte = models.DateField(null=True, blank=True)
    dernier_rendement_kg_ha = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pratiques_culturales = models.TextField(null=True, blank=True)
    utilise_fertilisants = models.BooleanField(default=False)
    type_fertilisants = models.TextField(null=True, blank=True)
    analyse_sol = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type_culture} ({self.parcelle.nom})"


class Project(models.Model):
    STATUS_CHOICES = [
        ('not_started', _('Not Started')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('on_hold', _('On Hold')),
        ('cancelled', _('Cancelled')),
    ]

    name = models.CharField(max_length=200, verbose_name=_("Project Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    start_date = models.DateField(verbose_name=_("Date de début"))
    end_date = models.DateField(verbose_name=_("Date de fin"), null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started', verbose_name=_("Status"))
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="managed_projects",
                                verbose_name=_("Project Manager"))
    members = models.ManyToManyField(Employee, related_name="projects", blank=True, verbose_name=_("Team Members"))
    parcelles = models.ManyToManyField(Parcelle, related_name="parcelle_projects", blank=True,
                                       verbose_name=_("parcelles"))
    marge_previsionnel = models.IntegerField(verbose_name=_("marge previsionnel"), null=True, blank=True)
    previsionnel = models.IntegerField(verbose_name=_("Budget Previsionnel"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ("can_edit", "Can edit "),
            ("can_create", "Can create "),
            ("can_view", "can view "),
            ("can_member", "can member "),
            ("can_view_task", "can view task "),
            ("can_view_budgets", "can view budget "),
            ("can_view_p&l", "can view p&l "),
        )

    def get_total_expenses(self):
        """
        Calcule la somme des dépenses associées au projet.
        """
        total_expenses = self.depenses.aggregate(total=Sum('montant'))['total'] or 0
        return total_expenses

    def get_total_hours_by_employee(self, employee):
        """
        Calcule le cumul des heures des tâches assignées à un employé spécifique pour ce projet.
        """
        total_hours = self.tasks.filter(assigned_to=employee).aggregate(total=models.Sum('nbr_heure'))
        return total_hours['total'] or 0

    # @property
    # def budget_estimatif(self):
    #     """
    #     Calcule le budget estimatif du projet en additionnant les montants des dépenses enregistrées.
    #     """
    #     depenses = Depense.objects.filter(projet=self)  # Récupère toutes les dépenses liées à ce projet
    #     total_depenses = depenses.aggregate(total_budget=models.Sum('montant'))  # Additionne toutes les dépenses
    #     return total_depenses['total_budget'] or 0  # Retourne le total des dépenses ou 0 si aucune dépense

    @property
    def budget_estimatif(self):
        """
        Calcule le budget estimatif du projet :
        1. Cumul des heures travaillées par les membres converties en jours et multipliées par leur selling price.
        2. Ajoute la somme des dépenses associées au projet.
        """
        # Récupérer les membres du projet
        total_hours_cost = 0
        for member in self.members.all():
            # Obtenir le total des heures de l'employé pour ce projet
            total_hours = self.get_total_hours_by_employee(member)

            # Convertir les heures en jours (8 heures par jour)
            total_days = total_hours / 8 if total_hours else 0

            # Calculer le coût basé sur le selling price journalier
            selling_price_daily = member.selling_price.get("selling_price_daily", 0)
            total_hours_cost += total_days * selling_price_daily

        # Calculer la somme des dépenses associées
        depenses = Depense.objects.filter(projet=self)  # Dépenses liées au projet
        total_depenses = depenses.aggregate(total_budget=Sum('montant'))['total_budget'] or 0

        # Somme des coûts des membres et des dépenses
        budget_total = total_hours_cost + total_depenses
        return budget_total

    @property
    def marge_estimatif(self):
        marge = self.previsionnel - self.budget_estimatif

        return marge

    @property
    def profit_percentage(self):
        """
        Calcule le pourcentage de profit basé sur la marge prévisionnelle et la marge estimative.
        """
        if self.marge_previsionnel and self.marge_estimatif:
            profit = max(self.marge_estimatif, 0)  # Seulement si la marge est positive
            return (profit / self.marge_previsionnel) * 100
        return 0

    @property
    def loss_percentage(self):
        """
        Calcule le pourcentage de perte basé sur la marge prévisionnelle et la marge estimative.
        """
        if self.marge_previsionnel and self.marge_estimatif:
            loss = max(-self.marge_estimatif, 0)  # Seulement si la marge est négative
            return (loss / self.marge_previsionnel) * 100
        return 0

    def __str__(self):
        return self.name

    @property
    def progress_percentage(self):
        """
        Calcule la progression en pourcentage entre la start_date et la end_date.
        """
        if not self.start_date or not self.end_date:
            return 0  # Retourne 0% si les dates ne sont pas définies

        today = datetime.date.today()
        total_duration = (self.end_date - self.start_date).days
        elapsed_duration = (today - self.start_date).days

        # Si la date actuelle dépasse la date de fin
        if elapsed_duration >= total_duration:
            return 100
        # Si la date actuelle est avant la date de début
        if elapsed_duration <= 0:
            return 0

        # Calculer le pourcentage
        progress = (elapsed_duration / total_duration) * 100
        return int(progress)


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]

    STATUS_CHOICES = [
        ('non_debute', _('non debuté')),
        ('en_cours', _('en cours')),
        ('Terminée', _('Completed')),
        ('en_attente', _('en attente')),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks", verbose_name=_("Projet"),
                                null=True, blank=True)
    name = models.CharField(max_length=200, verbose_name=_("Nom de la Tâche"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    start_date = models.DateTimeField(verbose_name=_("Start Date"), null=True, blank=True)
    due_date = models.DateTimeField(verbose_name=_("Due Date"), null=True, blank=True)
    nbr_heure = models.IntegerField(verbose_name=_("Nombre d\'Heure"), null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name=_("Priorité"),
                                null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='not_started', verbose_name=_("Status")
        , null=True, blank=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="assigned_tasks", verbose_name=_("Assigner à"))
    assigned_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="assigned_tasks_by", verbose_name=_("Assigner par"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # Si start_date et nbr_heure sont définis, on calcule due_date
        if self.start_date and self.nbr_heure:
            self.due_date = self.start_date + datetime.timedelta(hours=self.nbr_heure)

        # Appeler la méthode save de la classe parent pour enregistrer l'objet
        super().save(*args, **kwargs)

    class Meta:
        permissions = (
            ("can_edit", "Can edit "),
            ("can_create", "Can create "),
            ("can_view", "can view "),
            ("can_assign_task", "can assign task "),
        )

    def __str__(self):
        return self.name


class Milestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones", verbose_name=_("Project"))
    name = models.CharField(max_length=200, verbose_name=_("Milestone Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    due_date = models.DateField(verbose_name=_("Due Date"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Is Completed"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ("can_edit", "Can edit "),
            ("can_create", "Can create "),
            ("can_view", "can view "),
        )

    def __str__(self):
        return f"{self.name} ({'Completed' if self.is_completed else 'Pending'})"


class Depense(models.Model):
    # Choix pour les catégories de dépenses (ex: matériel, salaires, frais généraux, etc.)
    CATEGORIE_CHOICES = [
        ('matériel', 'Matériel'),
        ('salaires', 'Salaires'),
        ('frais_generaux', 'Frais généraux'),
        ('transport', 'Transport'),
        ('autre', 'Autre'),
    ]

    # Informations de base sur la dépense
    projet = models.ForeignKey('Project', on_delete=models.CASCADE, related_name="depenses")  # Relation avec le projet
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES)
    description = models.TextField(null=True, blank=True)  # Description optionnelle de la dépense
    montant = models.IntegerField(null=True, blank=True)  # Montant de la dépense
    date = models.DateField()  # Date de la dépense
    responsable = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True,
                                    blank=True)  # Responsable de la dépense
    justificatif = models.FileField(upload_to='depenses/justificatifs/', null=True,
                                    blank=True)  # Justificatif de la dépense

    # Méthode pour afficher des informations utiles sur la dépense
    def __str__(self):
        return f"{self.projet.name} - {self.categorie} - {self.montant} F CFA"

    class Meta:
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"
        ordering = ['-date']  # Tri par date, de la plus récente à la plus ancienne


class Deliverable(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="deliverables",
                                verbose_name=_("Project"))
    name = models.CharField(max_length=200, verbose_name=_("Deliverable Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    file = models.FileField(upload_to='deliverables/', verbose_name=_("File"), null=True, blank=True)
    is_approved = models.BooleanField(default=False, verbose_name=_("Is Approved"))
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Submitted At"))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ("can_edit", "Can edit "),
            ("can_create", "Can create "),
            ("can_view", "can view "),
        )

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom de l'événement")
    description = models.TextField(blank=True, verbose_name="Description")
    start_date = models.DateTimeField(verbose_name="Date de debut de l'événement")
    end_date = models.DateTimeField(verbose_name="Date de fin de l'événement")
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="Lieu")
    banner = models.FileField(upload_to='events/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class EventInvite(models.Model):
    INVITE_TYPE_CHOICES = [
        ('producteur', 'Producteur'),
        ('cooperative', 'Coopérative'),
        ('ville', 'Ville'),
        ('district', 'District'),
        ('region', 'Région'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="invites")
    invite_type = models.CharField(max_length=20, choices=INVITE_TYPE_CHOICES, verbose_name="Type d'invité")
    invite_id = models.IntegerField(
        verbose_name="ID de l'entité invitée")  # ID de l'entité associée (Producteur, Ville, etc.)
    confirmed = models.BooleanField(default=False, verbose_name="Confirmation de présence")
    confirmation_token = models.CharField(max_length=64, null=True, blank=True)
    confirmation_date = models.DateTimeField(null=True, blank=True,
                                             verbose_name="Date de confirmation")  # Nouveau champ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_invite(self):
        """
        Récupère l'objet correspondant au type et à l'ID d'invité.
        """
        if self.invite_type == 'producteur':
            return Producteur.objects.get(id=self.invite_id)
        elif self.invite_type == 'cooperative':
            return Cooperative.objects.get(id=self.invite_id)
        elif self.invite_type == 'ville':
            return Ville.objects.get(id=self.invite_id)
        elif self.invite_type == 'district':
            return DistrictSanitaire.objects.get(id=self.invite_id)
        elif self.invite_type == 'region':
            return Region.objects.get(id=self.invite_id)
        return None

    def __str__(self):
        # Use get_invite_type_display() to get the human-readable name of the invite_type field
        return f"{self.get_invite()} ({self.get_invite_type_display()})"


class DynamicForm(models.Model):
    project = models.ForeignKey(Project, related_name="forms", on_delete=models.CASCADE, verbose_name="Projet")
    name = models.CharField(max_length=255, verbose_name="Nom du Formulaire")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return f"{self.name} ({self.project.name})"


class DynamicField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('date', 'Date'),
        ('select', 'Select'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
    ]

    form = models.ForeignKey(DynamicForm, related_name="fields", on_delete=models.CASCADE, verbose_name="Formulaire")
    label = models.CharField(max_length=255, verbose_name="Label")
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES, verbose_name="Type de Champ")
    required = models.BooleanField(default=True, verbose_name="Requis")
    options = models.TextField(blank=True, null=True,
                               help_text="Valeurs séparées par des virgules pour 'select', 'checkbox', ou 'radio'.",
                               verbose_name="Options")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    def __str__(self):
        return f"{self.label} ({self.field_type})"


class FormResponse(models.Model):
    form = models.ForeignKey(DynamicForm, related_name="responses", on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)


class FieldResponse(models.Model):
    response = models.ForeignKey(FormResponse, related_name="field_responses", on_delete=models.CASCADE)
    field = models.ForeignKey(DynamicField, on_delete=models.CASCADE)
    value = models.TextField()
