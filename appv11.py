
import pandas as pd
import streamlit as st

# Function to process SIA error calculation
def calculate_sia_error(incision_axis, actual_mag, actual_axis, assumed_mag=0.5):
    import math
    # Convert degrees to radians
    rad_incision = math.radians(incision_axis)
    rad_actual = math.radians(actual_axis)
    rad_assumed = math.radians(incision_axis)  # Expected flattening in incision direction
    
    # Decompose vectors
    ax_actual_x = actual_mag * math.cos(2 * rad_actual)
    ax_actual_y = actual_mag * math.sin(2 * rad_actual)
    
    ax_expected_x = assumed_mag * math.cos(2 * rad_assumed)
    ax_expected_y = assumed_mag * math.sin(2 * rad_assumed)
    
    # Error vector = actual - expected
    err_x = ax_actual_x - ax_expected_x
    err_y = ax_actual_y - ax_expected_y
    
    # Magnitude of error
    err_mag = math.sqrt(err_x**2 + err_y**2)
    return round(err_mag, 3)

st.title("SIA Error Calculator - Single & Batch Mode")

mode = st.radio("Select Mode", ["Single Case", "Batch Processing"])

if mode == "Single Case":
    incision_axis = st.number_input("Incision Axis (degrees)", 0, 180, 180)
    actual_mag = st.number_input("Actual SIA Magnitude", 0.0, 5.0, 0.5)
    actual_axis = st.number_input("Actual SIA Axis (degrees)", 0, 180, 90)
    assumed_mag = st.number_input("Assumed SIA Magnitude", 0.0, 5.0, 0.5)
    
    if st.button("Calculate"):
        result = calculate_sia_error(incision_axis, actual_mag, actual_axis, assumed_mag)
        st.success(f"SIA Error: {result} D")
        
else:
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
            # Expecting columns: Incision Axis, Actual SIA Magnitude, Actual SIA Axis, Assumed SIA Magnitude
            df["SIA Error"] = df.apply(lambda row: calculate_sia_error(
                row["Incision Axis"],
                row["Actual SIA Magnitude"],
                row["Actual SIA Axis"],
                row.get("Assumed SIA Magnitude", 0.5)
            ), axis=1)
            
            st.dataframe(df)
            
            # Download updated Excel
            out_file = "SIA_Errors_Output.xlsx"
            df.to_excel(out_file, index=False, engine="openpyxl")
            with open(out_file, "rb") as f:
                st.download_button("Download Output Excel", f, file_name=out_file)
        
        except Exception as e:
            st.error(f"Error processing file: {e}")

# Provide sample template for download
sample_template = pd.DataFrame({
    "Incision Axis": [180],
    "Actual SIA Magnitude": [0.5],
    "Actual SIA Axis": [90],
    "Assumed SIA Magnitude": [0.5]
})
sample_template.to_excel("SIA_Batch_Template.xlsx", index=False, engine="openpyxl")
with open("SIA_Batch_Template.xlsx", "rb") as f:
    st.download_button("Download Sample Template", f, file_name="SIA_Batch_Template.xlsx")
