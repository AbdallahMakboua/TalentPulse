#!/usr/bin/env python3
"""Seed demo data via API call."""

import httpx
import sys

API_URL = "http://localhost:8000"


def main():
    print("🌱 Seeding TalentPulse demo data...")
    try:
        resp = httpx.post(f"{API_URL}/sync/run", timeout=60)
        resp.raise_for_status()
        data = resp.json()
        print(f"✅ {data['message']}")
        print(f"   Employees: {data['employees_processed']}")
        print(f"   Signal weeks: {data['weeks_generated']}")
        print(f"   Scores: {data['scores_computed']}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
