import os
from http import HTTPStatus
from typing import Any

import tinvest as ti


class HTTPError(Exception):
    pass


class CustomClient(ti.SyncClient):
    def request(self, *args, **kwargs) -> Any:
        response = super().request(*args, **kwargs)
        if response.status_code != HTTPStatus.OK:
            raise HTTPError(response.parse_error().json())

        return response.parse_json().payload


client = CustomClient(os.getenv('TINVEST_SANDBOX_TOKEN', ''), use_sandbox=True)
api = ti.OpenApi(client)


def main():
    portfolio: ti.Portfolio = api.portfolio.portfolio_get()
    print(portfolio)  # noqa:001


if __name__ == '__main__':
    main()