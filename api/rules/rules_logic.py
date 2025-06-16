from datetime import datetime

# analyzing company profiles across key risk criteria:
# evaluate the input and return a risk flag based on the rules

# validate if we’re getting the required fields from the research output and supplement them via scraping or follow-ups
REQUIRED_DATA = {
    "business_age": ["registration_year", "status", "last_year_report"],
    "business_model_viability": ["market_presence", "dealer_network", "revenue_trends"],
    "product_dependency": ["top_product_revenue_share", "product_lines"],
    "customer_concentration": ["top_50_percent_revenue", "num_clients", "top3_clients_share"]
}

# logic and templates for each rule
RULES = {
    "Business Age": {
        "key_fields": ["registration_year", "status", "last_report_year"],
        "prompt_template": (
            "Act as a legal entity analyst. Analyze the data below and generate a 2-5 sentence explanation, using facts, trends, and implications. "
            "Assign a risk flag: OK, Monitor, Review, or Flag.\n"
            "Data: registration_year={registration_year}, status={status}, last_report_year={last_report_year}"
        ),
        # each flag-logic in RULES refers to a rule engine function that is called when the flag is triggered
        "flag_logic": "business_age",
        "example_ok": "The company was incorporated in 2010 and remains active with filings up to 2023.",
        "on_flag": {
            "finding": "Based on available data, the company appears to be liquidated.",
            "option_1": "Ask for current company's legal status.",
            "option_2": "Could you please confirm the company's legal status for VAT #, and attach evidence?",
            "default": "Keep Flag"
        }
    },

    "Business Model Viability": {
        "key_fields": ["market_presence", "dealer_network", "revenue_trends"],
        "prompt_template": (
            "Act as a business analyst. Analyze the data below and generate a 2-5 sentence explanation, using facts, trends, and implications. "
            "Assign a risk flag: OK, Monitor, Review, or Flag.\n"
            "Data: market_presence={market_presence}, dealer_network={dealer_network}, revenue_trends={revenue_trends}"
        ),
        "flag_logic": "business_model_viability",
        "example_ok": "Revenue has grown 8% YoY and its products are distributed via a global 250 dealer network.",
        "on_flag": {
            "finding": "Available data suggests weak market presence and declining revenue.",
            "option_1": "Ask for current business context and actions to improve results and future growth.",
            "option_2": "Could you please clarify the current business context, your actions to improve results and future growth?",
            "default": "Keep Flag"
        }
    },

    "Product Dependency": {
        "key_fields": ["top_product_revenue_share", "product_lines"],
        "prompt_template": (
            "Act as a product risk analyst. Analyze the data below and generate a 2-5 sentence explanation, using facts, trends, and implications. "
            "Assign a risk flag: OK, Monitor, Review, or Flag.\n"
            "Data: top_product_revenue_share={top_product_revenue_share}, product_lines={product_lines}"
        ),
        "flag_logic": "product_dependency",
        "example_ok": "The main product line accounts for 12% of turnover.",
        "on_flag": {
            "finding": "Based on available data, the company appears to have strong dependence on the main product line.",
            "option_1": "Ask for company’s product portfolio and mitigation plan for dependency.",
            "option_2": "Could you please clarify the company's product portfolio and mitigation plan for dependency?",
            "default": "Keep Flag"
        }
    },

    "Customer Concentration": {
        "key_fields": ["top_client_share", "top3_clients_share"],
        "prompt_template": (
            "Act as a market risk analyst. Analyze the data below and generate a 2-5 sentence explanation, using facts, trends, and implications. "
            "Assign a risk flag: OK, Monitor, Review, or Flag.\n"
            "Data: top_client_share={top_client_share}, top3_clients_share={top3_clients_share}"
        ),
        "flag_logic": "customer_concentration",
        "example_ok": "No single customer accounts for more than 10% of annual sales.",
        "on_flag": {
            "finding": "Based on available data, the company appears to have strong dependence on a limited number of customers.",
            "option_1": "Ask for company's customer portfolio and mitigation plan for clients' dependency.",
            "option_2": "Could you please clarify the company's customer portfolio and mitigation plan for top clients' dependence?",
            "default": "Keep Flag"
        }
    }
}

# Functions for each flag-logic block
def business_age(data: dict) -> str:
    try:
        reg_year = int(data.get("registration_year", 0))
        last_report_year = int(data.get("last_report_year", 0))
        status = data.get("status", "").lower()
        current_year = datetime.now().year

        # Hard stop if company is dissolved or liquidated
        if status in ["liquidated", "dissolved"]:
            return "Flag"

        # status issues
        if status in ["inactive", "dormant"]:
            return "Review"

        age = current_year - reg_year

        if age >= 3:
            return "OK"
        elif 1 < age < 3:
            return "Monitor"
        elif age <= 1:
            return "Review"
    except Exception:
        pass

    return "Review"  # default fallback

def business_model_viability(data: dict) -> str:
    market_presence = data.get("market_presence", "").lower()
    dealer_network = data.get("dealer_network", "")
    revenue_trends = data.get("revenue_trends", "").lower()

    # convert dealer_network to a number if needed
    # try:
    #     dealer_network = int(dealer_network)
    # except (ValueError, TypeError):
    #     dealer_network = 0

    if "weak" in market_presence and "declining" in revenue_trends:
        return "Flag"
    if "weak" in market_presence or "declining" in revenue_trends:
        return "Review"
    if "moderate" in market_presence or "moderate" in revenue_trends:
        return "Monitor"
    if "global" in market_presence and "stable" in revenue_trends:
        return "OK"
    if "strong" in market_presence:
        return "OK"

    return "Review"  # default if unclear

def product_dependency(data: dict) -> str:
    try:
        share = float(data.get("top_product_revenue_share", 0))

        if share <= 15:
            return "OK"
        elif 15 < share <= 20:
            return "Monitor"
        elif 20 < share <= 30:
            return "Review"
        elif share > 30:
            return "Flag"
    except Exception:
        pass

    return "Review"  # default/fallback

def customer_concentration(data: dict) -> str:
    try:
        top1 = float(data.get("top_client_share", 0))
        top3 = float(data.get("top3_clients_share", 0))
        num_clients = int(data.get("number_of_clients", 0))

        if top1 > 50:
            return "Flag"
        if top3 > 50:
            return "Review"
        if top3 > 30:
            return "Monitor"
        if top1 <= 20:
            return "OK"
    except Exception:
        pass

    return "Review"

