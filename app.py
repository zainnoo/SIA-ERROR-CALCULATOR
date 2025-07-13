import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="SIA Error Calculator", layout="centered")

def calculate_sia_error(flattened_mag, flattened_axis, incision_axis, sim_sia):
    # Convert axis to radians for double-angle vector calculation
    theta_actual = np.deg2rad(2 * flattened_axis)
    J0_actual = -flattened_mag * np.cos(theta_actual)
    J45_actual = -flattened_mag * np.sin(theta_actual)

    theta_sim = np.deg2rad(2 * incision_axis)
    J0_sim = -sim_sia * np.cos(theta_sim)
    J45_sim = -sim_sia * np.sin(theta_sim)

    return np.sqrt((J0_actual - J0_sim)**2 + (J45_actual - J45_sim)**2)

st.title("SIA Error Calculator")

st.markdown("Input the **flattened axis and magnitude** (as provided by your SIA calculator). No need to enter negative signs — the app assumes flattening.")

with st.form("sia_form"):
    incision_axis = st.number_input("Incision Axis (°)", min_value=0.0, max_value=180.0, value=90.0, step=1.0)
    flattened_axis = st.number_input("Actual SIA Flattened Axis (°)", min_value=0.0, max_value=180.0, value=90.0, step=1.0)
    flattened_mag = st.number_input("Actual SIA Flattened Magnitude (D)", value=0.20, step=0.01, min_value=0.0, max_value=1.0)
    submitted = st.form_submit_button("Calculate")

if submitted:
    sims = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    error_data = {"SIA Assumed (D)": [], "Vectorial Error": []}

    for sim_sia in sims:
        error = calculate_sia_error(flattened_mag, flattened_axis, incision_axis, sim_sia)
        error_data["SIA Assumed (D)"].append(sim_sia)
        error_data["Vectorial Error"].append(round(error, 4))

    df_result = pd.DataFrame(error_data)

    min_error = df_result["Vectorial Error"].min()
    max_error = df_result["Vectorial Error"].max()
    best_sia = df_result[df_result["Vectorial Error"] == min_error]["SIA Assumed (D)"].values[0]
    worst_sia = df_result[df_result["Vectorial Error"] == max_error]["SIA Assumed (D)"].values[0]

    st.dataframe(df_result)

    st.markdown(f"<p><b style='color:green;'>✅ Least Error at SIA = {best_sia} D</b></p>", unsafe_allow_html=True)
    st.markdown(f"<p><b style='color:red;'>❌ Most Error at SIA = {worst_sia} D</b></p>", unsafe_allow_html=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_result.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="Download This Result as Excel",
        data=output,
        file_name="SIA_Result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )