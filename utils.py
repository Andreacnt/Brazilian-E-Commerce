import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
import config

# ======================================================================
# CONFIGURAZIONE LOGGER
# ======================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ======================================================================
# FUNZIONI DI CARICAMENTO / SALVATAGGIO
# ======================================================================

def carica_dataset(
    nome_file: str,
    data_path: Path = config.DATA_PATH,
    sep: str = ',',
    encoding: str = 'utf-8'
) -> Optional[pd.DataFrame]:
    """
    Carica un dataset CSV con gestione errori specifica.
    """
    file_path = data_path / nome_file

    try:
        logger.info(f"Caricamento dataset: {file_path}")
        df = pd.read_csv(file_path, sep=sep, encoding=encoding)
        logger.info(f"✓ Dataset caricato: {df.shape[0]} righe, {df.shape[1]} colonne")
        return df
    except FileNotFoundError:
        logger.error(f"✗ File non trovato: {file_path}")
        return None
    except pd.errors.ParserError as e:
        logger.error(f"✗ Errore parsing CSV {nome_file}: {e}")
        return None
    except Exception as e:
        logger.error(f"✗ Errore imprevisto caricando {nome_file}: {e}")
        return None


def salva_dataset(
    df: pd.DataFrame,
    nome_file: str,
    data_path: Path = config.OUTPUT_PATH,
    sep: str = ',',
    encoding: str = 'utf-8-sig'
) -> None:
    """
    Salva DataFrame in CSV.
    """
    output_path = data_path / nome_file

    try:
        data_path.mkdir(exist_ok=True, parents=True)
        df.to_csv(output_path, index=False, sep=sep, encoding=encoding)
        logger.info(f"✓ Dataset salvato: {output_path}")
        logger.info(f"  Dimensioni: {df.shape[0]} righe × {df.shape[1]} colonne")
    except Exception as e:
        logger.error(f"✗ Errore salvataggio {nome_file}: {e}")


# ======================================================================
# ANALISI QUALITÀ DATI
# ======================================================================

def analisi_qualita_dati(df: pd.DataFrame, nome_dataset: str = "") -> pd.DataFrame:
    """
    Analisi base qualità dati: valori mancanti e duplicati per colonna.
    """
    logger.info(f"\n{'='*50}")
    logger.info(f"ANALISI QUALITÀ DATI - {nome_dataset.upper() if nome_dataset else ''}")
    logger.info(f"{'='*50}")
    logger.info(f"Shape: {df.shape}")
    logger.info(f"Valori nulli totali: {df.isnull().sum().sum()}")
    logger.info(f"Duplicati totali: {df.duplicated().sum()}")
    logger.info(f"Memoria: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    return df


# ======================================================================
# TRADUZIONE E PREPARAZIONE DATASET
# ======================================================================

def traduci_dataset(
    df: pd.DataFrame,
    traduzione_colonne: Dict[str, str],
    traduzione_valori: Optional[Dict[str, Dict[str, str]]] = None
) -> pd.DataFrame:
    """
    Traduce nomi colonne e valori categorici di un DataFrame.
    
    Args:
        df: DataFrame da tradurre
        traduzione_colonne: Dizionario {nome_originale: nome_tradotto}
        traduzione_valori: Dizionario {nome_colonna: {valore_orig: valore_trad}}
        
    Returns:
        DataFrame tradotto
    """
    df_tradotto = df.copy()
    
    # Traduzione colonne
    df_tradotto = df_tradotto.rename(columns=traduzione_colonne)
    
    # Traduzione valori
    if traduzione_valori:
        for colonna, mappatura in traduzione_valori.items():
            if colonna in df_tradotto.columns:
                df_tradotto[colonna] = df_tradotto[colonna].map(mappatura).fillna(df_tradotto[colonna])
                logger.info(f"✓ Valori colonna '{colonna}' tradotti")
    
    return df_tradotto


def converti_colonne_data(df: pd.DataFrame, colonne: List[str]) -> pd.DataFrame:
    """
    Converte le colonne specificate in formato datetime.
    """
    df_copy = df.copy()

    for col in colonne:
        if col in df_copy.columns:
            try:
                df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
                logger.info(f"✓ Colonna '{col}' convertita a datetime")
            except Exception as e:
                logger.warning(f"⚠ Impossibile convertire '{col}': {e}")

    return df_copy


def rimuovi_duplicati_avanzato(
    df: pd.DataFrame,
    subset: Optional[str | List[str]] = None,
    keep: str = 'first'
) -> pd.DataFrame:
    """
    Rimuove duplicati con opzioni avanzate.
    Accetta subset come stringa singola o lista.
    """
    df_clean = df.copy()
    
    # Converti stringa in lista se necessario
    if isinstance(subset, str):
        subset = [subset]
    
    num_duplicati_prima = df_clean.duplicated(subset=subset).sum()

    if num_duplicati_prima == 0:
        logger.info("✓ Nessun duplicato trovato")
        return df_clean

    df_clean = df_clean.drop_duplicates(subset=subset, keep=keep)
    num_rimossi = num_duplicati_prima

    logger.info(f"✓ {num_rimossi} duplicati rimossi")
    logger.info(f"   Righe prima: {len(df):,} → dopo: {len(df_clean):,}")

    return df_clean


# ======================================================================
# AGGREGAZIONI (PAGAMENTI, ITEMS, REVIEWS)
# ======================================================================

def aggrega_pagamenti(df_pagamenti: pd.DataFrame) -> pd.DataFrame:
    """
    Aggrega i pagamenti per ordine.
    """
    if df_pagamenti.empty:
        return pd.DataFrame()
    
    # Trova la colonna id_ordine (potrebbe essere tradotta)
    id_col = None
    for col in ['id_ordine', 'order_id']:
        if col in df_pagamenti.columns:
            id_col = col
            break
    
    if id_col is None:
        logger.warning("⚠ Colonna id_ordine non trovata in pagamenti")
        return pd.DataFrame()
    
    # Trova colonne valore
    val_col = None
    for col in ['valore_pagamento_eur', 'payment_value', 'valore_pagamento']:
        if col in df_pagamenti.columns:
            val_col = col
            break
    
    type_col = None
    for col in ['tipo_pagamento', 'payment_type']:
        if col in df_pagamenti.columns:
            type_col = col
            break
    
    seq_col = None
    for col in ['sequenza_pagamento', 'payment_sequential']:
        if col in df_pagamenti.columns:
            seq_col = col
            break
    
    agg_dict = {}
    if val_col:
        agg_dict['pagamento_totale'] = (val_col, 'sum')
    if seq_col:
        agg_dict['num_pagamenti'] = (seq_col, 'max')
    if type_col:
        agg_dict['tipo_pagamento_principale'] = (
            type_col,
            lambda x: x.mode().iloc[0] if not x.mode().empty else None
        )
    
    if not agg_dict:
        logger.warning("⚠ Nessuna colonna valida trovata per aggregazione pagamenti")
        return pd.DataFrame()
    
    agg = df_pagamenti.groupby(id_col).agg(**agg_dict).reset_index()
    logger.info("✓ Pagamenti aggregati per ordine")
    return agg


def aggrega_order_items(df_items: pd.DataFrame) -> pd.DataFrame:
    """
    Aggrega gli articoli per ordine.
    """
    if df_items.empty:
        return pd.DataFrame()
    
    id_col = None
    for col in ['id_ordine', 'order_id']:
        if col in df_items.columns:
            id_col = col
            break
    
    if id_col is None:
        logger.warning("⚠ Colonna id_ordine non trovata in order_items")
        return pd.DataFrame()
    
    item_id_col = None
    for col in ['id_articolo_ordine', 'order_item_id']:
        if col in df_items.columns:
            item_id_col = col
            break
    
    price_col = None
    for col in ['prezzo_eur', 'price', 'prezzo']:
        if col in df_items.columns:
            price_col = col
            break
    
    freight_col = None
    for col in ['costo_spedizione_eur', 'freight_value', 'costo_spedizione']:
        if col in df_items.columns:
            freight_col = col
            break
    
    total_col = None
    for col in ['totale_articolo_eur', 'totale_ordine_eur']:
        if col in df_items.columns:
            total_col = col
            break
    
    agg_dict = {}
    if item_id_col:
        agg_dict['num_articoli'] = (item_id_col, 'count')
    if price_col:
        agg_dict['prezzo_totale'] = (price_col, 'sum')
    if freight_col:
        agg_dict['spedizione_totale'] = (freight_col, 'sum')
    if total_col:
        agg_dict['totale_ordine_eur'] = (total_col, 'sum')
    
    if not agg_dict:
        logger.warning("⚠ Nessuna colonna valida trovata per aggregazione items")
        return pd.DataFrame()
    
    agg = df_items.groupby(id_col).agg(**agg_dict).reset_index()
    logger.info("✓ Articoli aggregati per ordine")
    return agg


def aggrega_reviews(df_reviews: pd.DataFrame) -> pd.DataFrame:
    """
    Aggrega le recensioni per ordine.
    """
    if df_reviews.empty:
        return pd.DataFrame()
    
    id_col = None
    for col in ['id_ordine', 'order_id']:
        if col in df_reviews.columns:
            id_col = col
            break
    
    if id_col is None:
        logger.warning("⚠ Colonna id_ordine non trovata in reviews")
        return pd.DataFrame()
    
    score_col = None
    for col in ['punteggio_recensione', 'review_score']:
        if col in df_reviews.columns:
            score_col = col
            break
    
    review_id_col = None
    for col in ['id_recensione', 'review_id']:
        if col in df_reviews.columns:
            review_id_col = col
            break
    
    agg_dict = {}
    if score_col:
        agg_dict['punteggio_medio'] = (score_col, 'mean')
    if review_id_col:
        agg_dict['num_recensioni'] = (review_id_col, 'count')
    
    if not agg_dict:
        logger.warning("⚠ Nessuna colonna valida trovata per aggregazione reviews")
        return pd.DataFrame()
    
    agg = df_reviews.groupby(id_col).agg(**agg_dict).reset_index()
    logger.info("✓ Recensioni aggregate per ordine")
    return agg


# ======================================================================
# FEATURE ENGINEERING
# ======================================================================

def calcola_metriche_temporali(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcola metriche temporali come giorni di consegna e ritardi.
    """
    df_copy = df.copy()

    if 'data_consegna' in df_copy.columns and 'data_acquisto' in df_copy.columns:
        df_copy['giorni_consegna'] = (
            df_copy['data_consegna'] - df_copy['data_acquisto']
        ).dt.days

    if 'data_consegna' in df_copy.columns and 'data_consegna_stimata' in df_copy.columns:
        df_copy['ritardo_consegna'] = (
            df_copy['data_consegna'] - df_copy['data_consegna_stimata']
        ).dt.days

    if 'data_acquisto' in df_copy.columns:
        df_copy['mese_acquisto'] = df_copy['data_acquisto'].dt.to_period('M')
        df_copy['anno_acquisto'] = df_copy['data_acquisto'].dt.year
        df_copy['giorno_settimana'] = df_copy['data_acquisto'].dt.day_name()

    logger.info("✓ Metriche temporali calcolate")
    return df_copy


def crea_categorie_binning(
    df: pd.DataFrame,
    colonna: str,
    bins: List[float],
    labels: List[str],
    nome_output: Optional[str] = None
) -> pd.DataFrame:
    """
    Crea categorie per una colonna numerica usando binning.
    """
    df_copy = df.copy()
    if colonna not in df_copy.columns:
        logger.warning(f"⚠ Colonna '{colonna}' non trovata per binning")
        return df_copy

    out_col = nome_output or f"{colonna}_cat"
    df_copy[out_col] = pd.cut(
        df_copy[colonna],
        bins=bins,
        labels=labels,
        include_lowest=True
    )
    logger.info(f"✓ Binning creato per '{colonna}' → '{out_col}'")
    return df_copy


def segmenta_clienti(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Segmenta clienti per frequenza e valore (RFM semplificato).
    
    Returns:
        Tupla (df_originale, df_segmentazione_clienti)
    """
    # Trova colonne necessarie
    id_cliente_col = None
    for col in ['id_cliente', 'customer_id']:
        if col in df.columns:
            id_cliente_col = col
            break
    
    id_ordine_col = None
    for col in ['id_ordine', 'order_id']:
        if col in df.columns:
            id_ordine_col = col
            break
    
    valore_col = None
    for col in ['totale_ordine_eur', 'valore_pagamento_eur', 'pagamento_totale']:
        if col in df.columns:
            valore_col = col
            break
    
    data_col = None
    for col in ['data_acquisto', 'order_purchase_timestamp']:
        if col in df.columns:
            data_col = col
            break
    
    if not all([id_cliente_col, id_ordine_col, valore_col, data_col]):
        logger.warning("⚠ Colonne necessarie per segmentazione clienti non trovate")
        return df, pd.DataFrame()
    
    clienti_stats = df.groupby(id_cliente_col).agg({
        id_ordine_col: 'nunique',
        valore_col: 'sum',
        data_col: ['min', 'max']
    }).reset_index()
    
    clienti_stats.columns = ['id_cliente', 'num_ordini', 'spesa_totale', 'primo_acquisto', 'ultimo_acquisto']
    clienti_stats['vita_cliente_giorni'] = (
        clienti_stats['ultimo_acquisto'] - clienti_stats['primo_acquisto']
    ).dt.days
    clienti_stats['spesa_media_ordine'] = clienti_stats['spesa_totale'] / clienti_stats['num_ordini']
    
    # Segmentazione frequenza
    try:
        clienti_stats['segmento_frequenza'] = pd.cut(
            clienti_stats['num_ordini'],
            bins=config.BINNING_CONFIG['frequenza_ordini']['bins'],
            labels=config.BINNING_CONFIG['frequenza_ordini']['labels']
        )
    except:
        logger.warning("⚠ Impossibile creare segmento_frequenza")
    
    # Segmentazione valore
    try:
        clienti_stats['segmento_valore'] = pd.qcut(
            clienti_stats['spesa_totale'],
            q=3,
            labels=['Basso', 'Medio', 'Alto'],
            duplicates='drop'
        )
    except:
        logger.warning("⚠ Impossibile creare segmento_valore")
    
    logger.info("✓ Segmentazione clienti completata")
    return df, clienti_stats


# ======================================================================
# STATISTICHE FINALI
# ======================================================================

def stampa_statistiche_finali(df: pd.DataFrame) -> None:
    """
    Stampa statistiche descrittive finali del dataset.
    """
    logger.info("\n" + "="*60)
    logger.info("STATISTICHE FINALI DATASET")
    logger.info("="*60)

    try:
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Memoria: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Cerca colonne chiave
        for col_name in ['id_ordine', 'order_id']:
            if col_name in df.columns:
                logger.info(f"Ordini totali: {df[col_name].nunique():,}")
                break
        
        for col_name in ['id_cliente', 'customer_id']:
            if col_name in df.columns:
                logger.info(f"Clienti unici: {df[col_name].nunique():,}")
                break
        
        for col_name in ['totale_ordine_eur', 'valore_pagamento_eur', 'pagamento_totale']:
            if col_name in df.columns:
                logger.info(f"Valore medio ordine: €{df[col_name].mean():.2f}")
                logger.info(f"Valore totale: €{df[col_name].sum():,.2f}")
                break
                
    except Exception as e:
        logger.warning(f"⚠ Errore nel calcolo statistiche: {e}")