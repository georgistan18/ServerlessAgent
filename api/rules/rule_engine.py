# central router that takes a criteria string and data dictionary
# uses a dispatch map (RULES_FUNCTIONS) to call the corresponding logic function
# returns:
#   - flag (ok, review, etc)
#   - prompt to be used in LLM prompt chain
#   - any suggested follow-up actions
# coordinate which function to call for each `flag_logic` / evaluation

from .rules_logic import (
    # manufacturer
    business_age,
    business_model_viability,
    product_dependency,
    customer_concentration,
    supplier_concentration,
    asset_traceability,
    esg_compliance,
    cybersecurity,
    corporate_rating,

    # dealer
    # business_model_viability,
    tax_compliance,
    legal_disputes,
    reputation,
    beneficial_owner_aml,
    sanctions_watchlists,

    # asset
    market_demand,
    emission_compliance,
    asset_model_year,
)

RULES_FUNCTIONS = {
    # manufacturer
    "business_age": business_age,
    "business_model_viability": business_model_viability,
    "product_dependency": product_dependency,
    "customer_concentration": customer_concentration,
    "supplier_concentration": supplier_concentration,
    "asset_traceability": asset_traceability,
    "esg_compliance": esg_compliance,
    "cybersecurity": cybersecurity,
    "corporate_rating": corporate_rating,

    # dealer
    # "dealer_business_model_viability": dealer_business_model_viability,
    "tax_compliance": tax_compliance,
    "legal_disputes": legal_disputes,
    "reputation": reputation,
    "beneficial_owner_aml": beneficial_owner_aml,
    "sanctions_watchlists": sanctions_watchlists,

    # asset
    "market_demand": market_demand,
    "emission_compliance": emission_compliance,
    "asset_model_year": asset_model_year,

}

def evaluate_rule(criteria: str, data: dict) -> dict:
    if criteria not in RULES_FUNCTIONS:
        return {
            "status": "error",
            "message": f"No rule logic found for '{criteria}'"
        }

    # run logic
    flag = RULES_FUNCTIONS[criteria](data)

    # load prompt and follow-up action from RULES dict
    from .rules_logic import RULES
    rule_meta = RULES[criteria]
    
    return {
        "criteria": criteria,
        "flag": flag,
        "prompt": rule_meta["prompt_template"],
        "suggested_action": rule_meta.get("suggested_action"),
        "explanation_hint": rule_meta.get("how_to_explain") # helper from LLM
    }
