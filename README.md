# MessagePack Converter

本專案提供一個用於 JSON 與 MessagePack 格式互轉的 Python 函式庫，且**不使用任何第三方 MessagePack 函式庫**。所有功能皆依據 MessagePack 規範實作，支援所有格式（包含整數、浮點數、字串、二進位、陣列、字典以及擴充格式）。

## 執行環境

- **作業系統**：macOS 15.3.2
- **Python 版本**：3.13.2

## 檔案介紹

- **msgpack_lib.py**：實作 MessagePack 的編碼（`pack`）與解碼（`unpack`）邏輯，支援所有 MessagePack 格式。
- **main.py**：程式進入點，可根據命令列參數進行 JSON 與 MessagePack 之間的轉換。透過 `--encode` 將 JSON 轉成 MessagePack（以 hex 格式輸出），或透過 `--decode` 將 MessagePack 的 hex 字串轉回 JSON。
- **test_msgpack.py**：單元測試檔案，覆蓋所有 MessagePack 格式的測試案例，確保編碼與解碼功能正確。
- **README.md**：本說明文件。

## 如何執行程式

### 編碼 (JSON 轉 MessagePack)

執行以下指令，將 JSON 字串轉換成 MessagePack 格式，結果以 hex 字串顯示：

```bash
python main.py --encode '{"name": "Alice", "age": 30, "is_student": false}'

>> 83a46e616d65a5416c696365a36167651eaa69735f73747564656e74c2
```

### 解碼 (MessagePack 轉 JSON)

執行以下指令，將 MessagePack 格式轉換成 JSON 字串，結果以 JSON 字串顯示：

```bash
python main.py --decode 83a46e616d65a5416c696365a36167651eaa69735f73747564656e74c2

>> {"name": "Alice", "age": 30, "is_student": false}
```

## 單元測試
```
python -m unittest test_msgpack.py
```

or

```
python test_msgpack.py
```