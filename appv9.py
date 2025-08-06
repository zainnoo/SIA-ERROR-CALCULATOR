
import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

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

# ===== Streamlit UI =====
st.title("SIA Error Calculator (App v8 - RE Orientation)")

# Inputs
incision_axis = st.number_input("Incision Axis (degrees)", min_value=0.0, max_value=180.0, value=0.0)
expected_mag = st.number_input("Expected SIA Flattening Magnitude (D)", min_value=0.0, value=0.0, step=0.01)
actual_axis = st.number_input("Actual SIA Flattening Axis (degrees)", min_value=0.0, max_value=180.0, value=0.0)
actual_mag = st.number_input("Actual SIA Flattening Magnitude (D)", min_value=0.0, value=0.0, step=0.01)

# Expected axis = incision axis
expected_axis = incision_axis

# Calculate SIA error for multiple assumed SIA values
sia_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
errors = {}
for val in sia_values:
    errors[val] = vector_difference_magnitude(actual_mag, actual_axis, val, incision_axis)

# Find least and most error
least_sia = min(errors, key=errors.get)
most_sia = max(errors, key=errors.get)

# Display results - table view
st.subheader("SIA Error Table")
for val, err in errors.items():
    st.write(f"SIA {val:.1f} D: Error = {err:.3f} D")
st.markdown(f"**Least Error with SIA = {least_sia:.1f} D**", unsafe_allow_html=True)
st.markdown(f"<span style='color:red'>**Most Error with SIA = {most_sia:.1f} D**</span>", unsafe_allow_html=True)

# Copy-friendly box
copy_text = "SIA Value	Error (D)\n"
for val, err in errors.items():
    copy_text += f"{val:.1f}	{err:.3f}\n"
st.text_area("Copy errors for Excel:", value=copy_text, height=150)

# ===== Diagram =====
fig, ax = plt.subplots(figsize=(6, 6))

# Eye outer and inner circles
iris_outer = plt.Circle((0, 0), 1.0, fill=True, color=(0.6, 0.4, 0.2, 0.3), ec='black', lw=2)
pupil_inner = plt.Circle((0, 0), 0.85, fill=True, color=(1, 1, 0, 0.2), ec='black', lw=1)
ax.add_artist(iris_outer)
ax.add_artist(pupil_inner)

# Reference dotted lines
ax.plot([-1, 1], [0, 0], linestyle=':', color='gray')
ax.plot([0, 0], [-1, 1], linestyle=':', color='gray')

# Function to plot arrow for axis
def plot_vector(magnitude, axis_deg, color, label, style='-'):
    axis_rad = math.radians(axis_deg)
    x = magnitude * math.cos(axis_rad)
    y = magnitude * math.sin(axis_rad)
    ax.arrow(0, 0, x, y, head_width=0.05, head_length=0.1, fc=color, ec=color,
             linestyle=style, linewidth=2, label=label)

# Plot expected vector
plot_vector(expected_mag, incision_axis, 'blue', f'Expected ({expected_mag}D @ {incision_axis}°)')

# Plot actual vector
plot_vector(actual_mag, actual_axis, 'green', f'Actual ({actual_mag}D @ {actual_axis}°)')

# Plot error vector (true vector difference)
error_vec = vector_difference_components(actual_mag, actual_axis, expected_mag, expected_axis)
err_mag, err_axis = double_angle_to_polar(error_vec)
plot_vector(err_mag, err_axis, 'red', f'Error ({err_mag:.3f}D @ {err_axis:.1f}°)', style='--')

# Diagram settings
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_aspect('equal', adjustable='box')
ax.legend(loc='upper right')
ax.axis('off')

st.pyplot(fig)
