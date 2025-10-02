import asyncio
from bleak import BleakScanner
import json
from datetime import datetime

class SimpleBLEScanner:
    def __init__(self):
        self.devices_found = {}
        
    async def scan(self, duration=30):
        """Simple BLE scanning with telemetry data extraction"""
        print(f"Scanning for BLE devices for {duration} seconds...")
        print("Press Ctrl+C to stop early\n")
        
        def detection_callback(device, advertisement_data):
            current_time = datetime.now().isoformat()
            
            device_info = {
                'name': device.name or 'Unknown',
                'address': device.address,
                'rssi': device.rssi,
                'timestamp': current_time,
                'services': list(advertisement_data.service_uuids),
                'manufacturer_data': {},
                'local_name': advertisement_data.local_name,
                'tx_power': advertisement_data.tx_power
            }
            
            # Parse manufacturer data
            for manufacturer_id, data in advertisement_data.manufacturer_data.items():
                device_info['manufacturer_data'][f"{manufacturer_id:04X}"] = {
                    'hex': data.hex(),
                    'length': len(data)
                }
            
            self.devices_found[device.address] = device_info
            
            # Display device information
            print(f"[{current_time[11:19]}] {device.name or 'Unknown'} - {device.address}")
            print(f"  RSSI: {device.rssi} dBm")
            
            if advertisement_data.manufacturer_data:
                print("  Manufacturer Data:")
                for manuf_id, data in advertisement_data.manufacturer_data.items():
                    print(f"    {manuf_id:04X}: {data.hex()}")
            
            if advertisement_data.service_uuids:
                print(f"  Services: {', '.join(advertisement_data.service_uuids[:3])}")
                if len(advertisement_data.service_uuids) > 3:
                    print(f"    ... and {len(advertisement_data.service_uuids) - 3} more")
            
            print()
        
        scanner = BleakScanner(detection_callback=detection_callback)
        
        try:
            await scanner.start()
            await asyncio.sleep(duration)
            await scanner.stop()
        except KeyboardInterrupt:
            await scanner.stop()
            print("\nScan stopped by user")
        
        return self.devices_found
    
    def save_scan_results(self, filename="ble_scan_results.json"):
        """Save scan results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.devices_found, f, indent=2, default=str)
        print(f"Scan results saved to {filename}")
    
    def print_summary(self):
        """Print summary of found devices"""
        print("\n=== SCAN SUMMARY ===")
        print(f"Total devices found: {len(self.devices_found)}")
        
        # Group by device type
        device_types = {}
        for device in self.devices_found.values():
            name = device['name']
            if name == 'Unknown':
                device_type = 'Unknown'
            elif any(keyword in name.lower() for keyword in ['phone', 'mobile', 'iphone', 'samsung']):
                device_type = 'Phone'
            elif any(keyword in name.lower() for keyword in ['watch', 'fitbit', 'garmin', 'wear']):
                device_type = 'Wearable'
            elif any(keyword in name.lower() for keyword in ['sensor', 'temp', 'humidity']):
                device_type = 'Sensor'
            elif any(keyword in name.lower() for keyword in ['beacon', 'ibeacon']):
                device_type = 'Beacon'
            elif any(keyword in name.lower() for keyword in ['headset', 'earbud', 'airpod']):
                device_type = 'Audio'
            else:
                device_type = 'Other'
            
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        print("\nDevice types:")
        for dev_type, count in device_types.items():
            print(f"  {dev_type}: {count}")

# Quick usage example
async def quick_scan():
    scanner = SimpleBLEScanner()
    devices = await scanner.scan(duration=15)
    scanner.print_summary()
    scanner.save_scan_results()

if __name__ == "__main__":
    # Run quick scan
    asyncio.run(quick_scan())
