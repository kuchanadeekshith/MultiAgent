import csv

class TherapyAgent:
    
    def get_meds_data(self, filepath="./data/meds.csv"):
        """Load OTC medicines from CSV."""
        data = []
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        return data

    def recommend(self, condition_probs, patient_info, meds_path="./data/meds.csv"):
        """
        Recommend OTC meds based on top condition, age, and allergy info.
        Returns otc_options and red_flags.
        """

        age = patient_info.get("age", 0)
        allergies = patient_info.get("allergies", [])

        meds_data = self.get_meds_data(meds_path)

        # Find the most likely condition
        top_condition = max(condition_probs, key=condition_probs.get)

        otc_options = []
        for med in meds_data:
            # Skip if medicine does not match condition
            if med["indication"].lower() != top_condition.lower():
                continue
            # Skip if patient age is below minimum
            if int(med["age_min"]) > age:
                continue
            # Skip if allergy contraindicated
            if any(allergy.lower() in med.get("contra_allergy_keywords","").lower() for allergy in allergies):
                continue

            otc_options.append({
                "sku": med["sku"],
                "dose": med.get("dose", "N/A"),
                "freq": med.get("freq", "N/A"),
                "warnings": [f"contains {med['drug_name'].lower()}"]
            })

        # Dummy red flag logic: can extend based on notes if needed
        red_flags = []
        if "SpO2 < 92%" in patient_info.get("notes", ""):
            red_flags.append("SpO2 < 92%")

        return {
            "otc_options": otc_options,
            "red_flags": red_flags
        }
