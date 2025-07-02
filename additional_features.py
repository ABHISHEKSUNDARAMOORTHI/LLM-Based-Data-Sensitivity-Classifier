# additional_features.py

import streamlit as st
import pandas as pd
import json
from faker import Faker
import random
import io
from datetime import datetime
import logging # Added this import

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import utility functions
from utils import convert_numpy_types, create_session_summary_json

# Initialize Faker for generating fake data
fake = Faker()

def generate_fake_data(num_rows=100):
    """
    Generates a Pandas DataFrame with fake data for testing purposes,
    including columns that represent different sensitivity levels.
    """
    data = {
        "user_id": [i for i in range(1, num_rows + 1)],
        "first_name": [fake.first_name() for _ in range(num_rows)],
        "last_name": [fake.last_name() for _ in range(num_rows)],
        "email_address": [fake.email() for _ in range(num_rows)],
        "phone_number": [fake.phone_number() for _ in range(num_rows)],
        "street_address": [fake.address() for _ in range(num_rows)],
        "date_of_birth": [fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat() for _ in range(num_rows)],
        "credit_card_number_masked": [fake.credit_card_number(card_type=None)[-4:].rjust(16, '*') for _ in range(num_rows)],
        "revenue_usd": [round(random.uniform(1000.0, 100000.0), 2) for _ in range(num_rows)],
        "employee_id": [f"EMP-{1000 + i}" for i in range(num_rows)],
        "department": [random.choice(["Sales", "Marketing", "Engineering", "HR", "Finance"]) for _ in range(num_rows)],
        "product_code": [f"PROD-{random.randint(100, 999)}" for _ in range(num_rows)],
        "ip_address": [fake.ipv4() for _ in range(num_rows)],
        "internal_project_id": [f"INTPROJ-{random.randint(1, 5)}" for _ in range(num_rows)],
        "customer_segment": [random.choice(["Gold", "Silver", "Bronze"]) for _ in range(num_rows)],
        "is_active_customer": [random.choice([True, False]) for _ in range(num_rows)],
        "transaction_id": [fake.uuid4() for _ in range(num_rows)],
        "bank_account_last_4": [str(random.randint(1000, 9999)) for _ in range(num_rows)],
        "social_security_number_masked": [f"***-**-{random.randint(1000, 9999)}" for _ in range(num_rows)]
    }
    df = pd.DataFrame(data)
    return df

def test_mode_section():
    """
    Provides a section in the sidebar to generate fake data for testing.
    """
    st.header("🧪 Test Mode")
    st.info("Generate a synthetic dataset with various sensitive columns for quick testing.")
    
    num_rows = st.slider("Number of rows for fake data:", min_value=10, max_value=1000, value=100, step=10)
    
    if st.button(f"Generate {num_rows} Rows of Fake Data"):
        st.session_state.uploaded_df = generate_fake_data(num_rows)
        st.session_state.uploaded_filename = f"fake_data_{num_rows}_rows.csv"
        st.session_state.input_type = 'csv'
        st.session_state.classification_results = None # Clear previous results
        st.session_state.column_metadata_for_ai = [] # Clear previous metadata
        st.success(f"Generated {num_rows} rows of fake data!")
        st.rerun() # Rerun to update the main content area with the new data


def export_options_section(uploaded_df, classification_results, column_metadata_for_ai, uploaded_filename):
    """
    Provides options to export the classification results.
    """
    st.header("📤 Export Options")
    
    if uploaded_df is None or classification_results is None:
        st.info("Upload data and run classification to enable export options.")
        return

    st.subheader("Download Classified Data")

    # 1. Export as Annotated CSV
    if st.button("Download as Annotated CSV"):
        # Create a copy to avoid modifying the original DataFrame in session state
        df_export = uploaded_df.copy()
        
        # Create new columns for sensitivity level, confidence, and reasoning
        df_export['sensitivity_level'] = None
        df_export['confidence'] = None
        df_export['reasoning'] = None

        # Populate these columns based on classification results
        for col_result in classification_results:
            col_name = col_result.get('column_name')
            if col_name in df_export.columns:
                df_export['sensitivity_level'] = df_export['sensitivity_level'].mask(df_export.columns == col_name, col_result.get('sensitivity_level'))
                df_export['confidence'] = df_export['confidence'].mask(df_export.columns == col_name, col_result.get('confidence'))
                df_export['reasoning'] = df_export['reasoning'].mask(df_export.columns == col_name, col_result.get('reasoning'))
        
        # Convert DataFrame to CSV bytes
        csv_buffer = io.StringIO()
        df_export.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
        
        st.download_button(
            label="Download Annotated CSV",
            data=csv_bytes,
            file_name=f"classified_{uploaded_filename}",
            mime="text/csv",
            key="download_annotated_csv"
        )
        st.success("Annotated CSV ready for download!")

    # 2. Export as JSON Report
    if st.button("Download as JSON Report"):
        # Create a comprehensive JSON report
        json_report = {
            "timestamp": datetime.now().isoformat(),
            "original_filename": uploaded_filename,
            "column_metadata_sent_to_ai": column_metadata_for_ai,
            "classification_results": classification_results,
            "summary": {
                "total_columns": len(classification_results),
                "sensitive_columns_count": len([c for c in classification_results if c['sensitivity_level'] in ['PII', 'Finance-critical', 'Confidential']]),
                "public_columns_count": len([c for c in classification_results if c['sensitivity_level'] == 'Public']),
                "internal_columns_count": len([c for c in classification_results if c['sensitivity_level'] == 'Internal'])
            }
        }
        
        # Ensure the JSON report is fully serializable (though convert_numpy_types should handle most)
        json_report_cleaned = convert_numpy_types(json_report)

        json_string = json.dumps(json_report_cleaned, indent=4)
        
        st.download_button(
            label="Download JSON Report",
            data=json_string,
            file_name=f"classification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            key="download_json_report"
        )
        st.success("JSON report ready for download!")

    # 3. Export as Markdown Report
    if st.button("Download as Markdown Report"):
        markdown_content = f"# Data Sensitivity Classification Report\n\n"
        markdown_content += f"**Generated On:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        markdown_content += f"**Original File:** `{uploaded_filename}`\n\n"
        
        markdown_content += "## 📊 Classification Summary\n\n"
        markdown_content += "| Sensitivity Level | Count |\n"
        markdown_content += "|-------------------|-------|\n"
        
        level_counts = pd.DataFrame(classification_results)['sensitivity_level'].value_counts().to_dict()
        for level in ['PII', 'Finance-critical', 'Confidential', 'Internal', 'Public', 'Error', 'Blocked']:
            if level in level_counts:
                markdown_content += f"| {level} | {level_counts[level]} |\n"
            else:
                markdown_content += f"| {level} | 0 |\n"
        markdown_content += "\n"

        markdown_content += "## 📈 Detailed Column Classification\n\n"
        for col_result in classification_results:
            col_name = col_result.get('column_name', 'N/A')
            sensitivity = col_result.get('sensitivity_level', 'Unknown')
            confidence = col_result.get('confidence', 'N/A')
            reasoning = col_result.get('reasoning', 'No reasoning provided.')
            
            markdown_content += f"### Column: `{col_name}`\n"
            markdown_content += f"- **Sensitivity Level:** `{sensitivity}`\n"
            markdown_content += f"- **Confidence:** `{confidence}/5`\n"
            markdown_content += f"- **Reasoning:** {reasoning}\n\n"
        
        st.download_button(
            label="Download Markdown Report",
            data=markdown_content,
            file_name=f"classification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            key="download_markdown_report"
        )
        st.success("Markdown report ready for download!")


def column_history_log_section():
    """
    Displays a history of the last few analysis sessions.
    Stored in st.session_state.
    """
    st.header("📚 Analysis History")
    
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    if not st.session_state.analysis_history:
        st.info("No analysis history yet. Run a classification to see it here.")
        return

    with st.expander("View Recent Analyses", expanded=False):
        for i, analysis in enumerate(reversed(st.session_state.analysis_history)): # Show most recent first
            timestamp = analysis.get('timestamp', 'N/A')
            filename = analysis.get('original_filename', 'N/A')
            
            st.markdown(f"**Analysis {len(st.session_state.analysis_history) - i}**: `{filename}` ({timestamp})")
            
            # Display a summary table for each history item
            if 'classification_results' in analysis and analysis['classification_results']:
                history_df = pd.DataFrame(analysis['classification_results'])
                # Reorder columns for better readability if present
                display_cols = ['column_name', 'sensitivity_level', 'confidence', 'reasoning']
                history_df = history_df[[col for col in display_cols if col in history_df.columns]]
                st.dataframe(history_df, use_container_width=True)
            else:
                st.info("No classification results for this historical entry.")
            st.markdown("---")

    if st.button("Clear History"):
        st.session_state.analysis_history = []
        st.success("Analysis history cleared!")
        st.rerun()

def add_analysis_to_history(uploaded_filename, column_metadata_for_ai, classification_results):
    """
    Adds the current analysis results to the session history.
    Limits history to the last 5 entries.
    """
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []

    current_analysis = {
        "timestamp": datetime.now().isoformat(),
        "original_filename": uploaded_filename,
        "column_metadata_sent_to_ai": column_metadata_for_ai,
        "classification_results": classification_results
    }
    
    # Ensure the entry itself is JSON serializable before adding to history
    # This is important because session_state might try to pickle/serialize it
    cleaned_analysis = convert_numpy_types(current_analysis)

    st.session_state.analysis_history.append(cleaned_analysis)
    
    # Keep only the last 5 analyses to prevent session state from growing too large
    if len(st.session_state.analysis_history) > 5:
        st.session_state.analysis_history = st.session_state.analysis_history[-5:]
    
    logging.info(f"Added analysis for '{uploaded_filename}' to history. History size: {len(st.session_state.analysis_history)}")


# Example Usage (for direct testing of this file)
if __name__ == '__main__':
    st.set_page_config(layout="wide")
    st.title("Additional Features Module Test")

    # Initialize session state variables needed for testing
    if 'uploaded_df' not in st.session_state:
        st.session_state.uploaded_df = None
    if 'uploaded_filename' not in st.session_state:
        st.session_state.uploaded_filename = "test_file.csv"
    if 'classification_results' not in st.session_state:
        st.session_state.classification_results = None
    if 'column_metadata_for_ai' not in st.session_state:
        st.session_state.column_metadata_for_ai = []
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []

    # --- Test Mode Section ---
    with st.sidebar:
        test_mode_section()
        st.markdown("---")

    # --- Simulate Data for Export/History Testing ---
    if st.session_state.uploaded_df is None:
        st.info("Click 'Generate Fake Data' in the sidebar to populate data for testing export and history.")
        st.stop() # Stop execution if no data is present for main features

    st.subheader("Simulated Data for Classification")
    st.dataframe(st.session_state.uploaded_df.head())
    st.write(f"Filename: `{st.session_state.uploaded_filename}`")

    # --- Simulate Classification Results for Export/History Testing ---
    if st.session_state.classification_results is None:
        st.markdown("### Simulate Classification Results")
        if st.button("Simulate Classification Results"):
            # Create dummy classification results based on fake data columns
            dummy_results = []
            for col in st.session_state.uploaded_df.columns:
                level = "Public"
                reason = "General data."
                confidence = 3
                if "email" in col or "phone" in col or "address" in col or "ssn" in col or "name" in col or "birth" in col:
                    level = "PII"
                    reason = "Contains personally identifiable information."
                    confidence = 5
                elif "credit_card" in col or "revenue" in col or "bank_account" in col:
                    level = "Finance-critical"
                    reason = "Financial transaction data."
                    confidence = 5
                elif "internal" in col or "employee" in col or "project" in col:
                    level = "Internal"
                    reason = "Internal business data."
                    confidence = 4
                
                dummy_results.append({
                    "column_name": col,
                    "sensitivity_level": level,
                    "confidence": confidence,
                    "reasoning": reason
                })
            st.session_state.classification_results = dummy_results
            
            # Also simulate metadata for AI
            st.session_state.column_metadata_for_ai = [
                {"name": col, "type": str(st.session_state.uploaded_df[col].dtype), "sample_values": [str(st.session_state.uploaded_df[col].iloc[0]), str(st.session_state.uploaded_df[col].iloc[1])]}
                for col in st.session_state.uploaded_df.columns
            ]
            st.success("Simulated classification results!")
            st.rerun() # Rerun to enable export options

    if st.session_state.classification_results:
        st.subheader("Simulated Classification Results Table")
        st.dataframe(pd.DataFrame(st.session_state.classification_results), use_container_width=True)
        
        # --- Export Options Section ---
        export_options_section(
            st.session_state.uploaded_df,
            st.session_state.classification_results,
            st.session_state.column_metadata_for_ai,
            st.session_state.uploaded_filename
        )

        # --- Add to History ---
        if st.button("Add Current Analysis to History"):
            add_analysis_to_history(
                st.session_state.uploaded_filename,
                st.session_state.column_metadata_for_ai,
                st.session_state.classification_results
            )
            st.success("Analysis added to history!")
            st.rerun() # Rerun to update history display

        # --- History Log Section ---
        column_history_log_section()
