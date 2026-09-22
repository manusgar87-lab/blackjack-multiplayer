import tkinter as tk
import socket
import threading
import json

# INSERIRE L'IP DEL SERVER (Lascia '127.0.0.1' per testare da solo sullo stesso PC)
IP_SERVER = '127.0.0.1' 
PORTA = 5555

class BlackjackMultiplayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack Multiplayer")
        self.root.geometry("700x600")
        self.root.configure(bg="#2E8B57")

        # UI Elementi
        self.lbl_info = tk.Label(root, text="Connessione al server...", bg="#2E8B57", fg="yellow", font=("Helvetica", 14, "bold"))
        self.lbl_info.pack(pady=10)

        self.lbl_banco = tk.Label(root, text="Banco: ?\nCarte: [ ]", bg="#2E8B57", fg="white", font=("Helvetica", 12))
        self.lbl_banco.pack(pady=20)

        self.lbl_p1 = tk.Label(root, text="Giocatore 1\nCarte: [ ]\nPunti: 0", bg="#2E8B57", fg="white", font=("Helvetica", 12))
        self.lbl_p1.pack(pady=10)

        self.lbl_p2 = tk.Label(root, text="Giocatore 2\nCarte: [ ]\nPunti: 0", bg="#2E8B57", fg="white", font=("Helvetica", 12))
        self.lbl_p2.pack(pady=10)

        frame_btn = tk.Frame(root, bg="#2E8B57")
        frame_btn.pack(pady=20)

        self.btn_pesca = tk.Button(frame_btn, text="Pesca", state=tk.DISABLED, width=10, font=("Helvetica", 12), command=lambda: self.invia_azione("PESCA"))
        self.btn_pesca.grid(row=0, column=0, padx=10)

        self.btn_stai = tk.Button(frame_btn, text="Fermati", state=tk.DISABLED, width=10, font=("Helvetica", 12), command=lambda: self.invia_azione("STAI"))
        self.btn_stai.grid(row=0, column=1, padx=10)

        self.btn_nuova = tk.Button(frame_btn, text="Nuova Partita", state=tk.DISABLED, width=12, font=("Helvetica", 12), command=lambda: self.invia_azione("RIAVVIA"))
        self.btn_nuova.grid(row=0, column=2, padx=10)

        # Connessione al server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((IP_SERVER, PORTA))
            # Avvia un thread separato che ascolta i messaggi dal server in background
            threading.Thread(target=self.ascolta_server, daemon=True).start()
        except:
            self.lbl_info.config(text="Errore: Impossibile connettersi al server", fg="red")

    def invia_azione(self, azione):
        """Invia PESCA o STAI al server"""
        self.client_socket.sendall(azione.encode('utf-8'))

    def ascolta_server(self):
        """Riceve continuamente i JSON dal server e aggiorna l'interfaccia"""
        buffer = ""
        while True:
            try:
                dati = self.client_socket.recv(1024).decode('utf-8')
                if not dati: break
                
                buffer += dati
                if "\n" in buffer:
                    messaggi = buffer.split("\n")
                    for msg in messaggi[:-1]:
                        stato = json.loads(msg)
                        self.aggiorna_ui(stato)
                    buffer = messaggi[-1]
            except:
                break

    def aggiorna_ui(self, stato):
        """Aggiorna i testi sulla base dei dati ricevuti dal server"""
        def formatta_carte(mano):
            return " | ".join([c[0] for c in mano])
            
        # Per poter modificare la GUI da un Thread secondario in Tkinter, usiamo root.after
        self.root.after(0, self._esegui_aggiornamento, stato, formatta_carte)

    def _esegui_aggiornamento(self, stato, formatta_carte):
        self.lbl_info.config(text=stato["messaggio"])
        
        self.lbl_banco.config(text=f"Banco (Punti: {stato['punti_croupier']})\nCarte: {formatta_carte(stato['mano_croupier'])}")
        
        m1 = stato['mani_giocatori']["0"]
        m2 = stato['mani_giocatori']["1"]
        punteggio_m1 = sum(c[1] for c in m1) # Semplificazione solo per mostrare punti
        punteggio_m2 = sum(c[1] for c in m2)
        
        self.lbl_p1.config(text=f"Giocatore 1 (Punti: {punteggio_m1})\nCarte: {formatta_carte(m1)}")
        self.lbl_p2.config(text=f"Giocatore 2 (Punti: {punteggio_m2})\nCarte: {formatta_carte(m2)}")

        
        # Logica dei bottoni:
        if stato['turno'] == 2:
            # Fine partita: spegni Pesca/Stai e accendi Nuova Partita
            self.btn_pesca.config(state=tk.DISABLED)
            self.btn_stai.config(state=tk.DISABLED)
            self.btn_nuova.config(state=tk.NORMAL)
        else:
            # Durante la partita: accendi Pesca/Stai solo se è il tuo turno (turno 0 o 1), spegni Nuova Partita
            self.btn_pesca.config(state=tk.NORMAL if stato['turno'] < 2 else tk.DISABLED)
            self.btn_stai.config(state=tk.NORMAL if stato['turno'] < 2 else tk.DISABLED)
            self.btn_nuova.config(state=tk.DISABLED)


if __name__ == "__main__":
    finestra = tk.Tk()
    app = BlackjackMultiplayer(finestra)
    finestra.mainloop()