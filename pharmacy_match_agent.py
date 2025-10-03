class PharmacyMatchAgent:

    def load_pharmacies(self, filepath):
        with open(filepath) as f:
            pharmacies = json.load(f)
        return pharmacies

    def load_inventory(self, filepath):
        inventory = []
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                inventory.append(row)
        return inventory

    def find_pharmacy_with_stock(self, sku, pharmacies, inventory):
        # Loop through pharmacies
        for pharm in pharmacies:
            # Check inventory for this pharmacy and sku
            for item in inventory:
                if item["pharmacy_id"] == pharm["id"] and item["sku"] == sku and int(item["qty"]) > 0:
                    # Found pharmacy with product
                    return {
                        "pharmacy_id": pharm["id"],
                        "pharmacy_name": pharm["name"],
                        "items": [{"sku": sku, "qty": 1}],
                        "eta_min": 30,          #
                        "delivery_fee": 20      
                    }
        # No pharmacy found with stock
        return False
