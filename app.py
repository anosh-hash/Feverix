import streamlit as st
import pandas as pd
import os
import urllib.parse

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Feverix",
    page_icon="🩺",
    layout="wide"
)

# -------------------------------------------------
# BMI CATEGORY FUNCTION
# -------------------------------------------------
def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# -------------------------------------------------
# LOAD DATASET
# -------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("final_fever_dataset.xlsx")

medicine_df = load_data()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.title("🩺 Patient Details")

age = st.sidebar.number_input("Age", min_value=0, max_value=120, value=25)

temperature = st.sidebar.number_input(
    "Temperature (°F)",
    min_value=90.0,
    max_value=110.0,
    value=98.6
)

gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])

st.sidebar.subheader("Symptoms")
headache = st.sidebar.checkbox("Headache")
body_ache = st.sidebar.checkbox("Body Ache")
fatigue = st.sidebar.checkbox("Fatigue")
cough = st.sidebar.checkbox("Cough")
cold = st.sidebar.checkbox("Cold")
vomiting = st.sidebar.checkbox("Vomiting")

allergies = st.sidebar.text_input("Allergies (if any)")
diet = st.sidebar.selectbox("Diet Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])

pregnant = "No"
if gender == "Female":
    pregnant = st.sidebar.selectbox("Pregnant", ["No", "Yes"])

previous_med = st.sidebar.text_input("Previous Medication")

# -------------------------------------------------
# BMI SECTION
# -------------------------------------------------
st.sidebar.subheader("BMI Calculator")

height_cm = st.sidebar.number_input("Height (cm)", min_value=0.0)
weight = st.sidebar.number_input("Weight (kg)", min_value=0.0)

bmi = 0
bmi_category = "Not Calculated"

if height_cm > 0 and weight > 0:
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    bmi_category = get_bmi_category(bmi)

    st.sidebar.success(f"BMI: {round(bmi,2)}")
    st.sidebar.info(f"Category: {bmi_category}")

# -------------------------------------------------
# MAIN DASHBOARD
# -------------------------------------------------
st.title("🏥 Feverix")
st.markdown("### 🧠 Diagnosis & Recommendation")

if st.button("Analyze Patient Condition"):

    # Pediatric Warning
    if age < 5:
        st.error("⚠ Child below 5 years detected. Pediatric consultation required.")
        st.stop()

    # Pregnancy Warning
    if pregnant == "Yes":
        st.warning("⚠ Pregnancy detected. Consult doctor before medication.")

    # ✅ FINAL FIX: No fever → advice only
    if temperature < 98.50:
        st.success("✅ No significant fever detected.")
        st.info("💡 Advice: Stay hydrated, take rest, and monitor temperature 😇.")
        st.stop()

    # BMI Alerts
    if bmi_category == "Underweight":
        st.warning("⚠ Patient is underweight. Ensure proper nutrition.")
    elif bmi_category == "Obese":
        st.warning("⚠ Patient is obese. Monitor carefully.")

    # -----------------------------
    # 🔥 MATCHING LOGIC
    # -----------------------------
    safe_bmi = bmi if bmi > 0 else medicine_df["BMI"].mean()

    score = (
        abs(medicine_df["Age"] - age) +
        abs(medicine_df["Temperature"] - temperature) +
        abs(medicine_df["BMI"] - safe_bmi)
    )

    # ➕ Symptom matching
    symptom_score = 0

    if headache:
        symptom_score += (medicine_df["Headache"] == "Yes").astype(int)
    if body_ache:
        symptom_score += (medicine_df["Body_Ache"] == "Yes").astype(int)
    if fatigue:
        symptom_score += (medicine_df["Fatigue"] == "Yes").astype(int)
    if cough:
        symptom_score += (medicine_df["Cough"] == "Yes").astype(int)
    if cold:
        symptom_score += (medicine_df["Cold"] == "Yes").astype(int)
    if vomiting:
        symptom_score += (medicine_df["Vomiting"] == "Yes").astype(int)

    final_score = score - (symptom_score * 2)

    closest = medicine_df.loc[final_score.idxmin()]
    suggestion = closest["Medicine"]

    st.success(f"💊 Recommended Medicine: {suggestion}")

# -------------------------------------------------
# SAVE HISTORY 
# -------------------------------------------------
file_name = "health_history.csv"

if st.button("Save Record"):

    new_data = {
        "Age": age,
        "Temperature": temperature,
        "BMI": round(bmi, 2),
        "BMI_Category": bmi_category,
        "Gender": gender,
        "Pregnant": pregnant,
        "Previous Medication": previous_med
    }

    if os.path.exists(file_name):
        old_df = pd.read_csv(file_name)
        updated_df = pd.concat([old_df, pd.DataFrame([new_data])], ignore_index=True)
    else:
        updated_df = pd.DataFrame([new_data])

    updated_df.to_csv(file_name, index=False)
    st.success("✅ Record Saved Successfully! 🗒 ")

# -------------------------------------------------
# SHOW HISTORY 
# -------------------------------------------------
if os.path.exists(file_name):
    st.subheader("📁 Previous Health Records")
    history_df = pd.read_csv(file_name)
    st.dataframe(history_df)

# -------------------------------------------------
# HOSPITAL FINDER
# -------------------------------------------------
st.markdown("---")
st.subheader("🏥 Hospital Finder")

location = st.text_input("Enter your area / city")

if st.button("Find Nearby Hospital"):

    if location.strip() == "":
        st.warning("Please enter your location.")
    else:
        query = urllib.parse.quote(f"hospitals near {location}")
        maps_url = f"https://www.google.com/maps/search/{query}"
        st.markdown(f"[Click here to view hospitals near you]({maps_url})")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown("© 2026 Fever Treatment Professional Dashboard | Built with Streamlit")