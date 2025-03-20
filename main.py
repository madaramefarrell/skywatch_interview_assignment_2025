import sys
import json
import argparse
import binascii
import msgpack_lib

def main():
    parser = argparse.ArgumentParser(description="JSON 與 MessagePack 轉換工具")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--encode", action="store_true", help="將 JSON 轉換為 MessagePack")
    group.add_argument("--decode", action="store_true", help="將 MessagePack 轉換回 JSON")
    parser.add_argument("data", help="輸入資料：若 encode 則為 JSON 字串；若 decode 則為 MessagePack 的 hex 字串")
    args = parser.parse_args()

    if args.encode:
        try:
            obj = json.loads(args.data)
        except Exception as e:
            print("JSON 格式錯誤:", e)
            sys.exit(1)
        packed = msgpack_lib.pack(obj)
        # 輸出以 hex 表示，方便觀察
        print(binascii.hexlify(packed).decode())
    elif args.decode:
        try:
            packed = binascii.unhexlify(args.data)
        except Exception as e:
            print("hex 格式錯誤:", e)
            sys.exit(1)
        try:
            obj = msgpack_lib.unpack(packed)
        except Exception as e:
            print("解碼失敗:", e)
            sys.exit(1)
        print(json.dumps(obj, ensure_ascii=False))

if __name__ == "__main__":
    main()
