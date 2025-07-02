# features.py

import streamlit as st
import pandas as pd
import io
import json
import logging

# Import utility functions
from utils import load_csv_from_bytes, convert_numpy_types

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def upload_data_section():
    """
    Handles the data upload section in the Streamlit sidebar.
    Allows uploading CSV or JSON (for schema).
    Stores uploaded data and filenames in session state.
    """
    st.header("📥 Upload Data")
    st.info("Upload a CSV file or a JSON schema to classify its column sensitivity.")

    # File uploader for CSV
    uploaded_csv_file = st.file_uploader("Upload CSV File", type=["csv"], key="csv_uploader")
    
    if uploaded_csv_file is not None:
        try:
            df = load_csv_from_bytes(uploaded_csv_file.getvalue())
            st.session_state.uploaded_df = df
            st.session_state.uploaded_filename = uploaded_csv_file.name
            st.session_state.input_type = 'csv'
            st.success(f"CSV file '{uploaded_csv_file.name}' loaded successfully!")
            logging.info(f"CSV '{uploaded_csv_file.name}' loaded. Shape: {df.shape}")
        except Exception as e:
            st.error(f"Error loading CSV file: {e}. Please ensure it's a valid CSV.")
            st.session_state.uploaded_df = None
            st.session_state.uploaded_filename = None
            st.session_state.input_type = None
            logging.error(f"Failed to load CSV: {e}")

    st.markdown("---")
    st.info("Alternatively, paste or upload a JSON schema for classification.")
    
    # Text area for JSON schema input
    json_schema_input = st.text_area("Paste JSON Schema (Optional)", height=200, key="json_schema_input")
    
    # File uploader for JSON schema
    uploaded_json_file = st.file_uploader("Upload JSON Schema File (Optional)", type=["json"], key="json_uploader")

    json_data = None
    if uploaded_json_file is not None:
        try:
            json_data = json.load(uploaded_json_file)
            st.session_state.uploaded_filename = uploaded_json_file.name
            st.session_state.input_type = 'json'
            st.success(f"JSON schema file '{uploaded_json_file.name}' loaded successfully!")
            logging.info(f"JSON schema '{uploaded_json_file.name}' loaded.")
        except Exception as e:
            st.error(f"Error loading JSON schema file: {e}. Please ensure it's a valid JSON.")
            st.session_state.uploaded_filename = None
            st.session_state.input_type = None
            logging.error(f"Failed to load JSON: {e}")
    elif json_schema_input:
        try:
            json_data = json.loads(json_schema_input)
            st.session_state.uploaded_filename = "Pasted JSON Schema"
            st.session_state.input_type = 'json'
            st.success("JSON schema pasted successfully!")
            logging.info("JSON schema pasted.")
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {e}. Please check your JSON syntax.")
            st.session_state.uploaded_filename = None
            st.session_state.input_type = None
            logging.error(f"Invalid JSON pasted: {e}")
    
    # If JSON data is loaded/pasted, process it into a DataFrame-like structure for preview
    if json_data:
        # Assuming JSON schema might be a list of column definitions or a dict with a 'columns' key
        if isinstance(json_data, list):
            columns_info = json_data
        elif isinstance(json_data, dict) and 'columns' in json_data and isinstance(json_data['columns'], list):
            columns_info = json_data['columns']
        else:
            st.warning("JSON format not recognized. Expected a list of column definitions or a dict with a 'columns' key.")
            st.session_state.uploaded_df = None
            return

        # Create a mock DataFrame for preview from JSON schema
        mock_data = {}
        for col_def in columns_info:
            col_name = col_def.get('name')
            col_type = col_def.get('type')
            sample_values = col_def.get('sample_values', [])
            
            if col_name:
                # Use sample values or generate placeholders for preview
                if sample_values:
                    mock_data[col_name] = sample_values
                else:
                    # Generate simple placeholders based on type
                    if col_type == 'integer':
                        mock_data[col_name] = [1, 2]
                    elif col_type == 'float':
                        mock_data[col_name] = [1.0, 2.0]
                    elif col_type == 'boolean':
                        mock_data[col_name] = [True, False]
                    else: # Default to string
                        mock_data[col_name] = ["sample_val_1", "sample_val_2"]
        
        if mock_data:
            # Ensure all lists in mock_data are of the same length for DataFrame creation
            max_len = max(len(v) for v in mock_data.values()) if mock_data else 0
            for k in mock_data:
                while len(mock_data[k]) < max_len:
                    mock_data[k].append(None) # Pad with None
            
            st.session_state.uploaded_df = pd.DataFrame(mock_data)
        else:
            st.session_state.uploaded_df = None
            st.warning("No valid column definitions found in the JSON schema.")


def preview_data_section():
    """
    Displays a preview of the uploaded data (CSV or JSON-derived DataFrame)
    and allows for editing sample values.
    """
    if st.session_state.get('uploaded_df') is not None:
        st.subheader(f"🔍 Data Preview: `{st.session_state.uploaded_filename}`")
        st.write(f"Shape: {st.session_state.uploaded_df.shape}")
        st.dataframe(st.session_state.uploaded_df.head(), use_container_width=True)

        st.markdown("---")
        st.subheader("⚙️ Column Metadata for AI Classification")
        st.info("Review and optionally edit the sample values that will be sent to Gemini for classification. Providing relevant samples greatly improves accuracy.")

        column_metadata = []
        for col in st.session_state.uploaded_df.columns:
            col_type = str(st.session_state.uploaded_df[col].dtype)
            # Get up to 5 unique non-null sample values
            sample_values = st.session_state.uploaded_df[col].dropna().unique().tolist()
            # Convert numpy types in sample_values for JSON serialization
            sample_values = convert_numpy_types(sample_values)
            
            # Limit to 5 samples to save tokens
            limited_samples = sample_values[:5]

            # Allow user to edit/confirm samples
            with st.expander(f"Column: `{col}` (Type: `{col_type}`)", expanded=False):
                st.write(f"Inferred Type: `{col_type}`")
                
                # Display current samples as a string for editing
                current_samples_str = json.dumps(limited_samples)
                edited_samples_str = st.text_input(
                    f"Sample values for `{col}` (JSON array):",
                    value=current_samples_str,
                    key=f"sample_values_edit_{col}"
                )
                
                # Attempt to parse edited samples
                parsed_samples = []
                try:
                    parsed_samples = json.loads(edited_samples_str)
                    if not isinstance(parsed_samples, list):
                        st.error("Sample values must be a valid JSON array (e.g., [\"val1\", \"val2\"]).")
                        parsed_samples = [] # Reset to empty if invalid
                except json.JSONDecodeError:
                    st.error("Invalid JSON format for sample values. Please use a valid JSON array.")
                    parsed_samples = [] # Reset to empty if invalid
                
                # Store the potentially edited samples
                column_metadata.append({
                    "name": col,
                    "type": col_type,
                    "sample_values": parsed_samples[:5] # Ensure only up to 5 edited samples are kept
                })
        
        st.session_state.column_metadata_for_ai = column_metadata
        logging.info(f"Prepared metadata for AI for {len(column_metadata)} columns.")

    else:
        st.info("Upload a CSV file or provide a JSON schema in the sidebar to see a preview and configure column metadata.")


# Example Usage (for direct testing of this file)
if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.title("Features Module Test")

    # Initialize session state for testing
    if 'uploaded_df' not in st.session_state:
        st.session_state.uploaded_df = None
    if 'uploaded_filename' not in st.session_state:
        st.session_state.uploaded_filename = None
    if 'input_type' not in st.session_state:
        st.session_state.input_type = None
    if 'column_metadata_for_ai' not in st.session_state:
        st.session_state.column_metadata_for_ai = []

    # Apply styling (assuming styling.py exists and works)
    # from styling import apply_custom_css, theme_toggle_button
    # apply_custom_css()
    # theme_toggle_button()

    st.sidebar.write("---")
    upload_data_section()
    st.sidebar.write("---")

    st.write("---")
    preview_data_section()

    st.write("---")
    st.subheader("Final Metadata Sent to AI (for testing)")
    if st.session_state.column_metadata_for_ai:
        st.json(st.session_state.column_metadata_for_ai)
    else:
        st.write("No metadata generated yet.")

    # Simulate a CSV upload for testing purposes
    st.markdown("### Simulate CSV Upload for Testing")
    test_csv_content = """
name,age,email,salary,product_id,is_active
Alice,30,alice@example.com,60000,P101,True
Bob,24,bob.s@domain.com,45000,P102,False
Charlie,35,charlie@web.org,75000,P103,True
David,29,david@mail.net,50000,P104,False
Eve,40,eve@test.com,90000,P105,True
"""
    if st.button("Simulate CSV Upload"):
        st.session_state.uploaded_df = pd.read_csv(io.StringIO(test_csv_content))
        st.session_state.uploaded_filename = "simulated_data.csv"
        st.session_state.input_type = 'csv'
        st.rerun()

    st.markdown("### Simulate JSON Schema Upload for Testing")
    test_json_schema = """
[
  {"name": "customer_name", "type": "string", "sample_values": ["John Doe", "Jane Smith"]},
  {"name": "order_value", "type": "float", "sample_values": [123.45, 99.99]},
  {"name": "is_vip", "type": "boolean", "sample_values": [true, false]},
  {"name": "internal_id", "type": "integer"}
]
"""
    if st.button("Simulate JSON Schema Upload"):
        st.session_state.uploaded_df = None # Clear CSV
        st.session_state.uploaded_filename = "simulated_schema.json"
        st.session_state.input_type = 'json'
        try:
            json_data = json.loads(test_json_schema)
            # Manually process JSON data into a mock DataFrame for preview
            mock_data = {}
            for col_def in json_data:
                col_name = col_def.get('name')
                sample_values = col_def.get('sample_values', [])
                mock_data[col_name] = sample_values if sample_values else ["placeholder"] * 2
            
            # Ensure all lists are same length for DataFrame
            max_len = max(len(v) for v in mock_data.values()) if mock_data else 0
            for k in mock_data:
                while len(mock_data[k]) < max_len:
                    mock_data[k].append(None)
            
            st.session_state.uploaded_df = pd.DataFrame(mock_data)
            st.rerun()
        except Exception as e:
            st.error(f"Error simulating JSON: {e}")

