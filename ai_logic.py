# ai_logic.py

import google.generativeai as genai
import os
import json
import logging
from google.api_core.exceptions import GoogleAPIError, RetryError

# Import utility functions for retry logic and type conversion
from utils import retry_with_exponential_backoff, convert_numpy_types
from sensitivity_labels import SENSITIVITY_GUIDANCE, SENSITIVITY_LEVELS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def configure_gemini(api_key):
    """
    Configures the Google Gemini API with the provided key.
    Returns True on successful configuration and a basic connectivity test, False otherwise.
    """
    if not api_key or api_key == "your_google_gemini_api_key_here":
        logging.error("Gemini API Key is missing or is a placeholder. Please set GEMINI_API_KEY in your .env file.")
        return False
    
    if not api_key.startswith("AIza"):
        logging.error("Gemini API Key format appears invalid. It should start with 'AIza'.")
        return False

    try:
        genai.configure(api_key=api_key)
        logging.info("Gemini API configured successfully.")
        
        # Test connectivity by listing models (lightweight API call)
        try:
            list(genai.list_models())
            logging.info("Successfully connected to Gemini API (models listed).")
            return True
        except Exception as e:
            logging.error(f"Failed to connect/list models with provided API key. This often indicates an invalid key, network issue, or regional model availability: {e}")
            return False
            
    except Exception as e:
        logging.error(f"An unexpected error occurred during Gemini API configuration: {e}")
        return False

@retry_with_exponential_backoff(max_retries=5, initial_delay=1.0, exceptions=(GoogleAPIError, RetryError))
def get_sensitivity_classification(column_metadata, api_key):
    """
    Sends column metadata to Google Gemini for sensitivity classification.

    Args:
        column_metadata (list): A list of dictionaries, each containing 'name', 'type',
                                and 'sample_values' for a column.
                                (e.g., [{"name": "email", "type": "string", "sample_values": ["a@b.com", "c@d.net"]}]).
                                This list should already be cleansed of NumPy types.
        api_key (str): Your Google Gemini API key.

    Returns:
        list: A list of dictionaries, each with 'column_name', 'sensitivity_level',
              'confidence', and 'reasoning', or an error message string.
    """
    if not configure_gemini(api_key):
        return [{"column_name": "N/A", "sensitivity_level": "Error", "confidence": 0,
                 "reasoning": "AI Analysis Disabled: Invalid or missing Gemini API Key."}]

    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # <-- UPDATE THIS LINE

        # Prepare the guidance for the LLM
        sensitivity_guidance_str = ""
        for level in SENSITIVITY_LEVELS:
            guidance = SENSITIVITY_GUIDANCE[level]
            # Limit examples to minimize token usage
            limited_examples = guidance['examples'][:3] 
            sensitivity_guidance_str += (
                f"- **{level}**: {guidance['description']}\n"
                f"  *Examples*: {', '.join(limited_examples)}...\n"
            )

        # Prepare column metadata for the prompt
        # Ensure column_metadata is JSON serializable
        try:
            # It's crucial that column_metadata is already free of NumPy types
            # from the 'features.py' side, but we'll re-convert just in case.
            clean_column_metadata = convert_numpy_types(column_metadata)
            metadata_json_str = json.dumps(clean_column_metadata, indent=2)
        except TypeError as e:
            logging.error(f"TypeError during JSON serialization of column_metadata: {e}")
            return [{"column_name": "N/A", "sensitivity_level": "Error", "confidence": 0,
                     "reasoning": f"Internal Error: Column metadata not JSON serializable: {e}"}]

        prompt = f"""
You are an expert data privacy and governance assistant. Your task is to classify the sensitivity level of each data column provided, based on its name, inferred type, and sample values.

{sensitivity_guidance_str}

For each column, return a JSON object with the following structure:
```json
[
  {{
    "column_name": "string",
    "sensitivity_level": "string (one of the levels listed above)",
    "confidence": "integer (1-5, 5 being highest confidence)",
    "reasoning": "string (a brief, 1-2 sentence explanation for the classification)"
  }}
]
```
Ensure your response is ONLY the JSON array. Do not include any conversational text, markdown outside the JSON, or extra characters.

Column Metadata to Classify:
```json
{metadata_json_str}
```
"""
        logging.info(f"Sending prompt to Gemini (first 500 chars): {prompt[:500]}...")
        
        # Estimate token usage for warning
        # This is a heuristic, actual token count might vary
        estimated_tokens = len(prompt) / 4 # Rough estimate: 1 token ~ 4 characters
        if estimated_tokens > 4000: # Warn if prompt is getting large for free tier
            logging.warning(f"Estimated prompt tokens: {estimated_tokens}. This might be close to or exceed free tier limits.")

        # Generate content
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for factual, consistent classification
                top_p=0.95,
                top_k=40,
                max_output_tokens=1024 # Sufficient tokens for classification output
            ),
            # Instruct the model to return JSON
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )
        
        # Extract and parse the JSON response
        if response.candidates:
            gemini_raw_text = response.candidates[0].content.parts[0].text
            logging.info(f"Gemini raw response: {gemini_raw_text[:200]}...")
            
            # Attempt to extract JSON from the raw text
            try:
                # Sometimes LLMs wrap JSON in markdown code blocks
                if gemini_raw_text.strip().startswith("```json"):
                    json_str = gemini_raw_text.strip()[len("```json"):].strip()
                    if json_str.endswith("```"):
                        json_str = json_str[:-len("```")].strip()
                else:
                    json_str = gemini_raw_text.strip()

                classification_results = json.loads(json_str)
                
                # Basic validation of the JSON structure
                if not isinstance(classification_results, list):
                    raise ValueError("Expected a JSON array of classification results.")
                for item in classification_results:
                    if not all(k in item for k in ["column_name", "sensitivity_level", "confidence", "reasoning"]):
                        raise ValueError("Each item in the JSON array must contain 'column_name', 'sensitivity_level', 'confidence', 'reasoning'.")
                
                logging.info("Successfully parsed AI classification results.")
                return classification_results

            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON from Gemini response: {e}. Raw text: {gemini_raw_text}", exc_info=True)
                return [{"column_name": "N/A", "sensitivity_level": "Error", "confidence": 0,
                         "reasoning": f"AI Response Error: Could not parse JSON from Gemini. Raw: {gemini_raw_text[:100]}... Error: {e}"}]
            except ValueError as e:
                logging.error(f"Invalid structure in Gemini's JSON response: {e}. Raw text: {gemini_raw_text}", exc_info=True)
                return [{"column_name": "N/A", "sensitivity_level": "Error", "confidence": 0,
                         "reasoning": f"AI Response Error: Invalid JSON structure. Raw: {gemini_raw_text[:100]}... Error: {e}"}]
        else:
            feedback = response.prompt_feedback
            safety_ratings_str = ""
            if feedback and feedback.safety_ratings:
                safety_ratings_str = ", ".join([f"{s.category.name}: {s.probability.name}" for s in feedback.safety_ratings])
            
            logging.warning(f"Gemini response had no candidates. Prompt feedback: {feedback}")
            return [{"column_name": "N/A", "sensitivity_level": "Error", "confidence": 0,
                     "reasoning": f"AI Analysis Failed: No valid response from Gemini. This is often due to safety filters ({safety_ratings_str}), or API issues. (Feedback: {feedback}) "}]

    except genai.types.BlockedPromptException as e:
        logging.error(f"Gemini API BlockedPromptException: {e}. Prompt feedback: {e.response.prompt_feedback if hasattr(e.response, 'prompt_feedback') else 'N/A'}", exc_info=True)
        safety_ratings_str = ""
        if hasattr(e.response, 'prompt_feedback') and e.response.prompt_feedback.safety_ratings:
             safety_ratings_str = ", ".join([f"{s.category.name}: {s.probability.name}" for s in e.response.prompt_feedback.safety_ratings])
        return [{"column_name": "N/A", "sensitivity_level": "Blocked", "confidence": 0,
                 "reasoning": f"AI Analysis Blocked: Prompt flagged for safety/policy. Review input data. (Details: {safety_ratings_str}) "}]
    except genai.types.StopCandidateException as e:
        logging.error(f"Gemini API StopCandidateException: {e}", exc_info=True)
        return [{"column_name": "N/A", "sensitivity_level": "Error", "confidence": 0,
                 "reasoning": "AI Analysis Halted: Gemini stopped generating response prematurely. Try reducing prompt size or increasing max_output_tokens."}]
    except GoogleAPIError as e: # Catch general Google API errors
        logging.error(f"GoogleAPIError occurred during Gemini API call: {e}", exc_info=True)
        return [{"column_name": "N/A", "sensitivity_level": "Error", "confidence": 0,
                 "reasoning": f"AI Analysis API Error: Failed to connect to Gemini API or internal error. Check internet/API key. Error: {e}"}]
    except RetryError as e: # Catch errors from the retry decorator
        logging.error(f"RetryError: Function failed after multiple retries: {e}", exc_info=True)
        return [{"column_name": "N/A", "sensitivity_level": "Error", "confidence": 0,
                 "reasoning": f"AI Analysis Error: API call failed after multiple retries. Error: {e}"}]
    except Exception as e:
        logging.error(f"An unexpected error occurred during the Gemini API call process: {e}", exc_info=True)
        return [{"column_name": "N/A", "sensitivity_level": "Error", "confidence": 0,
                 "reasoning": f"AI Analysis Error: An unexpected error occurred: {e}. Check logs for details."}]

# Example Usage (for direct testing of this file)
if __name__ == '__main__':
    print("Running ai_logic.py example for testing purposes...")

    # Load API key from .env file (for standalone testing)
    from dotenv import load_dotenv
    load_dotenv()
    test_api_key = os.getenv("GEMINI_API_KEY")

    if not test_api_key or test_api_key == "your_google_gemini_api_key_here":
        print("--- WARNING: GEMINI_API_KEY is not set in your .env file. Cannot run full AI logic test. ---")
        print("Please set your API key in the .env file to test this module correctly.")
    else:
        # --- Test API Key Configuration ---
        print("\n--- Testing Gemini API Configuration ---")
        if configure_gemini(test_api_key):
            print("Gemini API configured and tested successfully.")
        else:
            print("Gemini API configuration failed. Check the error logs above for details.")
            # exit() # Uncomment this line to stop the script if config fails
        
        # --- Optional: List available models (useful for debugging 404 errors) ---
        try:
            print("\n--- Listing Available Gemini Models ---")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"  Model Name: {m.name}, Description: {m.description}")
            print("--------------------------------------")
        except Exception as e:
            print(f"Error listing models: {e}. This might indicate an API key issue or network problem even after successful configure.")

        # --- Simulate column metadata (as prepared by features.py) ---
        # This dictionary must contain standard Python types (int, float, str, list, dict),
        # NOT NumPy specific types like np.int64, np.float64, etc.
        sample_column_metadata = [
            {"name": "user_id", "type": "integer", "sample_values": [101, 102]},
            {"name": "email_address", "type": "string", "sample_values": ["test@example.com", "user@domain.org"]},
            {"name": "transaction_amount", "type": "float", "sample_values": [123.45, 99.99]},
            {"name": "product_category", "type": "string", "sample_values": ["Electronics", "Books"]},
            {"name": "ssn_last_4", "type": "string", "sample_values": ["1234", "5678"]},
            {"name": "internal_project_code", "type": "string", "sample_values": ["PROJ-ALPHA", "PROJ-BETA"]},
            {"name": "date_of_birth", "type": "string", "sample_values": ["1990-01-01", "1985-12-31"]},
            {"name": "credit_card_hash", "type": "string", "sample_values": ["xyz123abc", "def456ghi"]}
        ]

        print("\n--- Requesting AI Sensitivity Classification ---")
        classification_results = get_sensitivity_classification(sample_column_metadata, test_api_key)
        print("\n--- AI Classification Results (Output below) ---")
        print(json.dumps(classification_results, indent=2))

    print("\n--- AI Logic Example Test Complete ---")
