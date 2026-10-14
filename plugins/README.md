ScriptMonkey – Flipper Zero Bluetooth LE Add-on
================================================

Installation
1. Install bleak into the SAME Python environment used to start ScriptMonkey:
   py -m pip install bleak
2. In ScriptMonkey open Erweiterungen -> Add-on-/Plugin-Verwaltung (or the plugin manager).
3. Open the add-on folder, copy flipper_ble_transport.py into that folder.
4. Return to the plugin manager, refresh, select the add-on and activate it.
5. Use Erweiterungen -> Flipper Zero über Bluetooth LE verbinden…

Important compatibility note
----------------------------
This add-on uses the Nordic UART Service (NUS) GATT UUIDs. Ordinary Bluetooth pairing
with a Flipper Zero does NOT expose its USB serial CLI over BLE. Stock Flipper firmware
generally does not provide this NUS-to-CLI bridge. The device needs compatible custom
firmware or a separate bridge that exposes the Flipper CLI as NUS RX/TX characteristics.
If the service is absent, the add-on reports that clearly and does not claim the connection
works. USB connection and existing USB features are not modified.

Reuse of existing functions
---------------------------
When a compatible NUS transport is connected, the add-on installs a pyserial-like adapter
as ScriptMonkey's current serial connection. This allows existing serial-based CLI, console,
filesystem, upload, and download functions to use the BLE transport without rewriting the
main application. Actual commands still depend on the firmware bridge's CLI behavior and
BLE throughput/packet limits.
