#!/usr/bin/env python3
import socket
import struct
import time
import sys
import numpy as np
from multiprocessing import shared_memory

def main():
    shm_name = 'can_motor_speed'
    
    # 1. 共有メモリへの接続（Writer側が作っていなければ作成）
    try:
        shm = shared_memory.SharedMemory(name=shm_name, create=True, size=8)
        print(f"✨ 共有メモリ '{shm_name}' を新規作成しました。")
    except FileExistsError:
        shm = shared_memory.SharedMemory(name=shm_name)
        print(f"🔗 既存の共有メモリ '{shm_name}' に接続しました。")

    # 2. 共有メモリを numpy 配列としてキャスト (int16 x 4輪 = 8バイト)
    # [FL, FR, RL, RR] の順番を想定
    shared_data = np.ndarray((4,), dtype=np.int16, buffer=shm.buf)
    shared_data[:] = [0, 0, 0, 0] # 起動時は停止状態

    # 3. SocketCAN の設定 (AF_CAN=29, SOCK_RAW=3, CAN_RAW=1)
    try:
        sock = socket.socket(29, 3, 1)
        sock.bind(('can0',))
        # 送信バッファが一杯でも待機せず、即座に次のループへ回す（ノンブロッキング）
        sock.setblocking(False)
        print("🚀 SocketCAN (can0) 送信準備完了。監視を開始します...")
    except Exception as e:
        print(f"❌ CANソケットの初期化に失敗: {e}")
        sys.exit(1)

    last_data = np.zeros(4, dtype=np.int16)

    try:
        while True:
            # 4. 共有メモリ内のデータが更新されたかチェック
            if not np.array_equal(shared_data, last_data):
                # ID: 0x100, DLC: 8, Data: リトルエンディアン short x 4
                # struct.pack('<hhhh', ...) は 2byte整数×4 を 8byteバイナリに変換
                can_payload = struct.pack('<hhhh', *shared_data)
                
                # SocketCAN フレーム構造体 (ID 4B + DLC 1B + Padding 3B + Data 8B)
                can_frame = struct.pack("=IB3x8s", 0x100, 8, can_payload)
                
                try:
                    sock.send(can_frame)
                except (BlockingIOError, OSError):
                    # バッファが一杯（EAGAIN）の場合は、古いデータは捨てて次へ
                    pass
                
                # 最後に送信したデータを記録
                last_data[:] = shared_data[:]
            
            # CPU負荷を抑えるための微小な待機 (約 200Hz 周期)
            time.sleep(0.005)

    except KeyboardInterrupt:
        print("\n🛑 終了信号を受信。モーターを停止して終了します。")
        stop_payload = struct.pack('<hhhh', 0, 0, 0, 0)
        stop_frame = struct.pack("=IB3x8s", 0x100, 8, stop_payload)
        try:
            sock.send(stop_frame)
        except:
            pass
    finally:
        shm.close()

if __name__ == "__main__":
    main()