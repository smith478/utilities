import streamlit as st
from urllib.parse import unquote
import json

st.title("Patient Data from Chrome Extension")

# Get query parameters
query_params = st.experimental_get_query_params()
data_str = query_params.get("data", [None])[0]

if data_str:
    try:
        # Decode and parse data
        data_str = unquote(data_str)
        data = json.loads(data_str)
        
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
        
        # Clinical Findings
        st.header("Clinical Findings")
        st.write(data.get('clinicalFindings', 'No findings available'))
        
        # Report Findings
        st.header("Report Findings")
        st.write(data.get('reportFindings', 'No findings available'))
        
    except json.JSONDecodeError:
        st.error("Invalid data format received")
else:
    st.info("No data received. Use the Chrome Extension to send data.")