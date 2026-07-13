API_URL = "http://backend:80"

CATEGORY_LABELS = {
    "Σούπερ Μάρκετ": "supermarket",
    "Ενοίκιο": "rent",
    "Λογαριασμοί": "utilities",
    "Ψυχαγωγία": "entertainment",
    "Μετακίνηση": "transportation",
    "Άλλο": "other",
}

PAYMENT_METHOD_LABELS = {
    "Κάρτα": "card",
    "Μετρητά": "cash",
    "Τραπεζικό Έμβασμα": "bank_transfer",
}

SUMMARY_CATEGORY_LABELS = {"Όλες": "Όλες", **CATEGORY_LABELS}
FILTER_CATEGORY_LABELS = {"Όλα": "Όλα", **CATEGORY_LABELS}
FILTER_PAYMENT_LABELS = {"Όλα": "Όλα", **PAYMENT_METHOD_LABELS}

SORT_LABELS = {"Ημερομηνία": "created_at", "Ποσό": "amount"}
ORDER_LABELS = {
    "Νεότερα/Μεγαλύτερα πρώτα": "desc",
    "Παλαιότερα/Μικρότερα πρώτα": "asc",
}

CATEGORY_DISPLAY_MAP = {v: k for k, v in CATEGORY_LABELS.items()}
PAYMENT_DISPLAY_MAP = {v: k for k, v in PAYMENT_METHOD_LABELS.items()}

CUSTOM_CSS = """
<style>
[data-testid="stMetric"] {
    background-color: #F1F3F4;
    padding: 15px 20px;
    border-radius: 12px;
    border: 1px solid #E0E0E0;
}
div.stButton > button {
    border-radius: 8px;
    font-weight: 600;
}
div.stButton > button[kind="primary"] {
    background-color: #2E7D32;
}
.block-container {
    padding-top: 2rem;
}
</style>
"""

PAGE_CONFIG = {
    "page_title": "Διαχείριση Εξόδων",
    "page_icon": "💶",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}
