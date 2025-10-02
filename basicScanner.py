import asyncio
from bleak import BleakScanner

async def main():
    print("Scanning for Bluetooth LE devices...")
    devices = await BleakScanner.discover(timeout=8.0)
    if not devices:
        print("No BLE devices found.")
    else:
        print(f"Found {len(devices)} BLE devices:")
        for d in devices:
            print(f"  {d.address} - {d.name}")

if __name__ == "__main__":
    asyncio.run(main())
