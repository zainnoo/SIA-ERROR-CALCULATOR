
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SIA Error Calculator", layout="centered")

st.title("Surgically Induced Astigmatism (SIA) Error Calculator")

st.markdown("Use this tool to calculate the vectorial error in astigmatism induced during cataract surgery based on actual vs assumed SIA.")

incision_axis = st.number_input("Incision Axis (°)", min_value=0.0, max_value=180.0, step=1.0, value=90.0)
actual_axis = st.number_input("Actual SIA Flattened Axis (°)", min_value=0.0, max_value=180.0, step=1.0, value=90.0)
actual_mag = st.number_input("Actual SIA Flattened Magnitude (D)", min_value=0.0, max_value=5.0, step=0.01, value=0.0)

def compute_error(actual_axis, actual_mag, assumed_mag_list, incision_axis):
    theta_actual = np.deg2rad(2 * actual_axis)
    J0_actual = -actual_mag * np.cos(theta_actual)
    J45_actual = -actual_mag * np.sin(theta_actual)
    errors = []
    for assumed_mag in assumed_mag_list:
        theta_assumed = np.deg2rad(2 * incision_axis)
        J0_assumed = -assumed_mag * np.cos(theta_assumed)
        J45_assumed = -assumed_mag * np.sin(theta_assumed)
        error = round(np.sqrt((J0_actual - J0_assumed)**2 + (J45_actual - J45_assumed)**2), 4)
        errors.append(error)
    return errors

if st.button("Calculate"):
    assumed_sia_list = [round(i * 0.1, 1) for i in range(6)]
    errors = compute_error(actual_axis, actual_mag, assumed_sia_list, incision_axis)
    df = pd.DataFrame({
        "SIA Assumed (D)": assumed_sia_list,
        "Vectorial Error": errors
    })
    st.success("Calculation Complete")
    st.dataframe(df, use_container_width=True)

    min_idx = int(np.argmin(errors))
    max_idx = int(np.argmax(errors))
    st.markdown(f"✅ **Least Error at SIA = {assumed_sia_list[min_idx]:.1f} D**")
    st.markdown(f"❌ **Most Error at SIA = {assumed_sia_list[max_idx]:.1f} D**")

    # Download option
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download This Result as Excel", data=csv, file_name="SIA_error_results.csv", mime="text/csv")
