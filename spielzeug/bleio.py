import struct

import bluetooth
import micropython
from micropython import const

connected = True

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)
_ADV_APPEARANCE_GENERIC_REMOTE_CONTROL = const(384)


_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
_ADV_TYPE_UUID16_MORE = const(0x2)
_ADV_TYPE_UUID32_MORE = const(0x4)
_ADV_TYPE_UUID128_MORE = const(0x6)
_ADV_TYPE_APPEARANCE = const(0x19)

_ADV_MAX_PAYLOAD = const(31)


def advertising_payload(
    limited_disc=False, br_edr=False, name=None, services=None, appearance=0
):
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value

    _append(
        _ADV_TYPE_FLAGS,
        struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)),
    )

    if name:
        _append(_ADV_TYPE_NAME, name)

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)

    if appearance:
        _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

    if len(payload) > _ADV_MAX_PAYLOAD:
        raise ValueError("advertising payload too large")

    return payload


STATE_IDLE = 0
STATE_ADVERTISING = 1
STATE_CONNECTED = 2


class BLEIOConnector:
    def __init__(self, ble, name):
        self._ble = ble
        self._state = STATE_IDLE
        self._packet = b""
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services(
            (_UART_SERVICE,)
        )
        self._ble.gatts_set_buffer(self._rx_handle, 128, True)
        self._connection = None
        self._payload = advertising_payload(
            name=name,
            # appearance=_ADV_APPEARANCE_GENERIC_REMOTE_CONTROL,
            # services=[_UART_UUID],
        )
        self._force_disconnect = False
        self._packet_handlers = {}
        self._error_handler = print

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            if self._connection or not self._state == STATE_ADVERTISING:
                return 1
            conn_handle, _, _ = data
            self._connection = conn_handle
            self._state = STATE_CONNECTED
            self._advertise(None)
            self._force_disconnect = False
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connection = None
            if not self._force_disconnect:
                self._state = STATE_ADVERTISING
                self._advertise()
            else:
                self._state = STATE_IDLE
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if conn_handle == self._connection and value_handle == self._rx_handle:
                self._rx_handler(self._ble.gatts_read(self._rx_handle))

    def _rx_handler(self, data: bytes):
        self._packet += data
        if b"\x1a" in data:
            if len(self._packet) > 1:
                self._handle_packet(self._packet[: self._packet.index(b"\x1a")])
            self._packet = b""

    def _handle_packet(self, packet: bytes):
        packet_handler = self._packet_handlers.get(packet[0])
        if packet_handler is None:
            self._error_handler(packet, None)
            return
        arguments = packet[1:]
        try:
            packet_handler(arguments)
        except Exception as e:
            self._error_handler(packet, e)

    def set_handler(self, packet_id: int | bytes, handler):
        if isinstance(packet_id, bytes):
            packet_id = packet_id[0]
        self._packet_handlers[packet_id] = handler

    def handles(self, packet_id: int | bytes):
        if isinstance(packet_id, bytes):
            packet_id = packet_id[0]

        def wrapper(handler):
            self._packet_handlers[packet_id] = handler

        return wrapper

    def write(self, data):
        if self._connection is not None:
            self._ble.gatts_notify(self._connection, self._tx_handle, data)

    def send_packet(self, packet_id: int | bytes, data: bytes | None = None):
        if isinstance(packet_id, int):
            packet_id = packet_id.to_bytes()
        if data is None:
            data = b""
        self.write(packet_id + data + b"\x1a")

    def _close(self):
        if self._connection is not None:
            self._ble.gap_disconnect(self._connection)

    def disconnect(self):
        self._force_disconnect = True
        self._close()

    def _advertise(self, interval_us: int | None = 500):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def start_advertising(self):
        if self._state == STATE_IDLE:
            self._state = STATE_ADVERTISING
            self._advertise()
        else:
            raise RuntimeError(
                "Cannot start advertising from state {}".format(self._state)
            )

    def stop_advertising(self):
        if self._state == STATE_ADVERTISING:
            self._state = STATE_IDLE
            self._ble.gap_advertise(None)

    def is_idle(self):
        return self._state == STATE_IDLE

    def is_connected(self):
        return self._state == STATE_CONNECTED

    def is_advertising(self):
        return self._state == STATE_ADVERTISING


BLEIO = BLEIOConnector(bluetooth.BLE(), "GSG-Robots")

__all__ = ["BLEIO"]
