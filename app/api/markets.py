from http.client import HTTPResponse
from logging import getLogger
from typing import Optional
from app.schemas.data import OHLCV, HistoricalData, HistoricalDataResponse
from app.schemas.errors import (
    BadRequest,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
)
from app.services.market_service import MarketService
from fastapi.responses import JSONResponse
import joblib
import talib
from pydantic import ValidationError
import yfinance as yf
from fastapi import APIRouter, Depends, HTTPException, Query, logger
import yahooquery as yq

logger = getLogger("uvicorn")

router = APIRouter()


ERROR_RESPONSES = {
    400: BadRequest,
    401: UnauthorizedError,
    404: NotFoundError,
    500: InternalServerError,
}


memory = joblib.Memory()


@memory.cache
def fetch(symbol, interval="1d", period="6mo"):
    ticker = yf.Ticker(symbol)
    df = ticker.history(interval=interval, period=period)
    return df


def add_indicator(df, indicator):
    name, term = indicator.split("_")
    if term:
        term = int(term)
    else:
        raise Exception("format exception")

    match name:
        case "SMA":
            return talib.SMA(df.close, timeperiod=term)
        case "EMA":
            return talib.EMA(df.close, timeperiod=term)


def add_indicators(df, indicators: list[str]):
    for indicator in indicators:
        df[indicator] = add_indicator(df, indicator)
    return df


@router.get("/search")
def search_symbols(
    query: str = Query("", nullable=False),
    market_service: MarketService = Depends(MarketService),
):
    try:
        return market_service.find_quotes(query)
    except Exception as e:
        logger.error(e)
        return HTTPException(400)


@router.get(
    "/markets/{symbol}",
    response_model=HistoricalDataResponse,
    status_code=200,
    responses={
        200: {
            "description": "",
        },
        **ERROR_RESPONSES,
    },
)
def get_market(
    symbol: str,
    indicators: Optional[list[str]] = Query(None),
) -> list[OHLCV]:
    df = fetch(symbol)
    df.index.name = "Timestamp"
    df = df.reset_index()
    df.Timestamp = df.Timestamp.apply(lambda x: x.isoformat())
    df.rename(lambda x: x.lower(), axis=1, inplace=True)

    if indicators:
        df = add_indicators(df, indicators)

    data = [HistoricalData.model_validate(row) for row in df.to_dict(orient="records")]
    return HistoricalDataResponse(
        data=data,
        period="1mo",
        interval="1d",
        indicators=indicators if indicators else [],
    )
