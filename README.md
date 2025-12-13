# Brazilian-E-Commerce
# Analisi Esplorativa E-commerce Brasiliano (Olist)

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
 ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

---

## Descrizione

Questo progetto contiene un'analisi completa del dataset **Olist**, con pulizia dati, feature engineering e analisi statistica esplorativa.

---

## Struttura delle cartelle

```
/ (cartella principale)
│
├── data/                   # Dataset originali CSV (non versionati su Git)
├── outputs/                # File generati: dataset puliti, grafici, ecc. (non versionati su Git)
│   └── figures/            # Grafici salvati
├── eda.ipynb               # Notebook Jupyter con l'analisi
├── config.py               # Configurazioni e percorsi
├── utils.py                # Funzioni di utilità per caricamento, pulizia, aggregazione
├── requirements.txt        # Dipendenze Python
├── .gitignore              # File per escludere file/cartelle da Git
└── README.md               # Questo file
```

---

## Come usare

1. Clona il repository:

```bash
git clone <URL-del-repository>
cd <nome-cartella>
```

1. Crea e attiva un ambiente virtuale:

```bash
python -m venv env
source env/bin/activate  # Linux/macOS
.\env\Scripts\activate   # Windows
```

1. Installa le dipendenze:

```bash
pip install -r requirements.txt
```

1. Scarica i dataset originali e posizionali nella cartella `data/`

2. Esegui il notebook Jupyter:

```bash
jupyter notebook eda.ipynb
```

---

## Librerie principali

* `pandas`, `numpy` per manipolazione dati

* `matplotlib`, `seaborn` per visualizzazioni

* `scipy` per test statistici

* `missingno` per analisi dati mancanti

---

## Licenza

Questo progetto è rilasciato sotto licenza [MIT](https://opensource.org/licenses/MIT).

---

_Creato da Andrea Conti_
