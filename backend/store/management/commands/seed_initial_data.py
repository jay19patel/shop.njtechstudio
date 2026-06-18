from decimal import Decimal
from django.core.management.base import BaseCommand
from typing import Any
from store.models import Category, Product, ProductImage, Testimonial


CATEGORIES = [
    {
        "name": "Pants",
        "slug": "pants",
        "description": "Stylish and comfortable pants, jeans, trousers, and cargos.",
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "T-Shirts",
        "slug": "t-shirts",
        "description": "Cotton t-shirts, polo tees, and casual wear for everyday style.",
        "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Grocery",
        "slug": "grocery",
        "description": "Essential groceries, organic foods, oils, grains, and pantry items.",
        "image_url": "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "TV",
        "slug": "tv",
        "description": "High-definition televisions, smart OLED displays, and home cinema screens.",
        "image_url": "https://images.unsplash.com/photo-1593305841991-05c297ba4575?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Fan",
        "slug": "fan",
        "description": "High-speed ceiling fans, stand fans, and home cooling appliances.",
        "image_url": "https://images.unsplash.com/photo-1618943714243-23a54b38d380?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Mobile",
        "slug": "mobile",
        "description": "Next-generation 5G smartphones, mobile devices, and android phones.",
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "General",
        "slug": "general",
        "description": "General household items, decor, coffee mugs, and everyday lifestyle accessories.",
        "image_url": "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1200&q=80",
    },
]


PRODUCTS = [
    # ── Pants ──────────────────────────────────────────────────
    {
        "category": "pants",
        "name": "Slim Fit Blue Denim Jeans",
        "slug": "slim-fit-blue-jeans",
        "description": "Premium stretch denim jeans in classic blue, slim fit with 5 pockets. Soft, durable, and perfect for casual wear.",
        "base_price": "1999.00",
        "discount_percentage": "10.00",
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 40,
    },
    {
        "category": "pants",
        "name": "Olive Green Cargo Pants",
        "slug": "olive-green-cargo-pants",
        "description": "Durable cotton cargo pants with multiple utility pockets, perfect for outdoor adventures and utility style.",
        "base_price": "2499.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1517423568366-8b83523034fd?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 25,
    },
    {
        "category": "pants",
        "name": "Khaki Chino Trousers",
        "slug": "khaki-chino-trousers",
        "description": "Formal/casual hybrid khaki chino pants made from a breathable cotton blend. Smart fit, suitable for office or evenings out.",
        "base_price": "2199.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1479064555552-3ef4979f8908?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 30,
    },

    # ── T-Shirts ─────────────────────────────────────────────────────
    {
        "category": "t-shirts",
        "name": "Classic White Cotton T-Shirt",
        "slug": "classic-white-cotton-tshirt",
        "description": "Ultra-soft 100% organic cotton white t-shirt, crew neck, regular fit. An essential wardrobe staple.",
        "base_price": "799.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 80,
    },
    {
        "category": "t-shirts",
        "name": "Navy Blue Polo T-Shirt",
        "slug": "navy-blue-polo-tshirt",
        "description": "Premium knitted polo shirt in deep navy blue, featuring a ribbed collar and short sleeves. Comfort meets preppy style.",
        "base_price": "1299.00",
        "discount_percentage": "8.00",
        "image_url": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 50,
    },
    {
        "category": "t-shirts",
        "name": "Black Graphic Streetwear Tee",
        "slug": "black-graphic-streetwear-tee",
        "description": "Loose fit heavy-cotton black t-shirt with a modern graphic design on the back. Bold streetwear fashion statement.",
        "base_price": "1499.00",
        "discount_percentage": "10.00",
        "image_url": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 45,
    },

    # ── Grocery ──────────────────────────────────────────────────
    {
        "category": "grocery",
        "name": "Organic Extra Virgin Olive Oil 1L",
        "slug": "organic-extra-virgin-olive-oil",
        "description": "Cold-pressed extra virgin olive oil, rich in antioxidants and healthy fats. Ideal for Mediterranean cooking and salads.",
        "base_price": "1499.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 40,
    },
    {
        "category": "grocery",
        "name": "Premium Basmati Rice 5kg",
        "slug": "premium-basmati-rice-5kg",
        "description": "Long-grain aromatic basmati rice, aged to perfection. Offers a fluffy texture and delicious scent, ideal for biryanis.",
        "base_price": "999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 30,
    },
    {
        "category": "grocery",
        "name": "Pure Himalayan Pink Salt 1kg",
        "slug": "pure-himalayan-pink-salt",
        "description": "100% natural, mineral-rich pink salt sourced from pristine mountain mines. Fine grain, perfect for everyday seasoning.",
        "base_price": "299.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 60,
    },
    {
        "category": "grocery",
        "name": "Organic Raw Forest Honey 500g",
        "slug": "organic-raw-forest-honey",
        "description": "Pure, unfiltered honey sourced directly from wild forest beehives. Full of natural enzymes and a sweet, healthy choice.",
        "base_price": "499.00",
        "discount_percentage": "12.00",
        "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 35,
    },

    # ── TV ──────────────────────────────────────────────────
    {
        "category": "tv",
        "name": "55-inch Ultra HD 4K Smart TV",
        "slug": "55-inch-4k-smart-tv",
        "description": "55-inch LED 4K smart television featuring HDR10+, Dolby Audio, and built-in streaming apps like Netflix, Prime Video, and YouTube.",
        "base_price": "34999.00",
        "discount_percentage": "15.00",
        "image_url": "https://images.unsplash.com/photo-1593305841991-05c297ba4575?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 10,
    },
    {
        "category": "tv",
        "name": "65-inch OLED Premium Cinema TV",
        "slug": "65-inch-oled-premium-tv",
        "description": "Flagship 65-inch OLED television delivering deep blacks, infinite contrast, Dolby Vision, high refresh rate for gaming, and AI voice control.",
        "base_price": "89999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1593789198777-f29bc259780e?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 5,
    },

    # ── Fan ──────────────────────────────────────────────────
    {
        "category": "fan",
        "name": "High-Speed Ceiling Fan",
        "slug": "high-speed-ceiling-fan",
        "description": "3-blade decorative ceiling fan with a high-torque copper motor and rust-resistant aluminum body. Delivers high air delivery silently.",
        "base_price": "2499.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1618943714243-23a54b38d380?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 25,
    },
    {
        "category": "fan",
        "name": "Portable Pedestal Stand Fan",
        "slug": "portable-pedestal-fan",
        "description": "Adjustable height pedestal fan with silent operation, 3 speed settings, and wide-angle oscillation for cooling large rooms.",
        "base_price": "3499.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1618943714243-23a54b38d380?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 20,
    },

    # ── Mobile ──────────────────────────────────────────────────
    {
        "category": "mobile",
        "name": "Pro 5G Flagship Smartphone",
        "slug": "pro-5g-flagship-smartphone",
        "description": "Next-gen 5G mobile phone featuring a 120Hz AMOLED display, pro-grade 108MP triple camera, 8GB RAM, and 128GB high-speed storage.",
        "base_price": "29999.00",
        "discount_percentage": "10.00",
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 15,
    },
    {
        "category": "mobile",
        "name": "Budget Friendly Android Phone",
        "slug": "budget-android-phone",
        "description": "Affordable 4G Android phone with a long-lasting 5000mAh battery, 4GB RAM, and dual camera system. Perfect backup device.",
        "base_price": "8999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 30,
    },

    # ── General ──────────────────────────────────────────────────
    {
        "category": "general",
        "name": "Stainless Steel Vacuum Water Bottle",
        "slug": "stainless-steel-vacuum-bottle",
        "description": "Double-walled insulated flask keeping drinks hot or cold for 24 hours. Leak-proof design made of food-grade steel.",
        "base_price": "999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 40,
    },
    {
        "category": "general",
        "name": "Minimalist Ceramic Matte Mug",
        "slug": "ceramic-matte-coffee-mug",
        "description": "Elegant ceramic coffee cup with a comfortable handle and a premium matte black finish. Dishwasher and microwave safe.",
        "base_price": "499.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 100,
    },
]


TESTIMONIALS = [
    {
        "name": "Arjun Kapoor",
        "role": "Casual Shopper",
        "content": "Bought the cargo pants and cotton t-shirts. The fit was perfect, the material is extremely soft and breathable. Highly recommend!",
        "rating": 5,
        "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
    },
    {
        "name": "Sneha Iyer",
        "role": "Home Cook",
        "content": "The organic olive oil and pink salt are premium quality. Cooking salads with this cold-pressed oil is wonderful. Fast shipping!",
        "rating": 5,
        "image_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=400&q=80",
    },
    {
        "name": "Vikram Nair",
        "role": "Tech Enthusiast",
        "content": "The 55-inch 4K Smart TV display is stunning, bright, and the smart features work flawlessly. Mobile screen casting is very smooth.",
        "rating": 5,
        "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=400&q=80",
    },
]


class Command(BaseCommand):
    """Seed command to clean database and insert general products and categories."""

    help = "Clear existing products/categories and seed general catalog (7 categories, 18 products)."

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the seed command."""
        self.stdout.write("Clearing existing products and categories...")

        # Clear all active and stale tables with foreign keys via PostgreSQL CASCADE truncate
        from django.db import connection
        with connection.cursor() as cursor:
            try:
                cursor.execute("TRUNCATE TABLE store_product CASCADE;")
                self.stdout.write("  Truncated store_product and all referencing tables via CASCADE.")
            except Exception as e:
                self.stdout.write(f"  Warning during product truncate: {str(e)}")
            try:
                cursor.execute("TRUNCATE TABLE store_category CASCADE;")
                self.stdout.write("  Truncated store_category and all referencing tables via CASCADE.")
            except Exception as e:
                self.stdout.write(f"  Warning during category truncate: {str(e)}")

        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.WARNING("  Old data cleared."))

        self.stdout.write("Seeding categories...")
        categories = {}
        for item in CATEGORIES:
            category, _ = Category.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item["name"],
                    "description": item["description"],
                    "image_url": item["image_url"],
                },
            )
            categories[item["slug"]] = category
        self.stdout.write(self.style.SUCCESS(f"  {len(CATEGORIES)} categories seeded."))

        self.stdout.write("Seeding products...")
        for item in PRODUCTS:
            product, _ = Product.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "category": categories[item["category"]],
                    "name": item["name"],
                    "description": item["description"],
                    "base_price": Decimal(item["base_price"]),
                    "discount_percentage": Decimal(item.get("discount_percentage", "0.00")),
                    "available_quantity": item.get("available_quantity", 0),
                    "is_active": True,
                },
            )
            ProductImage.objects.update_or_create(
                product=product,
                is_primary=True,
                defaults={"image_url": item["image_url"]},
            )
        self.stdout.write(self.style.SUCCESS(f"  {len(PRODUCTS)} products seeded."))

        self.stdout.write("Seeding testimonials...")
        for item in TESTIMONIALS:
            Testimonial.objects.update_or_create(
                name=item["name"],
                defaults={
                    "role": item["role"],
                    "content": item["content"],
                    "rating": item["rating"],
                    "image_url": item["image_url"],
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"  {len(TESTIMONIALS)} testimonials seeded."))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone: {len(CATEGORIES)} categories, {len(PRODUCTS)} products, "
                f"{len(TESTIMONIALS)} testimonials."
            )
        )
