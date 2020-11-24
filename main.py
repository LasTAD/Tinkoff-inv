import os
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, List, Tuple

import pandas as pd
import plotly.graph_objects as go

import tinvest as ti

client = ti.SyncClient(os.getenv('TINVEST_TOKEN', ''))
api = ti.OpenApi(client)


class HTTPError(Exception):
    pass


def get_payload(response) -> Any:
    if response.status_code != HTTPStatus.OK:
        raise HTTPError(response.parse_error().json())
    return response.parse_json().payload


def main():
    response = api.portfolio.portfolio_get()
    payload: ti.Portfolio = get_payload(response)
    figis = [(p.figi, p.name) for p in payload.positions]
    fig = get_figure(figis)
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.show()


def get_figure(figis: List[Tuple[str, str]]) -> go.Figure:
    return go.Figure(
        data=[get_candlesstick(get_figi_data(figi), figi, name) for figi, name in figis]
    )


def get_candlesstick(df: pd.DataFrame, figi: str, name: str) -> go.Candlestick:
    return go.Candlestick(
        name=f'{name} {figi}',
        x=df['time'],
        open=df['o'],
        high=df['h'],
        low=df['l'],
        close=df['c'],
    )


def get_figi_data(figi: str) -> pd.DataFrame:
    now = datetime.now()
    response = api.market.market_candles_get(
        figi=figi,
        from_=now - timedelta(days=31 * 12),
        to=now,
        interval=ti.CandleResolution.week,
    )
    payload: ti.Candles = get_payload(response)
    return pd.DataFrame(c.dict() for c in payload.candles)


if __name__ == '__main__':
    main()