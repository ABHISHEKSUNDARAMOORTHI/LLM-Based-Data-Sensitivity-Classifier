# utils.py

import json
import logging
import time
from datetime import datetime
import numpy as np
import pandas as pd
import io
import functools # Import functools for @wraps

# Configure logging for the utility functions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def retry_with_exponential_backoff(max_retries=5, initial_delay=1.0, exceptions=(Exception,)):
    """
    A decorator factory to retry a function with exponential backoff on specified exceptions.

    Args:
        max_retries (int): Maximum number of retries.
        initial_delay (float): Initial delay in seconds before the first retry.
        exceptions (tuple): A tuple of exception types to catch and retry on.

    Returns:
        callable: A decorator that can be applied to a function.
    """
    def decorator(func):
        @functools.wraps(func) # Preserves func's metadata (name, docstring)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logging.warning(f"Attempt {i + 1}/{max_retries} failed for {func.__name__}: {e}")
                    if i < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2 # Exponential backoff
                    else:
                        logging.error(f"Function {func.__name__} failed after {max_retries} retries.")
                        raise # Re-raise the last exception if all retries fail
        return wrapper
    return decorator # This is the key: return the inner decorator function

def convert_numpy_types(obj):
    """
    Recursively converts NumPy-specific types (like np.integer, np.floating, np.bool_)
    within a dictionary or list to standard Python types for JSON serialization.
    This is crucial for ensuring data can be safely dumped to JSON.
    """
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(elem) for elem in obj]
    # Handle all NumPy integer types
    elif isinstance(obj, np.integer):
        return int(obj)
    # Handle all NumPy floating types
    elif isinstance(obj, np.floating):
        return float(obj)
    # Handle NumPy boolean type
    elif isinstance(obj, np.bool_):
        return bool(obj)
    # Handle NumPy arrays by converting them to Python lists
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    # Handle Pandas Timestamp objects (often found in datetime columns)
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat() # Convert to ISO 8601 string
    else:
        return obj

def load_csv_from_bytes(uploaded_file_bytes):
    """
    Loads a CSV file from bytes into a Pandas DataFrame.
    This function is used by Streamlit's file_uploader.

    Args:
        uploaded_file_bytes (bytes): The byte content of the uploaded CSV file.

    Returns:
        pd.DataFrame: The loaded DataFrame.
    """
    try:
        df = pd.read_csv(io.BytesIO(uploaded_file_bytes))
        logging.info(f"CSV loaded successfully. Shape: {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Error loading CSV from bytes: {e}")
        raise # Re-raise the exception for Streamlit to catch and display

def create_session_summary_json(
    baseline_filename, 
    current_filename, 
    drift_report, 
    drift_summary_table, 
    ai_explanation,
    classification_results=None # New parameter for sensitivity classifier
):
    """
    Creates a JSON-serializable dictionary summarizing the current session's analysis.
    This includes file names, the full drift report, the summary table,
    the AI explanation, and classification results if available.
    Ensures all NumPy types are converted to standard Python types.

    Args:
        baseline_filename (str): Name of the uploaded baseline file.
        current_filename (str): Name of the uploaded current file.
        drift_report (dict): The detailed data drift analysis report.
        drift_summary_table (list or None): The data drift summary table, expected as a list of dicts.
                                            Pass None if not available.
        ai_explanation (str): The AI-generated explanation for data drift.
        classification_results (list or None): List of dictionaries containing column sensitivity
                                               classification results. Pass None if not available.

    Returns:
        dict: A dictionary containing the session summary, ready for JSON serialization.
    """
    summary = {
        "timestamp": datetime.now().isoformat(),
        "baseline_file": baseline_filename,
        "current_file": current_filename,
        "data_drift_report": drift_report,
        "data_drift_summary_table": drift_summary_table,
        "data_drift_ai_explanation": ai_explanation,
        "data_sensitivity_classification_results": classification_results
    }

    # Ensure all NumPy types within the entire summary dictionary are converted
    cleaned_summary = convert_numpy_types(summary)
    
    logging.info("Session summary JSON created and cleaned of NumPy types.")
    return cleaned_summary

# Example Usage (for direct testing of this file)
if __name__ == '__main__':
    print("Running utils.py example...")

    # --- Test convert_numpy_types ---
    print("\n--- Testing convert_numpy_types ---")
    # Using np.array for testing as specific dtypes are usually created this way
    test_data = {
        "int_val": np.array(123, dtype=np.int64),
        "float_val": np.array(45.67, dtype=np.float32),
        "bool_val": np.array(True, dtype=bool),
        "array_val": np.array([1, 2, 3], dtype=np.int64),
        "nested_list": [np.array(1.1, dtype=np.float64), np.array(2, dtype=np.int64)],
        "nested_dict": {"key1": np.array(100, dtype=np.int32), "key2": "string"},
        "standard_str": "hello",
        "standard_int": 789,
        "pd_timestamp": pd.Timestamp('2023-01-01 10:30:00')
    }

    cleaned_data = convert_numpy_types(test_data)
    print("Original data types (from test_data values):")
    for k, v in test_data.items():
        print(f"  {k}: {type(v)}, Value: {v}")
    
    print("\nCleaned data types (after conversion):")
    for k, v in cleaned_data.items():
        print(f"  {k}: {type(v)}, Value: {v}")
    
    # Verify JSON serializability
    try:
        json_output = json.dumps(cleaned_data, indent=2)
        print("\nCleaned data is JSON serializable:\n", json_output)
    except TypeError as e:
        print(f"\nError: Cleaned data is NOT JSON serializable: {e}")

    # --- Test retry_with_exponential_backoff ---
    print("\n--- Testing retry_with_exponential_backoff ---")
    call_count = 0
    
    # Define a function to be decorated for testing purposes
    def _flaky_function(succeed_on_attempt):
        global call_count # Use global as this is in the script's global scope
        call_count += 1
        print(f"  Flaky function called, attempt {call_count}")
        if call_count < succeed_on_attempt:
            raise ValueError("Simulating a temporary error")
        return "Success!"

    # Decorate the test function
    flaky_function_decorated = retry_with_exponential_backoff(max_retries=3, initial_delay=0.1, exceptions=(ValueError,))(_flaky_function)

    try:
        call_count = 0
        result = flaky_function_decorated(2) # Should succeed on the 2nd attempt
        print(f"  Retry test 1 result: {result}")
    except ValueError:
        print("  Retry test 1 failed as expected (should not happen if succeed_on_attempt is within max_retries)")

    try:
        call_count = 0
        result = flaky_function_decorated(4) # Should fail after 3 retries
        print(f"  Retry test 2 result: {result}")
    except ValueError:
        print("  Retry test 2 failed as expected after max retries.")

    # --- Test create_session_summary_json ---
    print("\n--- Testing create_session_summary_json ---")
    mock_drift_report = {
        "schema_drift": {
            "added_columns": ["new_col"],
            "removed_columns": ["old_col"],
            "changed_columns": {"feature_x": {"old_type": "int64", "new_type": "float64"}}
        },
        "column_drift": {
            "feature_y": {
                "drift_score": np.float64(0.75),
                "null_pct_old": np.float64(1.5),
                "null_pct_new": np.float64(10.0),
                "type_old": "int64",
                "type_new": "int64",
                "missing_values_drift": True,
                "data_type_changed": False,
                "mean_old": np.float64(100.0),
                "mean_new": np.float64(120.5)
            },
            "feature_z": {
                "drift_score": np.float64(0.20),
                "null_pct_old": np.float64(0.0),
                "null_pct_new": np.float64(0.0),
                "type_old": "object",
                "type_new": "object",
                "missing_values_drift": False,
                "data_type_changed": False,
                "category_drift": {
                    "new_categories": ["Gamma"],
                    "missing_categories": [],
                    "top_categories_old": {"Alpha": np.float64(0.6), "Beta": np.float64(0.4)},
                    "top_categories_new": {"Alpha": np.float64(0.5), "Beta": np.float64(0.3), "Gamma": np.float64(0.2)}
                }
            }
        }
    }

    mock_drift_summary_table = [
        {"Column": "feature_y", "Drift Score": 0.75, "Missing % (New)": 10.00, "Comments": "Mean: 100.00 -> 120.50"},
        {"Column": "feature_z", "Drift Score": 0.20, "Missing % (New)": 0.00, "Comments": "New categories: Gamma"}
    ]

    mock_ai_explanation = "The data shows significant drift. AI insights provided."
    
    mock_classification_results = [
        {"column_name": "email", "sensitivity_level": "PII", "confidence": 5, "reasoning": "Contains email addresses."},
        {"column_name": "revenue", "sensitivity_level": "Finance-critical", "confidence": 4, "reasoning": "Financial data."}
    ]

    session_summary = create_session_summary_json(
        "baseline_data.csv",
        "current_data.csv",
        mock_drift_report,
        mock_drift_summary_table,
        mock_ai_explanation,
        mock_classification_results
    )

    print("\nGenerated Session Summary (first 1000 chars):")
    print(json.dumps(session_summary, indent=2)[:1000])

    try:
        json.dumps(session_summary)
        print("\nSession summary is successfully JSON serializable.")
    except TypeError as e:
        print(f"\nError: Session summary is NOT JSON serializable: {e}")

    print("\n--- Utils Example Complete ---")
