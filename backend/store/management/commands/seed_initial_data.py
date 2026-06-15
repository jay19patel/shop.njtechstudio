from decimal import Decimal

from django.core.management.base import BaseCommand

from store.models import Category, Product, ProductImage, Testimonial


CATEGORIES = [
    {
        "name": "Monitors & Displays",
        "slug": "monitors-displays",
        "description": "Full HD, QHD, and 4K monitors for gaming, design, and productivity.",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a573d5e59a?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Processors (CPU)",
        "slug": "processors-cpu",
        "description": "Intel and AMD desktop processors for every build from budget to workstation.",
        "image_url": "https://images.unsplash.com/photo-1555617981-dac3880eac6e?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Motherboards",
        "slug": "motherboards",
        "description": "ATX and Micro-ATX motherboards compatible with Intel and AMD platforms.",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "RAM & Memory",
        "slug": "ram-memory",
        "description": "DDR4 and DDR5 memory kits for smooth multitasking and high-performance gaming.",
        "image_url": "https://images.unsplash.com/photo-1562976540-1502c2145186?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Storage (SSD & HDD)",
        "slug": "storage-ssd-hdd",
        "description": "Fast NVMe SSDs and high-capacity HDDs to store your games, files, and media.",
        "image_url": "https://images.unsplash.com/photo-1601737487795-dab272f52420?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Graphics Cards (GPU)",
        "slug": "graphics-cards-gpu",
        "description": "NVIDIA and AMD GPUs for gaming, content creation, and AI workloads.",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Keyboards",
        "slug": "keyboards",
        "description": "Membrane and mechanical keyboards for typing, coding, and gaming.",
        "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Mice & Trackpads",
        "slug": "mice-trackpads",
        "description": "Wired and wireless mice built for precision, comfort, and competitive gaming.",
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Headsets & Audio",
        "slug": "headsets-audio",
        "description": "Gaming headsets and stereo headphones with crystal-clear mic quality.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Cooling & Fans",
        "slug": "cooling-fans",
        "description": "Air coolers, AIO liquid coolers, and case fans to keep your build running cool.",
        "image_url": "https://images.unsplash.com/photo-1555617748-4f1bdb3f06a2?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "PC Cases & Cabinets",
        "slug": "pc-cases-cabinets",
        "description": "Mid tower and full tower cases with excellent airflow and cable management.",
        "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Power Supply Units",
        "slug": "power-supply-units",
        "description": "80+ certified PSUs from 450W to 850W for reliable and efficient power delivery.",
        "image_url": "https://images.unsplash.com/photo-1562408590-e32931084e23?auto=format&fit=crop&w=1200&q=80",
    },
]


PRODUCTS = [
    # ── Monitors & Displays ──────────────────────────────────────────────────
    {
        "category": "monitors-displays",
        "name": "Dell 24\" Full HD IPS Monitor (E2422H)",
        "slug": "dell-24-fhd-monitor-e2422h",
        "description": "24-inch Full HD (1920×1080) IPS panel with ComfortView, 8ms response time, and VGA + HDMI connectivity. Perfect for everyday productivity and office work.",
        "base_price": "12999.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a573d5e59a?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 25,
    },
    {
        "category": "monitors-displays",
        "name": "LG 27\" QHD IPS Monitor (27QN600)",
        "slug": "lg-27-qhd-ips-monitor-27qn600",
        "description": "27-inch QHD (2560×1440) IPS panel with sRGB 99% colour accuracy, AMD FreeSync, and ultra-slim bezels. Ideal for designers and content creators.",
        "base_price": "22999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1547082299-de196ea013d6?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 15,
    },
    {
        "category": "monitors-displays",
        "name": "Samsung 27\" 144Hz Curved Gaming Monitor (Odyssey G5)",
        "slug": "samsung-27-144hz-curved-odyssey-g5",
        "description": "27-inch WQHD 144Hz VA curved panel with 1ms response time, AMD FreeSync Premium, and HDR10 support. Built for immersive gaming sessions.",
        "base_price": "28999.00",
        "discount_percentage": "8.00",
        "image_url": "https://images.unsplash.com/photo-1593640408182-31c228ea6efc?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 12,
    },
    {
        "category": "monitors-displays",
        "name": "BenQ 32\" 4K HDR Designer Monitor (EW3270U)",
        "slug": "benq-32-4k-hdr-monitor-ew3270u",
        "description": "32-inch 4K UHD (3840×2160) IPS with HDR400, 95% DCI-P3, USB-C 60W charging, and BenQ Eye-Care technology. The ultimate display for creative professionals.",
        "base_price": "45999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 8,
    },
    {
        "category": "monitors-displays",
        "name": "AOC 24\" 144Hz Gaming Monitor (24G2)",
        "slug": "aoc-24-144hz-gaming-monitor-24g2",
        "description": "24-inch Full HD 144Hz IPS panel with 1ms MPRT, AMD FreeSync, and ultra-thin bezels on three sides. An affordable entry into high-refresh gaming.",
        "base_price": "18499.00",
        "discount_percentage": "10.00",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a573d5e59a?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 20,
    },

    # ── Processors (CPU) ─────────────────────────────────────────────────────
    {
        "category": "processors-cpu",
        "name": "Intel Core i3-12100F 4-Core Processor",
        "slug": "intel-core-i3-12100f",
        "description": "4 cores / 8 threads, 3.3GHz base up to 4.3GHz boost, 12MB L3 cache. Excellent budget processor for everyday computing and light gaming without integrated graphics.",
        "base_price": "8499.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1555617981-dac3880eac6e?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 30,
    },
    {
        "category": "processors-cpu",
        "name": "Intel Core i5-12400F 6-Core Processor",
        "slug": "intel-core-i5-12400f",
        "description": "6 cores / 12 threads, 2.5GHz base up to 4.4GHz boost, 18MB L3 cache. Best mid-range gaming CPU for LGA1700 platform — outstanding price-to-performance ratio.",
        "base_price": "13499.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1555617981-dac3880eac6e?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 25,
    },
    {
        "category": "processors-cpu",
        "name": "Intel Core i7-13700K 16-Core Processor",
        "slug": "intel-core-i7-13700k",
        "description": "16 cores (8P+8E) / 24 threads, up to 5.4GHz boost, 30MB L3 cache, unlocked for overclocking. Handles the most demanding games and creative workloads simultaneously.",
        "base_price": "32999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1581092921461-eab62e97a780?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 10,
    },
    {
        "category": "processors-cpu",
        "name": "AMD Ryzen 5 5600X 6-Core Processor",
        "slug": "amd-ryzen-5-5600x",
        "description": "6 cores / 12 threads, 3.7GHz base up to 4.6GHz boost, 35MB total cache, AM4 socket. Top-performing mid-range gaming CPU with Wraith Stealth cooler included.",
        "base_price": "14999.00",
        "discount_percentage": "12.00",
        "image_url": "https://images.unsplash.com/photo-1555617981-dac3880eac6e?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 20,
    },
    {
        "category": "processors-cpu",
        "name": "AMD Ryzen 9 5900X 12-Core Processor",
        "slug": "amd-ryzen-9-5900x",
        "description": "12 cores / 24 threads, 3.7GHz base up to 4.8GHz boost, 70MB total cache. A powerhouse for 3D rendering, video editing, and simultaneous gaming and streaming.",
        "base_price": "34999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1581092921461-eab62e97a780?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 8,
    },

    # ── Motherboards ─────────────────────────────────────────────────────────
    {
        "category": "motherboards",
        "name": "MSI B660M PRO-A DDR4 Micro-ATX Motherboard",
        "slug": "msi-b660m-pro-a-ddr4",
        "description": "LGA1700 socket, Intel B660 chipset, 4x DDR4 slots (up to 128GB), PCIe 4.0, M.2 NVMe slot, 2.5G LAN, and USB 3.2 Gen 2. Solid budget board for 12th/13th Gen builds.",
        "base_price": "9999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 15,
    },
    {
        "category": "motherboards",
        "name": "ASUS ROG STRIX B550-F Wi-Fi ATX Motherboard",
        "slug": "asus-rog-strix-b550-f-wifi",
        "description": "AM4 socket, AMD B550 chipset, 4x DDR4 slots, PCIe 4.0, 2x M.2 NVMe, Wi-Fi 6, 2.5G LAN, and Aura Sync RGB. Premium feature set for Ryzen 5000-series builds.",
        "base_price": "18999.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 12,
    },
    {
        "category": "motherboards",
        "name": "Gigabyte Z790 AORUS Elite AX ATX Motherboard",
        "slug": "gigabyte-z790-aorus-elite-ax",
        "description": "LGA1700 socket, Intel Z790 chipset, DDR5 support, Wi-Fi 6E, 4x M.2 slots, Thunderbolt 4, and robust 16+1+2 VRM for 13th Gen overclocking builds.",
        "base_price": "28999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 8,
    },
    {
        "category": "motherboards",
        "name": "ASRock B450M Steel Legend Micro-ATX Motherboard",
        "slug": "asrock-b450m-steel-legend",
        "description": "AM4 socket, AMD B450 chipset, 4x DDR4 slots (up to 128GB), PCIe 3.0, M.2 slot, Steel Armor slot protection, and built-in RGB. Great budget AM4 board.",
        "base_price": "7499.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 18,
    },

    # ── RAM & Memory ─────────────────────────────────────────────────────────
    {
        "category": "ram-memory",
        "name": "Corsair Vengeance LPX 8GB DDR4 3200MHz",
        "slug": "corsair-vengeance-lpx-8gb-ddr4-3200",
        "description": "8GB single stick DDR4-3200MHz CL16, low-profile heat spreader for cooler clearance. XMP 2.0 support for one-click overclocking. Great for basic builds and upgrades.",
        "base_price": "2499.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1562976540-1502c2145186?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 50,
    },
    {
        "category": "ram-memory",
        "name": "G.Skill Ripjaws V 16GB DDR4 3600MHz (2×8GB)",
        "slug": "gskill-ripjaws-v-16gb-ddr4-3600",
        "description": "16GB dual-channel kit (2×8GB) DDR4-3600MHz CL16, XMP 2.0, low-profile fin heat spreader. Sweet spot for gaming builds — improved bandwidth over 3200MHz.",
        "base_price": "4999.00",
        "discount_percentage": "8.00",
        "image_url": "https://images.unsplash.com/photo-1562976540-1502c2145186?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 35,
    },
    {
        "category": "ram-memory",
        "name": "Kingston FURY Beast 32GB DDR4 3200MHz (2×16GB)",
        "slug": "kingston-fury-beast-32gb-ddr4-3200",
        "description": "32GB dual-channel kit (2×16GB) DDR4-3200MHz CL16, Plug N Play auto-overclocking, aggressive low-profile heat spreader. Ideal for content creation and heavy multitasking.",
        "base_price": "9499.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1562976540-1502c2145186?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 20,
    },
    {
        "category": "ram-memory",
        "name": "Crucial Ballistix 16GB DDR4 3200MHz RGB (2×8GB)",
        "slug": "crucial-ballistix-16gb-ddr4-3200-rgb",
        "description": "16GB dual-channel kit (2×8GB) DDR4-3200MHz CL16 with customisable RGB lighting, XMP 2.0, and optimised PCB layout. Style meets performance.",
        "base_price": "3999.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1562976540-1502c2145186?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 30,
    },

    # ── Storage (SSD & HDD) ──────────────────────────────────────────────────
    {
        "category": "storage-ssd-hdd",
        "name": "Western Digital Blue 1TB 7200RPM HDD",
        "slug": "wd-blue-1tb-7200rpm-hdd",
        "description": "1TB 3.5-inch hard drive at 7200RPM with 64MB cache, SATA 6Gb/s. Reliable long-term storage for games, media libraries, and backups.",
        "base_price": "2999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1601737487795-dab272f52420?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 40,
    },
    {
        "category": "storage-ssd-hdd",
        "name": "Seagate Barracuda 2TB 7200RPM HDD",
        "slug": "seagate-barracuda-2tb-7200rpm-hdd",
        "description": "2TB 3.5-inch hard drive at 7200RPM with 256MB cache, SATA 6Gb/s. Excellent capacity-to-cost ratio for secondary storage and bulk data archival.",
        "base_price": "4499.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1601737487795-dab272f52420?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 30,
    },
    {
        "category": "storage-ssd-hdd",
        "name": "Samsung 870 EVO 500GB SATA SSD",
        "slug": "samsung-870-evo-500gb-sata-ssd",
        "description": "500GB 2.5-inch SATA SSD with sequential read 560MB/s, write 530MB/s, MKX controller. Massive upgrade over any HDD — boot Windows in seconds.",
        "base_price": "4999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1601737487795-dab272f52420?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 25,
    },
    {
        "category": "storage-ssd-hdd",
        "name": "WD Blue SN570 1TB NVMe M.2 SSD",
        "slug": "wd-blue-sn570-1tb-nvme-ssd",
        "description": "1TB PCIe Gen 3 NVMe M.2 SSD with sequential read up to 3500MB/s. Dramatically faster than SATA, perfect as a primary drive for OS and frequently-played games.",
        "base_price": "6499.00",
        "discount_percentage": "10.00",
        "image_url": "https://images.unsplash.com/photo-1601737487795-dab272f52420?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 22,
    },
    {
        "category": "storage-ssd-hdd",
        "name": "Samsung 980 Pro 1TB NVMe PCIe 4.0 SSD",
        "slug": "samsung-980-pro-1tb-nvme-pcie4-ssd",
        "description": "1TB PCIe Gen 4 NVMe M.2 SSD with blazing sequential read up to 7000MB/s. The fastest consumer SSD for PS5 upgrades, high-end PCs, and professional workstations.",
        "base_price": "9999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1601737487795-dab272f52420?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 15,
    },

    # ── Graphics Cards (GPU) ─────────────────────────────────────────────────
    {
        "category": "graphics-cards-gpu",
        "name": "NVIDIA GeForce GTX 1650 4GB GDDR6",
        "slug": "nvidia-gtx-1650-4gb-gddr6",
        "description": "4GB GDDR6, 896 CUDA cores, HDMI 2.0 + DisplayPort 1.4, low-profile card that fits small cases and requires no external power connector. Entry-level 1080p gaming.",
        "base_price": "14999.00",
        "discount_percentage": "15.00",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 10,
    },
    {
        "category": "graphics-cards-gpu",
        "name": "NVIDIA GeForce RTX 3060 12GB GDDR6",
        "slug": "nvidia-rtx-3060-12gb-gddr6",
        "description": "12GB GDDR6, 3584 CUDA cores, PCIe 4.0, ray tracing, DLSS 2.0. Handles 1080p at ultra and 1440p at high settings across all modern titles.",
        "base_price": "28999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 8,
    },
    {
        "category": "graphics-cards-gpu",
        "name": "AMD Radeon RX 6600 8GB GDDR6",
        "slug": "amd-radeon-rx-6600-8gb-gddr6",
        "description": "8GB GDDR6, 1792 stream processors, PCIe 4.0, AMD FidelityFX Super Resolution. Strong 1080p performance and competitive pricing vs NVIDIA alternatives.",
        "base_price": "22999.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 10,
    },
    {
        "category": "graphics-cards-gpu",
        "name": "NVIDIA GeForce RTX 4070 12GB GDDR6X",
        "slug": "nvidia-rtx-4070-12gb-gddr6x",
        "description": "12GB GDDR6X, 5888 CUDA cores, DLSS 3.0 with Frame Generation, PCIe 4.0. Exceptional 1440p and capable 4K gaming in a power-efficient Ada Lovelace package.",
        "base_price": "52999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 5,
    },

    # ── Keyboards ────────────────────────────────────────────────────────────
    {
        "category": "keyboards",
        "name": "Logitech K120 Wired USB Keyboard",
        "slug": "logitech-k120-wired-usb-keyboard",
        "description": "Full-size spill-resistant keyboard with quiet typing, low-profile keys, and plug-and-play USB. The reliable everyday keyboard for office and home use.",
        "base_price": "599.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 100,
    },
    {
        "category": "keyboards",
        "name": "Redragon K552 Mechanical Gaming Keyboard",
        "slug": "redragon-k552-mechanical-keyboard",
        "description": "87-key tenkeyless layout with Outemu Blue switches, red single-zone backlight, and aircraft-grade aluminium backplate. Best entry-level mechanical keyboard under ₹3,000.",
        "base_price": "2499.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 40,
    },
    {
        "category": "keyboards",
        "name": "HyperX Alloy FPS Pro Mechanical Keyboard",
        "slug": "hyperx-alloy-fps-pro-mechanical",
        "description": "Tenkeyless mechanical keyboard with Cherry MX Red switches, bright red backlight, detachable braided cable, and N-key rollover. Compact footprint for gamers.",
        "base_price": "5999.00",
        "discount_percentage": "10.00",
        "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 25,
    },
    {
        "category": "keyboards",
        "name": "Logitech G Pro X Mechanical Gaming Keyboard",
        "slug": "logitech-g-pro-x-mechanical-keyboard",
        "description": "Compact tenkeyless with swappable GX switches (sold with Blue Clicky), per-key RGB LIGHTSYNC, and advanced USB report rate. Built for esports professionals.",
        "base_price": "8999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 15,
    },
    {
        "category": "keyboards",
        "name": "Corsair K70 RGB MK.2 Mechanical Keyboard",
        "slug": "corsair-k70-rgb-mk2-mechanical",
        "description": "Full-size keyboard with Cherry MX Speed switches, per-key dynamic RGB backlighting, aluminium frame, detachable wrist rest, and USB passthrough port. Premium build.",
        "base_price": "12999.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 10,
    },

    # ── Mice & Trackpads ─────────────────────────────────────────────────────
    {
        "category": "mice-trackpads",
        "name": "Logitech B100 Optical Wired Mouse",
        "slug": "logitech-b100-optical-wired-mouse",
        "description": "3-button optical mouse with 800 DPI sensor, plug-and-play USB, and ambidextrous design. Simple and durable mouse for everyday computing.",
        "base_price": "399.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 100,
    },
    {
        "category": "mice-trackpads",
        "name": "Logitech G102 Lightsync Gaming Mouse",
        "slug": "logitech-g102-lightsync-gaming-mouse",
        "description": "6-button gaming mouse with 8000 DPI sensor, 16.8M colour RGB, 1000Hz polling rate, and durable 10M click switches. Lightweight and great for beginners.",
        "base_price": "1299.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 50,
    },
    {
        "category": "mice-trackpads",
        "name": "Razer DeathAdder V2 Gaming Mouse",
        "slug": "razer-deathadder-v2-gaming-mouse",
        "description": "Focus+ 20K DPI optical sensor, 8 programmable buttons, Razer Chroma RGB, ergonomic right-hand form factor, and Speedflex cable. Industry-favourite shape.",
        "base_price": "3499.00",
        "discount_percentage": "8.00",
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 30,
    },
    {
        "category": "mice-trackpads",
        "name": "SteelSeries Rival 600 Gaming Mouse",
        "slug": "steelseries-rival-600-gaming-mouse",
        "description": "Dual TrueMove3+ sensor with depth detection, 12000 DPI, adjustable side weights, split trigger buttons, and SteelSeries Prism RGB. For precision-driven players.",
        "base_price": "4999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 20,
    },
    {
        "category": "mice-trackpads",
        "name": "Logitech G502 Hero High-Performance Mouse",
        "slug": "logitech-g502-hero-gaming-mouse",
        "description": "HERO 25K DPI sensor, 11 programmable buttons, adjustable weight system up to 18g, hyper-fast scrolling, and RGB LIGHTSYNC. The legendary high-performance gaming mouse.",
        "base_price": "4499.00",
        "discount_percentage": "12.00",
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 25,
    },

    # ── Headsets & Audio ─────────────────────────────────────────────────────
    {
        "category": "headsets-audio",
        "name": "Logitech H111 Stereo Headset",
        "slug": "logitech-h111-stereo-headset",
        "description": "Stereo headset with 3.5mm jack, rotating microphone, padded headband, and foldable design. A comfortable, no-fuss headset for calls and casual listening.",
        "base_price": "899.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 60,
    },
    {
        "category": "headsets-audio",
        "name": "HyperX Cloud Stinger Gaming Headset",
        "slug": "hyperx-cloud-stinger-gaming-headset",
        "description": "50mm directional drivers, swivel-to-mute noise-cancelling mic, volume slider on the ear cup, and memory foam ear cushions. Lightweight gaming comfort at an accessible price.",
        "base_price": "2999.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 35,
    },
    {
        "category": "headsets-audio",
        "name": "Corsair HS60 Pro Surround Gaming Headset",
        "slug": "corsair-hs60-pro-surround-headset",
        "description": "50mm neodymium drivers, Dolby 7.1 surround sound via USB adapter, detachable unidirectional mic, and memory foam ear pads. Immersive audio for competitive FPS.",
        "base_price": "5499.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 20,
    },
    {
        "category": "headsets-audio",
        "name": "SteelSeries Arctis 7 Wireless Gaming Headset",
        "slug": "steelseries-arctis-7-wireless-headset",
        "description": "2.4GHz lossless wireless with 24-hour battery, ClearCast bidirectional microphone, DTS Headphone:X 2.0 surround, and ski-goggle suspension headband. True wireless freedom.",
        "base_price": "11999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 12,
    },

    # ── Cooling & Fans ───────────────────────────────────────────────────────
    {
        "category": "cooling-fans",
        "name": "Cooler Master Hyper 212 RGB Black Edition",
        "slug": "cooler-master-hyper-212-rgb-black",
        "description": "4 direct-contact heat pipes, 120mm RGB fan, compatible with Intel LGA1700 and AMD AM5/AM4. The most popular budget air cooler — handles CPUs up to 150W TDP.",
        "base_price": "2799.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1555617748-4f1bdb3f06a2?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 30,
    },
    {
        "category": "cooling-fans",
        "name": "Noctua NH-D15 Premium CPU Cooler",
        "slug": "noctua-nh-d15-premium-cpu-cooler",
        "description": "Dual-tower design with twin NF-A15 PWM fans, SecuFirm2 mounting, and ultra-low noise operation. The benchmark for air cooling — handles any desktop CPU on the market.",
        "base_price": "7999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1555617748-4f1bdb3f06a2?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 15,
    },
    {
        "category": "cooling-fans",
        "name": "NZXT Kraken X53 240mm AIO Liquid Cooler",
        "slug": "nzxt-kraken-x53-240mm-aio-cooler",
        "description": "240mm radiator, two 120mm Aer P fans, infinite mirror cap with addressable RGB, and CAM software integration. Sleek all-in-one liquid cooling for mid-range builds.",
        "base_price": "10999.00",
        "discount_percentage": "8.00",
        "image_url": "https://images.unsplash.com/photo-1555617748-4f1bdb3f06a2?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 10,
    },
    {
        "category": "cooling-fans",
        "name": "Corsair iCUE H150i Elite Capellix 360mm AIO",
        "slug": "corsair-h150i-elite-capellix-360mm-aio",
        "description": "360mm radiator, three 120mm QL RGB fans (204 LEDs), Capellix RGB pump head, iCUE software control. Top-tier liquid cooling for overclocked flagship CPUs.",
        "base_price": "16999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1555617748-4f1bdb3f06a2?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 8,
    },

    # ── PC Cases & Cabinets ──────────────────────────────────────────────────
    {
        "category": "pc-cases-cabinets",
        "name": "Cooler Master MasterBox Q300L Micro-ATX Cabinet",
        "slug": "cooler-master-masterbox-q300l",
        "description": "Micro-ATX case with magnetic dust filters, transparent acrylic side panel, flexible I/O port placement, and multiple fan mounting positions. Great compact budget build.",
        "base_price": "3499.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 20,
    },
    {
        "category": "pc-cases-cabinets",
        "name": "NZXT H510 Compact ATX Mid Tower Case",
        "slug": "nzxt-h510-mid-tower-case",
        "description": "Steel and tempered glass mid tower, built-in cable management bar, two 120mm Aer F fans included, vertical GPU mount ready. Clean minimalist aesthetic.",
        "base_price": "7499.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 15,
    },
    {
        "category": "pc-cases-cabinets",
        "name": "Fractal Design Meshify C ATX Mid Tower",
        "slug": "fractal-design-meshify-c-mid-tower",
        "description": "High-airflow angular mesh front, tempered glass side panel, two Dynamic X2 GP-14 fans pre-installed, and excellent cable routing channels. Engineering-focused design.",
        "base_price": "8999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 12,
    },
    {
        "category": "pc-cases-cabinets",
        "name": "Lian Li PC-O11 Dynamic Mid Tower Case",
        "slug": "lian-li-pc-o11-dynamic-mid-tower",
        "description": "Dual-chamber design with tempered glass on two sides, support for up to 420mm radiator, and a showcase layout for water-cooled builds. The go-to choice for premium builds.",
        "base_price": "12999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 10,
    },

    # ── Power Supply Units ───────────────────────────────────────────────────
    {
        "category": "power-supply-units",
        "name": "Cooler Master MWE 450W 80+ White PSU",
        "slug": "cooler-master-mwe-450w-80plus-white",
        "description": "450W output, 80+ White efficiency (up to 85%), 120mm fan with automatic speed control, universal AC input, and standard ATX form factor. Dependable budget power supply.",
        "base_price": "2999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1562408590-e32931084e23?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 30,
    },
    {
        "category": "power-supply-units",
        "name": "Corsair CV550 550W 80+ Bronze PSU",
        "slug": "corsair-cv550-550w-80plus-bronze",
        "description": "550W output, 80+ Bronze certified (up to 88%), fixed cable design, single 12V rail, and 120mm quiet fan. Reliable power for mid-range gaming builds up to RTX 3060.",
        "base_price": "3799.00",
        "discount_percentage": "5.00",
        "image_url": "https://images.unsplash.com/photo-1562408590-e32931084e23?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 25,
    },
    {
        "category": "power-supply-units",
        "name": "Seasonic Focus GX-650 650W 80+ Gold PSU",
        "slug": "seasonic-focus-gx-650-80plus-gold",
        "description": "650W fully modular, 80+ Gold certified (up to 92%), Hybrid Fan Mode (fanless at low load), 10-year warranty, and 100% Japanese capacitors. Premium choice for quality builds.",
        "base_price": "7499.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1562408590-e32931084e23?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 15,
    },
    {
        "category": "power-supply-units",
        "name": "EVGA SuperNOVA 750 G6 750W 80+ Gold PSU",
        "slug": "evga-supernova-750-g6-80plus-gold",
        "description": "750W fully modular, 80+ Gold certified, compact 140mm depth fits tight builds, 10-year warranty, eco mode for silent low-load operation. Handles RTX 4070 and Ryzen 9 comfortably.",
        "base_price": "9999.00",
        "discount_percentage": "0.00",
        "image_url": "https://images.unsplash.com/photo-1562408590-e32931084e23?auto=format&fit=crop&w=800&q=80",
        "available_quantity": 12,
    },
]


TESTIMONIALS = [
    {
        "name": "Arjun Kapoor",
        "role": "PC Builder & Gamer",
        "content": "Built my first gaming rig using parts from here. The i5-12400F and RTX 3060 combo was exactly what I needed. Packaging was solid and delivery was fast.",
        "rating": 5,
        "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
    },
    {
        "name": "Sneha Iyer",
        "role": "Content Creator",
        "content": "Ordered the Ryzen 9 5900X and Samsung 980 Pro together. Render times on my video projects dropped by 40%. Great prices compared to other stores.",
        "rating": 5,
        "image_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=400&q=80",
    },
    {
        "name": "Vikram Nair",
        "role": "IT Professional",
        "content": "The SteelSeries Arctis 7 headset I got for WFH calls is outstanding. Mic clarity is excellent and the wireless range covers my whole apartment.",
        "rating": 5,
        "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=400&q=80",
    },
    {
        "name": "Pooja Sharma",
        "role": "Esports Enthusiast",
        "content": "The AOC 24G2 monitor at 144Hz was a game-changer. Everything arrived well-protected and the team replied quickly when I had a query about compatibility.",
        "rating": 4,
        "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
    },
]


class Command(BaseCommand):
    help = "Clear existing products/categories and seed computer-parts catalog (12 categories, 53 products)."

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing products and categories...")
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
