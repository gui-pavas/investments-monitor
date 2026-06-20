import tkinter as tk
from tkinter import ttk, messagebox
import requests
import datetime

# URL for our local FastAPI server
API_URL = "http://127.0.0.1:8000"


class AppMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Investimentos")
        self.root.geometry("750x500")

        self.is_running = False
        self.loop_id = None

        self.create_widgets()

        # Updated to use 'code' and 'name' matching the Pydantic model
        self.client_assets = [
            {"code": "LCO", "name": "Petróleo Brent"},
            {"code": "VALE.K", "name": "Vale ADR"},
            {"code": "PBR", "name": "Petrobras ADR"},
        ]

    def create_widgets(self):
        # Top Panel
        frame_top = tk.Frame(self.root, pady=10)
        frame_top.pack(fill=tk.X)

        self.btn_start = tk.Button(
            frame_top,
            text="▶ Iniciar Automação (5 min)",
            bg="lightgreen",
            command=self.start_automation,
        )
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(
            frame_top,
            text="⏹ Parar",
            bg="salmon",
            state=tk.DISABLED,
            command=self.stop_automation,
        )
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        self.lbl_status = tk.Label(
            frame_top, text="Status: Parado", fg="gray", font=("Arial", 10, "bold")
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=20)

        # Treeview (Table)
        columns = ("name", "code", "previous", "current", "variation", "status")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)

        self.tree.heading("name", text="Ativo")
        self.tree.heading("code", text="Código")
        self.tree.heading("previous", text="Prévio")
        self.tree.heading("current", text="Atual")
        self.tree.heading("variation", text="Variação %")
        self.tree.heading("status", text="Status")

        for col in columns:
            self.tree.column(col, width=110, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def start_automation(self):
        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.update_data()

    def stop_automation(self):
        self.is_running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.lbl_status.config(text="Status: Parado", fg="gray")
        if self.loop_id:
            self.root.after_cancel(self.loop_id)

    def update_data(self):
        if not self.is_running:
            return

        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.lbl_status.config(text=f"Atualizando dados... ({current_time})", fg="blue")
        self.root.update()

        try:
            # Notice the payload structure: {"items": [...]} to match BulkSyncRequest
            payload = {"items": self.client_assets}

            response = requests.post(f"{API_URL}/api/sync", json=payload)

            if response.status_code == 200:
                api_data = response.json()

                # Clear current table
                for item in self.tree.get_children():
                    self.tree.delete(item)

                # Populate table with new data
                for d in api_data:
                    formatted_var = f"{d['variation_percentage'] * 100:.2f}%"
                    self.tree.insert(
                        "",
                        tk.END,
                        values=(
                            d["name"],
                            d["code"],
                            d["previous"],
                            d["current_price"],
                            formatted_var,
                            d["classification"],
                        ),
                    )

                self.lbl_status.config(
                    text=f"Última atualização: {current_time}", fg="green"
                )
            else:
                self.lbl_status.config(
                    text=f"Erro na API: {response.status_code}", fg="red"
                )
                print("Detalhes do erro:", response.text)

        except requests.exceptions.ConnectionError:
            self.lbl_status.config(text="Erro: Servidor Desligado!", fg="red")
            self.stop_automation()
            messagebox.showerror(
                "Erro", "O servidor da API não está rodando. Verifique o Uvicorn."
            )
            return

        # 10000 ms = 10 seconds for testing (change to 300000 for 5 minutes in production)
        interval_ms = 10000
        self.loop_id = self.root.after(interval_ms, self.update_data)


if __name__ == "__main__":
    root = tk.Tk()
    app = AppMonitor(root)
    root.mainloop()
