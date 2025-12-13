import pandas as pd
import logging
from config import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Funzione per caricare dataset

def carica_dataset(nome_file, sep=';', encoding='utf-8'):
    """Carica un dataset CSV con parametri configurabili."""
    try:
        df = pd.read_csv(nome_file, sep=sep, encoding=encoding)
        logging.info(f"Dataset {nome_file} caricato con successo.")
        return df
    except Exception as e:
        logging.error(f"Errore nel caricamento del file {nome_file}: {e}")
        return None

# Funzione per analisi qualità dati

def analisi_qualita_dati(df):
    """Restituisce un DataFrame con informazioni su valori nulli e duplicati."""
    info = pd.DataFrame()
    info['missing'] = df.isnull().sum()
    info['missing_percent'] = df.isnull().mean() * 100
    info['duplicati'] = df.duplicated().sum()
    return info

# Funzione per traduzione dataset

def traduci_dataset(df, dizionario_traduzione):
    """Sostituisce i valori delle colonne del dataset secondo un dizionario di traduzione."""
    df_tradotto = df.copy()
    for colonna, mappa in dizionario_traduzione.items():
        if colonna in df_tradotto.columns:
            df_tradotto[colonna] = df_tradotto[colonna].map(mappa).fillna(df_tradotto[colonna])
    return df_tradotto

# Funzione per conversione colonne data

def converti_colonne_data(df, colonne):
    """Converte le colonne specificate in formato datetime."""
    for col in colonne:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

# Funzione per rimuovere duplicati avanzato

def rimuovi_duplicati_avanzato(df, subset=None):
    """Rimuove duplicati basandosi su subset di colonne, se fornito."""
    if subset:
        df_clean = df.drop_duplicates(subset=subset)
    else:
        df_clean = df.drop_duplicates()
    return df_clean

# Funzioni per aggregazione dati

def aggrega_pagamenti(df_pagamenti):
    """Aggrega i pagamenti per ordine."""
    agg = df_pagamenti.groupby('order_id').agg(
        pagamento_totale=('payment_value', 'sum'),
        num_pagamenti=('payment_sequential', 'max'),
        tipo_pagamento_principale=('payment_type', lambda x: x.mode().iloc[0] if not x.mode().empty else None)
    ).reset_index()
    return agg

def aggrega_order_items(df_items):
    """Aggrega gli articoli per ordine."""
    agg = df_items.groupby('order_id').agg(
        num_articoli=('order_item_id', 'count'),
        prezzo_totale=('price', 'sum'),
        spedizione_totale=('freight_value', 'sum')
    ).reset_index()
    return agg

def aggrega_reviews(df_reviews):
    """Aggrega le recensioni per ordine."""
    agg = df_reviews.groupby('order_id').agg(
        punteggio_medio=('review_score', 'mean'),
        num_recensioni=('review_id', 'count')
    ).reset_index()
    return agg

# Funzioni per feature engineering

def calcola_metriche_temporali(df):
    """Calcola metriche temporali come giorni di consegna e ritardi."""
    df['giorni_consegna'] = (df['data_consegna'] - df['data_acquisto']).dt.days
    df['ritardo_consegna'] = (df['data_consegna'] - df['data_consegna_stimata']).dt.days
    return df

def crea_categorie_binning(df, colonna, bins, labels):
    """Crea categorie per una colonna numerica usando binning."""
    df[f'{colonna}_cat'] = pd.cut(df[colonna], bins=bins, labels=labels, include_lowest=True)
    return df

# Funzioni per output

def salva_dataset(df, nome_file):
    """Salva il DataFrame in formato CSV nella cartella di output."""
    percorso = OUTPUT_PATH / nome_file
    df.to_csv(percorso, index=False, sep=';')
    logging.info(f"Dataset salvato in {percorso}")


def stampa_statistiche_finali(df):
    """Stampa statistiche descrittive finali del dataset."""
    print(df.describe(include='all'))
