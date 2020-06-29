import os

import youtube_dl


def youtube_wav_download(url, file_name, download_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'continue_dl': True,
        'outtmpl': os.path.join(download_path, file_name + '.mp3'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192'
        }]
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.cache.remove()
            info_dict = ydl.extract_info(url, download=False)
            ydl.prepare_filename(info_dict)
            ydl.download([url])

        return True

    except youtube_dl.utils.YoutubeDLError:
        youtube_wav_download(url, file_name, download_path)



def to_melspectrogram():
    pass


if __name__ == "__main__":
    youtube_wav_download('https://www.youtube.com/watch?v=OzMpkAwgH9k', 'test1', './download')