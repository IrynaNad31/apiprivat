import aiohttp
import asyncio
import datetime
import websockets
import json

API_URL = "https://api.privatbank.ua/p24api/exchange_rates"
CURRENCIES = ["EUR", "USD"]
DAYS_TO_FETCH = 10

async def fetch_exchange_rates(date, currencies):
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL, params={"json": "true", "date": date}) as response:
            data = await response.json()

    rates = {currency: {"sale": data["exchangeRate"][currency]["saleRate"],
                        "purchase": data["exchangeRate"][currency]["purchaseRate"]}
             for currency in currencies}

    return rates

async def get_exchange_rates_history(num_of_days, currencies):
    today = datetime.date.today()
    results = []

    for _ in range(num_of_days):
        date_str = today.strftime("%d.%m.%Y")
        rates = await fetch_exchange_rates(date_str, currencies)

        results.append({date_str: rates})
        today -= datetime.timedelta(days=1)

    return results

async def exchange_command(num_of_days, currencies):
    rates_history = await get_exchange_rates_history(num_of_days, currencies)
    return rates_history

async def handle_chat(websocket, path):
    while True:
        message = await websocket.recv()
        try:
            data = json.loads(message)
            if data["command"] == "exchange":
                num_of_days = data.get("num_of_days", 1)
                currencies = data.get("currencies", CURRENCIES)
                rates_history = await exchange_command(num_of_days, currencies)
                response = {"exchange_rates": rates_history}
                await websocket.send(json.dumps(response))
        except json.JSONDecodeError:
            await websocket.send("Invalid JSON format.")
        except Exception as e:
            await websocket.send(f"Error: {str(e)}")

def main():
    start_server = websockets.serve(handle_chat, "localhost", 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
