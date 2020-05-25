import os
import youtube_dl
import librosa


def youtube_mp3_download(url, file_name, download_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_path}/{file_name}.wav',
        'noplaylist': True,
        'continue_dl': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


if __name__ == "__main__":
    youtube_mp3_download('https://www.youtube.com/watch?v=m7pr7LdDX1E', 'test1', '.')
