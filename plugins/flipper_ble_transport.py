"""ScriptMonkey add-on: Flipper Zero BLE UART transport (requires compatible firmware)."""
from __future__ import annotations

import asyncio
import threading
import time
from collections import deque

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout,
    QMessageBox, QInputDialog
)

ADDON_NAME = "Flipper Zero Bluetooth LE"
VERSION = "1.0.0"
ADDON_DESCRIPTION = (
    "BLE-UART-Transport für kompatible Flipper-Firmware; nutzt die vorhandenen "
    "seriellen CLI-, Datei- und Payload-Funktionen, sofern die Firmware CLI über BLE bridged."
)

# Nordic UART Service (NUS). Stock Flipper Zero firmware does not generally expose
# the USB CLI as this service; compatible custom firmware/bridge is required.
NUS_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NUS_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # app -> device
NUS_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # device -> app notifications


class BleUartSerialAdapter:
    """Small pyserial-like adapter so existing ScriptMonkey serial features can be reused."""
    def __init__(self, device, loop, loop_thread, client, write_char, notify_char):
        self.device = device
        self.loop = loop
        self.loop_thread = loop_thread
        self.client = client
        self.write_char = write_char
        self.notify_char = notify_char
        self.is_open = True
        self.timeout = 0.15
        self.write_timeout = 3.0
        self._buffer = bytearray()
        self._buffer_lock = threading.Lock()
        self._write_lock = threading.Lock()

    @property
    def in_waiting(self):
        with self._buffer_lock:
            return len(self._buffer)

    def _notify(self, _sender, data):
        with self._buffer_lock:
            # Bound memory if the UI is not reading the console.
            self._buffer.extend(bytes(data))
            if len(self._buffer) > 2 * 1024 * 1024:
                del self._buffer[:len(self._buffer) - 1024 * 1024]

    def _run(self, coro, timeout=None):
        if not self.is_open:
            raise OSError("BLE-Verbindung ist geschlossen")
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        try:
            return future.result(timeout=timeout or self.write_timeout)
        except Exception:
            future.cancel()
            raise

    def write(self, data):
        if not self.is_open:
            raise OSError("BLE-Verbindung ist geschlossen")
        payload = bytes(data)
        if not payload:
            return 0
        # Keep packets small for devices whose negotiated ATT MTU is limited.
        chunk_size = 180
        with self._write_lock:
            async def send_all():
                for offset in range(0, len(payload), chunk_size):
                    await self.client.write_gatt_char(
                        self.write_char, payload[offset:offset + chunk_size], response=False
                    )
                    # Avoid flooding BLE stacks with back-to-back writes.
                    await asyncio.sleep(0.004)
            self._run(send_all(), timeout=max(self.write_timeout, len(payload) / 500 + 2))
        return len(payload)

    def flush(self):
        # BLE GATT writes are awaited in write(); there is no additional OS buffer.
        return None

    def read(self, size=1):
        size = max(0, int(size))
        if size == 0:
            return b""
        deadline = time.monotonic() + max(0.0, float(self.timeout or 0))
        while True:
            with self._buffer_lock:
                if self._buffer:
                    take = min(size, len(self._buffer))
                    result = bytes(self._buffer[:take])
                    del self._buffer[:take]
                    return result
            if time.monotonic() >= deadline or not self.is_open:
                return b""
            time.sleep(0.005)

    def reset_input_buffer(self):
        with self._buffer_lock:
            self._buffer.clear()

    def reset_output_buffer(self):
        # Writes are synchronous and awaited, so there is no pending local queue.
        return None

    def close(self):
        if not self.is_open:
            return
        self.is_open = False
        async def shutdown():
            try:
                if self.client.is_connected:
                    try:
                        await self.client.stop_notify(self.notify_char)
                    except Exception:
                        pass
                    await self.client.disconnect()
            finally:
                return
        try:
            asyncio.run_coroutine_threadsafe(shutdown(), self.loop).result(timeout=5)
        except Exception:
            pass
        try:
            self.loop.call_soon_threadsafe(self.loop.stop)
        except Exception:
            pass
        if self.loop_thread.is_alive() and threading.current_thread() is not self.loop_thread:
            self.loop_thread.join(timeout=2)


def _ble_worker(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()
    if pending:
        try:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            pass
    loop.close()


def _scan_dialog(ide, devices):
    dlg = QDialog(ide)
    dlg.setWindowTitle("Flipper Zero über Bluetooth LE auswählen")
    dlg.resize(560, 360)
    layout = QVBoxLayout(dlg)
    layout.addWidget(QLabel(
        "Wähle ein Gerät mit BLE-UART/NUS-Unterstützung. Ein angezeigter Flipper-Eintrag "
        "garantiert nicht, dass dessen Firmware die CLI über Bluetooth bereitstellt."
    ))
    listing = QListWidget(dlg)
    for device, adv_name in devices:
        name = adv_name or device.name or "Unbekanntes BLE-Gerät"
        listing.addItem(f"{name}    [{device.address}]")
    if devices:
        listing.setCurrentRow(0)
    layout.addWidget(listing, 1)
    row = QHBoxLayout()
    connect_btn = QPushButton("Verbinden", dlg)
    cancel_btn = QPushButton("Abbrechen", dlg)
    row.addStretch(1)
    row.addWidget(connect_btn)
    row.addWidget(cancel_btn)
    layout.addLayout(row)
    connect_btn.clicked.connect(dlg.accept)
    cancel_btn.clicked.connect(dlg.reject)
    if dlg.exec() != QDialog.DialogCode.Accepted or listing.currentRow() < 0:
        return None
    return devices[listing.currentRow()]


def register(ide):
    state = {"adapter": None}

    def connect_ble():
        if getattr(ide, "serial_conn", None) is not None and getattr(ide.serial_conn, "is_open", False):
            QMessageBox.information(ide, ADDON_NAME,
                                    "Es besteht bereits eine serielle Verbindung. Bitte zuerst trennen.")
            return
        try:
            from bleak import BleakScanner, BleakClient
        except ImportError:
            QMessageBox.warning(
                ide, "Bleak fehlt",
                "Für Bluetooth LE wird das Paket 'bleak' benötigt.\n\n"
                "Installation im gleichen Python-Environment wie ScriptMonkey:\n"
                "py -m pip install bleak"
            )
            return

        wait_s, ok = QInputDialog.getInt(ide, "BLE-Suche", "Suchdauer in Sekunden:", 6, 2, 20, 1)
        if not ok:
            return
        try:
            devices = asyncio.run(BleakScanner.discover(timeout=wait_s, return_adv=True))
            rows = []
            for _address, pair in devices.items():
                device, adv = pair
                adv_name = getattr(adv, "local_name", None)
                name = adv_name or getattr(device, "name", None) or ""
                # Show Flipper-like devices and devices advertising the UART service.
                uuids = [str(x).lower() for x in (getattr(adv, "service_uuids", None) or [])]
                if "flipper" in name.lower() or NUS_SERVICE_UUID in uuids or not name:
                    rows.append((device, adv_name))
            # If filtering yielded nothing, show all discovered devices rather than hiding them.
            if not rows:
                rows = [(pair[0], getattr(pair[1], "local_name", None)) for pair in devices.values()]
            rows.sort(key=lambda item: ((item[1] or item[0].name or "").lower(), item[0].address))
        except Exception as exc:
            QMessageBox.critical(ide, "BLE-Suche fehlgeschlagen", str(exc))
            return
        if not rows:
            QMessageBox.information(ide, "Keine Geräte gefunden",
                                    "Keine BLE-Geräte gefunden. Bluetooth aktivieren und erneut suchen.")
            return
        selected = _scan_dialog(ide, rows)
        if selected is None:
            return
        device, adv_name = selected
        loop = asyncio.new_event_loop()
        thread = threading.Thread(target=_ble_worker, args=(loop,), name="ScriptMonkey-BLE", daemon=True)
        thread.start()
        client = BleakClient(device)
        try:
            async def establish():
                await client.connect()
                services = await client.get_services()
                chars = {str(ch.uuid).lower(): ch for service in services for ch in service.characteristics}
                rx = chars.get(NUS_RX_UUID)
                tx = chars.get(NUS_TX_UUID)
                if rx is None or tx is None:
                    await client.disconnect()
                    raise RuntimeError(
                        "Das Gerät stellt den erwarteten Nordic-UART-Dienst nicht bereit.\n\n"
                        "Stock-Flipper-Firmware bietet normalerweise keinen BLE-zu-USB-CLI-Bridge-Dienst. "
                        "Für die Wiederverwendung der vorhandenen Datei-/CLI-/Payload-Funktionen ist "
                        "kompatible Firmware oder eine entsprechende BLE-UART-Bridge erforderlich."
                    )
                adapter = BleUartSerialAdapter(device, loop, thread, client, rx, tx)
                await client.start_notify(tx, adapter._notify)
                return adapter
            adapter = asyncio.run_coroutine_threadsafe(establish(), loop).result(timeout=20)
            state["adapter"] = adapter
            ide.serial_conn = adapter
            ide.serial_port = "BLE · " + (adv_name or device.name or device.address)
            ide.statusBar().showMessage("Flipper verbunden über Bluetooth LE")
            if hasattr(ide, "update_flipper_status"):
                try:
                    ide.update_flipper_status()
                except Exception:
                    pass
            QMessageBox.information(
                ide, "BLE verbunden",
                "BLE-UART-Verbindung hergestellt. Vorhandene ScriptMonkey-Funktionen können "
                "nun über diesen Transport arbeiten, sofern die Firmware die Flipper-CLI darüber bridged."
            )
        except Exception as exc:
            try:
                loop.call_soon_threadsafe(loop.stop)
                thread.join(timeout=2)
            except Exception:
                pass
            QMessageBox.warning(ide, "BLE-Verbindung fehlgeschlagen", str(exc))

    def disconnect_ble():
        adapter = state.get("adapter")
        if adapter is None:
            QMessageBox.information(ide, ADDON_NAME, "Keine BLE-Verbindung dieses Add-ons aktiv.")
            return
        try:
            adapter.close()
        finally:
            if getattr(ide, "serial_conn", None) is adapter:
                ide.serial_conn = None
                ide.serial_port = None
            state["adapter"] = None
            ide.statusBar().showMessage("Flipper Bluetooth LE getrennt")
            if hasattr(ide, "update_flipper_status"):
                try:
                    ide.update_flipper_status()
                except Exception:
                    pass

    ide.register_menu_action("Flipper Zero über Bluetooth LE verbinden…", connect_ble)
    ide.register_menu_action("Flipper Bluetooth LE trennen", disconnect_ble)


def unregister(ide):
    # ScriptMonkey removes registered menu actions itself. Transport cleanup is handled
    # by the callbacks during normal use; avoid touching unrelated USB serial connections.
    return None
