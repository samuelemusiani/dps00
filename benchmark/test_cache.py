"""
Measures average cache speedup for the /departures endpoint.
First request = cold (cache miss), second = warm (cache hit).
"""

import asyncio
import time
import httpx

BASE_URL = "http://localhost:8000"
QUERIES = ["Brussel", "Gent", "Antwerp", "Liège", "Brugge", "Leuven", "Namur", "Mechelen"]


async def timed_get(client: httpx.AsyncClient, q: str) -> float:
    t0 = time.perf_counter()
    await client.get(f"{BASE_URL}/departures", params={"q": q})
    return time.perf_counter() - t0


async def main():
    cold_times, warm_times = [], []

    async with httpx.AsyncClient(timeout=15) as client:
        for q in QUERIES:
            cold = await timed_get(client, q)
            warm = await timed_get(client, q)
            cold_times.append(cold)
            warm_times.append(warm)
            speedup = cold / warm if warm > 0 else float("inf")
            print(f"{q:<12}  cold={cold*1000:7.1f}ms  warm={warm*1000:7.1f}ms  speedup={speedup:.2f}x")

    avg_cold = sum(cold_times) / len(cold_times)
    avg_warm = sum(warm_times) / len(warm_times)
    avg_speedup = avg_cold / avg_warm if avg_warm > 0 else float("inf")

    print(f"\n{'Average':<12}  cold={avg_cold*1000:7.1f}ms  warm={avg_warm*1000:7.1f}ms  speedup={avg_speedup:.2f}x")


if __name__ == "__main__":
    asyncio.run(main())
