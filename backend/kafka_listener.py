#!/usr/bin/env python
"""
Kafka event listener service.
Listens to all shop events and logs them.

Run this as a separate service:
    python kafka_listener.py
"""
import logging
import sys
import os
import django

# Bootstrap Django environment before importing models/kafka consumers
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from insights.kafka import start_listener


def main() -> None:
    """Main entry point."""
    print("\n" + "=" * 80)
    print("🎧 KAFKA EVENT LISTENER SERVICE")
    print("=" * 80)

    try:
        start_listener()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
