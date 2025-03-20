import struct

class Ext:
    """
    表示 MessagePack 擴充型別（Extension Type）。
    type: 類型編號（通常在 -128 ~ 127 範圍內）
    data: bytes 型態的資料
    """
    def __init__(self, type: int, data: bytes):
        self.type = type
        self.data = data

    def __eq__(self, other):
        return isinstance(other, Ext) and self.type == other.type and self.data == other.data

def pack(obj):
    """將 Python 物件編碼為 MessagePack 格式的 bytes"""
    return _pack(obj)

def _pack(obj):
    if obj is None:
        return b'\xc0'  # nil
    elif isinstance(obj, bool):
        return b'\xc3' if obj else b'\xc2'
    elif isinstance(obj, int):
        if obj >= 0:
            if obj <= 0x7f:
                return struct.pack("B", obj)  # positive fixint
            elif obj <= 0xff:
                return b'\xcc' + struct.pack("B", obj)  # uint 8
            elif obj <= 0xffff:
                return b'\xcd' + struct.pack(">H", obj)  # uint 16
            elif obj <= 0xffffffff:
                return b'\xce' + struct.pack(">I", obj)  # uint 32
            elif obj <= 0xffffffffffffffff:
                return b'\xcf' + struct.pack(">Q", obj)  # uint 64
            else:
                raise OverflowError("Integer too large")
        else:
            if -32 <= obj < 0:
                return struct.pack("b", obj)  # negative fixint
            elif obj >= -128:
                return b'\xd0' + struct.pack("b", obj)  # int 8
            elif obj >= -32768:
                return b'\xd1' + struct.pack(">h", obj)  # int 16
            elif obj >= -2147483648:
                return b'\xd2' + struct.pack(">i", obj)  # int 32
            elif obj >= -9223372036854775808:
                return b'\xd3' + struct.pack(">q", obj)  # int 64
            else:
                raise OverflowError("Integer too small")
    elif isinstance(obj, float):
        # 皆以 float64 編碼 (0xcb)
        return b'\xcb' + struct.pack(">d", obj)
    elif isinstance(obj, str):
        encoded = obj.encode("utf-8")
        length = len(encoded)
        if length <= 31:
            return struct.pack("B", 0xa0 | length) + encoded  # fixstr
        elif length <= 0xff:
            return b'\xd9' + struct.pack("B", length) + encoded  # str 8
        elif length <= 0xffff:
            return b'\xda' + struct.pack(">H", length) + encoded  # str 16
        elif length <= 0xffffffff:
            return b'\xdb' + struct.pack(">I", length) + encoded  # str 32
        else:
            raise OverflowError("String too long")
    elif isinstance(obj, bytes):
        length = len(obj)
        if length <= 0xff:
            return b'\xc4' + struct.pack("B", length) + obj  # bin 8
        elif length <= 0xffff:
            return b'\xc5' + struct.pack(">H", length) + obj  # bin 16
        elif length <= 0xffffffff:
            return b'\xc6' + struct.pack(">I", length) + obj  # bin 32
        else:
            raise OverflowError("Binary data too long")
    elif isinstance(obj, list):
        length = len(obj)
        if length <= 15:
            result = struct.pack("B", 0x90 | length)  # fixarray
        elif length <= 0xffff:
            result = b'\xdc' + struct.pack(">H", length)  # array 16
        elif length <= 0xffffffff:
            result = b'\xdd' + struct.pack(">I", length)  # array 32
        else:
            raise OverflowError("Array too long")
        for item in obj:
            result += _pack(item)
        return result
    elif isinstance(obj, dict):
        length = len(obj)
        if length <= 15:
            result = struct.pack("B", 0x80 | length)  # fixmap
        elif length <= 0xffff:
            result = b'\xde' + struct.pack(">H", length)  # map 16
        elif length <= 0xffffffff:
            result = b'\xdf' + struct.pack(">I", length)  # map 32
        else:
            raise OverflowError("Map too large")
        for k, v in obj.items():
            result += _pack(k)
            result += _pack(v)
        return result
    elif isinstance(obj, Ext):
        data = obj.data
        length = len(data)
        if length == 1:
            return b'\xd4' + struct.pack("b", obj.type) + data  # fixext 1
        elif length == 2:
            return b'\xd5' + struct.pack("b", obj.type) + data  # fixext 2
        elif length == 4:
            return b'\xd6' + struct.pack("b", obj.type) + data  # fixext 4
        elif length == 8:
            return b'\xd7' + struct.pack("b", obj.type) + data  # fixext 8
        elif length == 16:
            return b'\xd8' + struct.pack("b", obj.type) + data  # fixext 16
        elif length <= 0xff:
            return b'\xc7' + struct.pack("B", length) + struct.pack("b", obj.type) + data  # ext 8
        elif length <= 0xffff:
            return b'\xc8' + struct.pack(">H", length) + struct.pack("b", obj.type) + data  # ext 16
        elif length <= 0xffffffff:
            return b'\xc9' + struct.pack(">I", length) + struct.pack("b", obj.type) + data  # ext 32
        else:
            raise OverflowError("Extension data too long")
    else:
        raise TypeError("Type not supported: " + str(type(obj)))

def unpack(b: bytes):
    """將 MessagePack 格式的 bytes 解碼成 Python 物件"""
    obj, offset = _unpack(b, 0)
    if offset != len(b):
        raise ValueError("Extra bytes found")
    return obj

def _unpack(b: bytes, offset: int):
    if offset >= len(b):
        raise ValueError("Unexpected end of data")
    first = b[offset]
    # positive fixint (0x00 - 0x7f)
    if first <= 0x7f:
        return first, offset + 1
    # fixmap (0x80 - 0x8f)
    elif 0x80 <= first <= 0x8f:
        length = first & 0x0f
        offset += 1
        result = {}
        for _ in range(length):
            key, offset = _unpack(b, offset)
            value, offset = _unpack(b, offset)
            result[key] = value
        return result, offset
    # fixarray (0x90 - 0x9f)
    elif 0x90 <= first <= 0x9f:
        length = first & 0x0f
        offset += 1
        result = []
        for _ in range(length):
            item, offset = _unpack(b, offset)
            result.append(item)
        return result, offset
    # fixstr (0xa0 - 0xbf)
    elif 0xa0 <= first <= 0xbf:
        length = first & 0x1f
        offset += 1
        s = b[offset:offset+length].decode("utf-8")
        return s, offset + length
    # nil (0xc0)
    elif first == 0xc0:
        return None, offset + 1
    # reserved (0xc1) -> 未使用，拋出例外
    elif first == 0xc1:
        raise ValueError("Reserved byte encountered: 0xc1")
    # false (0xc2)
    elif first == 0xc2:
        return False, offset + 1
    # true (0xc3)
    elif first == 0xc3:
        return True, offset + 1
    # bin 8 (0xc4)
    elif first == 0xc4:
        if offset + 2 > len(b):
            raise ValueError("Insufficient bytes for bin 8")
        length = b[offset+1]
        offset += 2
        if offset + length > len(b):
            raise ValueError("Insufficient bytes for bin8 data")
        data = b[offset:offset+length]
        return data, offset + length
    # bin 16 (0xc5)
    elif first == 0xc5:
        if offset + 3 > len(b):
            raise ValueError("Insufficient bytes for bin 16")
        length = struct.unpack(">H", b[offset+1:offset+3])[0]
        offset += 3
        if offset + length > len(b):
            raise ValueError("Insufficient bytes for bin16 data")
        data = b[offset:offset+length]
        return data, offset + length
    # bin 32 (0xc6)
    elif first == 0xc6:
        if offset + 5 > len(b):
            raise ValueError("Insufficient bytes for bin 32")
        length = struct.unpack(">I", b[offset+1:offset+5])[0]
        offset += 5
        if offset + length > len(b):
            raise ValueError("Insufficient bytes for bin32 data")
        data = b[offset:offset+length]
        return data, offset + length
    # ext 8 (0xc7)
    elif first == 0xc7:
        if offset + 2 > len(b):
            raise ValueError("Insufficient bytes for ext 8 length")
        length = b[offset+1]
        if offset + 3 + length > len(b):
            raise ValueError("Insufficient bytes for ext8 data")
        ext_type = struct.unpack("b", b[offset+2:offset+3])[0]
        data = b[offset+3:offset+3+length]
        return Ext(ext_type, data), offset + 3 + length
    # ext 16 (0xc8)
    elif first == 0xc8:
        if offset + 3 > len(b):
            raise ValueError("Insufficient bytes for ext 16 length")
        length = struct.unpack(">H", b[offset+1:offset+3])[0]
        if offset + 4 + length > len(b):
            raise ValueError("Insufficient bytes for ext16 data")
        ext_type = struct.unpack("b", b[offset+3:offset+4])[0]
        data = b[offset+4:offset+4+length]
        return Ext(ext_type, data), offset + 4 + length
    # ext 32 (0xc9)
    elif first == 0xc9:
        if offset + 5 > len(b):
            raise ValueError("Insufficient bytes for ext 32 length")
        length = struct.unpack(">I", b[offset+1:offset+5])[0]
        if offset + 6 + length > len(b):
            raise ValueError("Insufficient bytes for ext32 data")
        ext_type = struct.unpack("b", b[offset+5:offset+6])[0]
        data = b[offset+6:offset+6+length]
        return Ext(ext_type, data), offset + 6 + length
    # float 32 (0xca)
    elif first == 0xca:
        if offset + 5 > len(b):
            raise ValueError("Insufficient bytes for float32")
        value = struct.unpack(">f", b[offset+1:offset+5])[0]
        return value, offset + 5
    # float 64 (0xcb)
    elif first == 0xcb:
        if offset + 9 > len(b):
            raise ValueError("Insufficient bytes for float64")
        value = struct.unpack(">d", b[offset+1:offset+9])[0]
        return value, offset + 9
    # uint 8 (0xcc)
    elif first == 0xcc:
        if offset + 2 > len(b):
            raise ValueError("Insufficient bytes for uint8")
        value = b[offset+1]
        return value, offset + 2
    # uint 16 (0xcd)
    elif first == 0xcd:
        if offset + 3 > len(b):
            raise ValueError("Insufficient bytes for uint16")
        value = struct.unpack(">H", b[offset+1:offset+3])[0]
        return value, offset + 3
    # uint 32 (0xce)
    elif first == 0xce:
        if offset + 5 > len(b):
            raise ValueError("Insufficient bytes for uint32")
        value = struct.unpack(">I", b[offset+1:offset+5])[0]
        return value, offset + 5
    # uint 64 (0xcf)
    elif first == 0xcf:
        if offset + 9 > len(b):
            raise ValueError("Insufficient bytes for uint64")
        value = struct.unpack(">Q", b[offset+1:offset+9])[0]
        return value, offset + 9
    # int 8 (0xd0)
    elif first == 0xd0:
        if offset + 2 > len(b):
            raise ValueError("Insufficient bytes for int8")
        value = struct.unpack("b", b[offset+1:offset+2])[0]
        return value, offset + 2
    # int 16 (0xd1)
    elif first == 0xd1:
        if offset + 3 > len(b):
            raise ValueError("Insufficient bytes for int16")
        value = struct.unpack(">h", b[offset+1:offset+3])[0]
        return value, offset + 3
    # int 32 (0xd2)
    elif first == 0xd2:
        if offset + 5 > len(b):
            raise ValueError("Insufficient bytes for int32")
        value = struct.unpack(">i", b[offset+1:offset+5])[0]
        return value, offset + 5
    # int 64 (0xd3)
    elif first == 0xd3:
        if offset + 9 > len(b):
            raise ValueError("Insufficient bytes for int64")
        value = struct.unpack(">q", b[offset+1:offset+9])[0]
        return value, offset + 9
    # fixext 1 (0xd4)
    elif first == 0xd4:
        if offset + 3 > len(b):
            raise ValueError("Insufficient bytes for fixext 1")
        ext_type = struct.unpack("b", b[offset+1:offset+2])[0]
        data = b[offset+2:offset+3]
        return Ext(ext_type, data), offset + 3
    # fixext 2 (0xd5)
    elif first == 0xd5:
        if offset + 4 > len(b):
            raise ValueError("Insufficient bytes for fixext 2")
        ext_type = struct.unpack("b", b[offset+1:offset+2])[0]
        data = b[offset+2:offset+4]
        return Ext(ext_type, data), offset + 4
    # fixext 4 (0xd6)
    elif first == 0xd6:
        if offset + 6 > len(b):
            raise ValueError("Insufficient bytes for fixext 4")
        ext_type = struct.unpack("b", b[offset+1:offset+2])[0]
        data = b[offset+2:offset+6]
        return Ext(ext_type, data), offset + 6
    # fixext 8 (0xd7)
    elif first == 0xd7:
        if offset + 10 > len(b):
            raise ValueError("Insufficient bytes for fixext 8")
        ext_type = struct.unpack("b", b[offset+1:offset+2])[0]
        data = b[offset+2:offset+10]
        return Ext(ext_type, data), offset + 10
    # fixext 16 (0xd8)
    elif first == 0xd8:
        if offset + 18 > len(b):
            raise ValueError("Insufficient bytes for fixext 16")
        ext_type = struct.unpack("b", b[offset+1:offset+2])[0]
        data = b[offset+2:offset+18]
        return Ext(ext_type, data), offset + 18
    # str 8 (0xd9)
    elif first == 0xd9:
        if offset + 2 > len(b):
            raise ValueError("Insufficient bytes for str8 length")
        length = b[offset+1]
        offset += 2
        s = b[offset:offset+length].decode("utf-8")
        return s, offset + length
    # str 16 (0xda)
    elif first == 0xda:
        if offset + 3 > len(b):
            raise ValueError("Insufficient bytes for str16 length")
        length = struct.unpack(">H", b[offset+1:offset+3])[0]
        offset += 3
        s = b[offset:offset+length].decode("utf-8")
        return s, offset + length
    # str 32 (0xdb)
    elif first == 0xdb:
        if offset + 5 > len(b):
            raise ValueError("Insufficient bytes for str32 length")
        length = struct.unpack(">I", b[offset+1:offset+5])[0]
        offset += 5
        s = b[offset:offset+length].decode("utf-8")
        return s, offset + length
    # array 16 (0xdc)
    elif first == 0xdc:
        if offset + 3 > len(b):
            raise ValueError("Insufficient bytes for array16 length")
        length = struct.unpack(">H", b[offset+1:offset+3])[0]
        offset += 3
        result = []
        for _ in range(length):
            item, offset = _unpack(b, offset)
            result.append(item)
        return result, offset
    # array 32 (0xdd)
    elif first == 0xdd:
        if offset + 5 > len(b):
            raise ValueError("Insufficient bytes for array32 length")
        length = struct.unpack(">I", b[offset+1:offset+5])[0]
        offset += 5
        result = []
        for _ in range(length):
            item, offset = _unpack(b, offset)
            result.append(item)
        return result, offset
    # map 16 (0xde)
    elif first == 0xde:
        if offset + 3 > len(b):
            raise ValueError("Insufficient bytes for map16 length")
        length = struct.unpack(">H", b[offset+1:offset+3])[0]
        offset += 3
        result = {}
        for _ in range(length):
            key, offset = _unpack(b, offset)
            value, offset = _unpack(b, offset)
            result[key] = value
        return result, offset
    # map 32 (0xdf)
    elif first == 0xdf:
        if offset + 5 > len(b):
            raise ValueError("Insufficient bytes for map32 length")
        length = struct.unpack(">I", b[offset+1:offset+5])[0]
        offset += 5
        result = {}
        for _ in range(length):
            key, offset = _unpack(b, offset)
            value, offset = _unpack(b, offset)
            result[key] = value
        return result, offset
    # negative fixint (0xe0 - 0xff)
    elif first >= 0xe0:
        return struct.unpack("b", bytes([first]))[0], offset + 1
    else:
        raise ValueError("Unknown byte code: 0x%x at offset %d" % (first, offset))
