# locations/management/commands/import_countries.py
import csv
from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from locations.models import Country

# GeoNames countryInfo.txt / countries.txt (TSV) ustunlari:
# ISO, ISO3, ISO-Numeric, fips, Country, Capital, Area(in sq km), Population,
# Continent, tld, CurrencyCode, CurrencyName, Phone, Postal Code Format,
# Postal Code Regex, Languages, geonameid, neighbours, EquivalentFipsCode

CONTINENT_MAP = {
    "AF": "Africa",
    "AS": "Asia",
    "EU": "Europe",
    "NA": "North America",
    "OC": "Oceania",
    "SA": "South America",
    "AN": "Antarctica",
}

def _int_or_none(val: str) -> Optional[int]:
    val = (val or "").strip()
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None

def _str_or_empty(val: str) -> str:
    return (val or "").strip()

class Command(BaseCommand):
    help = "Import countries from GeoNames countryInfo.txt (countries.txt, TSV with comments)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--file", required=True,
            help="Path to GeoNames countryInfo.txt (or countries.txt)."
        )
        # MUHIM: argparse dest nomlari '_' bilan bo'ladi
        parser.add_argument(
            "--deactivate-missing", dest="deactivate_missing", action="store_true",
            help="Countries not present in the file will be set is_active=False."
        )
        parser.add_argument(
            "--reactivate", dest="reactivate", action="store_true",
            help="Set is_active=True for all countries that are (re)imported."
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        path = Path(opts["file"])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {path}"))
            return

        self.stdout.write(f"Reading: {path}")

        existing_iso2 = set(Country.objects.values_list("iso2", flat=True))
        seen_iso2 = set()

        created = 0
        updated = 0
        skipped = 0

        # Windows/UTF-8 BOM himoyasi uchun encoding='utf-8' yetarli bo'lmasa, 'utf-8-sig' ni sinab ko'ring
        with path.open(encoding="utf-8") as f:
            # '#' bilan boshlanadigan kommentlarni tashlaymiz
            filtered = (line for line in f if line.strip() and not line.startswith("#"))
            reader = csv.reader(filtered, delimiter="\t")

            for row in reader:
                # Bo'sh yoki to'liq bo'lmagan satrlarni tashlab yuboramiz
                if not row or len(row) < 17:
                    skipped += 1
                    continue

                iso2          = _str_or_empty(row[0]).upper()   # ISO
                iso3          = _str_or_empty(row[1]).upper()   # ISO3
                iso_numeric   = _str_or_empty(row[2])           # ISO-Numeric
                country_name  = _str_or_empty(row[4])           # Country
                capital       = _str_or_empty(row[5])           # Capital
                continent     = _str_or_empty(row[8])           # Continent code (EU/AS/...)
                currency_code = _str_or_empty(row[10])          # CurrencyCode
                phone_code    = _str_or_empty(row[12])          # Phone (dial)
                languages     = _str_or_empty(row[15]) if len(row) > 15 else ""  # Languages
                geoname_id    = _str_or_empty(row[16]) if len(row) > 16 else ""  # geonameid

                if not iso2 or not country_name:
                    skipped += 1
                    continue

                numeric_int = _int_or_none(iso_numeric)
                # UN M49 ko‘pincha ISO numeric bilan mos keladi
                m49_int = numeric_int

                region_name = CONTINENT_MAP.get(continent, "")
                subregion_name = ""  # GeoNames'da subregion yo'q — keyin UN M49 bilan boyitish mumkin

                defaults = {
                    "name": country_name,
                    "iso3": iso3 or None,
                    "numeric": numeric_int,
                    "m49": m49_int,
                    "phone_code": phone_code,
                    "region": region_name,
                    "subregion": subregion_name,
                    "currency": currency_code,
                    "capital": capital,
                    # countryInfo.txt da lat/lng yo'q
                    "lat": None,
                    "lng": None,
                }

                if opts.get("reactivate"):
                    defaults["is_active"] = True

                obj, is_created = Country.objects.update_or_create(
                    iso2=iso2,
                    defaults=defaults
                )
                seen_iso2.add(iso2)
                created += 1 if is_created else 0
                updated += 0 if is_created else 1

        if opts.get("deactivate_missing"):
            missing = existing_iso2 - seen_iso2
            if missing:
                Country.objects.filter(iso2__in=missing).update(is_active=False)
                self.stdout.write(self.style.WARNING(f"Deactivated missing: {len(missing)}"))

        self.stdout.write(self.style.SUCCESS(
            f"Done. created={created}, updated={updated}, skipped={skipped}"
        ))
