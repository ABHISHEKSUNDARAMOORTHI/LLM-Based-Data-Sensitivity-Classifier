# visualizer.py

import pandas as pd
import plotly.express as px
import logging

# Import sensitivity levels for consistent ordering
from sensitivity_labels import SENSITIVITY_LEVELS # ADDED THIS IMPORT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def plot_sensitivity_distribution(classification_results):
    """
    Generates a bar chart showing the distribution of sensitivity levels.

    Args:
        classification_results (list): A list of dictionaries, each containing
                                       'column_name', 'sensitivity_level', 'confidence', 'reasoning'.

    Returns:
        plotly.graph_objects.Figure: A Plotly bar chart figure, or None if data is insufficient.
    """
    if not classification_results:
        logging.warning("No classification results to plot sensitivity distribution.")
        return None

    df_results = pd.DataFrame(classification_results)

    if 'sensitivity_level' not in df_results.columns:
        logging.error("'sensitivity_level' column not found in classification results for plotting.")
        return None

    # Count occurrences of each sensitivity level
    sensitivity_counts = df_results['sensitivity_level'].value_counts().reset_index()
    sensitivity_counts.columns = ['Sensitivity Level', 'Count']

    # Define a custom order for sensitivity levels for consistent plotting
    # This order should align with the SENSITIVITY_LEVELS in sensitivity_labels.py
    # and include any potential error/blocked states.
    # Use SENSITIVITY_LEVELS directly and append error/unknown states
    custom_order = SENSITIVITY_LEVELS + ["Error", "Blocked", "Unknown"] # MODIFIED THIS LINE
    
    # Filter to only include levels present in the data and sort by custom order
    sensitivity_counts['Sensitivity Level'] = pd.Categorical(
        sensitivity_counts['Sensitivity Level'],
        categories=[level for level in custom_order if level in sensitivity_counts['Sensitivity Level'].unique()],
        ordered=True
    )
    sensitivity_counts = sensitivity_counts.sort_values('Sensitivity Level')

    # Define custom colors for better visual distinction
    color_map = {
        "PII": "#EF4444",          # Red
        "Finance-critical": "#F97316", # Orange
        "Confidential": "#F59E0B", # Amber
        "Internal": "#3B82F6",     # Blue
        "Public": "#22C55E",       # Green
        "Error": "#6B7280",        # Gray
        "Blocked": "#4B5563",      # Darker Gray
        "Unknown": "#9CA3AF"       # Lighter Gray
    }

    fig = px.bar(
        sensitivity_counts,
        x='Sensitivity Level',
        y='Count',
        title='Distribution of Data Sensitivity Levels',
        color='Sensitivity Level',
        color_discrete_map=color_map,
        template="plotly_dark", # Use dark theme for consistency with Streamlit app
        text='Count' # Display count on bars
    )

    fig.update_layout(
        xaxis_title="Sensitivity Level",
        yaxis_title="Number of Columns",
        xaxis_tickangle=-45,
        hovermode="x unified",
        title_x=0.5, # Center title
        font=dict(family="Inter, sans-serif") # Set font family
    )
    fig.update_traces(textposition='outside') # Position text outside bars for clarity
    fig.update_yaxes(rangemode="tozero") # Ensure y-axis starts at zero

    logging.info("Sensitivity distribution plot generated.")
    return fig

def plot_confidence_distribution(classification_results):
    """
    Generates a histogram of confidence scores.

    Args:
        classification_results (list): A list of dictionaries, each containing
                                       'column_name', 'sensitivity_level', 'confidence', 'reasoning'.

    Returns:
        plotly.graph_objects.Figure: A Plotly histogram figure, or None if data is insufficient.
    """
    if not classification_results:
        logging.warning("No classification results to plot confidence distribution.")
        return None

    df_results = pd.DataFrame(classification_results)

    if 'confidence' not in df_results.columns:
        logging.error("'confidence' column not found in classification results for plotting.")
        return None

    # Ensure confidence scores are numeric
    df_results['confidence'] = pd.to_numeric(df_results['confidence'], errors='coerce').dropna()

    if df_results['confidence'].empty:
        logging.warning("No valid numeric confidence scores to plot.")
        return None

    fig = px.histogram(
        df_results,
        x='confidence',
        nbins=5, # Confidence is 1-5, so 5 bins is appropriate
        title='Distribution of AI Confidence Scores',
        template="plotly_dark",
        color_discrete_sequence=["#8B5CF6"], # Violet color
        histnorm='percent' # Show percentage on Y-axis
    )

    fig.update_layout(
        xaxis_title="Confidence Score (1-5)",
        yaxis_title="Percentage of Columns",
        xaxis=dict(tickmode='array', tickvals=[1, 2, 3, 4, 5]), # Ensure ticks are at 1-5
        bargap=0.1, # Gap between bars
        title_x=0.5, # Center title
        font=dict(family="Inter, sans-serif") # Set font family
    )
    fig.update_yaxes(tickformat=".0f%") # Format y-axis as percentage without decimals

    logging.info("Confidence distribution plot generated.")
    return fig

# Example Usage (for direct testing of this file)
if __name__ == '__main__':
    print("Running visualizer.py example...")

    # Sample classification results for testing
    sample_results = [
        {"column_name": "email", "sensitivity_level": "PII", "confidence": 5, "reasoning": "Contains email addresses."},
        {"column_name": "first_name", "sensitivity_level": "PII", "confidence": 4, "reasoning": "Personal name."},
        {"column_name": "product_id", "sensitivity_level": "Public", "confidence": 5, "reasoning": "Public identifier."},
        {"column_name": "revenue_usd", "sensitivity_level": "Finance-critical", "confidence": 5, "reasoning": "Financial data."},
        {"column_name": "department", "sensitivity_level": "Internal", "confidence": 4, "reasoning": "Internal business unit."},
        {"column_name": "street_address", "sensitivity_level": "PII", "confidence": 5, "reasoning": "Physical address."},
        {"column_name": "internal_code", "sensitivity_level": "Internal", "confidence": 3, "reasoning": "Internal reference."},
        {"column_name": "salary", "sensitivity_level": "Confidential", "confidence": 5, "reasoning": "Sensitive employee compensation."},
        {"column_name": "tax_id", "sensitivity_level": "Finance-critical", "confidence": 5, "reasoning": "Tax identification number."},
        {"column_name": "status", "sensitivity_level": "Public", "confidence": 4, "reasoning": "General status."}
    ]

    # --- Test plot_sensitivity_distribution ---
    print("\n--- Testing plot_sensitivity_distribution ---")
    fig_sensitivity = plot_sensitivity_distribution(sample_results)
    if fig_sensitivity:
        fig_sensitivity.show() # This will open the plot in your browser or an interactive window

    # --- Test plot_confidence_distribution ---
    print("\n--- Testing plot_confidence_distribution ---")
    fig_confidence = plot_confidence_distribution(sample_results)
    if fig_confidence:
        fig_confidence.show()

    # Test with empty results
    print("\n--- Testing with empty results ---")
    fig_empty_sensitivity = plot_sensitivity_distribution([])
    print(f"Empty sensitivity plot result: {fig_empty_sensitivity}")
    fig_empty_confidence = plot_confidence_distribution([])
    print(f"Empty confidence plot result: {fig_empty_confidence}")

    print("\nVisualizer Example Complete.")
