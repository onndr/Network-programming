import struct
from typing import Optional


class ListNode:
    TITLE_LENGTH = 256
    serialized_struct = struct.Struct(f'=iihxxI{TITLE_LENGTH}sI')

    def __init__(self, id: int, rating: int, price: int, title: str, content: Optional[str], next=None):
        self.id = id
        self.next: Optional[ListNode] = next
        self.rating = rating
        self.price = price
        self.title = title
        self.content = content

    def serialize(self) -> bytes:
        return ListNode.serialized_struct.pack(
            self.id,
            self.next.id if self.next else -1,
            self.rating,
            self.price,
            self.title.encode("ascii"),
            len(self.content)) + self.content.encode("ascii")

    def __str__(self):
        return f"Node: {self.id}, rating: {self.rating}, price: {self.price}"


class DataList:
    def __init__(self):
        self.nodes: list[ListNode] = []
        self.root: Optional[ListNode] = None
        self.last: Optional[ListNode] = None

    def get_node_count(self)->int:
        return len(self.nodes)

    def serialize(self):
        buffer = bytes()
        for node in self.nodes:
            buffer += node.serialize()
        return buffer

    def deserialize(self, buffer: bytes):
        self.nodes = []
        assignments = []
        all_ids = []
        self.root = None
        self.last = None

        # initial decoding of nodes one by one
        offset = 0
        while offset < len(buffer):
            # header
            (
                node_id,
                next_id,
                rating,
                price,
                title,
                content_length
            ) = ListNode.serialized_struct.unpack_from(buffer, offset)
            new_node = ListNode(node_id, rating, price, title.decode("ascii"), None, None)
            offset += ListNode.serialized_struct.size
            # content
            new_node.content = buffer[offset:offset + content_length].decode("ascii")
            offset += content_length

            assignments.append(next_id)
            all_ids.append(node_id)
            self.nodes.append(new_node)

        # assigning pointers
        for next_id, node_i in zip(assignments, range(len(self.nodes))):
            if next_id == -1:
                # assigning last
                self.last = self.nodes[node_i]
                continue
            self.nodes[node_i].next = next(filter(lambda node: node.id == next_id, self.nodes))

        # assigning root
        root_id = next(filter(lambda node_id: node_id not in assignments, all_ids))
        self.root = next(filter(lambda node: node.id == root_id, self.nodes))

    def __str__(self):
        cur_node = self.root
        output = ""
        while cur_node.next is not None:
            output += str(cur_node) + "\n"
            cur_node = cur_node.next
        return output

    def get_root_node(self):
        return self.root

    def get_last_node(self):
        return self.last

    def add_node(self, node: ListNode):
        if self.root == None:
            self.root = node
            self.last = node
        self.nodes.append(node)
        self.last.next = node
        self.last = node
