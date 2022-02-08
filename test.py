#!/bin/python
import asyncio
import logging

from bleak import discover
from bleak import BleakClient

from Crypto.Cipher import AES


# class Cube:

#     def __init__(self):
#         self.state = name

#     def move(self, move):
#         if move == "U":
#             self.

# Top   | Bottom

# 2   3 | 6   7
#   W   |   W
# 1   0 | 5   4
#   G   |   G
#
# Top   | Bottom | Middle

#   3   |   7    | 10   11
# 2 W 0 | 6 W 4  |    W
#   1   |   5    |  9    8
#   G   |   G    |    G
#

class Cube:

    def __init__(self, corner_pos, corner_twist, edge_pos, edge_twist):
        self.corner_pos   = corner_pos
        self.corner_twist = corner_twist
        self.edge_pos     = edge_pos
        self.edge_twist   = edge_twist

    def move(self, move):
        for i in range(len(move)):
            corner_perm = []
            edge_perm = []
            twist_corners = False
            twist_edges = False
            if (move[i] == "U" or move[i] == "Up"):
                corner_perm   = [ 0, 1, 2, 3]
                edge_perm     = [ 0, 1, 2, 3]
                twist_corners = False
                twist_edges   = False
            elif (move[i] == "D" or move[i] == "Dp"):
                corner_perm   = [ 4, 7, 6, 5]
                edge_perm     = [ 4, 7, 6, 5]
                twist_corners = False
                twist_edges   = False
            elif (move[i] == "R" or move[i] == "Rp"):
                corner_perm   = [  3, 7, 4, 0]
                edge_perm     = [ 11, 4, 8, 0]
                twist_corners = True
                twist_edges   = False
            elif (move[i] == "L" or move[i] == "Lp"):
                corner_perm   = [ 1, 5, 6, 2]
                edge_perm     = [ 2, 9, 6,10]
                twist_corners = True
                twist_edges   = False
            elif (move[i] == "F" or move[i] == "Fp"):
                corner_perm   = [ 0, 4, 5, 1]
                edge_perm     = [ 1, 8, 5, 9]
                twist_corners = True
                twist_edges   = True
            elif (move[i] == "B" or move[i] == "Bp"):
                corner_perm   = [ 2, 6, 7, 3]
                edge_perm     = [10, 7,11, 3]
                twist_corners = True
                twist_edges   = True

            if (len(move[i]) == 1):
                self.permute_cwise(self.corner_pos, corner_perm)
                self.permute_cwise(self.corner_twist, corner_perm)
                self.permute_cwise(self.edge_pos, edge_perm)
                self.permute_cwise(self.edge_twist, edge_perm)
            else:
                self.permute_ccwise(self.corner_pos, corner_perm)
                self.permute_ccwise(self.corner_twist, corner_perm)
                self.permute_ccwise(self.edge_pos, edge_perm)
                self.permute_ccwise(self.edge_twist, edge_perm)

            if (twist_corners):
                self.twist_corners(self.corner_twist, corner_perm)

            if (twist_edges):
                self.twist_edges(self.edge_twist, edge_perm)

    def permute_cwise(self, vec, perm_indices):
        buffer = vec[perm_indices[3]]
        for i in [3,2,1]:
            vec[perm_indices[i]] = vec[perm_indices[i-1]]
        vec[perm_indices[0]] = buffer
        return vec

    def permute_ccwise(self, vec, perm_indices):
        buffer = vec[perm_indices[0]]
        for i in [0,1,2]:
            vec[perm_indices[i]] = vec[perm_indices[i+1]]
        vec[perm_indices[3]] = buffer
        return vec

    def twist_corners(self, vec, perm_indices):
        vec[perm_indices[0]] = (vec[perm_indices[0]] + 1) % 3
        vec[perm_indices[1]] = (vec[perm_indices[1]] + 2) % 3
        vec[perm_indices[2]] = (vec[perm_indices[2]] + 1) % 3
        vec[perm_indices[3]] = (vec[perm_indices[3]] + 2) % 3
        return vec

    def twist_edges(self, vec, perm_indices):
        vec[perm_indices[0]] = (vec[perm_indices[0]] + 1) % 2
        vec[perm_indices[1]] = (vec[perm_indices[1]] + 1) % 2
        vec[perm_indices[2]] = (vec[perm_indices[2]] + 1) % 2
        vec[perm_indices[3]] = (vec[perm_indices[3]] + 1) % 2
        return vec

    def print_state(self):
        print(self.corner_pos)
        print(self.corner_twist)
        print(self.edge_pos)
        print(self.edge_twist)



address = "AB:12:34:01:42:00"
device_key = [0x00, 0x42, 0x01, 0x34, 0x12, 0xab]

GAN_V2_KEY = [
    0x01, 0x02, 0x42, 0x28, 0x31, 0x91, 0x16, 0x07, 0x20, 0x05, 0x18, 0x54, 0x42, 0x11,
    0x12, 0x53,
]
GAN_V2_IV = [
    0x11, 0x03, 0x32, 0x28, 0x21, 0x01, 0x76, 0x27, 0x20, 0x95, 0x78, 0x14, 0x32, 0x12,
    0x02, 0x43,
]
UUID_LISTEN = "28be4cb6-cd67-11e9-a32f-2a2ae2dbcce4"
UUID_WRITE = "28be4a4a-cd67-11e9-a32f-2a2ae2dbcce4"

key = GAN_V2_KEY;
iv = GAN_V2_IV;

for idx, byte in enumerate(device_key) :
    key[idx] = ((key[idx] + byte) % 255)
    iv[idx] = ((iv[idx] + byte) % 255)

MOVES = [ "Up", "U", "Rp", "R", "Fp", "F", "Dp", "D", "Lp", "L", "Bp", "B" ];

MSG_CUBE_STATE = [4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
MSG_BATTERY_STATE = [9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]



def decrypt(value):

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

def encrypt(value):

    # encrypt first 16 bytes
    start_plain = value[: 16]

    cipher = AES.new(bytes(key), AES.MODE_CBC, bytes(iv))
    start_plain = cipher.encrypt(bytes(start_plain))
    for idx,byte in enumerate(start_plain) :
        value[idx] = byte

    # encrypt last 16 bytes
    offset = len(value) - 16;
    end_plain = value[offset :]

    cipher = AES.new(bytes(key), AES.MODE_CBC, bytes(iv))
    end_plain = cipher.encrypt(bytes(end_plain))
    for idx,byte in enumerate(end_plain) :
        value[offset+idx] = byte

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
    print(MOVES[move_num])

def notification_handler(sender, data):
    data = decrypt(data)
    message_type = extract_bits(data, 0, 4);
    if (message_type == 2) :
        decode_move(data)
    elif (message_type == 4) :
        decode_corners(data)
        decode_edges(data)
    elif (message_type == 9) :
        decode_battery_state(data)

    # print(', '.join('{:02x}'.format(x) for x in data))

def decode_battery_state(value):
    percent = extract_bits(value, 8, 8)
    print("Battery: ", percent, "%")

def decode_corners(value):
    # Decode corners. There are only 7 in the packet because the
    # last one is implicit (the one missing).
    corners = [0] * 8
    corner_twist = [0] * 8
    total_corner_twist = 0
    corners_left = list(range(8))
    for i in range(7):
        corners[i] = extract_bits(value, 12 + i * 3, 3)
        corner_twist[i] = extract_bits(value, 33 + i * 2, 2)
        total_corner_twist += corner_twist[i]
        corners_left.remove(corners[i])
    corners[7] = corners_left[0]
    corner_twist[7] = (3 - total_corner_twist % 3) % 3
    print(corners)
    print(corner_twist)

def decode_edges(value):
    # Decode edges. There are only 11 in the packet because the
    # last one is implicit (the one missing).
    edges = [0] * 12
    edge_parity = [0] * 12
    total_edge_parity = 0
    edges_left = list(range(12))
    for i in range(11):
        edges[i] = extract_bits(value, 47 + i * 4, 4)
        edge_parity[i] = extract_bits(value, 91 + i, 1)
        total_edge_parity += edge_parity[i]
        edges_left.remove(edges[i])
    edges[11] = edges_left[0]
    edge_parity[11] = total_edge_parity & 1
    print(edges)
    print(edge_parity)

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

        await client.start_notify(UUID_LISTEN, notification_handler)

        # get initial cube state
        await client.write_gatt_char(UUID_WRITE, encrypt(MSG_CUBE_STATE))
        await client.write_gatt_char(UUID_WRITE, encrypt(MSG_BATTERY_STATE))
        await asyncio.sleep(8.0)

        await client.stop_notify(UUID_LISTEN)


if __name__ == "__main__":

    #Run notify event
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    A = Cube([0,1,2,3,4,5,6,7],[0,0,0,0,0,0,0,0],[0,1,2,3,4,5,6,7,8,9,10,11],[0,0,0,0,0,0,0,0,0,0,0,0])
    A.move(["L", "U", "Lp", "Up", "B", "R", "Up", "D"])
    A.print_state()
    # A.move(["Up"])
    # A.print_state()
    loop.run_until_complete(run(address, True))
