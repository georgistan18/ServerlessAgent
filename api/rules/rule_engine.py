# central router that takes a criteria string and data dictionary
# uses a dispatch map (RULES_FUNCTIONS) to call the corresponding logic function
# returns:
#   - flag (ok, review, etc)
#   - prompt to be used in LLM prompt chain
#   - any suggested follow-up actions
# coordinate which function to call for each `flag_logic` / evaluation

from .rules_logic import (
    business_age,
    business_model_viability,
    product_dependency,
    customer_concentration,
)

RULES_FUNCTIONS = {
    "business_age": business_age,
    "business_model_viability": business_model_viability,
    "product_dependency": product_dependency,
    "customer_concentration": customer_concentration,
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

    