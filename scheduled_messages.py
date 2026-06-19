#!/usr/bin/env python3
"""Invia un messaggio a orari fissi (ora di Roma) in stile Guybrush Threepwood.

Pensato per girare via GitHub Actions. Il cron parte in UTC ed eventualmente
piu' volte: questo script calcola l'ora reale di Roma e manda il messaggio
giusto solo nello slot corretto, gestendo automaticamente l'ora legale.
"""

import os
import random
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

ROMA = ZoneInfo("Europe/Rome")

# Frasi originali in stile Guybrush Threepwood (Monkey Island):
# pirata maldestro, sarcastico, autoironico, duelli a insulti, grog.
FRASI = {
    "buongiorno": [
        "Buongiorno ciurma! Mi sono svegliato e sono ancora il pirata più temibile dei Castelli. Temibilmente impacciato, ma temibile.",
        "Sveglia mozzi! Il sole è alto, il grog è caldo... aspetta, no, è il contrario. Comunque, buongiorno!",
        "Un nuovo giorno all'orizzonte! Sento già l'odore di avventura. O forse è solo il caffè. Buongiorno a tutti!",
        "Buongiorno! Mi chiamo Guybrush Threepwood e voglio diventare un pirata. E anche fare colazione, prima.",
        "Alzate le ancore, ciurma! Oggi è il giorno giusto per diventare leggende. O almeno per non cadere dalla nave.",
        "Buongiorno! Ho trattenuto il respiro tutta la notte come fanno i pirati... no, aspetta, quello era sott'acqua. Vabbè, sono vivo!",
        "Sveglia mozzi! Ho già sconfitto tre nemici stamattina: il sonno, la sveglia e un cuscino particolarmente ostile.",
        "Buongiorno ciurma! Pronti a salpare verso nuove avventure? Io intanto salpo verso la caffettiera.",
    ],
    "pranzo": [
        "È ora di pranzo! Anche i pirati più temibili devono mangiare. Soprattutto quelli che combattono come contadini.",
        "Mezzogiorno suonato! Tempo di rifocillarsi. Consiglio del capitano: evitate il grog radioattivo di LeChuck.",
        "Pausa pranzo, ciurma! Ricordate: non si litiga a tavola, si litiga a colpi di insulti. È molto più elegante.",
        "Tutti a mangiare! Io ho con me solo questo pollo di gomma con la carrucola in mezzo, ma è il pensiero che conta.",
        "Pranzo, ciurma! Un buon pasto vale più di una mappa del tesoro. Beh, quasi. Dipende dal tesoro.",
        "A tavola, mozzi! Combatti come una mucca da latte... ma mangi come un vero pirata. E qui sei in vantaggio.",
        "Mezzogiorno! Ho cucinato io: stufato dello Scumm Bar. Tranquilli, le cose che galleggiano sono commestibili. Probabilmente.",
        "Pausa pranzo! Un pirata viaggia sullo stomaco. Per questo io faccio sempre naufragio: non mangio abbastanza.",
    ],
    "buonanotte": [
        "Buonanotte ciurma! Anche il pirata più coraggioso ha bisogno di riposo. E io ne ho bisogno parecchio.",
        "È tardi, mozzi. Tempo di ammainare le vele e andare a dormire. Domani altre avventure (e altri insulti).",
        "Buonanotte a tutti! Vado a sognare il tesoro di Big Whoop... o forse solo un letto comodo. Va bene uguale.",
        "Le stelle sono fuori e anch'io dovrei esserlo. Buonanotte ciurma, ci si vede all'alba con il vento in poppa!",
        "Buonanotte mozzi! Vado a riposare la spada e la lingua tagliente. Domani avrò di nuovo bisogno di entrambe.",
        "Si ammaina, ciurma. Una giornata da veri pirati: nessun tesoro trovato, ma neanche affogati. Direi un successo.",
        "Buonanotte a tutti! Conto le pecore... no, i galeoni. Sono un pirata serio, dopotutto. Più o meno.",
        "È ora di gettare l'ancora per oggi. Dormite bene ciurma, e attenti agli scimmioni a tre teste nei sogni.",
    ],
    # Sere di gioco (martedì e venerdì): doppio augurio, a chi dorme e a chi gioca.
    "buonanotte_gioco": [
        "Buonanotte a chi va a dormire... e buon gioco a chi resta a tavola! Che i dadi siano clementi e gli insulti taglienti.",
        "È sera di gioco, ciurma! A chi si ritira: dormite bene. A chi gioca fino a tardi: che la fortuna sia con voi (la bravura ce la mettete voi).",
        "Buonanotte ai saggi che vanno a riposare, e buon divertimento ai temerari che restano al tavolo! Combattete come contadini, vincete come pirati.",
        "Stasera si gioca! Buonanotte a chi sogna avventure, e buon gioco a chi le vive davvero fino a tarda notte. Avanti tutta!",
        "A chi spegne la luce: dolci sogni, mozzi. A chi tira ancora i dadi: che siano sempre numeri alti! Buona notte e buon gioco a tutti.",
        "Sera di gioco ai Castelli! Riposate bene voi che andate a nanna, e che i meeple siano con voi, prodi giocatori della notte!",
        "Buonanotte ciurma! Chi va a dormire conti i galeoni, chi resta a giocare conti i punti vittoria. A ciascuno la sua avventura!",
        "Si gioca stasera! Buonanotte a chi molla l'ancora, e buon gioco a chi naviga fino all'alba. Forza quel tavolo!",
    ],
}

# Giorni con gioco serale: martedì (1) e venerdì (4), secondo datetime.weekday().
GIORNI_DI_GIOCO = {1, 4}


def slot_corrente(ora: int, minuto: int) -> str | None:
    """Restituisce lo slot in base all'ora di Roma, altrimenti None."""
    if ora == 8:
        return "buongiorno"
    if ora == 13:
        return "pranzo"
    if ora == 22 and minuto >= 25:  # margine per ritardi del cron
        return "buonanotte"
    return None


def main() -> int:
    adesso = datetime.now(ROMA)
    slot = slot_corrente(adesso.hour, adesso.minute)

    if slot is None:
        print(f"[{adesso:%H:%M}] Nessuno slot attivo, esco.")
        return 0

    token = os.environ["TG_TOKEN"]
    chat_id = os.environ["TG_CHAT_ID"]

    # Martedì e venerdì la buonanotte diventa "buonanotte + buon gioco".
    chiave = slot
    if slot == "buonanotte" and adesso.weekday() in GIORNI_DI_GIOCO:
        chiave = "buonanotte_gioco"

    testo = random.choice(FRASI[chiave])

    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": testo},
        timeout=30,
    )
    resp.raise_for_status()
    print(f"[{adesso:%H:%M}] Inviato messaggio '{chiave}': {testo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
