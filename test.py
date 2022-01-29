#!/bin/python
import asyncio
import logging

from bleak import discover
from bleak import BleakClient

from Crypto.Cipher import AES


def decrypt(value):

    device_key = [0x00, 0x42, 0x01, 0x34, 0x12, 0xab]

    GAN_V2_KEY = [
        0x01, 0x02, 0x42, 0x28, 0x31, 0x91, 0x16, 0x07, 0x20, 0x05, 0x18, 0x54, 0x42, 0x11,
        0x12, 0x53,
    ]
    GAN_V2_IV = [
        0x11, 0x03, 0x32, 0x28, 0x21, 0x01, 0x76, 0x27, 0x20, 0x95, 0x78, 0x14, 0x32, 0x12,
        0x02, 0x43,
    ]

    key = GAN_V2_KEY;
    iv = GAN_V2_IV;

    for idx, byte in enumerate(device_key) :
        key[idx] = ((key[idx] + byte) % 255)
        iv[idx] = ((iv[idx] + byte) % 255)

    # decrypt last 16 bytes
    offset = len(value) - 16;
    end_plain = value[offset :]

    cipher = AES.new(bytes(key), AES.MODE_CBC, bytes(iv))
    end_plain = cipher.decrypt(bytes(end_plain))
    for idx,byte in enumerate(end_plain) :
        value[offset+idx] = byte

    # decrypt first 16 bytes
    start_plain = value[: 16]

    cipher = AES.new(bytes(key), AES.MODE_CBC, bytes(iv))
    # cipher.iv = bytes(iv)
    start_plain = cipher.decrypt(bytes(start_plain))
    for idx,byte in enumerate(start_plain) :
        value[idx] = byte

    return value

def extract_bits(data, start, count):
    result = 0
    for i in range(count):
        bit = start + i
        result = result << 1
        if data[bit // 8] & (1 << (7 - (bit % 8))) != 0:
            result |= 1;
    return result

def decode_move(value):

    message_type = extract_bits(value, 0, 4)
    current_move_count = extract_bits(value, 4, 8)

    # assume only one move has been performed
    i = 1;
    move_num = extract_bits(value, 12 + i * 5, 5)
    move_time = extract_bits(value, 12 + 7 * 5 + i * 16, 16)
    MOVES = [
        "Up",
        "U",
        "Rp",
        "R",
        "Fp",
        "F",
        "Dp",
        "D",
        "Lp",
        "L",
        "Bp",
        "B",
    ];
    print(MOVES[move_num])

def notification_handler(sender, data):
    # print(', '.join('{:02x}'.format(x) for x in data))
    data = decrypt(data)
    decode_move(data)


async def run(address, debug=False):
    log = logging.getLogger(__name__)
    if debug:
        import sys

        log.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        log.addHandler(h)

    async with BleakClient(address) as client:
        x = await client.is_connected()
        log.info("Connected: {0}".format(x))

        CHARACTERISTIC_UUID = "28be4cb6-cd67-11e9-a32f-2a2ae2dbcce4"

        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        await asyncio.sleep(20.0)
        await client.stop_notify(CHARACTERISTIC_UUID)


if __name__ == "__main__":

    address = "AB:12:34:01:42:00"

    #Run notify event
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(run(address, True))
