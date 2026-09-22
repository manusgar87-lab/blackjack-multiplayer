import socket
import threading
import json
import random

# --- LOGICA DEL MAZZO (presa dal tuo codice) ---
def crea_mazzo():
    semi = ["C", "Q", "F", "P"]
    valori = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    mazzo = []
    for seme in semi:
        for valore in valori:
            punteggio = 11 if valore == "A" else (10 if valore in ["J", "Q", "K"] else int(valore))
            mazzo.append([valore + seme, punteggio])
    random.shuffle(mazzo)
    return mazzo

def calcola_punteggio(mano):
    punti = sum(carta[1] for carta in mano)
    assi = sum(1 for carta in mano if carta[0].startswith("A"))
    while punti > 21 and assi > 0:
        punti -= 10
        assi -= 1
    return punti

# --- STATO DEL GIOCO ---
giocatori_connessi = []
mazzo = crea_mazzo()
mani = {0: [], 1: []} # Mani dei due giocatori
mano_croupier = []
turno_attuale = 0 # 0 = Giocatore 1, 1 = Giocatore 2, 2 = Croupier/Fine
messaggio_globale = "In attesa dei giocatori..."

def invia_stato_a_tutti():
    """Invia a tutti i client la situazione attuale del tavolo in formato JSON"""
    stato = {
        "mani_giocatori": mani,
        "mano_croupier": mano_croupier if turno_attuale == 2 else [mano_croupier[0], ["??", 0]],
        "punti_croupier": calcola_punteggio(mano_croupier) if turno_attuale == 2 else mano_croupier[0][1],
        "turno": turno_attuale,
        "messaggio": messaggio_globale
    }
    dati = json.dumps(stato).encode('utf-8')
    for conn in giocatori_connessi:
        try:
            conn.sendall(dati + b"\n") # \n fa da separatore tra i messaggi
        except:
            pass

def gestisci_croupier():
    global turno_attuale, messaggio_globale
    turno_attuale = 2
    
    # Il croupier pesca finché non ha 17
    while calcola_punteggio(mano_croupier) < 17:
        mano_croupier.append(mazzo.pop())
    
    punti_banco = calcola_punteggio(mano_croupier)
    punti_g1 = calcola_punteggio(mani[0])
    punti_g2 = calcola_punteggio(mani[1])
    
    risultati = []
    for i, punti in enumerate([punti_g1, punti_g2]):
        if punti > 21:
            risultati.append(f"G{i+1} sballa.")
        elif punti_banco > 21:
            risultati.append(f"G{i+1} vince (Banco sballa).")
        elif punti > punti_banco:
            risultati.append(f"G{i+1} vince.")
        elif punti < punti_banco:
            risultati.append(f"G{i+1} perde.")
        else:
            risultati.append(f"G{i+1} pareggia.")
            
    messaggio_globale = " | ".join(risultati)
    invia_stato_a_tutti()

def resetta_partita():
    """Ricrea il mazzo, lo mescola e distribuisce le carte per una nuova partita"""
    global mazzo, mani, mano_croupier, turno_attuale, messaggio_globale
    mazzo = crea_mazzo()
    mani[0] = [mazzo.pop(), mazzo.pop()]
    mani[1] = [mazzo.pop(), mazzo.pop()]
    mano_croupier = [mazzo.pop(), mazzo.pop()]
    turno_attuale = 0
    messaggio_globale = "Nuova partita iniziata! Turno del Giocatore 1."
    invia_stato_a_tutti()

def gestisci_client(conn, id_giocatore):
    global turno_attuale, messaggio_globale
    while True:
        try:
            richiesta = conn.recv(1024).decode('utf-8').strip()
            if not richiesta: break
            
            # Se la partita è finita e qualcuno clicca Nuova Partita
            if richiesta == "RIAVVIA" and turno_attuale == 2:
                resetta_partita()
                
            elif turno_attuale == id_giocatore:
                if richiesta == "PESCA":
                    mani[id_giocatore].append(mazzo.pop())
                    if calcola_punteggio(mani[id_giocatore]) > 21:
                        turno_attuale += 1 # Sballa, passa il turno
                        messaggio_globale = f"Giocatore {id_giocatore+1} ha sballato! Turno di Giocatore {turno_attuale+1}"
                    else:
                        messaggio_globale = f"Giocatore {id_giocatore+1} ha pescato."
                
                elif richiesta == "STAI":
                    turno_attuale += 1
                    messaggio_globale = f"Giocatore {id_giocatore+1} si ferma. Turno del Giocatore {turno_attuale+1}"
                
                # Se entrambi hanno giocato, tocca al croupier
                if turno_attuale == 2:
                    gestisci_croupier()
                else:
                    invia_stato_a_tutti()
        except:
            break

# --- AVVIO DEL SERVER ---
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5555)) # Ascolta sulla porta 5555
server.listen(2)

print("Server in ascolto sulla porta 5555...")

while len(giocatori_connessi) < 2:
    conn, addr = server.accept()
    id_g = len(giocatori_connessi)
    giocatori_connessi.append(conn)
    print(f"Giocatore {id_g+1} connesso da {addr}")
    
    if len(giocatori_connessi) == 2:
        # Quando si connette il secondo giocatore, inizia la partita
        mano_croupier = [mazzo.pop(), mazzo.pop()]
        mani[0] = [mazzo.pop(), mazzo.pop()]
        mani[1] = [mazzo.pop(), mazzo.pop()]
        messaggio_globale = "Partita iniziata! Turno del Giocatore 1."
        invia_stato_a_tutti()
        
        # Avvia i thread in ascolto per i due giocatori
        threading.Thread(target=gestisci_client, args=(giocatori_connessi[0], 0)).start()
        threading.Thread(target=gestisci_client, args=(giocatori_connessi[1], 1)).start()