import streamlit as st
import pandas as pd
import numpy as np

def calculate_sia_error(actual_mag, actual_axis, incision_axis, sim_sia):
    theta_actual = np.deg2rad(2 * actual_axis)
    J0_actual = -actual_mag / 2 * np.cos(theta_actual)
    J45_actual = -actual_mag / 2 * np.sin(theta_actual)

    theta_sim = np.deg2rad(2 * incision_axis)
    J0_sim = -sim_sia / 2 * np.cos(theta_sim)
    J45_sim = -sim_sia / 2 * np.sin(theta_sim)

    return np.sqrt((J0_actual - J0_sim) ** 2 + (J45_actual - J45_sim) ** 2)

st.title("SIA Error Simulator")

uploaded_file = st.file_uploader("Upload Excel file with columns: Incision Axis, SIA Axis, SIA Magnitude", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df_result = df.copy()

    for sim in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
        error_col = f"Error if SIA = {sim:.1f}"
        df_result[error_col] = df.apply(lambda row: calculate_sia_error(
            row["SIA Magnitude"], row["SIA Axis"], row["Incision Axis"], sim
        ), axis=1)

    df_result["Actual SIA Error"] = df.apply(lambda row: calculate_sia_error(
        row["SIA Magnitude"], row["SIA Axis"], row["Incision Axis"], 0
    ), axis=1)

    st.success("Calculation Complete")
    st.dataframe(df_result)

    st.download_button("Download Result as Excel", df_result.to_excel(index=False), file_name="SIA_Simulation_Output.xlsx")