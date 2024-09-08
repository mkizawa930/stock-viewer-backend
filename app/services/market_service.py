from typing import Self
import yahooquery as yq
import yfinance as yf


class MarketService:
    def find_quotes(self: Self, query: str):
        data = yq.search(query)
        return data["quotes"]
