/usr/bin/ffmpeg -hide_banner -y -loglevel error -rtsp_transport tcp -use_wallclock_as_timestamps 1 \
                -i rtsp://username:password@192.168.xxx.xxx/stream1 \
                -vcodec copy -acodec copy -f segment -reset_timestamps 1 -segment_time 900 -segment_format mkv \
                -strftime 1 /work/camera/record/garage_%F_%H-%M-%S.mkv
