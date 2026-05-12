"""
Run this script from the csv_data directory:
    cd C:\\Users\\Veer\\Desktop\\mauriguide-ai\\backend\\django_app\\datasets\\csv_data
    python fix_csvs.py

It splits the 'coordinates' column into separate 'latitude' and 'longitude'
columns for all 5 CSV files that need it. sites_to_visit.csv is already correct.
"""

import csv
import os
from pathlib import Path

# Each entry: (filename, position to insert lat/lng after removing coordinates)
FILES = [
    "beaches.csv",
    "food_outlets.csv",
    "water_activities.csv",
    "land_activities.csv",
    "hikes.csv",
]

def fix_csv(filename):
    path = Path(filename)
    if not path.exists():
        print(f"  SKIP — {filename} not found")
        return

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    if "coordinates" not in fieldnames:
        print(f"  SKIP — {filename} has no 'coordinates' column (already fixed?)")
        return

    # Build new fieldnames: replace 'coordinates' with 'latitude', 'longitude'
    new_fields = []
    for col in fieldnames:
        if col == "coordinates":
            new_fields.append("latitude")
            new_fields.append("longitude")
        else:
            new_fields.append(col)

    fixed_rows = []
    errors = []
    for i, row in enumerate(rows, start=2):
        coords = row.pop("coordinates", "").strip().strip('"')
        try:
            lat_str, lng_str = coords.split(",")
            row["latitude"] = lat_str.strip()
            row["longitude"] = lng_str.strip()
        except ValueError:
            row["latitude"] = ""
            row["longitude"] = ""
            errors.append(f"  Row {i}: could not parse coordinates '{coords}'")
        fixed_rows.append(row)

    # Write back
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(fixed_rows)

    print(f"  OK — {filename} — {len(fixed_rows)} rows fixed")
    for e in errors:
        print(e)


print("Fixing CSV files...\n")
for filename in FILES:
    fix_csv(filename)

print("\nDone! sites_to_visit.csv was already correct — not touched.")
print("\nVerifying column names in fixed files:")
for filename in FILES:
    path = Path(filename)
    if path.exists():
        with open(path, newline="", encoding="utf-8") as f:
            headers = csv.DictReader(f).fieldnames
        has_lat = "latitude" in headers
        has_lng = "longitude" in headers
        has_old = "coordinates" in headers
        status = "✅" if (has_lat and has_lng and not has_old) else "❌"
        print(f"  {status} {filename}: {headers}")
