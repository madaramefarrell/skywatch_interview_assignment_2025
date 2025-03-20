import unittest
import struct
import msgpack_lib

class TestMsgPackFormats(unittest.TestCase):
    # 正 fixint (0x00 - 0x7f)
    def test_positive_fixint(self):
        for value in [0, 1, 42, 127]:
            packed = msgpack_lib.pack(value)
            self.assertEqual(packed[0], value)
            self.assertEqual(msgpack_lib.unpack(packed), value)

    # 負 fixint (0xe0 - 0xff)
    def test_negative_fixint(self):
        for value in range(-32, 0):
            packed = msgpack_lib.pack(value)
            self.assertTrue(0xe0 <= packed[0] <= 0xff)
            self.assertEqual(msgpack_lib.unpack(packed), value)

    # uint 8 (0xcc)
    def test_uint8(self):
        for value in [128, 200, 255]:
            packed = msgpack_lib.pack(value)
            self.assertEqual(packed[0], 0xcc)
            self.assertEqual(msgpack_lib.unpack(packed), value)

    # uint 16 (0xcd)
    def test_uint16(self):
        for value in [256, 1000, 65535]:
            packed = msgpack_lib.pack(value)
            self.assertEqual(packed[0], 0xcd)
            self.assertEqual(msgpack_lib.unpack(packed), value)

    # uint 32 (0xce)
    def test_uint32(self):
        for value in [65536, 1000000, 0xffffffff]:
            packed = msgpack_lib.pack(value)
            self.assertEqual(packed[0], 0xce)
            self.assertEqual(msgpack_lib.unpack(packed), value)

    # uint 64 (0xcf)
    def test_uint64(self):
        for value in [0x100000000, 0xffffffffffffffff]:
            packed = msgpack_lib.pack(value)
            self.assertEqual(packed[0], 0xcf)
            self.assertEqual(msgpack_lib.unpack(packed), value)

    # int 8 (0xd0)
    def test_int8(self):
        for value in [-33, -50, -128]:
            packed = msgpack_lib.pack(value)
            self.assertEqual(packed[0], 0xd0)
            self.assertEqual(msgpack_lib.unpack(packed), value)

    # int 16 (0xd1)
    def test_int16(self):
        for value in [-129, -1000, -32768]:
            packed = msgpack_lib.pack(value)
            self.assertEqual(packed[0], 0xd1)
            self.assertEqual(msgpack_lib.unpack(packed), value)

    # int 32 (0xd2)
    def test_int32(self):
        for value in [-32769, -100000, -2147483648]:
            packed = msgpack_lib.pack(value)
            self.assertEqual(packed[0], 0xd2)
            self.assertEqual(msgpack_lib.unpack(packed), value)

    # int 64 (0xd3)
    def test_int64(self):
        for value in [-2147483649, -10000000000, -9223372036854775808]:
            packed = msgpack_lib.pack(value)
            self.assertEqual(packed[0], 0xd3)
            self.assertEqual(msgpack_lib.unpack(packed), value)

    # float 64 (0xcb)
    def test_float64(self):
        for value in [0.0, 3.14, -2.71828, 1.23456789e10]:
            packed = msgpack_lib.pack(value)
            self.assertEqual(packed[0], 0xcb)
            self.assertAlmostEqual(msgpack_lib.unpack(packed), value, places=5)

    # float 32 (0xca) 測試解碼 (手動建立)
    def test_float32_decoding(self):
        value = 3.14
        packed = b'\xca' + struct.pack(">f", value)
        result = msgpack_lib.unpack(packed)
        self.assertAlmostEqual(result, value, places=5)

    # fixstr (0xa0 - 0xbf)
    def test_fixstr(self):
        s = "hello"  # 長度 5 (<=31)
        packed = msgpack_lib.pack(s)
        self.assertTrue(0xa0 <= packed[0] <= 0xbf)
        self.assertEqual(msgpack_lib.unpack(packed), s)

    # str 8 (0xd9)
    def test_str8(self):
        s = "a" * 50  # 長度介於 32 ~ 255
        packed = msgpack_lib.pack(s)
        self.assertEqual(packed[0], 0xd9)
        self.assertEqual(struct.unpack("B", packed[1:2])[0], len(s))
        self.assertEqual(msgpack_lib.unpack(packed), s)

    # str 16 (0xda)
    def test_str16(self):
        s = "a" * 300  # 長度介於 256 ~ 65535
        packed = msgpack_lib.pack(s)
        self.assertEqual(packed[0], 0xda)
        self.assertEqual(struct.unpack(">H", packed[1:3])[0], len(s))
        self.assertEqual(msgpack_lib.unpack(packed), s)

    # str 32 (0xdb)
    def test_str32(self):
        s = "a" * 70000  # 長度大於 65535
        packed = msgpack_lib.pack(s)
        self.assertEqual(packed[0], 0xdb)
        self.assertEqual(struct.unpack(">I", packed[1:5])[0], len(s))
        self.assertEqual(msgpack_lib.unpack(packed), s)

    # nil (0xc0)
    def test_nil(self):
        packed = msgpack_lib.pack(None)
        self.assertEqual(packed, b'\xc0')
        self.assertIsNone(msgpack_lib.unpack(packed))

    # false (0xc2) 與 true (0xc3)
    def test_bool(self):
        for value, byte in [(False, 0xc2), (True, 0xc3)]:
            packed = msgpack_lib.pack(value)
            self.assertEqual(packed[0], byte)
            self.assertEqual(msgpack_lib.unpack(packed), value)

    # bin 8 (0xc4)
    def test_bin8(self):
        data = bytes(range(10))
        packed = msgpack_lib.pack(data)
        self.assertEqual(packed[0], 0xc4)
        self.assertEqual(struct.unpack("B", packed[1:2])[0], len(data))
        self.assertEqual(msgpack_lib.unpack(packed), data)

    # bin 16 (0xc5)
    def test_bin16(self):
        data = bytes([i % 256 for i in range(300)])
        packed = msgpack_lib.pack(data)
        self.assertEqual(packed[0], 0xc5)
        self.assertEqual(struct.unpack(">H", packed[1:3])[0], len(data))
        self.assertEqual(msgpack_lib.unpack(packed), data)

    # bin 32 (0xc6)
    def test_bin32(self):
        data = bytes([i % 256 for i in range(70000)])
        packed = msgpack_lib.pack(data)
        self.assertEqual(packed[0], 0xc6)
        self.assertEqual(struct.unpack(">I", packed[1:5])[0], len(data))
        self.assertEqual(msgpack_lib.unpack(packed), data)

    # fixarray (0x90 - 0x9f)
    def test_fixarray(self):
        arr = [1, 2, 3]
        packed = msgpack_lib.pack(arr)
        self.assertTrue(0x90 <= packed[0] <= 0x9f)
        self.assertEqual(msgpack_lib.unpack(packed), arr)

    # array 16 (0xdc)
    def test_array16(self):
        arr = list(range(16))
        packed = msgpack_lib.pack(arr)
        self.assertEqual(packed[0], 0xdc)
        self.assertEqual(struct.unpack(">H", packed[1:3])[0], len(arr))
        self.assertEqual(msgpack_lib.unpack(packed), arr)

    # array 32 (0xdd)
    def test_array32(self):
        arr = list(range(70000))
        packed = msgpack_lib.pack(arr)
        self.assertEqual(packed[0], 0xdd)
        self.assertEqual(struct.unpack(">I", packed[1:5])[0], len(arr))
        self.assertEqual(msgpack_lib.unpack(packed), arr)

    # fixmap (0x80 - 0x8f)
    def test_fixmap(self):
        d = {"a": 1, "b": 2}
        packed = msgpack_lib.pack(d)
        self.assertTrue(0x80 <= packed[0] <= 0x8f)
        self.assertEqual(msgpack_lib.unpack(packed), d)

    # map 16 (0xde)
    def test_map16(self):
        d = {f"key{i}": i for i in range(16)}
        packed = msgpack_lib.pack(d)
        self.assertEqual(packed[0], 0xde)
        self.assertEqual(struct.unpack(">H", packed[1:3])[0], len(d))
        self.assertEqual(msgpack_lib.unpack(packed), d)

    # map 32 (0xdf)
    def test_map32(self):
        d = {f"key{i}": i for i in range(70000)}
        packed = msgpack_lib.pack(d)
        self.assertEqual(packed[0], 0xdf)
        self.assertEqual(struct.unpack(">I", packed[1:5])[0], len(d))
        self.assertEqual(msgpack_lib.unpack(packed), d)

    # fixext 1 (0xd4)
    def test_fixext1(self):
        ext_obj = msgpack_lib.Ext(1, b'\x01')
        packed = msgpack_lib.pack(ext_obj)
        self.assertEqual(packed[0], 0xd4)
        self.assertEqual(msgpack_lib.unpack(packed), ext_obj)

    # fixext 2 (0xd5)
    def test_fixext2(self):
        ext_obj = msgpack_lib.Ext(2, b'\x01\x02')
        packed = msgpack_lib.pack(ext_obj)
        self.assertEqual(packed[0], 0xd5)
        self.assertEqual(msgpack_lib.unpack(packed), ext_obj)

    # fixext 4 (0xd6)
    def test_fixext4(self):
        ext_obj = msgpack_lib.Ext(3, b'\x01\x02\x03\x04')
        packed = msgpack_lib.pack(ext_obj)
        self.assertEqual(packed[0], 0xd6)
        self.assertEqual(msgpack_lib.unpack(packed), ext_obj)

    # fixext 8 (0xd7)
    def test_fixext8(self):
        ext_obj = msgpack_lib.Ext(4, b'\x01\x02\x03\x04\x05\x06\x07\x08')
        packed = msgpack_lib.pack(ext_obj)
        self.assertEqual(packed[0], 0xd7)
        self.assertEqual(msgpack_lib.unpack(packed), ext_obj)

    # fixext 16 (0xd8)
    def test_fixext16(self):
        ext_obj = msgpack_lib.Ext(5, b'\x01' * 16)
        packed = msgpack_lib.pack(ext_obj)
        self.assertEqual(packed[0], 0xd8)
        self.assertEqual(msgpack_lib.unpack(packed), ext_obj)

    # ext 8 (0xc7) - 非 fixext 長度，例：3 bytes
    def test_ext8(self):
        ext_obj = msgpack_lib.Ext(6, b'\x01\x02\x03')
        packed = msgpack_lib.pack(ext_obj)
        self.assertEqual(packed[0], 0xc7)
        self.assertEqual(struct.unpack("B", packed[1:2])[0], len(ext_obj.data))
        self.assertEqual(msgpack_lib.unpack(packed), ext_obj)

    # ext 16 (0xc8) - 例：300 bytes
    def test_ext16(self):
        ext_obj = msgpack_lib.Ext(7, b'\x01' * 300)
        packed = msgpack_lib.pack(ext_obj)
        self.assertEqual(packed[0], 0xc8)
        self.assertEqual(struct.unpack(">H", packed[1:3])[0], len(ext_obj.data))
        self.assertEqual(msgpack_lib.unpack(packed), ext_obj)

    # ext 32 (0xc9) - 例：70000 bytes
    def test_ext32(self):
        ext_obj = msgpack_lib.Ext(8, b'\x01' * 70000)
        packed = msgpack_lib.pack(ext_obj)
        self.assertEqual(packed[0], 0xc9)
        self.assertEqual(struct.unpack(">I", packed[1:5])[0], len(ext_obj.data))
        self.assertEqual(msgpack_lib.unpack(packed), ext_obj)

    # reserved 0xc1 (never used) 測試遇到時拋出例外
    def test_reserved_c1(self):
        with self.assertRaises(ValueError):
            msgpack_lib.unpack(b'\xc1')

if __name__ == '__main__':
    unittest.main()
