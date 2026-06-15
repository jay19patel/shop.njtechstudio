"""
simulate.py — Fake Customer Simulator (Faker edition)
══════════════════════════════════════════════════════
Uses the `faker` library with Indian locale for realistic names,
addresses, phone numbers, cities, and states.

Usage:
  python simulate.py                   # 100 customers
  python simulate.py --count 50
  python simulate.py --count 200
  python simulate.py --delay 0.15      # seconds between API calls

Requirements:
  pip install faker requests

Per customer (all via real API calls):
  1. Register  → POST /api/auth/register
  2. Login     → JWT token
  3. View 10-15 products  → GET  /api/products/{id}/         (PRODUCT_VIEWED)
  4. Like 2-5  products   → POST /api/likes/toggle-like/     (PRODUCT_LIKED)
  5. Cart 1-3  items      → POST /api/carts/{id}/add_item/   (CART_ITEM_ADDED)
  6. Checkout  (70%)      → POST /api/carts/{id}/checkout/   (ORDER_CREATED)
     └── full address: name, email, phone, city, state, pincode
"""

import argparse
import random
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from faker import Faker

# ─── Setup ────────────────────────────────────────────────────────────────────

API  = "http://127.0.0.1:8000/api"
fake = Faker("en_IN")          # Indian locale → realistic Indian data
Faker.seed(0)                  # reproducible names (remove for fully random)

DEVICES = ["desktop", "mobile", "tablet"]
UA = {
    "desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0",
    "mobile":  "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/118.0",
    "tablet":  "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
}


# ─── Customer ─────────────────────────────────────────────────────────────────

class Customer:
    """
    One fake customer. Generates realistic Indian data via Faker.
    All API calls go to the real Django server.
    """

    def __init__(self, index: int, delay: float):
        # ── Identity ─────────────────────────────────────────────────────────
        self.name    = fake.name()
        self.email   = f"sim.{uuid.uuid4().hex[:10]}@fakeshop.test"  # always unique
        self.pw      = "Sim@Pass#2024"
        self.phone   = fake.phone_number()[:15]     # Indian mobile number
        self.device  = random.choice(DEVICES)
        self.ip      = fake.ipv4_public()           # realistic public IP

        # ── Shipping address (full, realistic) ───────────────────────────────
        self.address = fake.street_address()
        self.city    = fake.city()
        self.state   = fake.state()
        self.pincode = fake.postcode()

        # ── Session state ─────────────────────────────────────────────────────
        self.delay   = delay
        self.token   = None
        self.cart_id = None
        self.stats   = dict(views=0, likes=0, cart_adds=0, orders=0, errors=0)

        # ── HTTP session ──────────────────────────────────────────────────────
        self.http = requests.Session()
        self.http.headers.update({
            "Content-Type":    "application/json",
            "X-Forwarded-For": self.ip,
            "User-Agent":      UA[self.device],
        })

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _get(self, path, params=None):
        try:
            r = self.http.get(f"{API}{path}", params=params, timeout=12)
            return r.json() if r.ok else {}
        except Exception:
            return {}

    def _post(self, path, body=None):
        try:
            r = self.http.post(f"{API}{path}", json=body or {}, timeout=12)
            return r.json() if r.ok else {}
        except Exception:
            return {}

    def _pause(self):
        """Realistic gap between actions — varies by ±50%."""
        time.sleep(self.delay * random.uniform(0.5, 1.5))

    # ── Phase 1: Authenticate (called sequentially to avoid email pile-up) ────

    def authenticate(self) -> bool:
        try:
            r = self.http.post(f"{API}/auth/register", json={
                "email":    self.email,
                "password": self.pw,
                "name":     self.name,
            }, timeout=30)   # generous — welcome email is sent here

            if r.status_code == 201:
                token = r.json().get("access") or r.json().get("token", "")
                if token:
                    self.http.headers["Authorization"] = f"Bearer {token}"
                    self.token = token
                    return True

            # Collision fallback (shouldn't happen with UUID email)
            if r.status_code == 400:
                lg = self.http.post(f"{API}/auth/login", json={
                    "email": self.email, "password": self.pw,
                }, timeout=12)
                if lg.ok:
                    token = lg.json().get("access") or lg.json().get("token", "")
                    if token:
                        self.http.headers["Authorization"] = f"Bearer {token}"
                        self.token = token
                        return True
        except Exception:
            pass
        return False

    # ── Phase 2: Shopping session (called in parallel) ────────────────────────

    def shop(self, all_products: list) -> dict:
        if not self.token or not all_products:
            self.stats["errors"] += 1
            return self.stats

        # Pick 2-3 categories this customer is interested in
        cats   = list({p["cat"] for p in all_products if p["cat"]})
        chosen = random.sample(cats, min(random.randint(2, 3), len(cats))) if cats else []
        pool   = [p for p in all_products if p["cat"] in chosen] or all_products

        random.shuffle(pool)
        lo, hi    = min(10, len(pool)), min(15, len(pool))
        my_prods  = pool[:random.randint(lo, hi)]

        # ── 1. View products ──────────────────────────────────────────────────
        # Each GET /products/{id}/ triggers a PRODUCT_VIEWED Kafka event
        for p in my_prods:
            self._get(f"/products/{p['id']}/")
            self._pause()
            self.stats["views"] += 1

        # ── 2. Like 2-5 products ──────────────────────────────────────────────
        like_count = random.randint(2, min(5, len(my_prods)))
        for p in random.sample(my_prods, like_count):
            self._post("/likes/toggle-like/", {"product_id": p["id"]})
            self._pause()
            self.stats["likes"] += 1

        # ── 3. Get or create cart ─────────────────────────────────────────────
        existing = self._get("/carts/")
        results  = existing.get("results", []) if isinstance(existing, dict) else []
        self.cart_id = results[0]["id"] if results else self._post("/carts/").get("id")

        # ── 4. Add 1-3 items to cart ──────────────────────────────────────────
        if self.cart_id:
            cart_count = random.randint(1, min(3, len(my_prods)))
            for p in random.sample(my_prods, cart_count):
                qty = random.randint(1, 2)
                res = self._post(f"/carts/{self.cart_id}/add_item/",
                                 {"product_id": p["id"], "quantity": qty})
                if not (res.get("id") or res.get("quantity")):
                    # Alternate URL pattern (some DRF configs use hyphen)
                    res = self._post(f"/carts/{self.cart_id}/add-item/",
                                     {"product_id": p["id"], "quantity": qty})
                if res.get("id") or res.get("quantity"):
                    self._pause()
                    self.stats["cart_adds"] += 1

        # ── 5. Checkout with full address details (70% of customers) ─────────
        # All fields now saved to Order model (backend fixed to read all fields)
        if self.stats["cart_adds"] > 0 and random.random() < 0.70:
            res = self._post(f"/carts/{self.cart_id}/checkout/", {
                # Required
                "shipping_address": self.address,
                # Customer identity (saved to Order.customer_*)
                "customer_name":  self.name,
                "customer_email": self.email,
                "customer_phone": self.phone,
                # Full address breakdown (saved to Order.city / .state / .pincode)
                "city":    self.city,
                "state":   self.state,
                "pincode": self.pincode,
            })
            if res.get("id"):
                self.stats["orders"] += 1

        return self.stats


# ─── Product loader ───────────────────────────────────────────────────────────

def load_products() -> list:
    print("  📦  Loading products from API…", end=" ", flush=True)
    try:
        r = requests.get(f"{API}/products/", params={"page_size": 100}, timeout=10)
        if not r.ok:
            print(f"FAILED ({r.status_code})")
            return []
        raw = r.json().get("results", [])
        products = []
        for p in raw:
            cat = p.get("category", {})
            cat_name = cat.get("name", "General") if isinstance(cat, dict) else "General"
            if p.get("available_quantity", 0) > 0:
                products.append({
                    "id":    p["id"],
                    "name":  p.get("name", ""),
                    "price": float(p.get("base_price", 0)),
                    "cat":   cat_name,
                })
        print(f"{len(products)} products ✓")
        return products
    except Exception as e:
        print(f"ERROR — {e}")
        return []


# ─── Progress bar ─────────────────────────────────────────────────────────────

def show_progress(done: int, total: int, t: dict):
    events = t["views"] + t["likes"] + t["cart_adds"] + t["orders"]
    filled = int(30 * done / max(total, 1))
    bar    = "█" * filled + "░" * (30 - filled)
    print(
        f"\r  [{bar}] {done:>4}/{total}"
        f"  events={events:<5}"
        f"  👁 {t['views']:<5}"
        f"  ❤ {t['likes']:<4}"
        f"  🛒 {t['cart_adds']:<4}"
        f"  📦 {t['orders']:<3}"
        f"  ❌ {t['errors']}",
        end="", flush=True,
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="NJShop fake customer simulator")
    parser.add_argument("--count",   type=int,   default=100,  help="Customers to simulate (default 100)")
    parser.add_argument("--delay",   type=float, default=0.15, help="Seconds between API calls (default 0.15)")
    parser.add_argument("--workers", type=int,   default=3,    help="Parallel workers for browsing (default 3)")
    args = parser.parse_args()

    # Show a sample of generated data so the user can verify it looks real
    sample = Customer(0, args.delay)
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║       🛒  NJShop — Fake Customer Simulator (Faker edition)  ║
╚══════════════════════════════════════════════════════════════╝
  Customers : {args.count}
  Workers   : {args.workers} parallel  (browsing phase)
  Delay     : {args.delay}s per call
  Locale    : en_IN  (Indian names, cities, states, phones)
  Expected  : ~{args.count * 18:,} Kafka events

  Sample customer data:
    Name    : {sample.name}
    Email   : {sample.email}
    Phone   : {sample.phone}
    Address : {sample.address}
    City    : {sample.city}
    State   : {sample.state}
    Pincode : {sample.pincode}
    IP      : {sample.ip}
    Device  : {sample.device}
""")

    # Verify Django server is up
    try:
        requests.get(f"{API}/products/", timeout=5)
    except Exception:
        print(f"  ❌  Cannot reach {API}")
        print("      Start the server:  uv run python manage.py runserver")
        sys.exit(1)

    # Load product catalog once — shared across all customers
    products = load_products()
    if not products:
        sys.exit(1)

    # ── Phase 1: Register all customers SEQUENTIALLY ─────────────────────────
    # Sequential to avoid hammering the email backend with parallel welcomes
    print(f"\n  👤  Phase 1 — Registering {args.count} customers…\n")

    customers: list[Customer] = []
    ok = 0

    for i in range(args.count):
        c = Customer(i, args.delay)
        success = c.authenticate()
        customers.append(c)
        ok += success
        mark = "✅" if success else "❌"
        print(
            f"\r    {mark}  {ok:>4}/{i+1:<4} done"
            f"  [{c.name:<28}]  {c.city}, {c.state}",
            end="", flush=True,
        )

    ready = [c for c in customers if c.token]
    print(f"\n\n  ✅  {len(ready)}/{args.count} authenticated")

    if not ready:
        print("  ❌  No customers authenticated. Exiting.")
        sys.exit(1)

    # ── Phase 2: Browsing in parallel ────────────────────────────────────────
    print(f"\n  🛍️   Phase 2 — {len(ready)} customers shopping…\n")

    tots = dict(views=0, likes=0, cart_adds=0, orders=0, errors=0)
    done = 0

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(c.shop, products): c for c in ready}
        for fut in as_completed(futures):
            try:
                s = fut.result()
            except Exception:
                s = dict(views=0, likes=0, cart_adds=0, orders=0, errors=1)
            for k in tots:
                tots[k] += s.get(k, 0)
            done += 1
            show_progress(done, len(ready), tots)

    # ── Report ────────────────────────────────────────────────────────────────
    total_events = tots["views"] + tots["likes"] + tots["cart_adds"] + tots["orders"]
    print(f"""

{'═' * 60}
  📈  COMPLETE
{'═' * 60}
  Customers : {len(ready)}/{args.count}
  ┌────────────────────────────────
  │  👁  Product views    : {tots['views']:>6}
  │  ❤  Product likes    : {tots['likes']:>6}
  │  🛒  Cart additions   : {tots['cart_adds']:>6}
  │  📦  Orders placed    : {tots['orders']:>6}
  │  ❌  Errors           : {tots['errors']:>6}
  └────────────────────────────────
  TOTAL Kafka events : {total_events:>6}
{'═' * 60}
""")


if __name__ == "__main__":
    main()
