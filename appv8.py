
import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

# ===== Helper Functions =====
def to_double_angle_vector(magnitude, axis_deg):
    axis_rad = math.radians(2 * axis_deg)
    return np.array([magnitude * math.cos(axis_rad),
                     magnitude * math.sin(axis_rad)])

def vector_difference(mag1, axis1, mag2, axis2):
    vec1 = to_double_angle_vector(mag1, axis1)
    vec2 = to_double_angle_vector(mag2, axis2)
    diff_vec = vec1 - vec2
    return np.linalg.norm(diff_vec)

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
    errors[val] = vector_difference(actual_mag, actual_axis, val, incision_axis)

# Find least and most error
least_sia = min(errors, key=errors.get)
most_sia = max(errors, key=errors.get)

# Display results
st.subheader("SIA Error Table")
for val, err in errors.items():
    st.write(f"SIA {val:.1f} D: Error = {err:.3f} D")
st.markdown(f"**Least Error with SIA = {least_sia:.1f} D**", unsafe_allow_html=True)
st.markdown(f"<span style='color:red'>**Most Error with SIA = {most_sia:.1f} D**</span>", unsafe_allow_html=True)

# ===== Diagram =====
fig, ax = plt.subplots(figsize=(6, 6))

# Eye outer and inner circles
iris_outer = plt.Circle((0, 0), 1.0, fill=True, color=(0.6, 0.4, 0.2, 0.3), ec='black', lw=2)  # Brown iris with black border
pupil_inner = plt.Circle((0, 0), 0.85, fill=True, color=(1, 1, 0, 0.2), ec='black', lw=1)  # Light translucent yellow pupil
ax.add_artist(iris_outer)
ax.add_artist(pupil_inner)

# Reference dotted lines
ax.plot([-1, 1], [0, 0], linestyle=':', color='gray')
ax.plot([0, 0], [-1, 1], linestyle=':', color='gray')

# Function to plot arrow for axis
def plot_vector(magnitude, axis_deg, color, label, style='-'):
    # Convert to radians for single-angle plotting
    axis_rad = math.radians(axis_deg)
    x = magnitude * math.cos(axis_rad)
    y = magnitude * math.sin(axis_rad)
    ax.arrow(0, 0, x, y, head_width=0.05, head_length=0.1, fc=color, ec=color,
             linestyle=style, linewidth=2, label=label)

# Plot expected vector (along incision axis)
plot_vector(expected_mag, incision_axis, 'blue', f'Expected ({expected_mag}D @ {incision_axis}°)')

# Plot actual vector
plot_vector(actual_mag, actual_axis, 'green', f'Actual ({actual_mag}D @ {actual_axis}°)')

# Plot error vector
err_mag = vector_difference(actual_mag, actual_axis, expected_mag, expected_axis)
plot_vector(err_mag, actual_axis, 'red', f'Error ({err_mag:.3f}D)', style='--')

# Diagram settings
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_aspect('equal', adjustable='box')
ax.legend(loc='upper right')
ax.axis('off')

st.pyplot(fig)
