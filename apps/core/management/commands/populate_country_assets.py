import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Q
from django.db.transaction import atomic, on_commit

from utils.helpers import extract_json_data_from_file, logger

from apps.core.models import CountryAsset

class Command(BaseCommand):

    def populate_country_data(self):
        asset_data = extract_json_data_from_file(
            os.path.join(settings.BASE_DIR, "country_assets.json")
        )
        logger.debug(f"asset data to be populated::::: {asset_data}")
        db_assets = []
        if asset_data:
            for asset in asset_data:
                data = {
                    "name": asset.get("name"),
                    "country": asset.get("country"),
                    "country_code": asset.get("country_code"),
                    "currency": asset.get("country_currency")
                }
                db_asset = CountryAsset.objects.filter(
                    Q(name__icontains=asset.get("name")) |
                    Q(country__icontains=asset.get("country")),
                    name__isnull=False, country__isnull=False
                ).first()
                if db_asset:
                    db_asset.update_self(data)
                else:
                    db_asset = CountryAsset(**data)
                    db_assets.append(db_asset)
        if db_assets:
            CountryAsset.objects.bulk_create(db_assets)

    def handle(self, *args, **kwargs):
        with atomic():
            self.populate_country_data()
        on_commit(
            lambda: logger.debug("assets populated!!")
        )
