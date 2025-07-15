
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout='centered')
st.title("Surgically Induced Astigmatism (SIA) Error Calculator with Plot")

# Input section
col1, col2 = st.columns(2)
with col1:
    eye =     incision_axis = st.number_input("Incision Axis (degrees)", min_value=0.0, max_value=180.0, value=150.0)
    actual_sia_axis = st.number_input("Actual SIA Flattened Axis (degrees)", min_value=0.0, max_value=180.0, value=30.0)
    actual_sia_magnitude = st.number_input("Actual SIA Flattening Magnitude (D)", min_value=0.0, max_value=2.0, value=0.5)
with col2:
    expected_sia_axis = st.number_input(" (degrees)", min_value=0.0, max_value=180.0, value=150.0)
    expected_sia_magnitude = st.number_input("Expected SIA Flattening Magnitude (D)", min_value=0.0, max_value=2.0, value=0.3)

# Vector math function
def sia_vector(magnitude, axis_deg, eye):
    angle_rad = np.deg2rad(axis_deg if eye == "RE" else 180 - axis_deg)
    x = magnitude * np.cos(angle_rad)
    y = magnitude * np.sin(angle_rad)
    return x, y

actual_x, actual_y = sia_vector(actual_sia_magnitude, actual_sia_axis, eye)
errors = {}

for sia_input in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
    assumed_x, assumed_y = sia_vector(sia_input, incision_axis, eye)
    error = np.sqrt((actual_x - assumed_x)**2 + (actual_y - assumed_y)**2)
    errors[sia_input] = round(error, 3)

# Determine best and worst assumptions
min_error_val = min(errors.values())
max_error_val = max(errors.values())
best_sia = [k for k, v in errors.items() if v == min_error_val][0]
worst_sia = [k for k, v in errors.items() if v == max_error_val][0]

# Display error table
st.subheader("SIA Error Table")
df = pd.DataFrame(list(errors.items()), columns=["Assumed SIA (D)", "SIA Error"])
st.dataframe(df, use_container_width=True)

# Highlight best and worst
st.markdown(f"✅ **Least SIA error if SIA taken as: {best_sia} D**", unsafe_allow_html=True)
st.markdown(f"❌ <span style='color:red'>Most SIA error if SIA taken as: {worst_sia} D</span>", unsafe_allow_html=True)

# Plotting the eye diagram
def polar_to_cartesian(mag, axis_deg, eye):
    angle = np.deg2rad(axis_deg if eye == "RE" else 180 - axis_deg)
    x = mag * np.cos(angle)
    y = mag * np.sin(angle)
    return x, y

# Vector base and tip
x_exp_tip, y_exp_tip = polar_to_cartesian(expected_sia_magnitude, expected_sia_axis, eye)
x_act_tip, y_act_tip = polar_to_cartesian(actual_sia_magnitude, actual_sia_axis, eye)
x_exp_base, y_exp_base = -x_exp_tip, -y_exp_tip
x_act_base, y_act_base = -x_act_tip, -y_act_tip
x_err_vec = [x_exp_base, x_act_base]
y_err_vec = [y_exp_base, y_act_base]

limbus_radius = 1.0
pupil_radius = 0.85
iris_radius = 0.95

x_inc, y_inc = polar_to_cartesian(limbus_radius, incision_axis, eye)
label_x, label_y = polar_to_cartesian(limbus_radius + 0.1, incision_axis, eye)

fig, ax = plt.subplots(figsize=(7, 7))
ax.set_aspect('equal')
ax.set_xlim(-1.3, 1.3)
ax.set_ylim(-1.3, 1.3)
ax.axis('off')

iris_ring = plt.Circle((0, 0), iris_radius, color='saddlebrown', fill=True, alpha=0.3)
outer_circle = plt.Circle((0, 0), limbus_radius, color='black', fill=False, linewidth=2)
pupil_circle = plt.Circle((0, 0), pupil_radius, edgecolor='black', facecolor='gold', linewidth=1.5, alpha=0.4)
ax.add_artist(iris_ring)
ax.add_artist(outer_circle)
ax.add_artist(pupil_circle)

ax.plot([-1.2, 1.2], [0, 0], linestyle='--', color='gray')
ax.plot([0, 0], [-1.2, 1.2], linestyle='--', color='gray')

ax.plot(x_inc, y_inc, marker='*', markersize=18, color='red', label='Incision')
ax.text(label_x, label_y, f"Incision @ {incision_axis}°", ha='center', va='center', fontsize=10, color='red')

ax.arrow(x_exp_base, y_exp_base, -x_exp_base, -y_exp_base, color='blue', width=0.01, length_includes_head=True, label='Expected SIA')
ax.arrow(x_act_base, y_act_base, -x_act_base, -y_act_base, color='green', width=0.01, length_includes_head=True, label='Actual SIA')
ax.plot(x_err_vec, y_err_vec, color='red', linestyle='--', linewidth=2, label='Error Vector')

ax.text(x_exp_base * 1.1, y_exp_base * 1.1, 'Expected', color='blue', fontsize=10)
ax.text(x_act_base * 1.1, y_act_base * 1.1, 'Actual', color='green', fontsize=10)

ax.set_title(f"SIA Vector Plot ({eye})", fontsize=14)
ax.legend(loc='lower left')
st.pyplot(fig)
