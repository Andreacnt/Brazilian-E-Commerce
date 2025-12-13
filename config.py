import os
from pathlib import Path

# Directory principale del progetto
BASE_DIR = Path(__file__).resolve().parent

# Percorso della cartella contenente i dati CSV
# Assicurati che i file CSV siano in questa cartella
DATA_PATH = BASE_DIR / "data"  # oppure BASE_DIR / "data" se usi una sottocartella

# Percorso della cartella per i file di output (grafici, dataset puliti, ecc.)
OUTPUT_PATH = BASE_DIR / "outputs"
OUTPUT_FIGURES_PATH = OUTPUT_PATH / "figures"

# Crea le cartelle di output se non esistono
OUTPUT_PATH.mkdir(exist_ok=True)
OUTPUT_FIGURES_PATH.mkdir(exist_ok=True)

# Tasso di cambio da BRL a EUR
BRL_TO_EUR = 0.19

# Mappatura dei file CSV
CSV_FILES = {
    'customers': 'olist_customers_dataset.csv',
    'geolocation': 'olist_geolocation_dataset.csv',
    'order_items': 'olist_order_items_dataset.csv',
    'order_payments': 'olist_order_payments_dataset.csv',
    'order_reviews': 'olist_order_reviews_dataset.csv',
    'orders': 'olist_orders_dataset.csv',
    'products': 'olist_products_dataset.csv',
    'sellers': 'olist_sellers_dataset.csv',
    'category_translation': 'product_category_name_translation.csv'
}

# File di output generati
OUTPUT_FILES = {
    'unified': 'dataset_ecommerce_brasile_unificato.csv',
    'tableau': 'dataset_tableau_avanzato.csv',
    'clean': 'dataset_ordini_pulito.csv'
}

# Traduzioni colonne
TRADUZIONE_COLONNE = {
    'customer_id': 'id_cliente',
    'customer_unique_id': 'id_cliente_unico',
    'customer_zip_code_prefix': 'cap_cliente',
    'customer_city': 'citta_cliente',
    'customer_state': 'stato_cliente',
    'order_id': 'id_ordine',
    'order_status': 'stato_ordine',
    'order_purchase_timestamp': 'data_acquisto',
    'order_approved_at': 'data_approvazione',
    'order_delivered_carrier_date': 'data_spedizione',
    'order_delivered_customer_date': 'data_consegna',
    'order_estimated_delivery_date': 'data_consegna_stimata',
    'order_item_id': 'id_articolo_ordine',
    'product_id': 'id_prodotto',
    'seller_id': 'id_venditore',
    'shipping_limit_date': 'data_limite_spedizione',
    'price': 'prezzo',
    'freight_value': 'costo_spedizione',
    'payment_sequential': 'sequenza_pagamento',
    'payment_type': 'tipo_pagamento',
    'payment_installments': 'rate_pagamento',
    'payment_value': 'valore_pagamento',
    'review_id': 'id_recensione',
    'review_score': 'punteggio_recensione',
    'review_comment_title': 'titolo_commento',
    'review_comment_message': 'messaggio_commento',
    'review_creation_date': 'data_creazione_recensione',
    'review_answer_timestamp': 'data_risposta_recensione',
    'seller_zip_code_prefix': 'cap_venditore',
    'seller_city': 'citta_venditore',
    'seller_state': 'stato_venditore',
    'product_category_name': 'categoria_prodotto',
    'product_name_lenght': 'lunghezza_nome_prodotto',
    'product_description_lenght': 'lunghezza_descrizione',
    'product_photos_qty': 'numero_foto',
    'product_weight_g': 'peso_prodotto_g',
    'product_length_cm': 'lunghezza_prodotto_cm',
    'product_height_cm': 'altezza_prodotto_cm',
    'product_width_cm': 'larghezza_prodotto_cm',
    'geolocation_zip_code_prefix': 'cap_geolocalizzazione',
    'geolocation_lat': 'latitudine',
    'geolocation_lng': 'longitudine',
    'geolocation_city': 'citta_geolocalizzazione',
    'geolocation_state': 'stato_geolocalizzazione'
}

# Traduzioni valori specifici
TRADUZIONE_STATI_ORDINE = {
    'delivered': 'consegnato',
    'shipped': 'spedito',
    'canceled': 'cancellato',
    'unavailable': 'non_disponibile',
    'invoiced': 'fatturato',
    'processing': 'in_elaborazione',
    'created': 'creato',
    'approved': 'approvato'
}

TRADUZIONE_PAGAMENTI = {
    'credit_card': 'carta_di_credito',
    'boleto': 'boleto',
    'voucher': 'voucher',
    'debit_card': 'carta_di_debito',
    'not_defined': 'non_definito'
}

# Liste di colonne data per conversione
COLONNE_DATA_ORDERS = [
    'data_acquisto', 
    'data_approvazione', 
    'data_spedizione', 
    'data_consegna', 
    'data_consegna_stimata'
]

COLONNE_DATA_REVIEWS = [
    'data_creazione_recensione', 
    'data_risposta_recensione'
]

# Configurazioni per binning (creazione categorie)
BINNING_CONFIG = {
    'volume_prodotto': {
        'bins': [0, 1000, 5000, 20000, float('inf')],
        'labels': ['Piccolo', 'Medio', 'Grande', 'Molto Grande']
    },
    'peso_prodotto': {
        'bins': [0, 500, 1000, 2000, float('inf')],
        'labels': ['Leggero', 'Medio', 'Pesante', 'Molto Pesante']
    },
    'valore_ordine': {
        'bins': [0, 50, 150, 300, float('inf')],
        'labels': ['Basso', 'Medio', 'Alto', 'Premium']
    },
    'giorni_consegna': {
        'bins': [0, 7, 14, 21, float('inf')],
        'labels': ['Veloce', 'Normale', 'Lento', 'Molto Lento']
    },
    'frequenza_ordini': {
        'bins': [0, 1, 3, float('inf')],
        'labels': ['Bassa', 'Media', 'Alta']
    }
}

# Configurazioni pandas per visualizzazione
PANDAS_DISPLAY_OPTIONS = {
    'display.max_columns': None,
    'display.max_rows': 10,
    'display.width': None,
    'display.float_format': '{:.2f}'.format
}

# Stile e palette per i grafici
PLOT_STYLE = 'seaborn-v0_8'
PLOT_PALETTE = 'husl'

# Configurazioni binning per compatibilità con notebook
BINNING_VALORE_ORDINE = BINNING_CONFIG['valore_ordine']
BINNING_GIORNI_CONSEGNA = BINNING_CONFIG['giorni_consegna']
