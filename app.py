import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie
import requests
from fpdf import FPDF
import datetime
import random
import tempfile
import os
import sqlite3

# ------------------------------
# Load Lottie Animation
# ------------------------------
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_animation = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_u4yrau.json")

# ------------------------------
# Custom CSS
# ------------------------------
st.markdown("""
<style>
.stApp { 
    background-color: #CBF9F8; 
    color: #31333F; 
    font-family: 'Arial', sans-serif; 
}
div.stButton > button { 
    background-color: #FF4B4B; 
    color: white; 
    font-size: 18px; 
    border-radius: 10px; 
    padding: 10px 20px; 
    margin-top: 10px; 
    transition: transform 0.2s; 
}
div.stButton > button:hover { 
    transform: scale(1.05); 
}
.recommend-tips {color: green; font-weight: bold;}
.recommend-diet {color: orange; font-weight: bold;}
.recommend-exercise {color: red; font-weight: bold;}
.section-bg {
    background-color: #F0F2F6; 
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Load Model
# ------------------------------
model = joblib.load("health_model.pkl")

# ------------------------------
# Health Recommendations
# ------------------------------
def get_health_recommendations(category):
    if category == "Low":
        return {"tips": "You may need to rest more and stay warm.",
                "diet": "Eat nutrient-rich foods like soups, warm meals, and protein.",
                "exercise": "Light stretching or yoga; avoid intense workouts."}
    elif category == "Normal":
        return {"tips": "Your body temperature is normal. Keep maintaining healthy habits!",
                "diet": "Balanced diet with fruits, vegetables, protein, and water.",
                "exercise": "Regular moderate exercise is good for health."}
    elif category == "High":
        return {"tips": "You may have a fever. Monitor your temperature closely.",
                "diet": "Stay hydrated; light meals, avoid spicy/oily food.",
                "exercise": "Rest is important; avoid strenuous activity."}
    else:
        return {"tips": "", "diet": "", "exercise": ""}

# ------------------------------
# PDF Export
# ------------------------------
def export_pdf(patient_data, pie_path, bp_path, bmi_hr_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Health Check-up Summary", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Patient Information", ln=True)
    pdf.set_font("Arial", "", 12)
    for key in ["Name","Age","Gender","Systolic","Diastolic","BMI","HeartRate","SleepHours"]:
        pdf.cell(0, 8, f"{key}: {patient_data[key]}", ln=True)
    pdf.ln(8)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Predicted Temperature Category", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"{patient_data['Prediction']}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Health Recommendations", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, f"Tips: {patient_data['Tips']}\nDiet: {patient_data['Diet']}\nExercise: {patient_data['Exercise']}")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Charts", ln=True)
    pdf.image(pie_path, w=180)
    pdf.ln(5)
    pdf.image(bp_path, w=180)
    pdf.ln(5)
    pdf.image(bmi_hr_path, w=180)
    
    pdf_file = f"Patient_Summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(pdf_file)
    return pdf_file

# ------------------------------
# Database Setup
# ------------------------------
def init_db():
    conn = sqlite3.connect("health_dashboard.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            sleep_hours REAL,
            bmi REAL,
            heart_rate INTEGER,
            systolic INTEGER,
            diastolic INTEGER,
            prediction TEXT,
            tips TEXT,
            diet TEXT,
            exercise TEXT,
            submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ------------------------------
# Streamlit Layout
# ------------------------------
st.set_page_config(page_title="Health Dashboard", layout="wide")
st.title("Health Temperature Dashboard")
st_lottie(lottie_animation, height=200)
st.markdown("Enter your details below to check your temperature category and visualize health trends.")
st.write("---")

# ------------------------------
# User Inputs
# ------------------------------
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Personal Info")
    name = st.text_input("Patient Name", "ARSHAD JAVED ALAM")
    age = st.number_input("Age (years)", 1, 120, 25)
    gender = st.selectbox("Gender", ["M","F"])
    sleep_hours = st.number_input("Sleep Hours per Day", 0, 24, 7)

with col2:
    st.markdown("### Body Stats & BP")
    bmi = st.number_input("BMI", 10.0, 50.0, 22.0, 0.1)
    heart_rate = st.number_input("Heart Rate (bpm)", 40, 200, 72)
    systolic = st.number_input("Systolic BP (mmHg)", 90, 180, 120)
    diastolic = st.number_input("Diastolic BP (mmHg)", 60, 120, 80)

st.write("---")

# ------------------------------
# Prediction & Save to Database
# ------------------------------
if st.button("Predict Temperature Category"):
    gender_encoded = 1 if gender=="F" else 0
    input_data = pd.DataFrame({
        "Age":[age],
        "Gender":[gender_encoded],
        "Systolic":[systolic],
        "Diastolic":[diastolic]
    })

    prediction = model.predict(input_data)[0]
    st.success(f"Predicted Temperature Category: {prediction}")
    recs = get_health_recommendations(prediction)

    # Save to database
    conn = sqlite3.connect("health_dashboard.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO submissions (name, age, gender, sleep_hours, bmi, heart_rate, systolic, diastolic, prediction, tips, diet, exercise)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, age, gender, sleep_hours, bmi, heart_rate, systolic, diastolic, prediction, recs['tips'], recs['diet'], recs['exercise']))
    conn.commit()
    conn.close()

    # Recommendations
    st.subheader("Health Recommendations")
    st.markdown(f"<p class='recommend-tips'>Tips: {recs['tips']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='recommend-diet'>Diet: {recs['diet']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='recommend-exercise'>Exercise: {recs['exercise']}</p>", unsafe_allow_html=True)

    # Charts & PDF
    week_categories = [random.choice(["Low","Normal","High"]) for _ in range(6)]
    week_categories.append(prediction)
    pie_data = pd.Series(week_categories).value_counts()
    fig_pie = px.pie(values=pie_data.values, names=pie_data.index,
                     title=f"{name}'s Temperature Category Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)

    df_bp = pd.DataFrame({
        "Day": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        "Systolic": [systolic+random.randint(-5,5) for _ in range(7)],
        "Diastolic": [diastolic+random.randint(-3,3) for _ in range(7)]
    })
    fig_bp = px.line(df_bp, x="Day", y=["Systolic","Diastolic"], markers=True, title="BP Trend Over Week")
    st.plotly_chart(fig_bp, use_container_width=True)

    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    bmi_trend = [bmi+random.uniform(-1,1) for _ in range(7)]
    hr_trend = [heart_rate+random.randint(-5,5) for _ in range(7)]
    plt.figure(figsize=(6,3))
    plt.plot(days, bmi_trend, marker='o', color='#FF4500', label="BMI")
    plt.plot(days, hr_trend, marker='o', color='#4B0082', label="Heart Rate")
    plt.fill_between(days, bmi_trend, color='#FFCC99', alpha=0.2)
    plt.fill_between(days, hr_trend, color='#C3CFE2', alpha=0.2)
    plt.xlabel("Day")
    plt.ylabel("Value")
    plt.title("BMI & Heart Rate Trend")
    plt.legend()
    st.pyplot(plt)
    plt.close()

    # Create temp files safely
    pie_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bp_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    bmi_hr_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")

    fig_pie.write_image(pie_tmp.name)
    fig_bp.write_image(bp_tmp.name)
    plt.savefig(bmi_hr_tmp.name)
    plt.close()

    patient_info = {
        "Name": name,
        "Age": age,
        "Gender": gender,
        "Systolic": systolic,
        "Diastolic": diastolic,
        "BMI": bmi,
        "HeartRate": heart_rate,
        "SleepHours": sleep_hours,
        "Prediction": prediction,
        "Tips": recs['tips'],
        "Diet": recs['diet'],
        "Exercise": recs['exercise']
    }

    pdf_file = export_pdf(patient_info, pie_tmp.name, bp_tmp.name, bmi_hr_tmp.name)

    # Download PDF and delete temp files safely
    with open(pdf_file, "rb") as f:
        st.download_button("Download Patient Summary PDF", data=f,
                           file_name=pdf_file, mime="application/pdf")

    pie_tmp.close()
    bp_tmp.close()
    bmi_hr_tmp.close()
    os.unlink(pie_tmp.name)
    os.unlink(bp_tmp.name)
    os.unlink(bmi_hr_tmp.name)

# ------------------------------
# SEARCH Previous Submissions
# ------------------------------
st.write("---")
st.header("Search Previous Submissions")
search_name = st.text_input("Search by Patient Name").strip()

if st.button("Search Database"):
    if search_name == "":
        st.warning("Please enter a name to search.")
    else:
        conn = sqlite3.connect("health_dashboard.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM submissions WHERE LOWER(name) LIKE ?", ('%' + search_name.lower() + '%',))
        results = cursor.fetchall()
        conn.close()

        if results:
            df_results = pd.DataFrame(results, columns=[
                "ID","Name","Age","Gender","SleepHours","BMI","HeartRate",
                "Systolic","Diastolic","Prediction","Tips","Diet","Exercise","SubmissionTime"])
            df_results["ID"] = range(1, len(df_results) + 1)  # sequential IDs
            st.success(f"Found {len(results)} result(s) for '{search_name}'")
            st.dataframe(df_results)
        else:
            st.warning(f"No submissions found for '{search_name}'.")

# ------------------------------
# SHOW ALL SUBMISSIONS
# ------------------------------
st.write("---")
st.header("All Submitted Patients Data")

conn = sqlite3.connect("health_dashboard.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM submissions ORDER BY submission_time DESC")
all_results = cursor.fetchall()
conn.close()

if all_results:
    df_all = pd.DataFrame(all_results, columns=[
        "ID","Name","Age","Gender","SleepHours","BMI","HeartRate",
        "Systolic","Diastolic","Prediction","Tips","Diet","Exercise","SubmissionTime"])
    df_all["ID"] = range(1, len(df_all) + 1)
    st.dataframe(df_all)
else:
    st.warning("No submissions found yet!")

# ------------------------------
# DELETE MULTIPLE RECORDS WITH AUTO REFRESH
# ------------------------------
st.write("---")
st.header("Delete Patient Records")

if "refresh_flag" not in st.session_state:
    st.session_state.refresh_flag = False

conn = sqlite3.connect("health_dashboard.db")
cursor = conn.cursor()
cursor.execute("SELECT id, name FROM submissions ORDER BY submission_time DESC")
patients = cursor.fetchall()
conn.close()

if patients:
    patient_dict = {f"{name} (ID: {id})": id for id, name in patients}
    selected_patients = st.multiselect("Select patients to delete", list(patient_dict.keys()))

    if st.button("Delete Selected Patients"):
        if selected_patients:
            conn = sqlite3.connect("health_dashboard.db")
            cursor = conn.cursor()
            for patient in selected_patients:
                cursor.execute("DELETE FROM submissions WHERE id=?", (patient_dict[patient],))
            conn.commit()
            conn.close()

            st.success(f"Deleted {len(selected_patients)} patient record(s) successfully.")
            st.session_state.refresh_flag = True

# Refresh table after deletion
if st.session_state.refresh_flag:
    st.session_state.refresh_flag = False
    st.experimental_rerun_disabled = True  # This just forces re-render

st.write("---")
st.write("Developed by: **Arshad Javed Alam** | Final Year Project")
