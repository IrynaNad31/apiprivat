import sys
from datetime import datetime, timedelta

import httpx
import asyncio
import platform


class HttpError(Exception):
    pass


async def request(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            raise HttpError(f"Error status: {r.status_code} for {url}")


async def main(days_to_fetch):
    data = []
    for day in range(int(days_to_fetch)):
        d = datetime.now() - timedelta(days=day)
        shift = d.strftime("%d.%m.%Y")
        try:
            response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
            if response and 'exchangeRate' in response:
                eur_rate = response['exchangeRate'].get('EUR', {})
                usd_rate = response['exchangeRate'].get('USD', {})
                data.append({shift: {'EUR': eur_rate, 'USD': usd_rate}})
        except HttpError as err:
            print(err)
    return data

if __name__ == '__main':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if len(sys.argv) != 2:
        print("Usage: python main.py <days_to_fetch>")
        sys.exit(1)

    days_to_fetch = sys.argv[1]
    result = asyncio.run(main(days_to_fetch))
    print(result)
