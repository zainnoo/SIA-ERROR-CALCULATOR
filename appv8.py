
# appv8_toric.py - Streamlit app with Toric IOL Analyzer (placeholder)
import streamlit as st
import numpy as np

def cyl_to_j0_j45(cyl, axis):
    theta = np.deg2rad(2 * axis)
    J0 = -cyl / 2 * np.cos(theta)
    J45 = -cyl / 2 * np.sin(theta)
    return J0, J45

def j0_j45_to_cyl_axis(J0, J45):
    mag = 2 * np.sqrt(J0**2 + J45**2)
    angle = 0.5 * np.arctan2(J45, J0)
    axis = np.rad2deg(angle) % 180
    return mag, axis

st.title("SIA Error Calculator v8 with Toric IOL Analyzer")

# Inputs
post_cyl = st.number_input("Post-op Subjective Cylinder (D)", value=-0.25)
post_axis = st.number_input("Post-op Subjective Axis (°)", min_value=0, max_value=180, value=170)

expected_cyl = st.number_input("Expected Residual Cylinder from Planning (D)", value=-0.15)
expected_axis = st.number_input("Expected Residual Axis (°)", min_value=0, max_value=180, value=174)

# Convert both to vectors
J0_post, J45_post = cyl_to_j0_j45(post_cyl, post_axis)
J0_exp, J45_exp = cyl_to_j0_j45(expected_cyl, expected_axis)

# Compute vector error
delta_J0 = J0_post - J0_exp
delta_J45 = J45_post - J45_exp
error_mag, error_axis = j0_j45_to_cyl_axis(delta_J0, delta_J45)

# Outputs
st.subheader("Analysis Output")
st.write(f"**Vector Error Magnitude:** {error_mag:.2f} D")
st.write(f"**Vector Error Axis:** {error_axis:.1f}°")
