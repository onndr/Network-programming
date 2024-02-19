import struct
import datastruct


class DataListProtocol:
    header_struct = struct.Struct('I')

    @staticmethod
    def serialize_packet(data_list: datastruct.DataList) -> bytes:
        data = DataListProtocol.header_struct.pack(data_list.get_node_count()) + data_list.serialize()
        return data
