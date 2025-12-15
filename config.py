# config.py

import os

# =========================
# CARTELLE BASE
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# cartella dove hai messo i csv Olist
DATA_PATH = os.path.join(BASE_DIR, "data")  # cambia se necessario, oppure metti BASE_DIR se i csv sono lì

# cartella output
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# FILE CSV
# =========================

CSV_FILES = {
    "orders": os.path.join(DATA_PATH, "olist_orders_dataset.csv"),
    "order_items": os.path.join(DATA_PATH, "olist_order_items_dataset.csv"),
    "order_payments": os.path.join(DATA_PATH, "olist_order_payments_dataset.csv"),
    "order_reviews": os.path.join(DATA_PATH, "olist_order_reviews_dataset.csv"),
    "customers": os.path.join(DATA_PATH, "olist_customers_dataset.csv"),
    "products": os.path.join(DATA_PATH, "olist_products_dataset.csv"),
    "sellers": os.path.join(DATA_PATH, "olist_sellers_dataset.csv"),
    "product_category": os.path.join(DATA_PATH, "product_category_name_translation.csv"),
}

# =========================
# DISPLAY PANDAS
# =========================

PANDAS_DISPLAY_OPTIONS = {
    "display.max_columns": None,
    "display.max_rows": 100,
    "display.float_format": lambda x: f"{x:,.2f}",
}

# =========================
# STILE PLOT
# =========================

PLOT_STYLE = "seaborn-v0_8"
PLOT_PALETTE = "viridis"

# =========================
# CAMBIO VALUTA
# =========================
# Tasso medio 2017 (IMF/CEIC): 1 BRL ≈ 0.278 EUR
BRL_TO_EUR = 0.278

# =========================
# TRADUZIONI
# =========================

TRADUZIONE_COLONNE = {
    # orders
    "order_id": "id_ordine",
    "customer_id": "id_cliente",
    "order_status": "stato_ordine",
    "order_purchase_timestamp": "data_acquisto",
    "order_approved_at": "data_approvazione",
    "order_delivered_carrier_date": "data_spedizione",
    "order_delivered_customer_date": "data_consegna",
    "order_estimated_delivery_date": "data_consegna_stimata",

    # customers
    "customer_unique_id": "id_cliente_univoco",
    "customer_zip_code_prefix": "cap_cliente",
    "customer_city": "citta_cliente",
    "customer_state": "stato_cliente",

    # order_items
    "order_item_id": "id_articolo_ordine",
    "product_id": "id_prodotto",
    "seller_id": "id_venditore",
    "shipping_limit_date": "data_limite_spedizione",
    "price": "prezzo",
    "freight_value": "costo_spedizione",

    # payments
    "payment_sequential": "sequenza_pagamento",
    "payment_type": "tipo_pagamento",
    "payment_installments": "rate_pagamento",
    "payment_value": "valore_pagamento",

    # reviews
    "review_id": "id_recensione",
    "review_score": "punteggio_recensione",
    "review_comment_title": "titolo_recensione",
    "review_comment_message": "testo_recensione",
    "review_creation_date": "data_creazione_recensione",
    "review_answer_timestamp": "data_risposta_recensione",
}

TRADUZIONE_STATI_ORDINE = {
    "delivered": "consegnato",
    "shipped": "spedito",
    "canceled": "cancellato",
    "unavailable": "non_disponibile",
    "processing": "in_elaborazione",
    "created": "creato",
    "approved": "approvato",
    "invoiced": "fatturato",
}

TRADUZIONE_PAGAMENTI = {
    "credit_card": "carta_di_credito",
    "boleto": "boleto",
    "voucher": "voucher",
    "debit_card": "carta_di_debito",
    "not_defined": "non_definito",
}

# =========================
# BINNING
# =========================

BINNING_VALORE_ORDINE = {
    # NB: queste soglie valgono se lavori in BRL; se usi EUR puoi ridurle
    "bins": [0, 100, 300, 1000, float("inf")],
    "labels": ["basso", "medio", "alto", "molto_alto"],
}

BINNING_GIORNI_CONSEGNA = {
    "bins": [0, 3, 7, 14, float("inf")],
    "labels": ["molto_rapida", "rapida", "normale", "lenta"],
}