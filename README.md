# 🔴 PokéNexus OS

> **The Ultimate Pokémon Analytics & RPG Dashboard**
> *Developed by Stefano Blando*

![Version](https://img.shields.io/badge/version-22.0-red)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-ff4b4b)
![Data](https://img.shields.io/badge/Data-PokéAPI-yellow)

**PokéNexus** è una dashboard interattiva avanzata costruita con Python e Streamlit che simula un vero e proprio "Sistema Operativo" per allenatori di Pokémon. Non è solo un Pokédex: è una suite completa che unisce **Analisi Dati Competitiva** (grafi, calcolatori, simulazioni) con elementi **RPG Gamificati** (economia, cattura, gestione inventario).

---

## ✨ Funzionalità Principali

L'applicazione è divisa in 10 moduli (Tab) interconnessi:

### 📊 Analisi & Dati
* **🕸️ Network:** Un grafo interattivo basato sulla fisica che visualizza le relazioni tra i Tipi (Debolezze/Resistenze). *Include ottimizzazione Lazy Loading per massime prestazioni.*
* **📖 Pokédex:** Schede tecniche dettagliate con statistiche base, abilità, sprite (Normal/Shiny) e grafici Radar. Include l'audio del verso del Pokémon.
* **📊 Stats (Matrix & EVs):**
    * **Matrix:** Grafico a bolle per confrontare Velocità vs Attacco di più Pokémon.
    * **EVs Calculator:** Simulatore di statistiche al Livello 50 modificando Nature ed EVs (Effort Values) in tempo reale.
* **🧮 Calculator:** Calcolatore difensivo istantaneo per scoprire debolezze (2x, 4x), resistenze e immunità di singoli o doppi tipi.

### ⚔️ Battaglia & Team
* **⚔️ Battle Arena:** Simulatore di lotta 1v1 con calcolo danni, STAB, Meteo dinamico e Speed check.
* **🛡️ Squad Builder:**
    * Costruttore di team da 6 slot con memoria di sessione.
    * **Offensive Coverage:** Analisi visiva della copertura dei tipi del team.
    * **NPC Challenge:** Simulatore di battaglie 6v6 contro Capipalestra, Elite 4 e Campioni di varie regioni (Kanto, Johto, Sinnoh).

### 🎮 RPG & Gameplay
* **🏪 PokéPlaza:**
    * **Pokémon Center:** Cura il team (ripristina HP) con effetti sonori e notifiche.
    * **PokéMart:** Negozio funzionante dove spendere i soldi vinti per acquistare Ball, Pozioni e Strumenti.
* **🌲 Safari Zone:** Sistema "Gacha" per catturare Pokémon selvatici (Comuni, Rari, Leggendari) usando le Ball dell'inventario.
* **💻 PC Storage:** Box visivo per ammirare la collezione dei Pokémon catturati.
* **🎮 Play:** Minigioco "Who's that Pokémon?" per guadagnare soldi extra.

---

## 🛠️ Tecnologie Utilizzate

* **Frontend/Backend:** [Streamlit](https://streamlit.io/)
* **Dati:** [PokéAPI](https://pokeapi.co/) (Live requests + Caching)
* **Visualizzazione Dati:** Plotly, PyVis, NetworkX
* **Data Manipulation:** Pandas
* **Features Avanzate:**
    * Gestione `Session State` per persistenza dati (Soldi, Inventario, Team).
    * Iniezione **JavaScript/HTML** per audio a bassa latenza.
    * CSS personalizzato per interfaccia "Cyber-Pokedex".

---

## 🚀 Installazione e Avvio

1.  **Clona la repository:**
    ```bash
    git clone [https://github.com/tuo-username/pokenexus.git](https://github.com/tuo-username/pokenexus.git)
    cd pokenexus
    ```

2.  **Crea un ambiente virtuale (Opzionale ma consigliato):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Installa le dipendenze:**
    Crea un file `requirements.txt` con il seguente contenuto e installalo:
    ```bash
    pip install streamlit pandas networkx pyvis plotly requests
    ```

4.  **Assicurati di avere la cartella icons:**
    L'app cerca le icone dei tipi in una cartella locale `icons/`. Assicurati che i file `.svg` dei tipi (fire.svg, water.svg, ecc.) siano presenti nella directory del progetto.

5.  **Avvia l'app:**
    ```bash
    streamlit run app.py
    ```

---

## 📸 Screenshots

*(Qui puoi inserire degli screenshot dell'app una volta caricata su GitHub)*

---

## 🔮 Roadmap Futura

* [ ] Salvataggio su database locale (SQLite) per non perdere i dati al refresh.
* [ ] Implementazione di Mosse specifiche e Abilità nella simulazione di lotta.
* [ ] Espansione del database NPC (Hoenn, Unova, Kalos).
* [ ] Export della scheda del team come immagine PNG.

---

## 📝 Licenza e Credits

* **Developer:** Stefano Blando © 2026
* **Data Source:** Tutti i dati e le immagini dei Pokémon sono forniti da [PokéAPI](https://pokeapi.co/).
* **Audio:** Effetti sonori da Pokémon Showdown e PokéAPI Cries.
* **License:** MIT License.

---

*Gotta Analyze 'Em All!* 🔴
