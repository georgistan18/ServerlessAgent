# contains actual logic fucntions like business_age(data) etc
# returns the risk flag (ok, monitor, review, flag) based on the data rules
# defines what fields are required per rule via REQUIRED_DATA
# also includes the RULES dictionary used for templating and hints

from datetime import datetime

# analyzing company profiles across key risk criteria:
# evaluate the input and return a risk flag based on the rules

# validate if we’re getting the required fields from the research output and supplement them via scraping or follow-ups
REQUIRED_DATA = {
    "business_age": ["registration_year", "status", "last_year_report"],
    "business_model_viability": ["market_presence", "dealer_network", "revenue_trends"],
    "product_dependency": ["top_product_revenue_share", "product_lines"],
    "customer_concentration": ["top_50_percent_revenue", "num_clients", "top3_clients_share"],
    "supplier_concentration": ["top_50_percent_cogs", "top3_suppliers_share"],
    "asset_traceability": ["traceability_system", "methods", "since"],
    "esg_compliance": ["esg_policy", "certifications", "incidents"],
    "cybersecurity": ["certifications", "measures", "incidents"],
    "corporate_rating": ["credit_rating", "agency"]
}

# logic and templates for each rule
RULES = {
    "business_age": {
        "name": "Business Age",
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

    "business_model_viability": {
         "name": "Business Model Viability",
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

    "product_dependency": {
        "name": "Product Dependency",
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

    "customer_concentration": {
        "name": "Customer Concentration",
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
    },

    "supplier_concentration": {
    "name": "Supplier Concentration",
    "key_fields": ["top_supplier_share", "top3_suppliers_share", "number_of_suppliers"],
    "prompt_template": (
        "Act as a supply chain risk analyst. Analyze the data below and generate a 2-5 sentence explanation, using facts, trends, and implications. "
        "Assign a risk flag: OK, Monitor, Review, or Flag.\n"
        "Data: top_supplier_share={top_supplier_share}, top3_suppliers_share={top3_suppliers_share}, number_of_suppliers={number_of_suppliers}"
    ),
    "flag_logic": "supplier_concentration",
    "example_ok": "The largest supplier contributes 12% of COGS, indicating healthy diversification.",
    "on_flag": {
        "finding": "Based on available data, the company appears to have strong dependence on a limited number of suppliers.",
        "option_1": (
            "Ask for company's supplier relations and mitigation plan for suppliers' dependency."
        ),
        "option_2": (
            "Could you please clarify the company's supplier relations and mitigation plan for top suppliers' dependence."
        ),
        "default": "Keep Flag"
        }
    },  

    "asset_traceability": {
    "name": "Asset Traceability",
    "key_fields": ["traceability_system", "methods", "since"],
    "prompt_template": (
        "Act as a supply chain auditor. Analyze the data below and generate a 2-5 sentence explanation, using facts, trends, and implications. "
        "Assign a risk flag: OK, Monitor, Review, or Flag.\n"
        "Data: traceability_system={traceability_system}, methods={methods}, since={since}"
    ),
    "flag_logic": "asset_traceability",
    "example_ok": "All equipment manufactured since 2021 is shipped with GPS and serialized QR codes for location tracking.",
    "on_flag": {
        "finding": "No information was found in relation to the Asset Traceability data possibility.",
        "option_1": (
            "Ask for company’s connectivity options for on-request or on-going Asset Traceability data."
        ),
        "option_2": (
            "Could you please clarify your Asset connectivity possibilities to provide on-request or on-going Asset Traceability data."
        ),
        "default": "Keep Flag"
        }
    },

    "esg_compliance": {
    "name": "ESG Compliance",
    "key_fields": ["esg_policy", "certifications", "incidents"],
    "prompt_template": (
        "Act as an ESG compliance expert. Analyze the data below and generate a 2-5 sentence explanation, using facts, trends, and implications. "
        "Assign a risk flag: OK, Monitor, Review, or Flag.\n"
        "Data: esg_policy={esg_policy}, certifications={certifications}, incidents={incidents}"
    ),
    "flag_logic": "esg_compliance",
    "example_ok": "The manufacturer holds ISO 14001 certification and reported zero environmental incidents in the past five years.",
    "on_flag": {
        "finding": "No clear information was found in relationg to your ESG strategy, scoring and certifications.",
        "option_1": (
            "Ask for ESG compliance and sustainability reporting."
        ),
        "option_2": (
            "Could you please detail your ESG compliance and sustainability reporting."
        ),
        "default": "Keep Flag"
        }
    },

    "cybersecurity": {
    "name": "Cybersecurity",
    "key_fields": ["certifications", "measures", "incidents"],
    "prompt_template": (
        "Act as a cybersecurity risk analyst. Analyze the data below and generate a 2-5 sentence explanation, using facts, trends, and implications. "
        "Assign a risk flag: OK, Monitor, Review, or Flag.\n"
        "Data: certifications={certifications}, measures={measures}, incidents={incidents}"
    ),
    "flag_logic": "cybersecurity",
    "example_ok": "Certified to ISO 27001 and no material security breaches reported since 2020.",
    "on_flag": {
        "finding": "No clear information was found in relationg to your Cybersecurity strategy, scoring and certifications.",
        "option_1": (
            " Ask for Cybersecurity compliance and reporting."
        ),
        "option_2": (
            "Could you please detail your Cybersecurity compliance and reporting."
        ),
        "default": "Keep Flag"
        }
    },

    "corporate_rating": {
    "name": "Corporate Rating",
    "key_fields": ["credit_rating", "agency"],
    "prompt_template": (
        "Act as a credit risk analyst. Analyze the data below and generate a 2-5 sentence explanation, using facts, trends, and implications. "
        "Assign a risk flag: OK, Monitor, Review, or Flag.\n"
        "Data: credit_rating={credit_rating}, agency={agency}"
    ),
    "flag_logic": "esg_compliance",
    "example_ok": "Rated BBB by S&P, outlook stable.",
    "on_flag": {
        "finding": "Based on available data, the company appears to have poor credit rating as per latest publicly available financial statements. ",
        "option_1": (
            "Ask for clarification for company's credit rating."
        ),
        "option_2": (
            "Could you please clarify the company’s current credit rating."
        ),
        "default": "Keep Flag"
        }
    },

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

def supplier_concentration(data: dict) -> str:
    top1 = float(data.get("top_supplier_share", 0))
    top3 = float(data.get("top3_suppliers_share", 0))
    if top1 > 50 or top3 > 75:
        return "Flag"
    elif top1 > 30 or top3 > 50:
        return "Review"
    return "OK"

def asset_traceability(data: dict) -> str:
    traceability = data.get("traceability", "").lower()
    if "none" in traceability:
        return "Flag"
    elif "limited" in traceability:
        return "Monitor"
    elif "partial" in traceability:
        return "Review"
    return "OK"

def esg_compliance(data: dict) -> str:
    certs = data.get("certifications", "").lower()
    incidents = data.get("incidents", "").lower()
    if "major" in incidents:
        return "Flag"
    elif "minor" in incidents:
        return "Monitor"
    elif not certs or certs == "none":
        return "Review"
    return "OK"

def cybersecurity(data: dict) -> str:
    certs = data.get("certifications", "").lower()
    measures = data.get("measures", "").lower()
    incidents = data.get("incidents", "").lower()
    if "major" in incidents or "breach" in incidents:
        return "Flag"
    elif "minor" in incidents:
        return "Monitor"
    elif "ok" not in certs and "ok" not in measures:
        return "Review"
    return "OK"

def corporate_rating(data: dict) -> str:
    rating = data.get("credit_rating", "").upper()
    if rating in ["CCC", "DEFAULT", "UNRATED"]:
        return "Flag"
    elif rating in ["BB-", "B+", "B", "B-"]:
        return "Monitor"
    elif rating in ["BBB", "BBB+", "BBB-", "A", "A-", "A+"]:
        return "OK"
    return "Review"


