import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
import django
django.setup()

from shop.models import Category, Product
from django.core.management.base import BaseCommand
from django.utils.text import slugify 
from shop.models import Category, Product

class Command(BaseCommand):
    help = 'Popola il database con prodotti e categorie'

    def handle(self, *args, **options):
        create_categories()
        create_products() 
        self.stdout.write(self.style.SUCCESS('Database popolato con successo!'))

def create_categories():
    Category.objects.get_or_create(
        name="Crumbl",
        defaults={
            'slug': 'crumbl',
            'description': 'Biscotti artigianali soffici e golosi'
        }
    )
    Category.objects.get_or_create(
        name="Muffin",
        defaults={
            'slug': 'muffin',
            'description': 'Muffin soffici e fragranti'
        }
    )
    Category.objects.get_or_create(
        name="Donuts",
        defaults={
            'slug': 'donuts',
            'description': 'Ciambelle glassate e creative'
        }
    )

def create_products():
    crumbl = Category.objects.get(name="Crumbl")
    muffin = Category.objects.get(name="Muffin")
    donuts = Category.objects.get(name="Donuts")

    crumbl_products = [
        {
            'name': "Chocolate Crumbl",
            'description': "Biscotto doppio cioccolato con gocce fondenti.",
            'price': 4.50,
            'image': "chocolate_crumbl_twsuf7",
            'ingredients': "Farina, burro, cioccolato fondente, zucchero, uova",
            'allergens': "Glutine, latte, uova"
        },
        {
            'name': "Baby Crumbl",
            'description': "Biscotto vaniglia in formato mini.",
            'price': 2.80,
            'image': "baby_crumbl_ieplq7",
            'ingredients': "Farina, burro, zucchero, uova, vaniglia",
            'allergens': "Glutine, latte, uova"
        },
        {
            'name': "Biscuits Crumbl",
            'description': "Biscotto friabile al burro con note di vaniglia.",
            'price': 3.50,
            'image': "biscuits_crumbl_tzj6ye",
            'ingredients': "Farina, burro, zucchero, sale marino",
            'allergens': "Glutine, latte"
        },
        {
            'name': "Caramell Crumbl",
            'description': "Biscotto al caramello con glassa salata.",
            'price': 4.50,
            'image': "caramell_crumbl_d3d8ml",
            'ingredients': "Farina, caramello, burro, zucchero",
            'allergens': "Glutine, latte"
        },
        {
            'name': "Confetti Crumbl",
            'description': "Base vaniglia con confetti colorati e glassa.",
            'price': 3.00,
            'image': "confetti_crumbl_uaxzic",
            'ingredients': "Farina, zucchero, coloranti alimentari",
            'allergens': "Glutine, coloranti"
        },
        {
            'name': "Lemon Crumbl",
            'description': "Biscotto al limone con glassa agrumata.",
            'price': 4.20,
            'image': "lemon_crumbl_fwbsjj",
            'ingredients': "Farina, limone, zucchero, burro",
            'allergens': "Glutine"
        },
        {
            'name': "Oreo Crumbl",
            'description': "Biscotto cacao con pezzi di Oreo e crema vaniglia.",
            'price': 4.00,
            'image': "oreo_crumbl_gphpw9",
            'ingredients': "Farina, biscotti Oreo, cacao, zucchero",
            'allergens': "Glutine, latte"
        },
        {
            'name': "Pink Crumbl",
            'description': "Biscotto rosa alla fragola con topping perlato.",
            'price': 3.20,
            'image': "pink_crumbl_flyhcn",
            'ingredients': "Farina, fragola, colorante rosa, zucchero",
            'allergens': "Glutine, coloranti"
        },
        {
            'name': "Red Velvet Crumbl",
            'description': "Biscotto red velvet con cuore al cream cheese.",
            'price': 4.50,
            'image': "Red_Velvet_crumbl_bqqwnd",
            'ingredients': "Farina, cacao, colorante rosso, cream cheese",
            'allergens': "Glutine, latte"
        },
        {
            'name': "Soft Crumbl",
            'description': "Biscotto al latte con consistenza nuvola.",
            'price': 3.20,
            'image': "soft_crumbl_xylyhm",
            'ingredients': "Farina, latte, zucchero, burro",
            'allergens': "Glutine, latte"
        },
        {
            'name': "Strawberries Crumbl",
            'description': "Biscotto alla fragola con pezzi di frutta.",
            'price': 4.20,
            'image': "strawberries_crumbl_pk6qqj",
            'ingredients': "Farina, fragole fresche, zucchero",
            'allergens': "Glutine"
        },
        {
            'name': "The Lotus Crumbl",
            'description': "Biscotto al burro con crema Lotus Biscoff.",
            'price': 4.20,
            'image': "the_lotus_crumbl_yhl2t5",
            'ingredients': "Farina, crema Lotus, burro, zucchero",
            'allergens': "Glutine, latte"
        }
    ]

    muffin_products = [
        {
            'name': "Cappuccino Muffin",
            'description': "Muffin al cappuccino con aroma intenso di caffè.",
            'price': 5.00,
            'image': "cappuccino_muffin_hcatxv",
            'ingredients': "Farina, caffè, latte, zucchero",
            'allergens': "Glutine, latte"
        },
        {
            'name': "Cherry Muffin",
            'description': "Muffin con ciliegie succose e glassa leggera.",
            'price': 4.60,
            'image': "cherry_muffin_ufvmit",
            'ingredients': "Farina, ciliegie, zucchero, burro",
            'allergens': "Glutine"
        },
        {
            'name': "Chocolate Muffin",
            'description': "Muffin al cioccolato con gocce fondenti.",
            'price': 4.50,
            'image': "chocolate_muffin_bd9sad",
            'ingredients': "Farina, cioccolato, uova, zucchero",
            'allergens': "Glutine, uova"
        },
        {
            'name': "Classic Muffin",
            'description': "Muffin semplice alla vaniglia con glassa liscia.",
            'price': 4.00,
            'image': "classic_muffin_ubrkox",
            'ingredients': "Farina, vaniglia, zucchero, burro",
            'allergens': "Glutine"
        },
        {
            'name': "Flower Muffin",
            'description': "Muffin decorato con motivi floreali in glassa.",
            'price': 4.80,
            'image': "flower_muffin_kxxbxs",
            'ingredients': "Farina, coloranti alimentari, zucchero",
            'allergens': "Glutine, coloranti"
        },
        {
            'name': "Matcha Muffin",
            'description': "Muffin al tè matcha con gusto erbaceo.",
            'price': 4.80,
            'image': "macha_muffin_pbrxmm",
            'ingredients': "Farina, tè matcha, zucchero, burro",
            'allergens': "Glutine"
        },
        {
            'name': "Marshmallow Muffin",
            'description': "Muffin farcito con marshmallow filante.",
            'price': 4.70,
            'image': "marshmallow_muffin_xqcxud",
            'ingredients': "Farina, marshmallow, zucchero",
            'allergens': "Glutine, gelatina"
        },
        {
            'name': "Rainbow Muffin",
            'description': "Muffin colorato con gocce di cioccolato arcobaleno.",
            'price': 4.00,
            'image': "rainbow_muffin_t7sguh",
            'ingredients': "Farina, coloranti alimentari, cioccolato",
            'allergens': "Glutine, coloranti"
        },
        {
            'name': "Red Velvet Muffin",
            'description': "Muffin red velvet con glassa al formaggio.",
            'price': 5.00,
            'image': "redvelvet_muffin_cbmzru",
            'ingredients': "Farina, cacao, colorante rosso, cream cheese",
            'allergens': "Glutine, latte"
        },
        {
            'name': "Raspberry Muffin",
            'description': "Muffin ai lamponi con glassa ai frutti di bosco.",
            'price': 4.60,
            'image': "ruspberry_muffin_byeqeh",
            'ingredients': "Farina, lamponi, zucchero",
            'allergens': "Glutine"
        },
        {
            'name': "Strawberry Muffin",
            'description': "Muffin alle fragole con pezzi di frutta fresca.",
            'price': 4.70,
            'image': "strawberry_muffin_cba03l",
            'ingredients': "Farina, fragole, zucchero, burro",
            'allergens': "Glutine"
        }
    ]

    donuts_products = [
        {
            'name': "Blue Coriandoli Donut",
            'description': "Donut glassato di blu con coriandoli colorati.",
            'price': 4.50,
            'image': "blue_coriandoli_donut_qykgxo",
            'ingredients': "Farina, colorante blu, coriandoli, glassa",
            'allergens': "Glutine, coloranti"
        },
        {
            'name': "Cereal Donut",
            'description': "Donut ricoperto di cereali croccanti.",
            'price': 4.50,
            'image': "cereal_donut_fx82pj",
            'ingredients': "Farina, cereali, zucchero, latte",
            'allergens': "Glutine, latte"
        },
        {
            'name': "Chocolate Sparkles Donut",
            'description': "Donut alla vaniglia con glassa al cioccolato.",
            'price': 4.50,
            'image': "chocolate_sprinkles_donut_zhwmn3",
            'ingredients': "Farina, cioccolato, zucchero, granella",
            'allergens': "Glutine"
        },
        {
            'name': "Classic Donut",
            'description': "Donut tradizionale con glassa liscia e lucida.",
            'price': 4.00,
            'image': "classic_donut_oetta4",
            'ingredients': "Farina, zucchero, vaniglia, glassa",
            'allergens': "Glutine"
        },
        {
            'name': "Dark Chocolate Donut",
            'description': "Donut con glassa al cioccolato fondente.",
            'price': 4.50,
            'image': "dark_chocolate_donut_rfx41c",
            'ingredients': "Farina, cioccolato fondente, zucchero",
            'allergens': "Glutine"
        },
        {
            'name': "M&M's Donut",
            'description': "Donut glassato ricoperto di M&M's colorati.",
            'price': 4.50,
            'image': "MM_donut_uh3mg0",
            'ingredients': "Farina, M&M's, zucchero, coloranti",
            'allergens': "Glutine, coloranti"
        },
        {
            'name': "Oreo Donut",
            'description': "Donut farcito o glassato con crema Oreo.",
            'price': 4.50,
            'image': "oreo_donut_tpls6t",
            'ingredients': "Farina, biscotti Oreo, crema, zucchero",
            'allergens': "Glutine, latte"
        },
        {
            'name': "Pink Coriandoli Donut",
            'description': "Donut glassato rosa con coriandoli variopinti.",
            'price': 4.30,
            'image': "pink_coriandoli_donut_a7zjkc",
            'ingredients': "Farina, colorante rosa, coriandoli, glassa",
            'allergens': "Glutine, coloranti"
        },
        {
            'name': "Pistacchio Donut",
            'description': "Donut con glassa al pistacchio e granella.",
            'price': 4.70,
            'image': "pistacchio_dunut_xrv0gi",
            'ingredients': "Farina, pistacchio, zucchero, latte",
            'allergens': "Glutine, latte, frutta a guscio"
        },
        {
            'name': "Red Velvet Donut",
            'description': "Donut red velvet con glassa al formaggio.",
            'price': 4.80,
            'image': "red_velvet_donut_zrd20b",
            'ingredients': "Farina, cacao, colorante rosso, cream cheese",
            'allergens': "Glutine, latte"
        },
        {
            'name': "Strawberry Donut",
            'description': "Donut glassato alla fragola con zuccherini.",
            'price': 4.80,
            'image': "strawberry_donut_nnozwv",
            'ingredients': "Farina, fragola, zucchero, colorante rosso",
            'allergens': "Glutine, coloranti"
        },
        {
            'name': "White Coriandoli Donut",
            'description': "Donut glassato bianco con coriandoli colorati.",
            'price': 4.30,
            'image': "white_coriandoli_donut_awejgs",
            'ingredients': "Farina, glassa bianca, coriandoli, zucchero",
            'allergens': "Glutine"
        }
    ]

    for product_data in crumbl_products:
        Product.objects.get_or_create(
            name=product_data['name'],
            defaults={
                'description': product_data['description'],
                'price': product_data['price'],
                'category': crumbl,
                'image': product_data['image'],
                'ingredients': product_data['ingredients'],
                'allergens': product_data['allergens']
            }
        )

    for product_data in muffin_products:
        Product.objects.get_or_create(
            name=product_data['name'],
            defaults={
                'description': product_data['description'],
                'price': product_data['price'],
                'category': muffin,
                'image': product_data['image'],
                'ingredients': product_data['ingredients'],
                'allergens': product_data['allergens']
            }
        )

    for product_data in donuts_products:
        Product.objects.get_or_create(
            name=product_data['name'],
            defaults={
                'description': product_data['description'],
                'price': product_data['price'],
                'category': donuts,
                'image': product_data['image'],
                'ingredients': product_data['ingredients'],
                'allergens': product_data['allergens']
            }
        )

if __name__ == '__main__':
    create_categories()
    create_products()
    print("Database popolato con successo! 35 prodotti creati.")