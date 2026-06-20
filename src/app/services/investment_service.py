import yfinance as yf


class InvestmentService:
    def __init__(self):
        # Dicionário de Tradução: Investing.com -> Yahoo Finance
        # Aqui você vai mapear os códigos que o seu cliente usa na planilha
        # para os códigos que o Yahoo Finance entende.
        self.ticker_map = {
            "LCO": "BZ=F",  # Petróleo Brent Futuros
            "GC": "GC=F",  # Ouro Futuros
            "HG": "HG=F",  # Cobre Futuros
            "CL": "CL=F",  # Petróleo WTI
            "VALE.K": "VALE",  # Vale SA ADR
            "PBR": "PBR",  # Petrobras ADR
            "EWZ": "EWZ",  # iShares MSCI Brazil ETF
            "XIN9.FGI": "FXI",  # FTSE China A50 Futuros (Yahoo tem esse código alternativo)
            # Adicione os outros da planilha depois...
        }

    def fetch_data(self, original_code: str, name: str) -> dict:
        """
        Busca os dados do ativo no Yahoo Finance e já formata
        exatamente como o nosso banco de dados SQLite espera.
        """
        # Pega o código traduzido ou tenta usar o original se não estiver no mapa
        yf_code = self.ticker_map.get(original_code, original_code)

        try:
            ticker = yf.Ticker(yf_code)
            info = ticker.fast_info

            # Coleta os valores usando .get() ou fallback seguro para None
            previous_close = getattr(info, "previous_close", None)
            current_price = getattr(info, "last_price", None)

            # Função auxiliar interna para arredondar sem quebrar com NoneType
            def safe_round(value, decimals=2):
                if value is None:
                    return 0.0
                try:
                    return round(float(value), decimals)
                except (ValueError, TypeError):
                    return 0.0

            # Se os dados vitais vierem nulos do Yahoo (mercado fechado/indisponível)
            if previous_close is None or current_price is None:
                print(
                    f"⚠️ [API] Yahoo retornou dados incompletos para {yf_code}. Mantendo valores zerados."
                )
                return {
                    "name": name,
                    "classification": "Aguardando Carga",
                    "code": original_code,
                    "extended_negotiation": None,
                    "extended_negotiation_percentage": None,
                    "previous": 0.0,
                    "current_price": 0.0,
                    "variation_percentage": 0.0,
                }

            # Previne divisão por zero caso a API retorne algo estranho
            if previous_close > 0:
                variation = (current_price - previous_close) / previous_close
            else:
                variation = 0.0

            # Define a classificação automaticamente
            if variation > 0:
                classification = "Alta"
            elif variation < 0:
                classification = "Queda"
            else:
                classification = "Neutro"

            return {
                "name": name,
                "classification": classification,
                "code": original_code,  # Salvamos o código original para o cliente reconhecer
                "extended_negotiation": None,
                "extended_negotiation_percentage": None,
                "previous": safe_round(previous_close, 2),
                "current_price": safe_round(current_price, 2),
                "variation_percentage": safe_round(
                    variation * 100, 2
                ),  # Multiplicado por 100 para visualização amigável na Treeview (ex: 0.66)
            }

        except Exception as e:
            print(f"❌ Erro crítico ao buscar {original_code} ({yf_code}): {e}")
            return None
