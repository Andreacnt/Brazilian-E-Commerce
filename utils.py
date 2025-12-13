"""
Modulo di funzioni di utilità per l'analisi dei dati Olist.
Contiene funzioni per caricamento, pulizia, traduzione e aggregazione dei dati.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import config

# Configurazione logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def carica_dataset(nome_file):
    """
    Carica un dataset CSV gestendo eventuali errori.
    
    Args:
        nome_file (str): Nome del file CSV da caricare
        
    Returns:
        pd.DataFrame or None: DataFrame caricato o None se errore
    """
    try:
        file_path = config.DATA_PATH / nome_file
        df = pd.read_csv(file_path, low_memory=False)
        logger.info(f"Dataset {nome_file} caricato con successo: {df.shape}")
        return df
    except FileNotFoundError:
        logger.error(f"File non trovato: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Errore nel caricamento di {nome_file}: {e}")
        return None

def analisi_qualita_dati(df, nome_dataset):
    """
    Esegue un'analisi di base sulla qualità del dataset.
    
    Args:
        df (pd.DataFrame): DataFrame da analizzare
        nome_dataset (str): Nome identificativo del dataset
    """
    print(f"\n=== ANALISI QUALITA' DATI: {nome_dataset} ===")
    print(f"Dimensioni: {df.shape}")
    print(f"Valori mancanti totali: {df.isnull().sum().sum()}")
    print(f"Duplicati: {df.duplicated().sum()}")
    print(f"Tipi di dato:\n{df.dtypes.value_counts()}")

def traduci_dataset(df, mappa_colonne, mappa_valori=None):
    """
    Traduce nomi colonne e valori secondo le mappe fornite.
    
    Args:
        df (pd.DataFrame): DataFrame da tradurre
        mappa_colonne (dict): Dizionario {vecchio_nome: nuovo_nome}
        mappa_valori (dict): Dizionario {colonna: {vecchio_valore: nuovo_valore}}
        
    Returns:
        pd.DataFrame: DataFrame con colonne e valori tradotti
    """
    df_tradotto = df.rename(columns=mappa_colonne)
    
    if mappa_valori:
        for colonna, mappa in mappa_valori.items():
            colonna_nuova = mappa_colonne.get(colonna, colonna)
            if colonna_nuova in df_tradotto.columns:
                df_tradotto[colonna_nuova] = df_tradotto[colonna_nuova].replace(mappa)
    
    return df_tradotto

def converti_colonne_data(df, colonne_data):
    """
    Converte le colonne specificate in formato datetime.
    
    Args:
        df (pd.DataFrame): DataFrame da processare
        colonne_data (list): Lista di nomi di colonne da convertire
        
    Returns:
        pd.DataFrame: DataFrame con colonne convertite
    """
    df_convertito = df.copy()
    for col in colonne_data:
        if col in df_convertito.columns:
            df_convertito[col] = pd.to_datetime(df_convertito[col], errors='coerce')
    return df_convertito

def rimuovi_duplicati_avanzato(df, subset=None):
    """
    Rimuove duplicati con log dettagliato.
    
    Args:
        df (pd.DataFrame): DataFrame da processare
        subset (str or list): Colonne su cui controllare duplicati
        
    Returns:
        pd.DataFrame: DataFrame senza duplicati
    """
    duplicati_iniziali = df.duplicated(subset=subset).sum()
    df_pulito = df.drop_duplicates(subset=subset, keep='first')
    
    if duplicati_iniziali > 0:
        logger.info(f"Rimossi {duplicati_iniziali} duplicati da {subset if subset else 'tutte le colonne'}")
    
    return df_pulito

def aggrega_pagamenti(df_pagamenti):
    """
    Aggrega i dati di pagamento per ordine.
    
    Args:
        df_pagamenti (pd.DataFrame): DataFrame pagamenti
        
    Returns:
        pd.DataFrame: DataFrame aggregato per ordine
    """
    if df_pagamenti.empty:
        return None
    
    agg_pagamenti = df_pagamenti.groupby('id_ordine').agg({
        'tipo_pagamento': lambda x: x.mode().iloc[0] if not x.mode().empty else 'non_definito',
        'valore_pagamento': 'sum',
        'rate_pagamento': 'max'
    }).reset_index()
    
    agg_pagamenti.rename(columns={
        'tipo_pagamento': 'tipo_pagamento_principale',
        'valore_pagamento': 'valore_pagamento_totale',
        'rate_pagamento': 'massimo_rate'
    }, inplace=True)
    
    return agg_pagamenti

def aggrega_order_items(df_items):
    """
    Aggrega i dati degli articoli per ordine.
    
    Args:
        df_items (pd.DataFrame): DataFrame articoli
        
    Returns:
        pd.DataFrame: DataFrame aggregato per ordine
    """
    if df_items.empty:
        return None
    
    agg_items = df_items.groupby('id_ordine').agg({
        'id_prodotto': 'count',
        'prezzo': 'sum',
        'costo_spedizione': 'sum'
    }).reset_index()
    
    agg_items.rename(columns={
        'id_prodotto': 'numero_articoli',
        'prezzo': 'totale_prezzo',
        'costo_spedizione': 'totale_spedizione'
    }, inplace=True)
    
    # Aggiunta totale ordine in EUR se presenti le colonne convertite
    if 'prezzo_eur' in df_items.columns and 'costo_spedizione_eur' in df_items.columns:
        agg_items_eur = df_items.groupby('id_ordine').agg({
            'prezzo_eur': 'sum',
            'costo_spedizione_eur': 'sum'
        }).reset_index()
        
        agg_items = agg_items.merge(agg_items_eur, on='id_ordine', how='left')
        agg_items['totale_ordine_eur'] = agg_items['prezzo_eur'] + agg_items['costo_spedizione_eur']
    
    return agg_items

def aggrega_reviews(df_reviews):
    """
    Aggrega i dati delle recensioni per ordine.
    
    Args:
        df_reviews (pd.DataFrame): DataFrame recensioni
        
    Returns:
        pd.DataFrame: DataFrame aggregato per ordine
    """
    if df_reviews.empty:
        return None
    
    agg_reviews = df_reviews.groupby('id_ordine').agg({
        'punteggio_recensione': 'mean',
        'id_recensione': 'count'
    }).reset_index()
    
    agg_reviews.rename(columns={
        'punteggio_recensione': 'punteggio_medio_recensioni',
        'id_recensione': 'numero_recensioni'
    }, inplace=True)
    
    return agg_reviews

def calcola_metriche_temporali(df):
    """
    Calcola metriche temporali come giorni di consegna e tempo di approvazione.
    
    Args:
        df (pd.DataFrame): DataFrame ordini
        
    Returns:
        pd.DataFrame: DataFrame con metriche temporali aggiunte
    """
    df_temporale = df.copy()
    
    # Giorni per la spedizione
    if 'data_approvazione' in df_temporale.columns and 'data_spedizione' in df_temporale.columns:
        df_temporale['giorni_approvazione_spedizione'] = (
            df_temporale['data_spedizione'] - df_temporale['data_approvazione']
        ).dt.days
    
    # Giorni di consegna effettivi
    if 'data_acquisto' in df_temporale.columns and 'data_consegna' in df_temporale.columns:
        df_temporale['giorni_consegna'] = (
            df_temporale['data_consegna'] - df_temporale['data_acquisto']
        ).dt.days
    
    # Differenza tra consegna stimata e effettiva
    if 'data_consegna_stimata' in df_temporale.columns and 'data_consegna' in df_temporale.columns:
        df_temporale['differenza_giorni_stima'] = (
            df_temporale['data_consegna'] - df_temporale['data_consegna_stimata']
        ).dt.days
    
    return df_temporale

def crea_categorie_binning(df, colonna, bins, labels, nome_nuova_colonna):
    """
    Crea categorie discrete da una colonna numerica usando binning.
    
    Args:
        df (pd.DataFrame): DataFrame da processare
        colonna (str): Nome della colonna da discretizzare
        bins (list): Lista di limiti dei bin
        labels (list): Lista di etichette per i bin
        nome_nuova_colonna (str): Nome della nuova colonna categorica
        
    Returns:
        pd.DataFrame: DataFrame con nuova colonna categorica
    """
    df_binned = df.copy()
    df_binned[nome_nuova_colonna] = pd.cut(
        df_binned[colonna], 
        bins=bins, 
        labels=labels, 
        include_lowest=True
    )
    return df_binned

def segmenta_clienti(df):
    """
    Crea una semplice segmentazione RFM dei clienti.
    
    Args:
        df (pd.DataFrame): DataFrame ordini
        
    Returns:
        tuple: (DataFrame con segmentazione, dict con stats)
    """
    if 'data_acquisto' not in df.columns or 'id_cliente' not in df.columns:
        logger.warning("Colonne necessarie per RFM non presenti")
        return df, {}
    
    # Determina la colonna del valore monetario
    colonna_valore = 'totale_ordine_eur' if 'totale_ordine_eur' in df.columns else 'valore_pagamento'
    if colonna_valore not in df.columns:
        logger.warning("Nessuna colonna valore monetario trovata per RFM")
        return df, {}
    
    # Calcolo RFM
    ref_date = df['data_acquisto'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('id_cliente').agg({
        'data_acquisto': lambda x: (ref_date - x.max()).days,  # Recency
        'id_ordine': 'count',  # Frequency
        colonna_valore: 'sum'  # Monetary
    }).reset_index()
    
    rfm.columns = ['id_cliente', 'recency', 'frequency', 'monetary']
    
    # Assegnazione punteggi RFM (1-5)
    rfm['r_score'] = pd.qcut(rfm['recency'].rank(method='first'), 5, labels=[5,4,3,2,1])
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
    rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1,2,3,4,5])
    
    # Segmentazione semplice basata su F e M
    conditions = [
        (rfm['f_score'].astype(int) >= 4) & (rfm['m_score'].astype(int) >= 4),
        (rfm['f_score'].astype(int) >= 3) & (rfm['m_score'].astype(int) >= 3),
        (rfm['f_score'].astype(int) <= 2) & (rfm['m_score'].astype(int) <= 2)
    ]
    choices = ['Alto Valore', 'Medio Valore', 'Basso Valore']
    rfm['segmento_cliente'] = np.select(conditions, choices, default='Medio-Basso Valore')
    
    # Merge con dataset principale
    df_segmentato = df.merge(rfm[['id_cliente', 'segmento_cliente']], on='id_cliente', how='left')
    
    # Statistiche segmentazione
    stats = {
        'totale_clienti': len(rfm),
        'clienti_per_segmento': rfm['segmento_cliente'].value_counts().to_dict()
    }
    
    logger.info(f"Segmentazione clienti completata: {stats['clienti_per_segmento']}")
    return df_segmentato, stats

def salva_dataset(df, nome_file):
    """
    Salva il dataset in formato CSV con log.
    
    Args:
        df (pd.DataFrame): DataFrame da salvare
        nome_file (str): Nome del file di output
    """
    try:
        output_path = config.OUTPUT_PATH / nome_file
        df.to_csv(output_path, index=False)
        logger.info(f"Dataset salvato in {output_path}: {df.shape}")
    except Exception as e:
        logger.error(f"Errore nel salvataggio di {nome_file}: {e}")

def stampa_statistiche_finali(df):
    """
    Stampa statistiche finali del dataset.
    
    Args:
        df (pd.DataFrame): DataFrame finale
    """
    print("\n" + "="*60)
    print("STATISTICHE FINALI DATASET")
    print("="*60)
    print(f"Dimensioni finali: {df.shape}")
    print(f"Numero ordini unici: {df['id_ordine'].nunique()}")
    print(f"Numero clienti unici: {df['id_cliente'].nunique()}")
    print(f"Periodo analisi: {df['data_acquisto'].min()} a {df['data_acquisto'].max()}")