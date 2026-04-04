#!/bin/bash

# --- 1. カーネルモジュールのロード ---
echo "--- Loading CAN Kernel Modules ---"

# CANプロトコルの基本機能
sudo modprobe can
# 生のCANソケットを扱うためのプロトコル
sudo modprobe can_raw
# Jetson Orin内蔵のCANコントローラ用ドライバ (Multi-Target TT CAN)
sudo modprobe mttcan

# モジュールが反映されるまで少し待機
sleep 1

# --- 2. インターフェース設定 (can0) ---
echo "--- Initializing CAN Hardware (can0) ---"

# 設定変更のために一度停止
sudo ip link set can0 down 2>/dev/null

# 【物理設定の詳細】
# bitrate 1000000 : 通信速度 1Mbps
# restart-ms 100  : エラー（バスオフ）発生時に100ミリ秒で自動復帰
# one-shot on     : 重要！ACKがなくても再送を繰り返さず、次へ進む設定
sudo ip link set can0 up type can bitrate 1000000 restart-ms 100 one-shot on

# 【バッファ（キュー）設定】
# txqueuelen 10   : 送信待ちバッファをあえて小さく（10件）制限
# これにより、通信が詰まっても古いデータが破棄され、最新の指令が優先される
sudo ip link set can0 txqueuelen 10

# --- 3. 状態確認 ---
if [ $? -eq 0 ]; then
    echo "✅ SUCCESS: can0 is UP and READY (1Mbps, One-Shot)!"
    # 現在のステータスを表示
    ip -details link show can0 | grep -E "state|bitrate|one-shot"
else
    echo "❌ ERROR: Failed to bring up can0. Check cables or Device Tree."
    exit 1
fi