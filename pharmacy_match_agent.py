import json
import pandas as pd
from location import haversine_manual

def find_pharmacies_with_stock(
    sku_or_name,
    user_lat,
    user_lon,
    pharmacies_file="data/pharmacies.json",
    inventory_file="data/inventory.csv",
    max_distance=100
):
    with open(pharmacies_file) as f:
        pharmacies = json.load(f)
    inventory = pd.read_csv(inventory_file)

    search_key = str(sku_or_name).strip().lower()
    matches = []

    for pharm in pharmacies:
        inv = inventory[
            (inventory["pharmacy_id"] == pharm["id"]) &
            (
                (inventory["sku"].str.lower() == search_key) |
                (inventory["drug_name"].str.lower() == search_key)
            ) &
            (inventory["qty"] > 0)
        ]

        if not inv.empty:
            distance = haversine_manual(user_lat, user_lon, float(pharm["lat"]), float(pharm["lon"]))
            if distance <= max_distance:
                matches.append({
                    "pharmacy_id": pharm["id"],
                    "pharmacy_name": pharm["name"],
                    "distance": round(distance, 2),
                    "price": int(inv.iloc[0]["price"]),
                    "delivery_fee": 50,
                    "available_qty": int(inv.iloc[0]["qty"]),
                    "sku": inv.iloc[0]["sku"],
                    "drug_name": inv.iloc[0]["drug_name"],
                    "eta_min":round(distance*2,2)
                })

    matches = sorted(matches, key=lambda x: x["distance"])
    return matches[:3]
