"""
live_sim.py — Continuous Realistic Traffic Simulator
═════════════════════════════════════════════════════
Runs forever (until Ctrl+C), simulating slow but steady realistic user traffic.

One independent thread per activity type. Each thread sleeps between events
so rates stay close to the configured hourly targets.

Usage:
  python live_sim.py                  # Default rates
  python live_sim.py --speed 2.0      # 2x faster  (e.g. testing)
  python live_sim.py --speed 0.5      # Half speed  (even slower)

Requires:
  pip install faker requests
"""

import argparse
import random
import signal
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

import requests
from faker import Faker

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG — change these to tune traffic intensity
# ─────────────────────────────────────────────────────────────────────────────

RATES = {
    "views_per_hour":     50,   # Product page opens  (~1 every 72s)
    "likes_per_hour":      4,   # Likes               (~1 every 15min)
    "cart_adds_per_hour": 10,   # Items added to cart (~1 every 6min)
    "orders_per_hour":     2,   # Checkouts placed    (~1 every 30min)
    "new_users_per_hour":  3,   # New registrations   (~1 every 20min)
}

MAX_POOL_SIZE = 30      # Max logged-in users kept in memory
INITIAL_POOL  = 5       # Users to bootstrap before traffic starts
DISPLAY_EVERY = 15      # Seconds between stats line refresh

API  = "http://127.0.0.1:8000/api"
fake = Faker("en_IN")

DEVICES = ["desktop", "mobile", "tablet"]
UA = {
    "desktop": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0",
    "mobile":  "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/118.0",
    "tablet":  "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
}

# ─────────────────────────────────────────────────────────────────────────────
#  Shared state
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class User:
    name:    str
    email:   str
    pw:      str
    phone:   str
    address: str
    city:    str
    state:   str
    pincode: str
    device:  str
    ip:      str
    token:   str
    cart_id: Optional[int]             = None
    session: requests.Session          = field(default_factory=requests.Session)


class Stats:
    def __init__(self):
        self._lock   = threading.Lock()
        self.views   = 0
        self.likes   = 0
        self.cart    = 0
        self.orders  = 0
        self.users   = 0
        self.errors  = 0

    def inc(self, name: str, n: int = 1):
        with self._lock:
            setattr(self, name, getattr(self, name) + n)

    @property
    def total_events(self):
        return self.views + self.likes + self.cart + self.orders


stats     = Stats()
user_pool: List[User] = []
products:  List[dict] = []
pool_lock = threading.Lock()
running   = True

# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get(session: requests.Session, path: str, params=None) -> dict:
    try:
        r = session.get(f"{API}{path}", params=params, timeout=12)
        return r.json() if r.ok else {}
    except Exception:
        return {}


def _post(session: requests.Session, path: str, body=None) -> dict:
    try:
        r = session.post(f"{API}{path}", json=body or {}, timeout=12)
        return r.json() if r.ok else {}
    except Exception:
        return {}


def jitter(base: float) -> float:
    """Return base seconds ±30% so traffic isn't perfectly uniform."""
    return base * random.uniform(0.70, 1.30)


def pick_user() -> Optional[User]:
    with pool_lock:
        return random.choice(user_pool) if user_pool else None


def pick_product() -> Optional[dict]:
    return random.choice(products) if products else None


def ensure_cart(user: User) -> Optional[int]:
    """Return an existing cart_id or create a new cart."""
    if user.cart_id:
        return user.cart_id
    existing = _get(user.session, "/carts/")
    results  = existing.get("results", []) if isinstance(existing, dict) else []
    if results:
        user.cart_id = results[0]["id"]
    else:
        cart = _post(user.session, "/carts/")
        user.cart_id = cart.get("id")
    return user.cart_id

# ─────────────────────────────────────────────────────────────────────────────
#  User registration helper
# ─────────────────────────────────────────────────────────────────────────────

def register_user() -> Optional[User]:
    """Register a fresh fake Indian user. Returns authenticated User or None."""
    email = f"sim.{uuid.uuid4().hex[:10]}@livesim.test"
    pw    = "Sim@Pass#2024"
    name  = fake.name()
    dev   = random.choice(DEVICES)
    ip    = fake.ipv4_public()

    session = requests.Session()
    session.headers.update({
        "Content-Type":    "application/json",
        "X-Forwarded-For": ip,
        "User-Agent":      UA[dev],
    })

    try:
        r = session.post(f"{API}/auth/register", json={
            "email": email, "password": pw, "name": name,
        }, timeout=30)

        if r.status_code == 201:
            data  = r.json()
            token = data.get("access") or data.get("token", "")
            if token:
                session.headers["Authorization"] = f"Bearer {token}"
                return User(
                    name=name, email=email, pw=pw,
                    phone=fake.phone_number()[:15],
                    address=fake.street_address(),
                    city=fake.city(), state=fake.state(),
                    pincode=fake.postcode(),
                    device=dev, ip=ip, token=token, session=session,
                )
    except Exception:
        pass
    return None

# ─────────────────────────────────────────────────────────────────────────────
#  Worker threads — one per activity type
# ─────────────────────────────────────────────────────────────────────────────

def thread_new_users(interval: float):
    """Register new users and add them to the pool."""
    time.sleep(random.uniform(5, 20))           # stagger start

    while running:
        user = register_user()
        if user:
            with pool_lock:
                if len(user_pool) < MAX_POOL_SIZE:
                    user_pool.append(user)
            stats.inc("users")
        else:
            stats.inc("errors")
        time.sleep(jitter(interval))


def thread_views(interval: float):
    """Simulate users loading product detail pages."""
    time.sleep(random.uniform(2, 15))

    while running:
        user = pick_user()
        prod = pick_product()
        if user and prod:
            _get(user.session, f"/products/{prod['id']}/")
            stats.inc("views")
        time.sleep(jitter(interval))


def thread_likes(interval: float):
    """Simulate product likes (toggle-like endpoint)."""
    time.sleep(random.uniform(60, 180))         # likes come after some views

    while running:
        user = pick_user()
        prod = pick_product()
        if user and prod:
            _post(user.session, "/likes/toggle-like/", {"product_id": prod["id"]})
            stats.inc("likes")
        time.sleep(jitter(interval))


def thread_cart(interval: float):
    """Simulate adding items to cart."""
    time.sleep(random.uniform(90, 240))

    while running:
        user = pick_user()
        prod = pick_product()
        if user and prod:
            cart_id = ensure_cart(user)
            if cart_id:
                qty = random.randint(1, 2)
                # Try both URL styles (DRF configs vary)
                res = _post(user.session, f"/carts/{cart_id}/add_item/",
                            {"product_id": prod["id"], "quantity": qty})
                if not (res.get("id") or res.get("quantity")):
                    res = _post(user.session, f"/carts/{cart_id}/add-item/",
                                {"product_id": prod["id"], "quantity": qty})
                if res.get("id") or res.get("quantity"):
                    stats.inc("cart")
                else:
                    stats.inc("errors")
        time.sleep(jitter(interval))


def thread_orders(interval: float):
    """Simulate checkouts — the rarest but highest-weight event."""
    time.sleep(random.uniform(180, 400))        # orders need cart items first

    while running:
        user = pick_user()
        if user:
            cart_id = ensure_cart(user)
            if cart_id:
                res = _post(user.session, f"/carts/{cart_id}/checkout/", {
                    "shipping_address": user.address,
                    "customer_name":    user.name,
                    "customer_email":   user.email,
                    "customer_phone":   user.phone,
                    "city":             user.city,
                    "state":            user.state,
                    "pincode":          user.pincode,
                })
                if res.get("id"):
                    user.cart_id = None         # Cart is cleared after order
                    stats.inc("orders")
        time.sleep(jitter(interval))


def thread_display(start_time: float):
    """Print a live stats line every DISPLAY_EVERY seconds."""
    while running:
        time.sleep(DISPLAY_EVERY)
        elapsed = time.time() - start_time
        m, s = divmod(int(elapsed), 60)
        h, m = divmod(m, 60)
        print(
            f"\r  ⏱ {h:02d}:{m:02d}:{s:02d}"
            f"  pool={len(user_pool):>2}"
            f"  👁 views={stats.views:<5}"
            f"  ❤ likes={stats.likes:<4}"
            f"  🛒 cart={stats.cart:<4}"
            f"  📦 orders={stats.orders:<3}"
            f"  👤 +users={stats.users:<3}"
            f"  ❌ err={stats.errors:<3}"
            f"  total_events={stats.total_events}",
            flush=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    global running, products

    parser = argparse.ArgumentParser(description="NJShop — Live Continuous Traffic Simulator")
    parser.add_argument(
        "--speed", type=float, default=1.0,
        help=(
            "Speed multiplier applied to all intervals. "
            "1.0 = real-time (default). 2.0 = twice as fast. 0.5 = half speed."
        ),
    )
    args = parser.parse_args()
    speed = max(0.1, args.speed)   # Guard against 0

    # Calculate seconds between events for each activity
    iv = {k: (3600 / v) / speed for k, v in RATES.items()}

    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║       🔄  NJShop — Live Continuous Traffic Simulator             ║
╚═══════════════════════════════════════════════════════════════════╝

  Target rates (at {speed}x speed):
    👤  New users     : {RATES['new_users_per_hour']} /hr   → 1 every ~{iv['new_users_per_hour']:.0f}s
    👁  Product views : {RATES['views_per_hour']} /hr   → 1 every ~{iv['views_per_hour']:.0f}s
    ❤  Likes         : {RATES['likes_per_hour']} /hr   → 1 every ~{iv['likes_per_hour']:.0f}s
    🛒  Cart adds     : {RATES['cart_adds_per_hour']} /hr   → 1 every ~{iv['cart_adds_per_hour']:.0f}s
    📦  Orders        : {RATES['orders_per_hour']} /hr   → 1 every ~{iv['orders_per_hour']:.0f}s

  Max user pool : {MAX_POOL_SIZE}
  Stats refresh : every {DISPLAY_EVERY}s

  Change RATES dict at top of this file to adjust intensity.
  Press Ctrl+C to stop.
""")

    # Verify server is reachable
    try:
        requests.get(f"{API}/products/", timeout=5)
    except Exception:
        print(f"  ❌  Cannot reach {API}")
        print("      Start Django: python manage.py runserver")
        sys.exit(1)

    # Load product catalog
    print("  📦  Loading products…", end=" ", flush=True)
    try:
        r   = requests.get(f"{API}/products/", params={"page_size": 200}, timeout=10)
        raw = r.json().get("results", []) if r.ok else []
        products = [
            {
                "id":   p["id"],
                "name": p.get("name", ""),
                "cat":  (p.get("category") or {}).get("name", ""),
            }
            for p in raw
            if p.get("available_quantity", 0) > 0
        ]
        print(f"{len(products)} active products ✓")
    except Exception as e:
        print(f"ERROR — {e}")
        sys.exit(1)

    if not products:
        print("  ❌  No in-stock products found. Add products first.")
        sys.exit(1)

    # Bootstrap initial user pool before traffic starts
    print(f"\n  👥  Bootstrapping {INITIAL_POOL} initial users (may take ~30s)…")
    for i in range(INITIAL_POOL):
        u = register_user()
        if u:
            with pool_lock:
                user_pool.append(u)
            stats.inc("users")
            print(f"       [{i+1}/{INITIAL_POOL}] ✅  {u.name:<28}  {u.city}, {u.state}")
        else:
            print(f"       [{i+1}/{INITIAL_POOL}] ❌  Registration failed")

    if not user_pool:
        print("\n  ❌  Could not register any users. Check your Django server.")
        sys.exit(1)

    print(f"\n  Pool ready with {len(user_pool)} users.\n")

    # Handle Ctrl+C gracefully
    def shutdown(sig, frame):
        global running
        running = False
        print("\n\n  ✋  Shutdown signal received — stopping threads…")

    signal.signal(signal.SIGINT, shutdown)

    # Launch all worker threads
    start_time = time.time()
    threads = [
        threading.Thread(target=thread_new_users, args=(iv["new_users_per_hour"],), daemon=True, name="users"),
        threading.Thread(target=thread_views,     args=(iv["views_per_hour"],),     daemon=True, name="views"),
        threading.Thread(target=thread_likes,     args=(iv["likes_per_hour"],),     daemon=True, name="likes"),
        threading.Thread(target=thread_cart,      args=(iv["cart_adds_per_hour"],), daemon=True, name="cart"),
        threading.Thread(target=thread_orders,    args=(iv["orders_per_hour"],),    daemon=True, name="orders"),
        threading.Thread(target=thread_display,   args=(start_time,),               daemon=True, name="display"),
    ]
    for t in threads:
        t.start()

    print("  🚀  All threads running. Watching for traffic…\n")

    # Keep main thread alive until Ctrl+C
    while running:
        time.sleep(0.5)

    elapsed = time.time() - start_time
    h, rem  = divmod(int(elapsed), 3600)
    m, s    = divmod(rem, 60)

    print(f"""
{'═' * 65}
  📈  SIMULATION COMPLETE  (ran for {h:02d}h {m:02d}m {s:02d}s)
{'═' * 65}
  👤  New users registered  : {stats.users}
  👁  Product views         : {stats.views}
  ❤  Likes                 : {stats.likes}
  🛒  Cart additions        : {stats.cart}
  📦  Orders placed         : {stats.orders}
  ❌  Errors                : {stats.errors}
  ─────────────────────────────────────────────
  Total Kafka events        : {stats.total_events}
{'═' * 65}
""")


if __name__ == "__main__":
    main()
