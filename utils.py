# utils.py

import logging
import os
from datetime import datetime

import numpy as np
import pandas as pd

import config

# =========================
# LOGGER
# =========================

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# =========================
# CARICAMENTO E ANALISI BASE
# =========================

def carica_dataset(path, sep=","):
    """Carica un CSV e logga shape + missing."""
    try:
        df = pd.read_csv(path, sep=sep)
        logger.info(f"Caricato dataset da {path} con shape {df.shape}")
        missing = df.isna().mean()
        logger.info(
            "Valori mancanti (prime 5 colonne con più missing):\n%s",
            missing.sort_values(ascending=False).head(5)
        )
        return df
    except FileNotFoundError:
        logger.error(f"File non trovato: {path}")
        return None
    except Exception as e:
        logger.error(f"Errore nel caricamento di {path}: {e}")
        return None


def analisi_qualita_dati(df, nome="dataset"):
    """Ritorna un piccolo report di qualità (tipi + percentuale missing)."""
    n_righe, n_colonne = df.shape
    logger.info(f"{nome}: {n_righe} righe, {n_colonne} colonne")

    missing = df.isna().mean().rename("percent_missing")
    tipi = df.dtypes.rename("dtype")
    report = pd.concat([tipi, missing], axis=1)
    return report

# =========================
# TRADUZIONE
# =========================

def traduci_dataset(df, mappa_colonne=None, mappa_valori=None):
    """
    Traduci colonne e valori (dizionario di dizionari).
    mappa_colonne: {colonna_orig: colonna_nuova}
    mappa_valori: {nome_colonna: {valore_orig: valore_nuovo}}
    """
    df_trad = df.copy()

    # colonne
    if mappa_colonne:
        # solo le colonne presenti
        mappa_filtrata = {c_old: c_new for c_old, c_new in mappa_colonne.items() if c_old in df_trad.columns}
        df_trad = df_trad.rename(columns=mappa_filtrata)

    # valori
    if mappa_valori:
        for col, mapping in mappa_valori.items():
            if col in df_trad.columns:
                df_trad[col] = df_trad[col].replace(mapping)

    return df_trad

# =========================
# DATE E DUPLICATI
# =========================

def converti_colonne_data(df, colonne):
    """Converte le colonne elencate in datetime, se esistono."""
    df = df.copy()
    for col in colonne:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def rimuovi_duplicati_avanzato(df, subset):
    """
    Rimuove duplicati sul subset indicato.
    subset può essere colonna singola (string) o lista.
    """
    df = df.copy()
    logger.info(f"Rimozione duplicati su {subset}")
    prima = len(df)
    df = df.drop_duplicates(subset=subset, keep="first")
    dopo = len(df)
    logger.info(f"Rimosse {prima - dopo} righe duplicate")
    return df

# =========================
# AGGREGAZIONI
# =========================

def aggrega_pagamenti(df_pagamenti):
    """
    Aggrega pagamenti a livello di ordine, usando le colonne tradotte:
    - 'id_ordine'
    - 'valore_pagamento' (BRL)
    - 'valore_pagamento_eur' se esiste
    """
    if df_pagamenti.empty:
        logger.warning("aggregazione pagamenti: df vuoto")
        return None

    df = df_pagamenti.copy()
    if "id_ordine" not in df.columns:
        logger.error("aggregazione pagamenti: colonna 'id_ordine' mancante")
        return None

    agg_dict = {
        "valore_pagamento": "sum",
    }
    if "sequenza_pagamento" in df.columns:
        agg_dict["sequenza_pagamento"] = "nunique"
    if "valore_pagamento_eur" in df.columns:
        agg_dict["valore_pagamento_eur"] = "sum"

    agg = (
        df.groupby("id_ordine", as_index=False)
          .agg(agg_dict)
          .rename(columns={
              "valore_pagamento": "valore_pagamento_brl",
              "sequenza_pagamento": "n_pagamenti",
              "valore_pagamento_eur": "valore_pagamento_eur"
          })
    )
    logger.info(f"Pagamenti aggregati con shape {agg.shape}")
    return agg


def aggrega_order_items(df_items):
    """
    Aggrega order_items a livello di 'id_ordine' con colonne tradotte:
    - 'id_articolo_ordine'
    - 'prezzo' (BRL)
    - 'costo_spedizione' (BRL)
    - versioni in EUR se presenti
    """
    if df_items.empty:
        logger.warning("aggregazione order_items: df vuoto")
        return None

    df = df_items.copy()
    if "id_ordine" not in df.columns:
        logger.error("aggregazione order_items: colonna 'id_ordine' mancante")
        return None

    agg_dict = {
        "id_articolo_ordine": "count",
    }
    if "prezzo" in df.columns:
        agg_dict["prezzo"] = "sum"
    if "costo_spedizione" in df.columns:
        agg_dict["costo_spedizione"] = "sum"
    if "prezzo_eur" in df.columns:
        agg_dict["prezzo_eur"] = "sum"
    if "costo_spedizione_eur" in df.columns:
        agg_dict["costo_spedizione_eur"] = "sum"

    agg = (
        df.groupby("id_ordine", as_index=False)
          .agg(agg_dict)
          .rename(columns={
              "id_articolo_ordine": "n_articoli",
              "prezzo": "totale_prezzo_brl",
              "costo_spedizione": "totale_spedizione_brl",
              "prezzo_eur": "totale_prezzo_eur",
              "costo_spedizione_eur": "totale_spedizione_eur",
          })
    )

    # totale_ordine_eur se abbiamo sia prezzo_eur che spedizione_eur
    if "totale_prezzo_eur" in agg.columns and "totale_spedizione_eur" in agg.columns:
        agg["totale_ordine_eur"] = agg["totale_prezzo_eur"].fillna(0) + agg["totale_spedizione_eur"].fillna(0)

    logger.info(f"Order_items aggregati con shape {agg.shape}")
    return agg


def aggrega_reviews(df_reviews):
    """
    Aggrega recensioni per 'id_ordine':
    - punteggio medio
    - numero recensioni
    - data prima/ultima recensione
    """
    if df_reviews.empty:
        logger.warning("aggregazione reviews: df vuoto")
        return None

    df = df_reviews.copy()
    if "id_ordine" not in df.columns:
        logger.error("aggregazione reviews: colonna 'id_ordine' mancante")
        return None

    agg = (
        df.groupby("id_ordine", as_index=False)
          .agg({
              "punteggio_recensione": "mean",
              "id_recensione": "count",
              "data_creazione_recensione": "min",
              "data_risposta_recensione": "max",
          })
          .rename(columns={
              "punteggio_recensione": "punteggio_medio",
              "id_recensione": "n_recensioni",
              "data_creazione_recensione": "prima_recensione",
              "data_risposta_recensione": "ultima_risposta",
          })
    )
    logger.info(f"Reviews aggregate con shape {agg.shape}")
    return agg

# =========================
# FEATURE ENGINEERING
# =========================

def calcola_metriche_temporali(df):
    """
    Su df con:
    - data_acquisto
    - data_consegna
    - data_consegna_stimata
    aggiunge:
    - giorni_consegna
    - ritardo_consegna (consegna - stimata)
    """
    df = df.copy()
    if "data_acquisto" in df.columns and "data_consegna" in df.columns:
        df["giorni_consegna"] = (df["data_consegna"] - df["data_acquisto"]).dt.days

    if "data_consegna" in df.columns and "data_consegna_stimata" in df.columns:
        df["ritardo_consegna"] = (df["data_consegna"] - df["data_consegna_stimata"]).dt.days

    return df


def crea_categorie_binning(df, colonna, bins, labels, nome_nuova):
    """Crea una colonna categoriale con pd.cut."""
    df = df.copy()
    if colonna not in df.columns:
        logger.warning(f"crea_categorie_binning: colonna {colonna} non trovata")
        return df
    df[nome_nuova] = pd.cut(df[colonna], bins=bins, labels=labels, include_lowest=True)
    return df


def segmenta_clienti(df):
    """
    Segmentazione RFM semplificata:
    - recency: giorni dall'ultimo acquisto
    - frequency: numero ordini
    - monetary: somma colonna_valore (EUR se disponibile)
    """
    if "id_cliente" not in df.columns or "id_ordine" not in df.columns or "data_acquisto" not in df.columns:
        logger.warning("segmenta_clienti: colonne minime mancanti")
        return df, None

    colonna_valore = "totale_ordine_eur" if "totale_ordine_eur" in df.columns else "valore_pagamento_eur"
    if colonna_valore not in df.columns:
        logger.warning("segmenta_clienti: colonna monetaria non trovata, uso 0")
        df[colonna_valore] = 0.0

    ref_date = df["data_acquisto"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("id_cliente").agg(
        recency=("data_acquisto", lambda x: (ref_date - x.max()).days),
        frequency=("id_ordine", "count"),
        monetary=(colonna_valore, "sum"),
    ).reset_index()

    # segmenti grezzi (solo per avere un esempio)
    rfm["segmento"] = "bronze"
    rfm.loc[(rfm["frequency"] >= 3) & (rfm["monetary"] >= rfm["monetary"].median()), "segmento"] = "silver"
    rfm.loc[(rfm["frequency"] >= 5) & (rfm["monetary"] >= rfm["monetary"].quantile(0.75)), "segmento"] = "gold"

    df_seg = df.merge(rfm[["id_cliente", "segmento"]], on="id_cliente", how="left")

    stats_segmentazione = rfm["segmento"].value_counts()
    logger.info("Segmentazione clienti (conteggio per segmento):\n%s", stats_segmentazione.to_string())
    return df_seg, stats_segmentazione

# =========================
# SALVATAGGIO E STATISTICHE FINALI
# =========================

def salva_dataset(df, nome_file):
    """Salva in config.OUTPUT_DIR."""
    path = os.path.join(config.OUTPUT_DIR, nome_file)
    df.to_csv(path, index=False)
    logger.info(f"Dataset salvato in {path}")
    return path


def stampa_statistiche_finali(df_ordini):
    """Stampa statistiche base sul valore monetario ordine."""
    colonna_valore = "totale_ordine_eur" if "totale_ordine_eur" in df_ordini.columns else "valore_pagamento_eur"
    if colonna_valore not in df_ordini.columns:
        logger.warning("stampa_statistiche_finali: colonna valore non trovata")
        return

    serie = df_ordini[colonna_valore].dropna()
    logger.info(f"Statistiche per {colonna_valore}:")
    logger.info("count: %d", serie.count())
    logger.info("mean: %.2f", serie.mean())
    logger.info("median: %.2f", serie.median())
    logger.info("std: %.2f", serie.std())
    logger.info("min: %.2f", serie.min())
    logger.info("max: %.2f", serie.max())