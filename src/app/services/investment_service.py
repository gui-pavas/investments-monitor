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

            previous_close = info.previous_close
            current_price = info.last_price

            # Previne divisão por zero caso a API retorne algo estranho
            if previous_close and previous_close > 0:
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
                "extended_negotiation": None,  # Podemos deixar nulo por enquanto
                "extended_negotiation_percentage": None,  # Podemos deixar nulo por enquanto
                "previous": round(previous_close, 2),
                "current_price": round(current_price, 2),
                "variation_percentage": round(
                    variation, 4
                ),  # 4 casas (ex: 0.0066 = 0.66%)
            }

        except Exception as e:
            print(f"Erro ao buscar {original_code} ({yf_code}): {e}")
            return None
