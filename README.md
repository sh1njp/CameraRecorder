<img width="280" height="49" alt="image" src="https://github.com/user-attachments/assets/c942d354-8b67-4a41-8c46-cbff08d66abf" /># CameraRecorder
防犯カメラの映像保存と動体検知の参考例です。

## 基本的な考え方

- 防犯カメラのRTSPサーバ機能を使用する。
- Linuxを使って処理して必要な映像や画像を保存する。
- 古いファイルの自動削除や保存や動体検知の処理が停止していないかなどの監視処理や再稼働処理などは割愛します。
- 動画や画像ファイルは /wor/camera 配下に保存されます。

## 動体検知の画像例

動体検知の画像をアニメーションGIFにしました。（6枚分）
![img](walk_cat.gif)

## 事前準備

### 防犯カメラの選定
- RTSPサーバが使用できるものを選定します。

### Linuxの準備
- ubuntu2204とかあたりで。
- 必要なライブラリの準備
```
pip install opencv-python numpy imutils
```

### 防犯カメラの初期設定
- RTSPサーバ機能を有効化する。（必要に応じて防犯カメラのマニュアルを参照ください）
- 以下のようなURLで防犯カメラのストリームにアクセスが可能となります。

```
RTSP_URL = "rtsp://[username]:[password]@[IPアドレス]:[ポート]/[ストリームパス]"
```

## 映像保存
- [record-camnera.sh](record-camnera.sh)
- 映像保存先：/work/camera/record

### 映像保存の方法
- ffmpegを使用して、RTSPサーバのストリームを保存します。
- [Saving RTSP Camera Streams with FFmpeg](https://medium.com/@tom.humph/saving-rtsp-camera-streams-with-ffmpeg-baab7e80d767) を参考にしました。
```
ffmpeg -hide_banner -y -loglevel error -rtsp_transport tcp -use_wallclock_as_timestamps 1 -i rtsp://username:password@192.168.1.123:554/stream1 -vcodec copy -acodec copy -f segment -reset_timestamps 1 -segment_time 900 -segment_format mkv -segment_atclocktime 1 -strftime 1 %Y%m%dT%H%M%S.mkv
```
但し、上記のサイトの segment_atclocktime 1 を入れると、保存されるファイルが900秒ではなく5秒単位のファイルに保存される動作をしているため、除いてあります。おそらく5秒毎にブロック化されているから？

## 動体検知
- [detect_motion.py](detect_motion.py)
- 検知画像保存先：/work/camera/detected_motion_images

### 動体検知の方法
- Geminiに相談しました。

- 質問内容
> RTSPのストリームから動体検知して検知した動体を静止画像ファイルにする方法
> Linuxとpythonを使用してください。 

- 回答内容
> RTSPストリームからPythonとOpenCVを使用して動体検知を行い、検知した動体を静止画像ファイルとして保存する一般的な手順は以下の通りです。(略)

いい感じのプログラムが出てきます。
Geminiの文章の注意事項として、動体検知の感度を調整、背景フレームの更新を行うなどにより、誤検知を調整します。

実行のポイント（Geminiさんコメント）

    MIN_AREAの調整: MIN_AREA の値を調整することで、動体検知の感度を調整できます。値を大きくすると、小さい動きは無視されるようになり、小さくすると、わずかな動きにも反応しやすくなります。

    背景フレームの更新: 上記のコードでは背景フレームを一度だけ初期化していますが、実際の環境では明るさの変化などにより誤検知が増えることがあります。より高度な実装では、時間が経過するにつれて背景フレームを少しずつ現在のフレームに更新していく処理（例: cv2.accumulateWeighted())を加えるのが一般的です。

    cv2.CAP_FFMPEG: cv2.VideoCapture()の第2引数にcv2.CAP_FFMPEGを指定することで、RTSPストリームのデコードにFFmpegバックエンドを強制的に使用できます。これにより、ストリームの安定性が向上する場合があります。
