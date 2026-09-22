# 🃏 Python Blackjack Multiplayer

Un gioco del Blackjack in Python con architettura Client-Server e interfaccia grafica nativa in Tkinter. Permette a due giocatori di sfidarsi contro il banco (croupier).

## ✨ Caratteristiche
* **Logica Server-Side:** Il server gestisce il mazzo, i punteggi e i turni, prevenendo qualsiasi tipo di cheat.
* **Interfaccia Grafica:** Realizzata interamente con `tkinter` (libreria standard di Python, nessuna dipendenza esterna).
* **Regole Integrate:** Gestione dinamica dell'Asso (11 o 1 in caso di sballo) e regola del croupier (pesca fino a 17).
* **Multigiocatore Flessibile:** Giocabile sullo stesso PC, sulla stessa rete Wi-Fi domestica o a distanza tramite Internet.

---

## 🚀 Come giocare (Guida alla connessione)

Prima di avviare il gioco, è fondamentale configurare correttamente le primissime righe del file `client.py` in base a come volete giocare. 

Il file `server.py` **non va mai modificato**, va solo avviato da chi decide di ospitare la partita (l'Host).

### Scenario 1: Giocare da soli (Test sullo stesso PC)
Ideale per provare il gioco. Farai sia da server che da giocatore 1 e giocatore 2.
1. Nel file `client.py`, lascia le impostazioni di default:
   ```python
   IP_SERVER = '127.0.0.1' 
   PORTA = 5555