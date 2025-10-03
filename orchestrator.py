class CoordinatorAgent:
    def __init__(self):
        pass

    def extract_red_flags_from_notes(self, notes):
        """
        Heuristic method to find red flag symptoms in patient notes text.
        """
        red_flag_keywords = [
            "chest pain",
            "shortness of breath",
            "severe cough",
            "high fever",
            "loss of consciousness"
        ]
        found_flags = []
        notes_lower = notes.lower()
        for keyword in red_flag_keywords:
            if keyword in notes_lower:
                found_flags.append(keyword)
        return found_flags

    def consolidate(self, imaging_output, therapy_output, notes):
        """
        Consolidate all agent outputs and patient notes into a final plan.
        """
        red_flags = therapy_output.get("red_flags", [])

        # Extract red flags from notes
        red_flags += self.extract_red_flags_from_notes(notes)
        red_flags = list(set(red_flags))  # remove duplicates

        # Check if condition severity is severe
        severity = imaging_output.get("severity_hint", "").lower()
        if severity == "severe":
            red_flags.append("Severe condition detected in imaging")

        # Final plan
        final_plan = {
            "condition_probs": imaging_output.get("condition_probs", {}),
            "severity_hint": severity,
            "otc_options": therapy_output.get("otc_options", []),
            "red_flags": red_flags,
            "advice": "This is not medical advice. Consult a healthcare professional for diagnosis and treatment."
        }

        # Immediate care advice if red flags present
        if red_flags:
            final_plan["immediate_care_advice"] = "Red flags detected. Advise immediate medical attention."

        return final_plan
