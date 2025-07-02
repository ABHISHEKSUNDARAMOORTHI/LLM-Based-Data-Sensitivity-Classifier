# sensitivity_labels.py

# This file defines the sensitivity levels and provides examples
# to guide the LLM's classification.

SENSITIVITY_LEVELS = [
    "Public",
    "Internal",
    "Confidential",
    "PII",
    "Finance-critical"
]

# Provide clear definitions and examples for each sensitivity level.
# These will be used in the AI prompt to ensure consistent classification.
SENSITIVITY_GUIDANCE = {
    "Public": {
        "description": "Data that is generally available or poses very low risk if exposed. Can be shared widely.",
        "examples": [
            "product_id", "category_name", "public_website_url", "city_name",
            "country_code", "product_description", "timestamp_utc", "log_level"
        ]
    },
    "Internal": {
        "description": "Data for internal business use only. Not intended for public disclosure, but not highly sensitive.",
        "examples": [
            "employee_id", "internal_project_code", "department_name", "office_location",
            "internal_ticket_id", "system_status_message", "server_ip_address_internal",
            "application_version"
        ]
    },
    "Confidential": {
        "description": "Data requiring restricted access within the organization. Unauthorized disclosure could cause moderate harm.",
        "examples": [
            "salary_range", "performance_review_score", "unreleased_product_roadmap",
            "proprietary_algorithm_name", "business_strategy_document_id", "customer_segment_internal",
            "supplier_contract_id", "internal_audit_findings"
        ]
    },
    "PII": {
        "description": "Personally Identifiable Information. Data that can directly or indirectly identify an individual. Unauthorized disclosure could lead to significant harm (e.g., identity theft, privacy violation).",
        "examples": [
            "first_name", "last_name", "email_address", "phone_number", "home_address",
            "social_security_number", "date_of_birth", "passport_number", "driver_license_id",
            "national_id", "medical_record_number", "biometric_data", "ip_address_public",
            "user_id_hashed", "device_id" # Even hashed/device IDs can be PII if linkable
        ]
    },
    "Finance-critical": {
        "description": "Data directly related to financial transactions, assets, or sensitive financial operations. Unauthorized disclosure could lead to severe financial loss or fraud.",
        "examples": [
            "credit_card_number", "bank_account_number", "routing_number", "revenue_amount",
            "profit_margin", "transaction_value", "investment_portfolio_value", "loan_amount",
            "balance_sheet_item", "tax_id_number", "invoice_id", "payment_gateway_token"
        ]
    }
}

def get_sensitivity_guidance_for_prompt():
    """
    Formats the sensitivity levels and their guidance into a string suitable for an LLM prompt.
    """
    guidance_str = "Classify each column below with a sensitivity level from the provided list:\n"
    for level in SENSITIVITY_LEVELS:
        guidance_str += f"- {level}: {SENSITIVITY_GUIDANCE[level]['description']}\n"
        # Optionally add examples to the prompt, but be mindful of token limits
        # guidance_str += f"  Examples: {', '.join(SENSITIVITY_GUIDANCE[level]['examples'][:3])}...\n" # Limit examples
    return guidance_str

# Example Usage (for direct testing of this file)
if __name__ == '__main__':
    print("Running sensitivity_labels.py example...")

    print("\n--- Defined Sensitivity Levels ---")
    for level in SENSITIVITY_LEVELS:
        print(f"- {level}")

    print("\n--- Detailed Sensitivity Guidance ---")
    for level, data in SENSITIVITY_GUIDANCE.items():
        print(f"\nLevel: {level}")
        print(f"  Description: {data['description']}")
        print(f"  Examples: {', '.join(data['examples'])}")

    print("\n--- Formatted Guidance for LLM Prompt ---")
    llm_guidance = get_sensitivity_guidance_for_prompt()
    print(llm_guidance)

    print("\n--- Sensitivity Labels Example Complete ---")
