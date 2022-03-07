time ./concat.py ../2_horiz/orig/ 60

snap run ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -r 120 -y -f image2 -i /home/shmalex/Videos/Aerogarden/2_horiz/renamed/%7d.jpg  -tune hq -b:v 20M -bufsize 20M -maxrate 20M -c:v h264_nvenc -crf 30 ../2_horiz/video_fps120.mp4

snap run ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -r 240 -y -f image2 -i /home/shmalex/Videos/Aerogarden/2_horiz/renamed/%7d.jpg  -tune hq -b:v 20M -bufsize 20M -maxrate 20M -c:v h264_nvenc -crf 30 ../2_horiz/video_fps240.mp4
