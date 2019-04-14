
import json

class PacketRW:
    def __init__(self, conn):
        self.all_bytes = bytes()
        self.conn = conn

    def recv(self):
        while True:
            # find the first complete packet in the buffer
            pos = self.all_bytes.find(b'\x00')
            if pos == -1:
                # no valid packets in buffer, wait for more data
                self.all_bytes += self.conn.recv(1024)
            else:
                # a null terminator (packet terminator) is in the buffer, pop
                # off and return decoded value
                packet = self.all_bytes[0:pos]
                self.all_bytes = self.all_bytes[pos+1:]
                return json.loads(packet)

    def send(self, d):
        json_packet = json.dumps(d, separators=(',', ':'))
        self.conn.sendall(json_packet.encode() + b'\x00')

