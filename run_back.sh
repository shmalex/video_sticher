#backyard 
folder_id=1XUH7efaFP9cyp_nxW-7Zjn_mnhkmY5v4
base_dir=/home/shmalex/Videos/Aerogarden/3_backyard

orig_path=$base_dir/orig/
renamed_dir=$base_dir/renamed

time ./concat.py $orig_path $folder_id

snap run ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -r 10 -y -f image2 -i $renamed_dir/%7d.jpg  -tune hq -b:v 20M -bufsize 20M -maxrate 20M -c:v h264_nvenc -crf 30 $base_dir/video_fps10.mp4