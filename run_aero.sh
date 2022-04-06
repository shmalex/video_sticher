# Aerogarden
folder_id=1vRpM2GnlTqRbpsqnOGJBp18QLKdyk_Gh
base_dir=/home/shmalex/Videos/Aerogarden/2_horiz

orig_path=$base_dir/orig/
renamed_dir=$base_dir/renamed

time ./concat.py $orig_path $folder_id

snap run ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -r 120 -y -f image2 -i $renamed_dir/%7d.jpg  -tune hq -b:v 20M -bufsize 20M -maxrate 20M -c:v h264_nvenc -crf 30 $base_dir/video_fps120.mp4

snap run ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -r 240 -y -f image2 -i $renamed_dir/%7d.jpg  -tune hq -b:v 20M -bufsize 20M -maxrate 20M -c:v h264_nvenc -crf 30 $base_dir/video_fps240.mp4
