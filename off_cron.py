from django_cron import CronJobBase, Schedule
from .models import Product
import requests
import time

class OffCronJob(CronJobBase):
    RUN_EVERY_MINS = 60 * 24 * 7  # every week

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'home.offcron'

    def do(self):
        products = Product.objects.all()
        if not products:
            return

        url = "https://fr.openfoodfacts.org/api/v0/product/{}.json"
        for product in products:
            data = requests.get(url.format(product.id_off)).json()
            # Product not found
            if not data['status']: 
                product.delete()
                continue

            data = data['product']
            # If product no more supported by OFF
            if not all(k in data for k in ("product_name", "brands", "id", "nutrition_grade_fr", "categories_prev_tags")):
                product.delete()
                continue
            if not all(k in data['nutriments'] for k in ("fat_100g", "saturated-fat_100g", "sugars_100g", "salt_100g")):
                product.delete()
                continue

            if product.name != data['product_name']:
                product.name = data['product_name']
            if product.brands != data['brands']:
                product.brands = data['brands']
            if product.nutrition_grade != data['nutrition_grade_fr']:
                product.nutrition_grade = data['nutrition_grade_fr']
            if product.satured_fat != float(data['nutriments']['saturated-fat_100g']):
                product.satured_fat = float(data['nutriments']['saturated-fat_100g'])
            if product.fat != float(data['nutriments']['fat_100g']):
                product.fat = float(data['nutriments']['fat_100g'])
            if product.sugar != float(data['nutriments']['sugars_100g']):
                product.sugar = float(data['nutriments']['sugars_100g'])
            if product.salt != float(data['nutriments']['salt_100g']):
                product.salt = float(data['nutriments']['salt_100g'])
            if product.img_url != data['image_front_url']:
                product.img_url = data['image_front_url']
            if product.categorie != max(data['categories_prev_tags'], key=len):
                product.categorie = max(data['categories_prev_tags'], key=len)
            product.save()
            time.sleep(.5)