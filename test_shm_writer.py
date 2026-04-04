#!/usr/bin/env python3
import time
import numpy as np
from multiprocessing import shared_memory
import sys

def main():
    shm_name = 'can_motor_speed'
    
    try:
        # 1. 共有メモリに接続
        shm = shared_memory.SharedMemory(name=shm_name)
        shared_data = np.ndarray((4,), dtype=np.int16, buffer=shm.buf)
        print(f"🔗 共有メモリ '{shm_name}' に接続しました。")
    except FileNotFoundError:
        print(f"❌ エラー: '{shm_name}' が見つかりません。")
        print("先に 'bash start_robot.sh' を実行してください。")
        return

    # テスト用の速度設定 (例: 300 mm/s)
    test_speed = 300 
    print(f"🚀 テスト開始: 全輪に速度 {test_speed} を送信し続けます...")
    print("停止するには [Ctrl + C] を押してください。")

    try:
        while True:
            # 共有メモリを更新
            shared_data[:] = [test_speed, test_speed, test_speed, test_speed]
            
            # 50msごとに書き込み（ネイティブ送信機がこれを検知してCANへ送る）
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n🛑 停止信号を受信。速度を0に戻します。")
        shared_data[:] = [0, 0, 0, 0]
    finally:
        shm.close()

if __name__ == "__main__":
    main()