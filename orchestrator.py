from pharmacy_match_agent import find_pharmacies_with_stock

class CoordinatorAgent:
    def __init__(self):
        pass

    def route_pharmacy_request(self, sku, user_lat, user_lon):
        # Calls Pharmacy Match Agent
        pharmacies = find_pharmacies_with_stock(sku, user_lat=user_lat, user_lon=user_lon)
        return pharmacies

    def finalize_plan(self, cart_items, teleconsult=None):
        plan = {"cart": cart_items}
        if teleconsult:
            plan["teleconsult"] = teleconsult
        return plan
