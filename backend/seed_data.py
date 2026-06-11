import os
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

from store.models import Category, Product, ProductImage, FAQ, Testimonial

def seed_data():
    print("Clearing existing catalog data...")
    ProductImage.objects.all().delete()

    Product.objects.all().delete()
    Category.objects.all().delete()
    FAQ.objects.all().delete()
    Testimonial.objects.all().delete()

    print("Creating Categories...")
    # Category 1: T-Shirts
    cat_tshirts = Category.objects.create(
        name="T-Shirts",
        slug="t-shirts",
        description="Premium casual t-shirts for everyday wear.",
        image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=800&q=80"
    )

    # Category 2: Shirts
    cat_shirts = Category.objects.create(
        name="Shirts",
        slug="shirts",
        description="Elegant and comfortable shirts for all occasions.",
        image_url="https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80"
    )

    # Category 3: Jackets
    cat_jackets = Category.objects.create(
        name="Jackets",
        slug="jackets",
        description="Stylish jackets to keep you warm and looking sharp.",
        image_url="https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=800&q=80"
    )

    print("Creating Products...")
    
    # --- Product 1 ---
    prod1 = Product.objects.create(
        category=cat_tshirts,
        name="Classic White Crew Neck T-Shirt",
        slug="classic-white-crew-neck",
        description="A timeless classic white t-shirt made with 100% organic cotton for ultimate comfort.",
        base_price=Decimal("499.00"),
        is_active=True
    )
    ProductImage.objects.create(
        product=prod1,
        image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=800&q=80",
        is_primary=True
    )


    # --- Product 2 ---
    prod2 = Product.objects.create(
        category=cat_tshirts,
        name="Graphic Oversized T-Shirt",
        slug="graphic-oversized-tshirt",
        description="Oversized fit graphic tee with a modern cyberpunk aesthetic. Perfect for streetwear lovers.",
        base_price=Decimal("799.00"),
        is_active=True
    )
    ProductImage.objects.create(
        product=prod2,
        image_url="https://images.unsplash.com/photo-1503342394128-c104d54dba01?auto=format&fit=crop&w=800&q=80",
        is_primary=True
    )


    # --- Product 3 ---
    prod3 = Product.objects.create(
        category=cat_shirts,
        name="Slim Fit Oxford Shirt",
        slug="slim-fit-oxford-shirt",
        description="Classic oxford shirt in light blue. Tailored slim fit for a sharp, professional look.",
        base_price=Decimal("1299.00"),
        is_active=True
    )
    ProductImage.objects.create(
        product=prod3,
        image_url="https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80",
        is_primary=True
    )


    # --- Product 4 ---
    prod4 = Product.objects.create(
        category=cat_shirts,
        name="Casual Flannel Shirt",
        slug="casual-flannel-shirt",
        description="Soft, cozy flannel shirt in a red and black check pattern.",
        base_price=Decimal("999.00"),
        is_active=True
    )
    ProductImage.objects.create(
        product=prod4,
        image_url="https://images.unsplash.com/photo-1589902860314-e910cb96d32f?auto=format&fit=crop&w=800&q=80",
        is_primary=True
    )


    # --- Product 5 ---
    prod5 = Product.objects.create(
        category=cat_jackets,
        name="Classic Denim Jacket",
        slug="classic-denim-jacket",
        description="Vintage wash denim jacket with silver hardware. A must-have staple for your wardrobe.",
        base_price=Decimal("2499.00"),
        is_active=True
    )
    ProductImage.objects.create(
        product=prod5,
        image_url="https://images.unsplash.com/photo-1576871337622-98d48d1cf531?auto=format&fit=crop&w=800&q=80",
        is_primary=True
    )


    # --- Product 6 ---
    prod6 = Product.objects.create(
        category=cat_jackets,
        name="Faux Leather Biker Jacket",
        slug="faux-leather-biker-jacket",
        description="Edgy biker jacket made from premium vegan leather.",
        base_price=Decimal("3499.00"),
        is_active=True
    )
    ProductImage.objects.create(
        product=prod6,
        image_url="https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=800&q=80",
        is_primary=True
    )


    print("Creating FAQs...")
    FAQ.objects.create(
        question="How long does shipping take?",
        answer="We process all orders within 24 hours. Standard shipping typically takes 3-5 business days depending on your location.",
        order=1
    )
    FAQ.objects.create(
        question="What is your return policy?",
        answer="We offer a 15-day return policy for all unworn and unwashed items with tags attached. Please contact our support team to initiate a return.",
        order=2
    )
    FAQ.objects.create(
        question="Do you ship internationally?",
        answer="Currently, we only ship within India. We are working hard to bring our products to international customers soon!",
        order=3
    )

    print("Creating Testimonials...")
    Testimonial.objects.create(
        name="Rahul Verma",
        role="Verified Buyer",
        content="The fit of the classic white t-shirt is just perfect. Will definitely buy more!",
        rating=5,
        image_url="https://i.pravatar.cc/150?u=rahul"
    )
    Testimonial.objects.create(
        name="Priya Sharma",
        role="Verified Buyer",
        content="Absolutely in love with the denim jacket. The quality is top-notch and it looks amazing.",
        rating=5,
        image_url="https://i.pravatar.cc/150?u=priya"
    )
    Testimonial.objects.create(
        name="Aman Gupta",
        role="Verified Buyer",
        content="Great collection of shirts. The flannel one is extremely comfortable for daily wear.",
        rating=4,
        image_url="https://i.pravatar.cc/150?u=aman"
    )

    print("Successfully seeded catalog data with clothing, FAQs, and Testimonials!")

if __name__ == '__main__':
    seed_data()
