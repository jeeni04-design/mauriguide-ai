"""
Django management command to import dataset CSVs one by one.

Usage (run from django_app directory):
    python manage.py import_dataset beaches
    python manage.py import_dataset food_outlets
    python manage.py import_dataset water_activities
    python manage.py import_dataset land_activities
    python manage.py import_dataset hikes
    python manage.py import_dataset sites_to_visit
    python manage.py import_dataset all
"""

import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from datasets.models import Beach, FoodOutlet, WaterActivity, LandActivity, Hike, SiteToVisit

CSV_DIR = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "csv_data"

DATASET_MAP = {
    "beaches": {
        "model": Beach,
        "file": "beaches.csv",
        "fields": ["name", "location", "description", "latitude", "longitude"],
    },
    "food_outlets": {
        "model": FoodOutlet,
        "file": "food_outlets.csv",
        "fields": ["name", "location", "contact_number", "speciality", "latitude", "longitude", "description"],
    },
    "water_activities": {
        "model": WaterActivity,
        "file": "water_activities.csv",
        "fields": ["activity", "category", "segment", "location", "latitude", "longitude", "description"],
    },
    "land_activities": {
        "model": LandActivity,
        "file": "land_activities.csv",
        "fields": ["activity", "place", "latitude", "longitude", "category", "description"],
    },
    "hikes": {
        "model": Hike,
        "file": "hikes.csv",
        "fields": ["trail_name", "difficulty", "latitude", "longitude", "details"],
    },
    "sites_to_visit": {
        "model": SiteToVisit,
        "file": "sites_to_visit.csv",
        "fields": ["place", "address", "location", "latitude", "longitude", "why_visit", "visitor_info", "best_time", "tips"],
    },
}


class Command(BaseCommand):
    help = "Import dataset CSV files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "dataset",
            type=str,
            help="Dataset to import: beaches, food_outlets, water_activities, land_activities, hikes, sites_to_visit, or 'all'"
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing records before importing"
        )

    def handle(self, *args, **options):
        dataset = options["dataset"]
        clear = options["clear"]

        if dataset == "all":
            for name in DATASET_MAP:
                self._import(name, clear)
        elif dataset in DATASET_MAP:
            self._import(dataset, clear)
        else:
            raise CommandError(
                f"Unknown dataset '{dataset}'. "
                f"Choose from: {', '.join(DATASET_MAP.keys())}, all"
            )

    def _import(self, name, clear):
        config = DATASET_MAP[name]
        Model = config["model"]
        csv_path = CSV_DIR / config["file"]
        fields = config["fields"]

        self.stdout.write(f"\n{'='*50}")
        self.stdout.write(f"Importing: {name}")
        self.stdout.write(f"File: {csv_path}")

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"  File not found: {csv_path}"))
            return

        if clear:
            count, _ = Model.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"  Cleared {count} existing records"))

        created = 0
        skipped = 0
        errors = []

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, start=2):
                # Strip whitespace from all values
                row = {k.strip(): v.strip() for k, v in row.items() if k}

                # Validate latitude and longitude
                try:
                    lat = float(row.get("latitude", ""))
                    lng = float(row.get("longitude", ""))
                except (ValueError, TypeError):
                    skipped += 1
                    errors.append(f"  Row {i}: invalid or missing coordinates — skipped")
                    continue

                # Build data dict from only known model fields
                model_fields = {f.name for f in Model._meta.fields}
                data = {}
                for field in fields:
                    if field in model_fields and field not in ("id", "created_at", "image"):
                        data[field] = row.get(field, "")

                data["latitude"] = lat
                data["longitude"] = lng

                # Type coercion for integer fields (e.g. Hike.difficulty)
                for f in Model._meta.fields:
                    if f.name in data:
                        if f.get_internal_type() == "IntegerField":
                            try:
                                data[f.name] = int(float(data[f.name]))
                            except (ValueError, TypeError):
                                skipped += 1
                                errors.append(f"  Row {i}: invalid integer for '{f.name}' — skipped")
                                data = None
                                break
                        elif f.get_internal_type() == "FloatField":
                            try:
                                data[f.name] = float(data[f.name])
                            except (ValueError, TypeError):
                                skipped += 1
                                errors.append(f"  Row {i}: invalid float for '{f.name}' — skipped")
                                data = None
                                break

                if data is None:
                    continue

                try:
                    Model.objects.create(**data)
                    created += 1
                except Exception as e:
                    skipped += 1
                    errors.append(f"  Row {i}: {e}")

        # Summary
        self.stdout.write(self.style.SUCCESS(f"  ✅ Created: {created} records"))
        if skipped:
            self.stdout.write(self.style.WARNING(f"  ⚠️  Skipped: {skipped} records"))
        for err in errors:
            self.stdout.write(self.style.ERROR(err))
        self.stdout.write(f"  Total in DB: {Model.objects.count()}")
