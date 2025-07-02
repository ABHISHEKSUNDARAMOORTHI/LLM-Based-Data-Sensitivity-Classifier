# app.py

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import json
import logging

# Import project modules
from styling import apply_custom_css, theme_toggle_button
from utils import load_csv_from_bytes, create_session_summary_json
from features import upload_data_section, preview_data_section
from sensitivity_labels import SENSITIVITY_LEVELS, SENSITIVITY_GUIDANCE
from ai_logic import get_sensitivity_classification
from additional_features import generate_fake_data, test_mode_section, export_options_section, column_history_log_section, add_analysis_to_history
from visualizer import plot_sensitivity_distribution, plot_confidence_distribution # Import plotting functions

# Configure logging for the main app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables (for GEMINI_API_KEY)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="LLM-Based Data Sensitivity Classifier",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Apply Custom CSS ---
apply_custom_css()

# --- Session State Initialization ---
# Initialize session state variables if they don't exist
if 'uploaded_df' not in st.session_state:
    st.session_state.uploaded_df = None
if 'uploaded_filename' not in st.session_state:
    st.session_state.uploaded_filename = None
if 'input_type' not in st.session_state: # 'csv' or 'json'
    st.session_state.input_type = None
if 'column_metadata_for_ai' not in st.session_state:
    st.session_state.column_metadata_for_ai = []
if 'classification_results' not in st.session_state:
    st.session_state.classification_results = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = [] # For storing past analyses

# --- Sidebar Content ---
with st.sidebar:
    theme_toggle_button() # Theme toggle button
    st.markdown("---")
    upload_data_section() # Handles CSV/JSON upload
    st.markdown("---")
    test_mode_section() # Generate fake data for testing
    st.markdown("---")
    column_history_log_section() # Display analysis history

# --- Main Content Area ---
st.title("🔐 LLM-Based Data Sensitivity Classifier")
st.markdown("Automatically classify data column sensitivity using Google Gemini AI.")

# Display current loaded file info
if st.session_state.uploaded_filename:
    st.info(f"**Loaded File:** `{st.session_state.uploaded_filename}` (Type: `{st.session_state.input_type.upper() if st.session_state.input_type else 'N/A'}`)")
else:
    st.warning("No data loaded. Please upload a file or generate fake data in the sidebar.")

# Section for data preview and metadata editing
preview_data_section()

# Only show classification button if data is loaded and metadata is extracted
if st.session_state.uploaded_df is not None and st.session_state.column_metadata_for_ai:
    st.markdown("---")
    st.subheader("🚀 Run Sensitivity Classification")
    
    if st.button("Classify Data Sensitivity with Gemini AI"):
        with st.spinner("Classifying columns with Gemini AI... This may take a moment."):
            try:
                # Call AI logic to get classification results
                results = get_sensitivity_classification(
                    st.session_state.column_metadata_for_ai,
                    GEMINI_API_KEY
                )
                
                # Check if the result is an error message string or actual results
                if isinstance(results, list) and all(isinstance(item, dict) for item in results):
                    st.session_state.classification_results = results
                    st.success("Classification complete!")
                    # Add to history if successful
                    add_analysis_to_history(
                        st.session_state.uploaded_filename,
                        st.session_state.column_metadata_for_ai,
                        st.session_state.classification_results
                    )
                else:
                    # If results is not a list of dicts, it's an error message
                    st.error(f"Classification failed: {results[0]['reasoning'] if isinstance(results, list) and results else 'Unknown error.'}")
                    st.session_state.classification_results = None # Clear results on error
                    logging.error(f"Classification returned an error: {results}")

            except Exception as e:
                st.error(f"An unexpected error occurred during classification: {e}. Check terminal for details.")
                st.session_state.classification_results = None # Clear results on error
                logging.error(f"Unexpected error in main classification call: {e}", exc_info=True)
else:
    st.info("Upload data and ensure column metadata is extracted to enable classification.")


# --- Display Classification Results ---
if st.session_state.classification_results:
    st.markdown("---")
    st.header("Results: Data Sensitivity Classification")

    # Create tabs for detailed results and visualizations
    tab_table, tab_viz = st.tabs(["Detailed Table", "Visualizations"])

    with tab_table:
        st.subheader("Detailed Column Classification Table")
        # Convert results to DataFrame for better display
        results_df = pd.DataFrame(st.session_state.classification_results)
        
        # Reorder columns for display
        display_cols = ['column_name', 'sensitivity_level', 'confidence', 'reasoning']
        results_df = results_df[[col for col in display_cols if col in results_df.columns]]

        st.dataframe(results_df, use_container_width=True)

        st.markdown("---")
        st.subheader("Summary by Sensitivity Level")
        
        # Group by sensitivity level and count
        summary_counts = results_df['sensitivity_level'].value_counts().reset_index()
        summary_counts.columns = ['Sensitivity Level', 'Count']
        
        # Order by sensitivity levels as defined in sensitivity_labels.py
        summary_counts['Sensitivity Level'] = pd.Categorical(
            summary_counts['Sensitivity Level'], 
            categories=SENSITIVITY_LEVELS + ['Error', 'Blocked', 'Unknown'], # Include potential error states
            ordered=True
        )
        summary_counts = summary_counts.sort_values('Sensitivity Level').reset_index(drop=True)

        st.dataframe(summary_counts, use_container_width=True)

    with tab_viz:
        st.subheader("Visual Summary of Classification")

        # Plot Sensitivity Distribution
        st.markdown("#### Distribution of Sensitivity Levels")
        sensitivity_fig = plot_sensitivity_distribution(st.session_state.classification_results)
        if sensitivity_fig:
            st.plotly_chart(sensitivity_fig, use_container_width=True)
        else:
            st.warning("Could not generate sensitivity distribution chart.")

        st.markdown("---")

        # Plot Confidence Distribution
        st.markdown("#### Distribution of AI Confidence Scores")
        confidence_fig = plot_confidence_distribution(st.session_state.classification_results)
        if confidence_fig:
            st.plotly_chart(confidence_fig, use_container_width=True)
        else:
            st.warning("Could not generate confidence distribution chart.")

    st.markdown("---")
    export_options_section(
        st.session_state.uploaded_df,
        st.session_state.classification_results,
        st.session_state.column_metadata_for_ai,
        st.session_state.uploaded_filename
    )

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit, Faker, Pandas, Plotly, and Google Gemini AI.")
st.markdown("Project by Abhishek Sundaramoorthi")
