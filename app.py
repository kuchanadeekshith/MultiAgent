import streamlit as st
from PIL import Image
from ingestion import ingestion_agent
from imaging_agent import imaging_agent
from therapy import therapy_agent
from pharmacy_match_agent import find_pharmacies_with_stock
from orchestrator import CoordinatorAgent
from tensorflow.keras.models import load_model
import csv

coordinator = CoordinatorAgent()

# --- Page setup ---
st.set_page_config(page_title="Chest X-ray Triaging App", layout="wide")

# --- Load model ---
model = load_model("Covid.h5")

# --- Session State Initialization ---
if "page" not in st.session_state:
    st.session_state.page = "xray_upload"
if "ingested" not in st.session_state:
    st.session_state.ingested = None
if "imaging_results" not in st.session_state:
    st.session_state.imaging_results = None
if "therapy_results" not in st.session_state:
    st.session_state.therapy_results = None
if "therapy_triggered" not in st.session_state:
    st.session_state.therapy_triggered = False
if "selected_otc" not in st.session_state:
    st.session_state.selected_otc = []
if "cart_items" not in st.session_state:
    st.session_state.cart_items = []
if "nearest_pharmacies" not in st.session_state:
    st.session_state.nearest_pharmacies = []
if "tele_consult_fee" not in st.session_state:
    st.session_state.tele_consult_fee = 0
if "selected_doctor" not in st.session_state:
    st.session_state.selected_doctor = None

# ---------------------- X-RAY UPLOAD & ANALYSIS ----------------
if st.session_state.page == "xray_upload":
    st.title("Chest X-ray Triaging System")
    xray_file = st.file_uploader("Upload Chest X-ray (PNG/JPG)", type=["png", "jpg", "jpeg"])
    pdf_file = st.file_uploader("Optional PDF report", type=["pdf"])

    xray_path = pdf_path = None
    if xray_file:
        xray_path = f"temp_{xray_file.name}"
        with open(xray_path, "wb") as f:
            f.write(xray_file.getbuffer())
        st.image(Image.open(xray_path), caption="Uploaded X-ray", use_column_width=True)
    if pdf_file:
        pdf_path = f"temp_{pdf_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())

    if st.button("Run Ingestion"):
        st.session_state.ingested = ingestion_agent(xray_path, pdf_path)
        st.success("Ingestion complete!")

    if st.session_state.ingested:
        patient = st.session_state.ingested["patient"]
        st.markdown("### Patient Details")
        col1, col2, col3 = st.columns(3)
        col1.metric("Age", patient['age'])
        col2.metric("Allergies", ", ".join(patient['allergies']))
        col3.metric("Detected Symptoms", ", ".join(st.session_state.ingested['symptoms']) if st.session_state.ingested['symptoms'] else "None")

        with st.expander("View Extracted Notes"):
            st.text(st.session_state.ingested.get("notes", "No notes extracted."))

        if st.button("Run Imaging Analysis"):
            st.session_state.imaging_results = imaging_agent(model, xray_path)
            st.session_state.therapy_results = None
            st.success("Imaging analysis complete!")

    if st.session_state.imaging_results:
        results = st.session_state.imaging_results
        st.subheader("Imaging Analysis Results")
        prob_cols = st.columns(len(results["condition_probs"]))
        for idx, (cond, prob) in enumerate(results["condition_probs"].items()):
            pct = f"{prob*100:.1f}%"
            if cond.lower() in ["covid suspect", "pneumonia"]:
                if prob > 0.6:
                    prob_cols[idx].error(f"{cond}: {pct}")
                elif prob > 0.3:
                    prob_cols[idx].warning(f"{cond}: {pct}")
                else:
                    prob_cols[idx].success(f"{cond}: {pct}")
            else:
                if prob > 0.6:
                    prob_cols[idx].success(f"{cond}: {pct}")
                elif prob > 0.3:
                    prob_cols[idx].warning(f"{cond}: {pct}")
                else:
                    prob_cols[idx].error(f"{cond}: {pct}")

        severity = results.get("severity_hint", "unknown")
        severity_text = {
            "critical": "Critical - urgent attention required",
            "moderate": "Moderate concern",
            "mild": "Mild concern",
            "none": "No critical condition detected",
            "unknown": "Unknown"
        }[severity]

        if severity == "critical":
            st.error(f"**Severity:** {severity_text}")
        elif severity == "moderate":
            st.warning(f"**Severity:** {severity_text}")
        elif severity == "mild":
            st.success(f"**Severity:** {severity_text}")
        else:
            st.info(f"**Severity:** {severity_text}")

    if st.session_state.ingested and st.session_state.imaging_results:
        if st.button("Run Therapy Agent"):
            st.session_state.therapy_results = therapy_agent(
                st.session_state.imaging_results["condition_probs"],
                st.session_state.ingested["patient"]
            )
            st.session_state.therapy_triggered = True
            st.success("Therapy agent suggestions generated!")

    if st.session_state.therapy_results and st.session_state.therapy_triggered:
        therapy_results = st.session_state.therapy_results
        st.markdown(f"### Main Condition Detected: **{therapy_results.get('main_condition','Unknown')}**")
        st.markdown("### Recommended OTC Medications")
        advice_list = therapy_results.get("advice_text", "").split("\n")
        otc_options = [med.strip("- ").strip() for med in advice_list if med.startswith("-")]
        st.session_state.selected_otc = otc_options
        for line in advice_list:
            if line.startswith("-"):
                st.success(line[1:].strip())
            elif line.lower().startswith("note"):
                st.warning(line)
            else:
                st.info(line)
        st.button("Next → Select OTC Medications", on_click=lambda: st.session_state.update({"page": "otc_multiselect"}))

# ---------------------- OTC MULTISELECT & PHARMACY ----------------
# ---------------------- OTC MULTISELECT & PHARMACY ----------------
elif st.session_state.page == "otc_multiselect":
    st.title("Step 3: Select OTC Medications")

    otc_options = st.session_state.selected_otc
    selected_otc = st.multiselect(
        "Select OTC Medications to Add to Cart",
        otc_options,
        default=otc_options
    )
    st.session_state.selected_otc = selected_otc

    if st.button("Add Selected OTCs to Cart"):
        for med in selected_otc:
            st.session_state.cart_items.append({
                "sku": med,
                "price": 0,
                "qty": 1,
                "delivery_fee": 0,
                "total_price": 0
            })
        st.success("OTC medications added to cart!")

    st.button("Next → Pharmacy Finder", on_click=lambda: st.session_state.update({"page": "pharmacy"}))

elif st.session_state.page == "pharmacy":
    st.title("Step 4: Nearest Pharmacy Finder")

    if not st.session_state.selected_otc:
        st.warning("Please select OTCs first.")
        st.stop()

    sku_to_find = st.selectbox("Select OTC to find nearby pharmacies", st.session_state.selected_otc)
    user_lat = st.number_input("Your latitude", value=18.93352, format="%.6f")
    user_lon = st.number_input("Your longitude", value=72.823485, format="%.6f")

    if st.button("Find Nearest Pharmacies"):
        nearest = find_pharmacies_with_stock(sku_to_find, user_lat, user_lon)
        if nearest:
            st.session_state.nearest_pharmacies = nearest
            st.success(f"Found {len(nearest)} pharmacies nearby!")
        else:
            st.warning("No pharmacies found within range.")

    if st.session_state.nearest_pharmacies:
        selected_pharm = st.selectbox(
            "Select Pharmacy to Add OTC to Cart",
            [f"{p['pharmacy_name']} - {p['drug_name']} - Rs {p['price']} ({p['available_qty']} available)"
             for p in st.session_state.nearest_pharmacies]
        )

        if st.button("Add Selected OTC to Cart"):
            idx = [f"{p['pharmacy_name']} - {p['drug_name']} - Rs {p['price']} ({p['available_qty']} available)"
                   for p in st.session_state.nearest_pharmacies].index(selected_pharm)
            pharm = st.session_state.nearest_pharmacies[idx]
            st.session_state.cart_items.append({
                "sku": pharm['sku'],
                "price": pharm['price'],
                "qty": 1,
                "delivery_fee": pharm['delivery_fee'],
                "total_price": pharm['price'] + pharm['delivery_fee'],
                "eta_min": pharm.get('eta_min', 45)
            })
            st.success(f"{pharm['drug_name']} added to cart from {pharm['pharmacy_name']}!")

    st.button("Next → Tele-Consult", on_click=lambda: st.session_state.update({"page": "teleconsult"}))


# ---------------------- TELE-CONSULT ----------------
elif st.session_state.page == "teleconsult":
    st.title("Optional Tele-Consult (Rs 500)")
    # Load doctors
    def load_doctors(filepath="data/doctors.csv"):
        doctors = []
        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                doctors.append({
                    "doctor_id": row["doctor_id"],
                    "name": row["name"],
                    "specialty": row["specialty"]
                })
        return doctors
    doctors = load_doctors()
    doctor_options = [f"{doc['doctor_id']}: {doc['name']} ({doc['specialty']})" for doc in doctors]
    selected = st.selectbox("Select a doctor (optional)", ["None"] + doctor_options)
    if selected != "None":
        st.session_state.tele_consult_fee = 500
        st.session_state.selected_doctor = selected
    else:
        st.session_state.tele_consult_fee = 0
        st.session_state.selected_doctor = None

    cols = st.columns(2)
    with cols[0]:
        st.button("Next → Checkout", on_click=lambda: st.session_state.update({"page":"checkout"}))
    with cols[1]:
        st.button("← Back to Pharmacy", on_click=lambda: st.session_state.update({"page":"otc_multiselect"}))

# ---------------------- CHECKOUT ----------------
elif st.session_state.page == "checkout":
    st.title("Final Cart & Checkout")
    total = st.session_state.tele_consult_fee

    # ✅ Filter out items with qty <= 0
    valid_cart_items = [
    item for item in st.session_state.cart_items
    if item.get("qty", 0) > 0 and item.get("price", 0) > 0
                        ]


    if valid_cart_items:
        st.subheader("Cart Items")

        for idx, item in enumerate(valid_cart_items):
            with st.container():
                st.markdown(
                    f"""
                    <div style='
                        padding:15px; 
                        border:1px solid #ccc; 
                        border-radius:10px; 
                        margin-bottom:10px; 
                        background-color:#f9f9f9; 
                        color:#111;
                    '>
                        <h4 style='color:#111;'>{item['sku']}</h4>
                        <p>Price/unit: <b>Rs {item['price']}</b></p>
                        <p>Delivery: <b>Rs {item['delivery_fee']}</b></p>
                        <p>ETA: <b>{item.get('eta_min', 'N/A')} min</b></p>
                    </div>
                    """, unsafe_allow_html=True
                )

                qty = st.number_input(
                    f"Qty for {item['sku']}",
                    min_value=1,
                    value=item['qty'],
                    key=f"qty_{item['sku']}_{idx}"
                )

                # ✅ Update quantity and total dynamically
                item['qty'] = qty
                item['total_price'] = item['price'] * qty + item['delivery_fee']
                total += item['total_price']

        if st.session_state.selected_doctor:
            st.info(
                f"Tele-Consult with **{st.session_state.selected_doctor}** "
                f"(Fee: Rs {st.session_state.tele_consult_fee})"
            )

        st.subheader(f"Grand Total: Rs {total}")

        cols = st.columns(2)
        with cols[0]:
            if st.button("Checkout"):
                st.success(f"✅ Checkout successful! Total paid: Rs {total}")
                st.session_state.cart_items = []
                st.session_state.tele_consult_fee = 0
                st.session_state.selected_doctor = None
                st.session_state.page = "pharmacy"
        with cols[1]:
            st.button("← Back to Tele-Consult", on_click=lambda: st.session_state.update({"page": "teleconsult"}))

    else:
        st.warning("Cart is empty. Add items before checkout.")
        st.button("← Back", on_click=lambda: st.session_state.update({"page": "teleconsult"}))
