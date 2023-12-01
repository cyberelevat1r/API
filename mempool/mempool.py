import asyncio
import random
import aiohttp
import aiofiles
from hdwallet import HDWallet
from hdwallet.symbols import BTC
import time

# Create a lock to synchronize print statements
print_lock = asyncio.Lock()

# Counters
address_counter = 0
checked_addresses = 0
total_keys_checked = 0
found_addresses_counter = 0
error_count = 0

# Time tracking
start_time = time.time()

async def get_bal_async(session, addr, max_retries=3):
    url = f"https://mempool.space/api/address/{addr}"

    for attempt in range(max_retries):
        try:
            async with session.get(url) as response:
                if 'application/json' not in response.headers.get('Content-Type', ''):
                    raise ValueError(f"Unexpected response format: {response.content}")

                data = await response.json()
                if 'error' in data:
                    raise ValueError(f"API Error: {data['error']}")
                return float(data['chain_stats']['funded_txo_sum']) / 100000000  # Assuming balance is in satoshis
        except Exception as e:
            async with print_lock:
                line_to_print = f"\rError fetching balance for {addr}. Retrying... (Attempt {attempt + 1}/{max_retries}) - Errors: {error_count + 1}"
                print(line_to_print, end='', flush=True)
            error_count += 1
            await asyncio.sleep(1)

    raise ValueError(f"Failed to fetch balance for {addr} after {max_retries} attempts.")

async def generate_random_private_key_and_address():
    private_key = "".join(random.choice("0123456789abcdef") for _ in range(64))
    hd_btc = HDWallet(BTC)
    hd_btc.from_private_key(private_key)
    btc_address = hd_btc.p2pkh_address()
    return private_key, btc_address

async def save_to_file_async(private_key, btc_address, balance):
    if balance > 0.00001:
        global address_counter
        address_counter += 1
        file_name = f"{btc_address}.txt"
        async with aiofiles.open(file_name, 'w') as file:
            await file.write(f"Private Key: {private_key}\n")
            await file.write(f"Bitcoin Address: {btc_address}\n")
            await file.write(f"Balance: {balance} BTC\n")
        async with print_lock:
            print(f"Data saved to {file_name}")

async def generate_and_check_address():
    global checked_addresses, start_time, total_keys_checked, found_addresses_counter, error_count
    try:
        private_key, btc_address = await generate_random_private_key_and_address()

        async with aiohttp.ClientSession() as session:
            balance = await get_bal_async(session, btc_address)

        checked_addresses += 1
        total_keys_checked += 1
        elapsed_time = time.time() - start_time
        speed = checked_addresses / elapsed_time

        async with print_lock:
            line_to_print = (
    f"\rAPI: Mempool.space | "  # Replace "Mempool.space" with the actual name of your API
    f"Total Keys Checked: {total_keys_checked} | "
    f"Found Addresses: {found_addresses_counter} | "
    f"Errors: {error_count} | "
    f"Speed: {speed:.2f} key/s"
)

            print(line_to_print, end='', flush=True)

        if balance > 0.00001:
            found_addresses_counter += 1
            async with print_lock:
                line_to_print += (
                    f" | Address #{address_counter}: {btc_address} - "
                    f"Private Key: {private_key[:6]}...{private_key[-3:]} - "
                    f"Balance: {balance} BTC"
                )
                line_to_print += f" | Found Addresses with Balance: {found_addresses_counter}"
                print(line_to_print)

            await save_to_file_async(private_key, btc_address, balance)

    except Exception as e:
        async with print_lock:
            line_to_print = f"\rAn err occu: {e}       Fixed Errors: {error_count}"
            print(line_to_print, end='', flush=True)
        error_count += 1

async def main():
    num_threads = 25

    while True:
        tasks = [generate_and_check_address() for _ in range(num_threads)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())

