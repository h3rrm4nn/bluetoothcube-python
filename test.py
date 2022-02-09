#!/bin/python
import asyncio
import logging

from bleak import discover
from bleak import BleakClient

from Crypto.Cipher import AES


# Top   | Bottom

# 2   3 | 6   7
#   W   |   W
# 1   0 | 5   4
#   G   |   G
#
# Top   | Middle  | Bottom

#   3   | 10   11 |   7
# 2 W 0 |    W    | 6 W 4
#   1   |  9    8 |   5
#   G   |    G    |   G
#

class Cube:

    def __init__(self, corner_pos, corner_twist, edge_pos, edge_twist):
        self.corner_pos   = corner_pos
        self.corner_twist = corner_twist
        self.edge_pos     = edge_pos
        self.edge_twist   = edge_twist

    def set_state(self, corner_pos, corner_twist, edge_pos, edge_twist):
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
            # TODO:
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
                # corner_perm   = [ 4, 7, 3, 0]
                # edge_perm     = [ 8, 4,11, 0]
                twist_corners = True
                twist_edges   = False
            elif (move[i] == "L" or move[i] == "Lp"):
                corner_perm   = [ 6, 2, 1, 5]
                edge_perm     = [ 6,10, 2, 9]
                # corner_perm   = [ 1, 2, 6, 5]
                # edge_perm     = [ 2,10, 6, 9]
                twist_corners = True
                twist_edges   = False
            elif (move[i] == "F" or move[i] == "Fp"):
                corner_perm   = [ 0, 4, 5, 1]
                edge_perm     = [ 1, 8, 5, 9]
                # corner_perm   = [ 5, 4, 0, 1]
                # edge_perm     = [ 5, 8, 1, 9]
                twist_corners = True
                twist_edges   = True
            elif (move[i] == "B" or move[i] == "Bp"):
                corner_perm   = [ 7, 3, 2, 6]
                edge_perm     = [11, 3,10, 7]
                # corner_perm   = [ 2, 3, 7, 6]
                # edge_perm     = [10, 3,11, 7]
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
        buffer = vec[perm_indices[0]]
        for i in [0,1,2]:
            vec[perm_indices[i]] = vec[perm_indices[i+1]]
        vec[perm_indices[3]] = buffer
        return vec

    def permute_ccwise(self, vec, perm_indices):
        buffer = vec[perm_indices[3]]
        for i in [3,2,1]:
            vec[perm_indices[i]] = vec[perm_indices[i-1]]
        vec[perm_indices[0]] = buffer
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


class Bluetooth_cube:

    def __init__(self):

        # Device dependent key
        self.address = "AB:12:34:01:42:00"
        self.device_key = [0x00, 0x42, 0x01, 0x34, 0x12, 0xab]

        # Service UUIDs for GAN bluetooth cubes version 2
        self.UUID_LISTEN = "28be4cb6-cd67-11e9-a32f-2a2ae2dbcce4"
        self.UUID_WRITE = "28be4a4a-cd67-11e9-a32f-2a2ae2dbcce4"

        # Key for GAN bluetooth cubes version 2
        GAN_V2_KEY = [
            0x01, 0x02, 0x42, 0x28, 0x31, 0x91, 0x16, 0x07, 0x20, 0x05, 0x18, 0x54, 0x42, 0x11,
            0x12, 0x53,
        ]
        GAN_V2_IV = [
            0x11, 0x03, 0x32, 0x28, 0x21, 0x01, 0x76, 0x27, 0x20, 0x95, 0x78, 0x14, 0x32, 0x12,
            0x02, 0x43,
        ]

        # Compute device key
        self.key = GAN_V2_KEY;
        self.iv = GAN_V2_IV;
        for idx, byte in enumerate(self.device_key) :
            self.key[idx] = ((self.key[idx] + byte) % 255)
            self.iv[idx] = ((self.iv[idx] + byte) % 255)

        # Move mapping for GAN cube
        self.MOVES = [ "Up", "U", "Rp", "R", "Fp", "F", "Dp", "D", "Lp", "L", "Bp", "B" ];

        # Write message to initialize cube state reply
        self.MSG_CUBE_STATE = [4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        # Write message to initialize battery state reply
        self.MSG_BATTERY_STATE = [9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        # Init virtual cube
        self.cube = Cube([0,1,2,3,4,5,6,7],[0,0,0,0,0,0,0,0],[0,1,2,3,4,5,6,7,8,9,10,11],[0,0,0,0,0,0,0,0,0,0,0,0])

        self.move_count = 0;
        self.cube_initialized = False;


    def decrypt(self, value):

        # decrypt last 16 bytes
        offset = len(value) - 16;
        end_plain = value[offset :]

        cipher = AES.new(bytes(self.key), AES.MODE_CBC, bytes(self.iv))
        end_plain = cipher.decrypt(bytes(end_plain))
        for idx,byte in enumerate(end_plain) :
            value[offset+idx] = byte

        # decrypt first 16 bytes
        start_plain = value[: 16]

        cipher = AES.new(bytes(self.key), AES.MODE_CBC, bytes(self.iv))
        # cipher.iv = bytes(iv)
        start_plain = cipher.decrypt(bytes(start_plain))
        for idx,byte in enumerate(start_plain) :
            value[idx] = byte

        return value

    def encrypt(self, value):

        # encrypt first 16 bytes
        start_plain = value[: 16]

        cipher = AES.new(bytes(self.key), AES.MODE_CBC, bytes(self.iv))
        start_plain = cipher.encrypt(bytes(start_plain))
        for idx,byte in enumerate(start_plain) :
            value[idx] = byte

        # encrypt last 16 bytes
        offset = len(value) - 16;
        end_plain = value[offset :]

        cipher = AES.new(bytes(self.key), AES.MODE_CBC, bytes(self.iv))
        end_plain = cipher.encrypt(bytes(end_plain))
        for idx,byte in enumerate(end_plain) :
            value[offset+idx] = byte

        return value

    def extract_bits(self, data, start, count):
        result = 0
        for i in range(count):
            bit = start + i
            result = result << 1
            if data[bit // 8] & (1 << (7 - (bit % 8))) != 0:
                result |= 1;
        return result

    def notification_handler(self, sender, data):
        data = self.decrypt(data)
        message_type = self.extract_bits(data, 0, 4);
        if (message_type == 2) :
            if (self.cube_initialized):
                current_move_count = self.extract_bits(data, 4, 8)
                move_count = current_move_count - self.move_count
                self.move_count = current_move_count
                for j in range(move_count):
                    i = (move_count - 1) - j
                    move_num = self.extract_bits(data, 12 + i * 5, 5)
                    # move_time = self.extract_bits(data, 12 + 7 * 5 + i * 16, 16)
                    move = self.MOVES[move_num]
                    self.cube.move([move])
        elif (message_type == 4) :
            self.move_count = self.extract_bits(data, 4, 8)
            self.cube_initialized = True
            [corner_pos, corner_twist] = self.decode_corners(data)
            [edge_pos, edge_twist] = self.decode_edges(data)
            self.cube.set_state(corner_pos, corner_twist, edge_pos, edge_twist)
            self.cube.print_state()
        elif (message_type == 9) :
            self.decode_battery_state(data)

    def decode_battery_state(self, value):
        percent = self.extract_bits(value, 8, 8)
        print("Battery: ", percent, "%")

    def decode_corners(self, value):
        # Decode corners. There are only 7 in the packet because the
        # last one is implicit (the one missing).
        corners = [0] * 8
        corner_twist = [0] * 8
        total_corner_twist = 0
        corners_left = list(range(8))
        for i in range(7):
            corners[i] = self.extract_bits(value, 12 + i * 3, 3)
            corner_twist[i] = self.extract_bits(value, 33 + i * 2, 2)
            total_corner_twist += corner_twist[i]
            corners_left.remove(corners[i])
        corners[7] = corners_left[0]
        corner_twist[7] = (3 - total_corner_twist % 3) % 3
        return corners, corner_twist

    def decode_edges(self, value):
        # Decode edges. There are only 11 in the packet because the
        # last one is implicit (the one missing).
        edges = [0] * 12
        edge_parity = [0] * 12
        total_edge_parity = 0
        edges_left = list(range(12))
        for i in range(11):
            edges[i] = self.extract_bits(value, 47 + i * 4, 4)
            edge_parity[i] = self.extract_bits(value, 91 + i, 1)
            total_edge_parity += edge_parity[i]
            edges_left.remove(edges[i])
        edges[11] = edges_left[0]
        edge_parity[11] = total_edge_parity & 1
        return edges, edge_parity

async def run(bt_cube, debug=False):

    async with BleakClient(bt_cube.address) as client:
        x = await client.is_connected()

        await client.start_notify(bt_cube.UUID_LISTEN, bt_cube.notification_handler)

        # get initial cube state
        await client.write_gatt_char(bt_cube.UUID_WRITE, bt_cube.encrypt(bt_cube.MSG_CUBE_STATE))
        await client.write_gatt_char(bt_cube.UUID_WRITE, bt_cube.encrypt(bt_cube.MSG_BATTERY_STATE))
        await asyncio.sleep(50.0)

        await client.stop_notify(bt_cube.UUID_LISTEN)

if __name__ == "__main__":

    #Run notify event
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    bt_cube = Bluetooth_cube()
    loop.run_until_complete(run(bt_cube, True))
    bt_cube.cube.print_state()
