import cv2
import datetime
import imutils
import time
import os

# --- 設定 ---
RTSP_URL = "rtsp://username:password@192.168.xxx.xxx/stream1"
OUTPUT_DIR = "/work/camera/detected_motion_images"
MIN_AREA = 10000  # 動体と見なす最小のピクセル面積

# 新しい設定: 背景学習率 (ALPHA)
# 値が小さいほど、背景はゆっくり更新されます (例: 0.01 = 1%)
ALPHA = 0.01
# -------------

# 出力ディレクトリを作成
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# RTSPストリームを開く
cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

if not cap.isOpened():
    print(f"エラー: RTSPストリーム ({RTSP_URL}) を開けませんでした。")
    exit()

# 最初のフレームを読み込み、背景モデルとして初期化
ret, frame = cap.read()
if not ret:
    print("エラー: 最初のフレームを読み込めませんでした。")
    cap.release()
    exit()

# 1. 背景フレームをグレースケール、ぼかし処理
background_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
background_frame = cv2.GaussianBlur(background_frame, (21, 21), 0)

# 2. accumulateWeighted()を使用するため、背景フレームをfloat型に変換
# これが背景モデルの「器」となります
background_frame = background_frame.astype("float")

print("動体検知を開始します...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("ストリームが終了したか、フレームの読み込みエラーが発生しました。再接続を試みます...")
        cap.release()
        cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
        time.sleep(5)
        continue

    # 現在のフレームをグレースケールに変換し、ぼかしを適用
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # 3. cv2.accumulateWeighted()で背景モデルを徐々に更新
    # background_frame = (1 - ALPHA) * background_frame + ALPHA * gray
    cv2.accumulateWeighted(gray, background_frame, ALPHA)

    # 4. 更新された背景モデルを8bit整数型に戻し、現在のフレームと比較できるようにする
    bg_model_8bit = cv2.convertScaleAbs(background_frame)

    # 背景モデル(8bit)と現在のフレーム(gray)の差分を計算
    frame_delta = cv2.absdiff(bg_model_8bit, gray)

    # 差分画像を二値化 (動いている部分を強調)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

    # ノイズ除去と領域結合
    thresh = cv2.dilate(thresh, None, iterations=2)

    # 輪郭（動体の候補）を見つける
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    motion_detected = False

    for c in contours:
        if cv2.contourArea(c) < MIN_AREA:
            continue

        # 動体を検知した際の処理
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        motion_detected = True

    if motion_detected:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(OUTPUT_DIR, f"motion_{timestamp}.jpg")

        cv2.imwrite(filename, frame)
        print(f"動体を検知し、静止画を保存しました: {filename}")

    # 'q'キーが押されたらループを終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 終了処理
cap.release()
cv2.destroyAllWindows()
