import streamlit as st
from urllib.parse import unquote
import json

st.title("Patient Data from Chrome Extension")

# Get query parameters
query_params = st.experimental_get_query_params()
data_str = query_params.get("data", [None])[0]

if data_str:
    try:
        # Debug: Show raw data before processing
        st.write("Raw data string:", data_str)
        
        decoded_data = unquote(data_str)
        data = json.loads(decoded_data)
        
        # Display patient information
        st.header("Patient Information")
        st.write(f"**Patient ID:** {data.get('patientId', 'N/A')}")
        st.write(f"**Patient Name:** {data.get('patientName', 'N/A')}")
        st.write(f"**Species:** {data.get('species', 'N/A')}")
        st.write(f"**Breed:** {data.get('breed', 'N/A')}")
        st.write(f"**Gender:** {data.get('gender', 'N/A')}")
        st.write(f"**Weight:** {data.get('weight', 'N/A')}")
        st.write(f"**Age:** {data.get('age', 'N/A')}")
        st.write(f"**Date of Birth:** {data.get('dateOfBirth', 'N/A')}")
        
        st.header("Clinical Findings")
        st.write(data.get('clinicalFindings', 'No findings available'))
        
        st.header("Report Findings")
        st.write(data.get('reportFindings', 'No findings available'))
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        st.json(data_str)  # Show raw data for debugging
else:
    st.info("No data received. Use the Chrome Extension to send data.")