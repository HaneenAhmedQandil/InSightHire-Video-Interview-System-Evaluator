def extract_audio_from_video(video_path, audio_path):
    import ffmpeg
    ffmpeg.input(video_path).output(audio_path).run()

def convert_video_format(video_path, output_format):
    import moviepy.editor as mp
    video = mp.VideoFileClip(video_path)
    output_path = video_path.rsplit('.', 1)[0] + '.' + output_format
    video.write_videofile(output_path, codec='libx264')
    return output_path

def get_video_duration(video_path):
    import moviepy.editor as mp
    video = mp.VideoFileClip(video_path)
    return video.duration

def resize_video(video_path, output_path, width, height):
    import moviepy.editor as mp
    video = mp.VideoFileClip(video_path)
    resized_video = video.resize(newsize=(width, height))
    resized_video.write_videofile(output_path, codec='libx264')