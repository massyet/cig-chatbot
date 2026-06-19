import os
import logging
import asyncio
import treni_command
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Risposte ────────────────────────────────────────────────────────────────

RISPOSTE = {
    "dove": (
        "📍 *Dove siamo*\n\n"
        "Centro Anziani di Marino, Via della Repubblica.\n\n"
        "Sì, anziani. No, non giochiamo a briscola. "
        "Sì, sanno chi è Guybrush Threepwood."
    ),
    "quando": (
        "🗓 *Quando siamo aperti*\n\n"
        "Ogni martedì e venerdì sera dalle 21:00.\n\n"
        "Se arrivi di mercoledì, siediti fuori e contempla le stelle. "
        "Torneranno presto."
    ),
    "tessera": (
        "📋 *Come tesserarsi*\n\n"
        "Compila il modulo su [castellingioco.it](https://www.castellingioco.it) e paga 10€.\n\n"
        "È meno pericoloso che sfidare LeChuck a duello, "
        "e quasi altrettanto soddisfacente."
    ),
    "socio": (
        "🏴‍☠️ *Posso venire senza essere socio?*\n\n"
        "Certo! Le prime serate sono libere.\n\n"
        "Poi, come nelle migliori trappole pirata, "
        "potresti non voler più andartene."
    ),
    "giochi": (
        "🎲 *Quanti giochi abbiamo*\n\n"
        "Abbastanza da farti perdere il conto, il sonno e "
        "occasionalmente la ragione.\n\n"
        "La ludoteca completa è visibile sul sito ai soci: "
        "[castellingioco.it](https://www.castellingioco.it)"
    ),
    "serata": (
        "🌙 *Come funziona la serata*\n\n"
        "Arrivi, scegli un gioco, trovi qualcuno con cui giocare "
        "o ti aggreghi a un tavolo già avviato.\n\n"
        "Non serve esperienza. Serve solo non aver paura di perdere."
    ),
    "portare": (
        "🎒 *Posso portare qualcosa?*\n\n"
        "I tuoi giochi preferiti sono benvenuti.\n\n"
        "Il rum è opzionale ma apprezzato. "
        "Le scimmiette a tre teste le lasci a casa."
    ),
    "costo": (
        "💰 *Quanto costa*\n\n"
        "La tessera annuale è 10€.\n\n"
        "Per questo puoi partecipare a tutte le serate, agli eventi speciali, "
        "accedere alla ludoteca con prestiti gratuiti e dire ai tuoi amici "
        "che fai parte di un'associazione culturale. _Culturale._"
    ),
    "tipo": (
        "♟ *Che tipo di giochi facciamo*\n\n"
        "Di tutto. Dai german più cerebrali che ti faranno rimpiangere di "
        "avere un cervello, agli american più caotici che ti faranno "
        "rimpiangere di avere amici.\n\n"
        "Passando per party game, cooperative, astratti e qualunque cosa "
        "qualcuno si porti sotto il braccio.\n\n"
        "L'unica costante è che qualcuno perderà male, "
        "ma si divertirà tantissimo."
    ),
}

# ── Parole chiave → risposta ─────────────────────────────────────────────────

KEYWORDS = {
    "dove":    ["dove", "indirizzo", "sede", "luogo", "posto", "come arrivo", "via"],
    "quando":  ["quando", "orari", "orario", "aperti", "apertura", "giorni", "martedì", "venerdì"],
    "tessera": ["tesser", "iscri", "modulo", "associarmi", "diventare socio", "come mi"],
    "socio":   ["senza essere socio", "non sono socio", "venire senza", "prima volta", "ospite"],
    "giochi":  ["quanti giochi", "ludoteca", "catalogo", "inventario", "biblioteca"],
    "serata":  ["come funziona", "funziona la serata", "come si fa", "cosa si fa", "arrivo"],
    "portare": ["portare", "porto", "posso portare", "porto qualcosa", "rum"],
    "costo":   ["quanto costa", "prezzo", "costo", "10", "euro", "€", "pagare"],
    "tipo":    ["tipo di giochi", "che giochi", "quali giochi", "german", "american", "party"],
}

def match_keyword(text: str) -> str | None:
    text = text.lower()
    for key, words in KEYWORDS.items():
        for w in words:
            if w in text:
                return key
    return None

# ── Tastiera principale ──────────────────────────────────────────────────────

def main_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("📍 Dove siete?",          callback_data="dove"),
            InlineKeyboardButton("🗓 Quando aprite?",        callback_data="quando"),
        ],
        [
            InlineKeyboardButton("📋 Come mi tessero?",      callback_data="tessera"),
            InlineKeyboardButton("🏴‍☠️ Senza essere socio?", callback_data="socio"),
        ],
        [
            InlineKeyboardButton("🎲 Quanti giochi?",        callback_data="giochi"),
            InlineKeyboardButton("🌙 Come funziona?",        callback_data="serata"),
        ],
        [
            InlineKeyboardButton("🎒 Posso portare qualcosa?", callback_data="portare"),
            InlineKeyboardButton("💰 Quanto costa?",           callback_data="costo"),
        ],
        [
            InlineKeyboardButton("♟ Che giochi fate?",       callback_data="tipo"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)

BENVENUTO = (
    "⚓ *Benvenuto nella chat di Castelli in Gioco!*\n\n"
    "Siamo un'associazione ludica a Marino, nei Castelli Romani.\n"
    "Giochiamo a giochi da tavolo ogni martedì e venerdì sera.\n\n"
    "Scegli una domanda dal menu oppure scrivimi liberamente — "
    "capisco anche l'italiano, non solo il piratico."
)

# ── Handler ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        BENVENUTO,
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Usa il menu qui sotto oppure scrivimi direttamente — "
        "provo a capirti anche senza mappa del tesoro. 🗺",
        reply_markup=main_keyboard(),
    )

async def treni_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra i prossimi treni regionali (orario, binario, ritardo) sulle tratte."""
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    # La chiamata a ViaggiaTreno e' bloccante: la eseguo in un thread separato
    # per non bloccare il loop del bot mentre attende la risposta.
    testo = await asyncio.to_thread(treni_command.tabellone)
    await update.message.reply_text(
        testo,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    key = query.data
    if key in RISPOSTE:
        await query.message.reply_text(
            RISPOSTE[key],
            parse_mode="Markdown",
            reply_markup=main_keyboard(),
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    key = match_keyword(text)
    if key:
        await update.message.reply_text(
            RISPOSTE[key],
            parse_mode="Markdown",
            reply_markup=main_keyboard(),
        )
    else:
        await update.message.reply_text(
            "🦜 Non ho trovato la risposta nella mia mappa del tesoro.\n\n"
            "Prova a scegliere dal menu qui sotto, oppure scrivici su "
            "[castellingioco.it](https://www.castellingioco.it).",
            parse_mode="Markdown",
            reply_markup=main_keyboard(),
        )

# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("Variabile d'ambiente TELEGRAM_BOT_TOKEN non impostata.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_command))
    app.add_handler(CommandHandler("treni", treni_handler))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("Bot CiG avviato.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
