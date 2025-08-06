
import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from io import BytesIO

# ===== Helper Functions =====
def to_double_angle_vector(magnitude, axis_deg):
    axis_rad = math.radians(2 * axis_deg)
    return np.array([magnitude * math.cos(axis_rad),
                     magnitude * math.sin(axis_rad)])

def vector_difference_components(mag1, axis1, mag2, axis2):
    vec1 = to_double_angle_vector(mag1, axis1)
    vec2 = to_double_angle_vector(mag2, axis2)
    diff_vec = vec1 - vec2
    return diff_vec

def vector_difference_magnitude(mag1, axis1, mag2, axis2):
    diff_vec = vector_difference_components(mag1, axis1, mag2, axis2)
    return np.linalg.norm(diff_vec)

def double_angle_to_polar(vec):
    mag = np.linalg.norm(vec)
    axis_rad = 0.5 * math.atan2(vec[1], vec[0])
    axis_deg = math.degrees(axis_rad) % 180
    return mag, axis_deg

# ===== Sidebar for mode selection =====
mode = st.sidebar.radio("Select Mode", ["Single Case", "Batch Processing"])

if mode == "Single Case":
    st.title("SIA Error Calculator (Single Case)")

    incision_axis = st.number_input("Incision Axis (degrees)", min_value=0.0, max_value=180.0, value=0.0)
    expected_mag = st.number_input("Expected SIA Flattening Magnitude (D)", min_value=0.0, value=0.0, step=0.01)
    actual_axis = st.number_input("Actual SIA Flattening Axis (degrees)", min_value=0.0, max_value=180.0, value=0.0)
    actual_mag = st.number_input("Actual SIA Flattening Magnitude (D)", min_value=0.0, value=0.0, step=0.01)

    expected_axis = incision_axis

    sia_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    errors = {val: vector_difference_magnitude(actual_mag, actual_axis, val, incision_axis) for val in sia_values}

    least_sia = min(errors, key=errors.get)
    most_sia = max(errors, key=errors.get)

    st.subheader("SIA Error Table")
    for val, err in errors.items():
        st.write(f"SIA {val:.1f} D: Error = {err:.3f} D")
    st.markdown(f"**Least Error with SIA = {least_sia:.1f} D**", unsafe_allow_html=True)
    st.markdown(f"<span style='color:red'>**Most Error with SIA = {most_sia:.1f} D**</span>", unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(6, 6))
    iris_outer = plt.Circle((0, 0), 1.0, fill=True, color=(0.6, 0.4, 0.2, 0.3), ec='black', lw=2)
    pupil_inner = plt.Circle((0, 0), 0.85, fill=True, color=(1, 1, 0, 0.2), ec='black', lw=1)
    ax.add_artist(iris_outer)
    ax.add_artist(pupil_inner)
    ax.plot([-1, 1], [0, 0], linestyle=':', color='gray')
    ax.plot([0, 0], [-1, 1], linestyle=':', color='gray')

    def plot_vector(magnitude, axis_deg, color, label, style='-'):
        axis_rad = math.radians(axis_deg)
        x = magnitude * math.cos(axis_rad)
        y = magnitude * math.sin(axis_rad)
        ax.arrow(0, 0, x, y, head_width=0.05, head_length=0.1, fc=color, ec=color,
                 linestyle=style, linewidth=2, label=label)

    plot_vector(expected_mag, incision_axis, 'blue', f'Expected ({expected_mag}D @ {incision_axis}°)')
    plot_vector(actual_mag, actual_axis, 'green', f'Actual ({actual_mag}D @ {actual_axis}°)')
    error_vec = vector_difference_components(actual_mag, actual_axis, expected_mag, expected_axis)
    err_mag, err_axis = double_angle_to_polar(error_vec)
    plot_vector(err_mag, err_axis, 'red', f'Error ({err_mag:.3f}D @ {err_axis:.1f}°)', style='--')

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect('equal', adjustable='box')
    ax.legend(loc='upper right')
    ax.axis('off')

    st.pyplot(fig)

elif mode == "Batch Processing":
    st.title("SIA Error Calculator (Batch Processing)")

    # Provide a sample template for download
    template_df = pd.DataFrame({
        "INCISION LOCATION": [],
        "ACTUAL SIA MAGNITUDE": [],
        "ACTUAL SIA AXIS": []
    })
    template_buffer = BytesIO()
    with pd.ExcelWriter(template_buffer, engine="xlsxwriter") as writer:
        template_df.to_excel(writer, index=False)
    st.download_button(
        label="Download Sample Template",
        data=template_buffer.getvalue(),
        file_name="SIA_Batch_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    if uploaded_file is not None:
        # FIX: Specify engine for reliable reading on Streamlit Cloud
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        required_cols = ["INCISION LOCATION", "ACTUAL SIA MAGNITUDE", "ACTUAL SIA AXIS"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"Excel must contain columns: {required_cols}")
        else:
            sia_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
            for idx, row in df.iterrows():
                incision_axis = row['INCISION LOCATION']
                actual_mag = row['ACTUAL SIA MAGNITUDE']
                actual_axis = row['ACTUAL SIA AXIS']
                for val in sia_values:
                    col_name = f"SIA ERROR {val:.1f}".rstrip('0').rstrip('.') if val != 0 else "SIA ERROR 0"
                    error_val = vector_difference_magnitude(actual_mag, actual_axis, val, incision_axis)
                    df.at[idx, col_name] = round(error_val, 3)
            
            st.subheader("Calculated SIA Errors")
            st.dataframe(df)

            # Prepare file for download
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Results')
            st.download_button(label="Download Excel with SIA Errors",
                               data=output.getvalue(),
                               file_name="SIA_Errors_Filled.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
