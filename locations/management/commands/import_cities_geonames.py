# locations/management/commands/import_cities_geonames.py
import csv
from pathlib import Path
from typing import Optional, Iterable, Dict, Set

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from locations.models import Country, City

"""
GeoNames 'cities15000.txt' (yoki cities500.txt, cities1000.txt) TSV ustunlari (0-based):
0 geonameid, 1 name, 2 asciiname, 3 alternatenames, 4 latitude, 5 longitude,
6 feature class, 7 feature code, 8 country code (ISO2), 9 cc2,
10 admin1 code, 11 admin2 code, 12 admin3 code, 13 admin4 code,
14 population, 15 elevation, 16 dem, 17 timezone, 18 modification date
"""

def _int_or_zero(val: str) -> int:
    try:
        return int(val)
    except Exception:
        return 0

def _float_or_none(val: str) -> Optional[float]:
    try:
        return float(val)
    except Exception:
        return None

def _str(val: str) -> str:
    return (val or "").strip()

def _read_rows(path: Path) -> Iterable[list]:
    # '#' bilan boshlanadigan kommentlar yo‘q, ammo har ehtimolga qarshi filtrlab o‘tamiz
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            yield next(csv.reader([line], delimiter="\t"))

class Command(BaseCommand):
    help = "Import cities from GeoNames cities*.txt (e.g., cities15000.txt)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--file", required=True, help="Path to cities*.txt (TSV).")
        parser.add_argument(
            "--min-pop", type=int, default=15000,
            help="Minimum population filter (default: 15000)."
        )
        parser.add_argument(
            "--countries", type=str, default="",
            help="Comma-separated ISO2 filters (e.g., UZ,KZ,TR). If empty, all countries."
        )
        parser.add_argument(
            "--reactivate", action="store_true",
            help="Set is_active=True for imported/updated cities."
        )
        parser.add_argument(
            "--deactivate-missing", dest="deactivate_missing", action="store_true",
            help="Deactivate cities not present in this import (scope = filtered countries or all)."
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        path = Path(opts["file"])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {path}"))
            return

        min_pop = int(opts["min_pop"])
        iso_filter: Set[str] = {x.strip().upper() for x in opts["countries"].split(",") if x.strip()} if opts["countries"] else set()

        # Country cache: iso2 -> Country
        countries: Dict[str, Country] = {c.iso2: c for c in Country.objects.all()}
        if iso_filter:
            # mavjud bo‘lmagan iso2 larni oldindan ogohlantiramiz
            missing_iso = iso_filter - set(countries.keys())
            if missing_iso:
                self.stderr.write(self.style.WARNING(f"Countries not in DB (skip): {', '.join(sorted(missing_iso))}"))

        self.stdout.write(f"Reading: {path} (min_pop={min_pop}{', countries='+','.join(sorted(iso_filter)) if iso_filter else ''})")

        # deactivate-missing uchun eslab qolamiz:
        # agar countries filtri berilgan bo‘lsa — o‘sha davlat(lar) doirasida,
        # bo‘lmasa — global scope
        if iso_filter:
            existing_qs = City.objects.filter(country__iso2__in=iso_filter)
        else:
            existing_qs = City.objects.all()
        existing_ids: Set[int] = set(existing_qs.values_list("geoname_id", flat=True))
        seen_ids: Set[int] = set()

        created = 0
        updated = 0
        skipped = 0
        skipped_country = 0
        skipped_pop = 0
        skipped_parse = 0

        for row in _read_rows(path):
            # himoya: ustun yetarliligi
            if len(row) < 19:
                skipped_parse += 1
                continue

            try:
                geoname_id = int(row[0])
                name = _str(row[1])
                asciiname = _str(row[2])
                lat = _float_or_none(row[4])
                lng = _float_or_none(row[5])
                iso2 = _str(row[8]).upper()
                admin1 = _str(row[10])
                admin2 = _str(row[11])
                population = _int_or_zero(row[14])
                tz = _str(row[17])
            except Exception:
                skipped_parse += 1
                continue

            if iso_filter and iso2 not in iso_filter:
                skipped += 1
                continue

            if population < min_pop:
                skipped_pop += 1
                continue

            country = countries.get(iso2)
            if not country:
                skipped_country += 1
                continue

            defaults = {
                "name": name,
                "ascii_name": asciiname,
                "country": country,
                "admin1": admin1,
                "admin2": admin2,
                "tz": tz,
                "population": population,
                "lat": lat,
                "lng": lng,
            }
            if opts.get("reactivate"):
                defaults["is_active"] = True
                defaults["is_deleted"] = False

            obj, is_created = City.objects.update_or_create(
                geoname_id=geoname_id,
                defaults=defaults
            )
            seen_ids.add(geoname_id)

            if is_created:
                created += 1
            else:
                updated += 1

        if opts.get("deactivate_missing"):
            missing_ids = existing_ids - seen_ids
            if missing_ids:
                City.objects.filter(geoname_id__in=missing_ids).update(is_active=False)
                self.stdout.write(self.style.WARNING(f"Deactivated missing cities: {len(missing_ids)}"))

        self.stdout.write(self.style.SUCCESS(
            "Done. created=%d, updated=%d, skipped=%d, skipped_country=%d, skipped_pop=%d, skipped_parse=%d"
            % (created, updated, skipped, skipped_country, skipped_pop, skipped_parse)
        ))
