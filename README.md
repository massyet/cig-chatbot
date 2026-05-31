# CiG Chatbot 🎲

Bot Telegram per l'associazione **Castelli in Gioco** (Marino, Castelli Romani).  
Username: [@CiGchatbot](https://t.me/CiGchatbot)

---

## Struttura

```
bot.py            # logica del bot
requirements.txt  # dipendenze Python
Procfile          # processo per Railway
```

---

## Deploy su Railway

### 1. Crea la repo su GitHub

```bash
git init
git add .
git commit -m "primo commit"
git branch -M main
git remote add origin https://github.com/TUO-USERNAME/cig-chatbot.git
git push -u origin main
```

### 2. Crea il progetto su Railway

1. Vai su [railway.app](https://railway.app) e fai login
2. **New Project → Deploy from GitHub repo**
3. Seleziona la repo `cig-chatbot`
4. Railway rileva automaticamente il `Procfile`

### 3. Imposta la variabile d'ambiente

In Railway → scheda **Variables**, aggiungi:

| Nome | Valore |
|------|--------|
| `TELEGRAM_BOT_TOKEN` | il tuo token da @BotFather |

> ⚠️ Non inserire mai il token direttamente nel codice o nel repo.

### 4. Deploy

Railway parte automaticamente dopo ogni `git push` sul branch `main`.  
Controlla i log nella scheda **Deployments** per verificare che il bot sia attivo.

---

## Sviluppo locale

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="il-tuo-token"
python bot.py
```

---

## Funzionalità

- Menu a pulsanti inline con 9 domande frequenti
- Riconoscimento parole chiave nei messaggi liberi
- Risposte in stile Monkey Island con le info reali dell'associazione
- Fallback con link al sito per domande non riconosciute
