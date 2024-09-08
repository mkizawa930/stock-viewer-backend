from datetime import datetime
from pydantic import BaseModel, ConfigDict, Extra, Field


class OHLCV(BaseModel):
    timestamp: str = Field(..., examples=["yyyy-mm-ddTHH:MM:SS.sssZ"])
    open: float
    high: float
    low: float
    close: float
    volume: float


class HistoricalData(OHLCV):
    model_config = ConfigDict(extra="allow")


class HistoricalDataResponse(BaseModel):
    interval: str
    period: str
    indicators: list[str]
    data: list[HistoricalData]
