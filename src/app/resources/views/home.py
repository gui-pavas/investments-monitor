import tkinter as tk
from tkinter import ttk, messagebox
import requests
import datetime

API_URL = "http://127.0.0.1:8000"

# --- COMPONENTES VISUAIS ---


class ScoreBoard(tk.Frame):
    """Componente responsável pelos contadores de Alta e Queda."""

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.X, padx=10, pady=5)
        self._create_widgets()

    def _create_widgets(self):
        # Bloco de ALTA (Verde)
        self.alta_frame = tk.Frame(self, bg="#00B050", height=40)
        self.alta_frame.pack(fill=tk.X, side=tk.TOP, expand=True, pady=2)
        self.alta_frame.pack_propagate(False)

        tk.Label(
            self.alta_frame,
            text="ALTA",
            bg="#00B050",
            fg="black",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, padx=10)
        self.lbl_alta_count = tk.Label(
            self.alta_frame,
            text="0",
            bg="#00B050",
            fg="black",
            font=("Arial", 20, "bold"),
        )
        self.lbl_alta_count.pack(expand=True)

        # Bloco de QUEDA (Vermelho)
        self.queda_frame = tk.Frame(self, bg="red", height=40)
        self.queda_frame.pack(fill=tk.X, side=tk.TOP, expand=True, pady=2)
        self.queda_frame.pack_propagate(False)

        tk.Label(
            self.queda_frame,
            text="QUEDA",
            bg="red",
            fg="black",
            font=("Arial", 10, "bold"),
        ).pack(side=tk.LEFT, padx=10)
        self.lbl_queda_count = tk.Label(
            self.queda_frame, text="0", bg="red", fg="black", font=("Arial", 20, "bold")
        )
        self.lbl_queda_count.pack(expand=True)

    def update_scores(self, alta, queda):
        self.lbl_alta_count.config(text=str(alta))
        self.lbl_queda_count.config(text=str(queda))


class ControlPanel(tk.Frame):
    """Componente que agrupa botões de controle e o status da aplicação."""

    def __init__(self, parent, start_cmd, stop_cmd):
        super().__init__(parent)
        self.pack(fill=tk.X, pady=10)

        self.btn_start = tk.Button(
            self, text="▶ Iniciar Automação (5 min)", bg="lightgreen", command=start_cmd
        )
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(
            self, text="⏹ Parar", bg="salmon", state=tk.DISABLED, command=stop_cmd
        )
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        self.lbl_status = tk.Label(
            self, text="Status: Parado", fg="gray", font=("Arial", 10, "bold")
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=20)

    def set_running_state(self, is_running):
        if is_running:
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
        else:
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            self.set_status("Status: Parado", "gray")

    def set_status(self, text, color):
        self.lbl_status.config(text=text, fg=color)


class DataGrid(tk.Frame):
    """Componente dedicado à exibição de dados tabulares."""

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._create_widgets()

    def _create_widgets(self):
        columns = ("name", "code", "previous", "current", "variation", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)

        self.tree.heading("name", text="Ativo")
        self.tree.heading("code", text="Código")
        self.tree.heading("previous", text="Prévio")
        self.tree.heading("current", text="Atual")
        self.tree.heading("variation", text="Variação %")
        self.tree.heading("status", text="Status")

        for col in columns:
            self.tree.column(col, width=110, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert_row(self, values):
        self.tree.insert("", tk.END, values=values)


# --- CLASSE ORQUESTRADORA (APP PRINCIPAL) ---


class AppMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Investimentos")
        self.root.geometry("750x500")

        self.is_running = False
        self.loop_id = None

        # Instanciando Componentes Limpos
        self.score_board = ScoreBoard(self.root)
        self.control_panel = ControlPanel(
            self.root, self.start_automation, self.stop_automation
        )
        self.data_grid = DataGrid(self.root)

        # Puxa os dados iniciais do banco
        self.load_stored_data()

    def start_automation(self):
        self.is_running = True
        self.control_panel.set_running_state(True)
        self.update_data()

    def stop_automation(self):
        self.is_running = False
        self.control_panel.set_running_state(False)
        if self.loop_id:
            self.root.after_cancel(self.loop_id)

    def load_stored_data(self):
        try:
            self.data_grid.clear()

            # Adicionamos timeout=5 para evitar o congelamento da tela
            response = requests.get(f"{API_URL}/api/investments", timeout=5)

            if response.status_code != 200:
                print("⚠️ Não foi possível recuperar os dados do banco.")
                return

            investments = response.json()
            alta_counter = 0
            queda_counter = 0

            for inv in investments:
                status = inv.get("classification", "Aguardando Carga")

                if "Alta" in status:
                    alta_counter += 1
                elif "Queda" in status:
                    queda_counter += 1

                self.data_grid.insert_row(
                    (
                        inv.get("name"),
                        inv.get("code"),
                        inv.get("previous_price", 0.0),
                        inv.get("current_price", 0.0),
                        f"{inv.get('variation', 0.0)}%",
                        status,
                    )
                )

            self.score_board.update_scores(alta_counter, queda_counter)

        except requests.exceptions.Timeout:
            print("⏳ Erro: O servidor demorou muito para responder (Timeout).")
        except requests.exceptions.ConnectionError:
            print("🔌 Erro: O servidor da API (Uvicorn) parece estar desligado.")
        except Exception as e:
            print(f"❌ Erro ao carregar dados iniciais: {e}")

    def update_data(self):
        if not self.is_running:
            return

        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.control_panel.set_status(f"Atualizando dados... ({current_time})", "blue")
        self.root.update()

        try:
            response = requests.get(f"{API_URL}/api/latest")

            if response.status_code == 200:
                api_data = response.json()
                self.data_grid.clear()

                alta_counter = 0
                queda_counter = 0

                for d in api_data:
                    status = d.get("classification", "Aguardando Carga")

                    if "Alta" in status:
                        alta_counter += 1
                    elif "Queda" in status:
                        queda_counter += 1

                    formatted_var = f"{d.get('variation_percentage', 0.0) * 100:.2f}%"
                    self.data_grid.insert_row(
                        (
                            d.get("name", ""),
                            d.get("code", ""),
                            d.get("previous", 0.0),
                            d.get("current_price", 0.0),
                            formatted_var,
                            status,
                        )
                    )

                self.score_board.update_scores(alta_counter, queda_counter)
                self.control_panel.set_status(
                    f"Última atualização: {current_time}", "green"
                )
            else:
                self.control_panel.set_status(
                    f"Erro na API: {response.status_code}", "red"
                )

        except requests.exceptions.ConnectionError:
            self.control_panel.set_status("Erro: Servidor Desligado!", "red")
            self.stop_automation()
            messagebox.showerror(
                "Erro", "O servidor da API não está rodando. Verifique o Uvicorn."
            )
            return

        self.loop_id = self.root.after(5000, self.update_data)


if __name__ == "__main__":
    root = tk.Tk()
    app = AppMonitor(root)
    root.mainloop()
