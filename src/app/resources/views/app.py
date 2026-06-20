import tkinter as tk
from tkinter import ttk, messagebox

import requests
import datetime

import subprocess
import sys
import os

import matplotlib

matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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
        self.root.title("Monitor de Investimentos Macro")
        self.root.geometry("1300x850")

        self.is_running = False
        self.loop_id = None
        self.cached_investments = (
            []
        )  # Armazena os últimos dados para renderizar nos gráficos

        # 1. Criação do Sistema de Abas (Notebook)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 2. Definição dos frames containers de cada aba
        self.tab_monitor = ttk.Frame(self.notebook)
        self.tab_graphs = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_monitor, text="📊 Monitoramento")
        self.notebook.add(self.tab_graphs, text="📈 Gráficos Analíticos")

        # 3. Inicialização dos componentes internos da Aba 1 (Monitoramento)
        self.score_board = ScoreBoard(self.tab_monitor)
        self.control_panel = ControlPanel(
            self.tab_monitor, self.start_automation, self.stop_automation
        )
        self.data_grid = DataGrid(self.tab_monitor)

        # 4. Inicialização do Canvas de Gráficos na Aba 2 (Gráficos)
        self.setup_graphs_layout()

        # Puxa os dados iniciais do banco local
        self.load_stored_data()

    def setup_graphs_layout(self):
        """Prepara o container do Matplotlib dentro da aba de gráficos."""
        # Criamos uma figura com 3 subplots (1 linha, 3 colunas)
        self.fig, (self.ax_comm, self.ax_rates, self.ax_forex) = plt.subplots(
            1, 3, figsize=(15, 5)
        )
        self.fig.patch.set_facecolor("#f0f0f0")  # Cor de fundo padrão cinza do Tkinter

        # Cria o widget de canvas do matplotlib acoplado ao Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_graphs)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Renderiza os gráficos vazios inicialmente
        self.render_charts()

    def render_charts(self):
        """Limpa os eixos e redesenha os gráficos analíticos macro com dados reais."""
        # Reseta os subplots para evitar sobreposição de linhas/barras
        self.ax_comm.clear()
        self.ax_rates.clear()
        self.ax_forex.clear()

        # Dicionários de agrupamento macro com base nos tickers salvos no banco
        commodity_map = {
            "BZ=F": "Brent",
            "GC=F": "Ouro",
            "HG=F": "Cobre",
            "ZS=F": "Soja",
        }
        rate_map = {"^IRX": "2 Anos", "^FVX": "5 Anos", "^TNX": "10 Anos"}
        forex_map = {
            "MXN=X": "Peso MX",
            "NOK=X": "Coroa NO",
            "KRW=X": "Won KR",
            "EURBRL=X": "Euro/BRL",
        }

        # Listas para coletar dados filtrados do loop
        comm_labels, comm_vars = [], []
        rate_labels, rate_prices = [], []
        forex_labels, forex_vars = [], []

        # Filtra os dados da API salvos no cache para preencher as métricas dos gráficos
        for inv in self.cached_investments:
            code = inv.get("code")
            # Correção de tipagem se a variação ou preço vier como string ou formato incorreto
            try:
                var_val = float(inv.get("variation_percentage", 0.0)) * 100
                price_val = float(inv.get("current_price", 0.0))
            except (ValueError, TypeError):
                var_val = 0.0
                price_val = 0.0

            if code in commodity_map:
                comm_labels.append(commodity_map[code])
                comm_vars.append(var_val)
            elif code in rate_map:
                rate_labels.append(rate_map[code])
                rate_prices.append(price_val)
            elif code in forex_map:
                forex_labels.append(forex_map[code])
                forex_vars.append(var_val)

        # --- GRÁFICO 1: Termômetro de Commodities (Barras Horizontais) ---
        if comm_labels:
            colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in comm_vars]
            self.ax_comm.barh(comm_labels, comm_vars, color=colors, edgecolor="grey")
            self.ax_comm.axvline(0, color="black", linewidth=0.8, linestyle="--")
        self.ax_comm.set_title(
            "Commodities (Variação %)", fontsize=10, fontweight="bold"
        )
        self.ax_comm.grid(True, linestyle=":", alpha=0.5)

        # --- GRÁFICO 2: Curva de Juros EUA / Treasuries (Linha de Rendimento) ---
        if rate_labels:
            # Ordena os prazos (2Y -> 5Y -> 10Y) para a linha fazer sentido macroeconômico
            order = {"2 Anos": 0, "5 Anos": 1, "10 Anos": 2}
            sorted_rates = sorted(
                zip(rate_labels, rate_prices), key=lambda x: order.get(x[0], 9)
            )
            r_labels, r_prices = zip(*sorted_rates)

            self.ax_rates.plot(
                r_labels,
                r_prices,
                marker="o",
                color="#2980b9",
                linewidth=2,
                markersize=6,
            )
        self.ax_rates.set_title(
            "Curva de Juros EUA (Rendimento %)", fontsize=10, fontweight="bold"
        )
        self.ax_rates.grid(True, linestyle=":", alpha=0.5)

        # --- GRÁFICO 3: Câmbio e Moedas Globais (Barras Verticais) ---
        if forex_labels:
            colors_fx = ["#2ecc71" if v >= 0 else "#e74c3c" for v in forex_vars]
            self.ax_forex.bar(
                forex_labels, forex_vars, color=colors_fx, edgecolor="grey"
            )
            self.ax_forex.axhline(0, color="black", linewidth=0.8, linestyle="--")
        self.ax_forex.set_title(
            "Moedas vs Dólar (Variação %)", fontsize=10, fontweight="bold"
        )
        self.ax_forex.grid(True, linestyle=":", alpha=0.5)
        plt.setp(self.ax_forex.get_xticklabels(), rotation=15, ha="right")

        # Ajusta as margens e atualiza o Canvas dentro do loop do Tkinter
        self.fig.tight_layout()
        self.canvas.draw()

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
            response = requests.get(f"{API_URL}/api/investments", timeout=5)

            if response.status_code != 200:
                print("⚠️ Não foi possível recuperar os dados do banco.")
                return

            self.cached_investments = response.json()
            alta_counter = 0
            queda_counter = 0

            for inv in self.cached_investments:
                status = inv.get("classification", "Aguardando Carga")

                if "Alta" in status:
                    alta_counter += 1
                elif "Queda" in status:
                    queda_counter += 1

                # Formata exibição da variação salva vinda do banco
                try:
                    raw_var = float(inv.get("variation", 0.0))
                    # Se já estiver multiplicada no banco exibe direto, senão formata
                    formatted_var = (
                        f"{raw_var:.2f}%"
                        if raw_var > 1 or raw_var < -1
                        else f"{raw_var * 100:.2f}%"
                    )
                except (ValueError, TypeError):
                    formatted_var = "0.00%"

                self.data_grid.insert_row(
                    (
                        inv.get("name"),
                        inv.get("code"),
                        inv.get("previous_price", 0.0),
                        inv.get("current_price", 0.0),
                        formatted_var,
                        status,
                    )
                )

            self.score_board.update_scores(alta_counter, queda_counter)
            self.render_charts()  # Plota os gráficos com o histórico inicial recuperado

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
                self.cached_investments = response.json()
                self.data_grid.clear()

                alta_counter = 0
                queda_counter = 0

                for d in self.cached_investments:
                    status = d.get("classification", "Aguardando Carga")

                    if "Alta" in status:
                        alta_counter += 1
                    elif "Queda" in status:
                        queda_counter += 1

                    # Caso o backend multiplique por 100, exibe direto, senão multiplica
                    raw_pct = d.get("variation_percentage", 0.0)
                    if -1.0 <= raw_pct <= 1.0 and raw_pct != 0:
                        formatted_var = f"{raw_pct * 100:.2f}%"
                    else:
                        formatted_var = f"{raw_pct:.2f}%"

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
                self.render_charts()  # Atualiza dinamicamente as barras e linhas do gráfico em tempo real

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

        # Mantém a automação atualizando em background a cada 5 segundos
        self.loop_id = self.root.after(5000, self.update_data)


if __name__ == "__main__":
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.app.server:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    root = tk.Tk()
    app = AppMonitor(root)

    # Garante que quando o cliente fechar a janela do Tkinter, o Uvicorn também morra
    def on_closing():
        backend_process.terminate()  # Mata o Uvicorn
        root.destroy()  # Fecha o Tkinter

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
