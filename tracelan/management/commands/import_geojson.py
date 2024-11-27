import json
from django.core.management.base import BaseCommand
from tracelan.models import Region, DistrictSanitaire, Ville
from django.contrib.gis.geos import Point, GEOSGeometry


class Command(BaseCommand):
    help = 'Import regions from a GeoJSON file into the database.'

    def add_arguments(self, parser):
        parser.add_argument('geojson_file', type=str, help='Path to the GeoJSON file')

    def handle(self, *args, **kwargs):
        geojson_file = kwargs['geojson_file']
        try:
            with open(geojson_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for feature in data['features']:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', None)

                # Get the name of the region
                name = properties.get('name')
                if not name:
                    self.stdout.write(self.style.WARNING("Skipping a feature with no name"))
                    continue

                # Save region
                region, created = Region.objects.get_or_create(name=name)
                if geometry:
                    region_geom = GEOSGeometry(json.dumps(geometry))
                    region.geom = region_geom

                region.save()
                status = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f"{status} region: {name}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during import: {e}"))
