import feedparser
import datetime as dt
from typing import List, Dict, Optional, Any
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import os
import pydub
import openai
import nltk
import configparser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytube import YouTube
# Read config file
config = configparser.ConfigParser()
config.read('config.ini')


from googleapiclient.discovery import build

def get_transcript(program,dir_save_program= ''):
    """
    Retrieve the transcript from the given program.

    Args:
        program: A string representing the program to retrieve the transcript from.
        dir_save_program: A string representing the directory to save the transcript.

    Returns:
        A dictionary containing information about the program, including its title, format,
        and transcript.
    """
    
    # get metadata from program normalize
    info = program
    file_save = os.path.join(dir_save_program,info['title']+'.'+info['format'])
    file_save_txt = os.path.join(dir_save_program,info['title']+'.txt')
    info['exist'] = False
    text = ''
    # check if file_save_txt
    if info['format'] == 'mp3' and not os.path.exists(file_save_txt):
        download_mp3(info['link'], file_save)
        files_div = divide_audio(info['title'], file_save, dir_save_program,format=info['format'])
        #Transcribe all segments
        transcripts = []
        for file_div in files_div:
            audio_file= open(file_div, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            transcripts.append(transcript)
        text = ' \n'.join([t['text'] for t  in transcripts])
        
    elif info['format'] == 'youtube':
        # download youtube transcript
        video_id = info['link'].split('=')[-1]
        if 'http' in video_id:
            video_id = info['link'].split('/')[-1]

        transcripts = YouTubeTranscriptApi.get_transcript(video_id, languages=['es','en','fr'])
    
        text = ""
        for item in transcripts:
            text += item['text'] + " "
    else:
        print('Format not supported')
            
    info['transcript'] = text
    info['file_save_txt'] = file_save_txt
    return info


def divide_text(text, max_length=4096):
    while len(text) > 0:
        # Si el texto es más largo que el máximo permitido,
        # debemos buscar el último espacio para evitar dividir una palabra.
        if len(text) > max_length:
            divider_position = text.rfind(' ', 0, max_length)
        else:
            divider_position = len(text)

        # Extraer la parte del texto y eliminarla del texto original.
        part = text[:divider_position]
        text = text[divider_position:]  # Esto comenzará con un espacio.

        yield part


def get_video_details(link):
    """
    Retrieves the details of a specific YouTube video.

    Args:
        video_id (str): The ID of the YouTube video to retrieve details from.

    Returns:
        dict: A dictionary containing the video details.
    """
    video_id = link.split('v=')[-1]
    DEVELOPER_KEY = config['youtube']['api_key']
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    response = request.execute()

    return response['items'][0] if 'items' in response and len(response['items']) > 0 else None


def get_channel_videos(feed_url, max_results=50, last_days = 7):
    channel_id = feed_url.split('channel_id=')[-1]
    DEVELOPER_KEY = config['youtube']['api_key']
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    
    # Recupera la lista de uploads del canal.
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    videos = []
    next_page_token = None
    
    while 1:
        res = youtube.playlistItems().list(playlistId=playlist_id, 
                                           part='snippet', 
                                           maxResults=max_results,
                                           pageToken=next_page_token).execute()
        videos += res['items']
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break

        last = dt.datetime.strptime(videos[-1]['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        delta = dt.datetime.now() - last
        if delta.days >= 7:
            break
    
    return videos

def get_recent_podcasts(feed_url: str, program_name: Optional[str] = None, is_link: bool = False,
                         last_days: int = 7) -> List[Dict[str, Any]]:
    """
    Get a list of recent podcast entries from the RSS feed located at `feed_url`.

    Args:
        feed_url (str): The URL of the RSS feed to parse.
        program_name (str, optional): If provided, only entries whose title contains
            this string (case-insensitive) will be included in the result.

    Returns:
        list[dict]: A list of dictionaries, each representing a recent podcast entry
            with the following keys:
            - title (str): The title of the podcast episode.
            - link (str): The URL of the podcast episode.
            - published_parsed (time.struct_time): The publication date of the podcast
              episode as a struct_time object.

    """
    recent_podcasts = []

    if 'youtube' in feed_url and not is_link: # youtube channel
        videos = get_channel_videos(feed_url, last_days=last_days)
        for video in videos:
            # normalize entry
            snippet = video['snippet']
            entry = {}
            entry['author'] = snippet['channelTitle']
            entry['summary'] = snippet['description']
            entry['published'] = dt.datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            entry['title'] = snippet['title'].replace('/', '-').replace("'", "")
            entry['image'] = None
            entry['link'] = 'https://www.youtube.com/watch?v=' + snippet['resourceId']['videoId']
            entry['format'] = 'youtube'
            delta = dt.datetime.now() - entry['published']
            if delta.days <= last_days:
                if program_name:
                    if program_name.lower() in entry['title'].lower():
                        # add and normalice entry
                        recent_podcasts.append(entry)
                else:
                    # add and normalice entry
                    recent_podcasts.append(entry)
        # sort by date
        recent_podcasts.sort(key=lambda x: x['published'], reverse=True)
        return recent_podcasts
    
    elif 'youtube' in feed_url and is_link: # link youtube video
        video = get_video_details(feed_url)
        snippet = video['snippet'] #type: ignore
        entry = {}
        entry['title'] = snippet['title'].replace('/', '-').replace("'", "")
        entry['author'] = snippet['channelTitle']
        entry['summary'] = snippet['description']
        entry['published'] = dt.datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        entry['link'] = 'https://www.youtube.com/watch?v=' + snippet['resourceId']['videoId']
        entry['image'] = None
        entry['link'] = feed_url
        entry['format'] = 'youtube'
        recent_podcasts = [entry]
        return recent_podcasts

    else: # general rss feed
        feed = feedparser.parse(feed_url, agent='Mozilla/5.0')

        for entry in feed.entries:
            published_date = dt.datetime(*entry.published_parsed[:6])
            delta = dt.datetime.now() - published_date
            if delta.days >= last_days:
                if program_name:
                    if program_name.lower() in entry['title'].lower():
                        # add and normalice entry
                        recent_podcasts.append(normalize_program(entry))
                else:
                    # add and normalice entry
                    recent_podcasts.append(normalize_program(entry))
        # sort by date
        recent_podcasts.sort(key=lambda x: x['published'], reverse=True)
        return recent_podcasts

def download_mp3(url: str, filename: str) -> None:
    """
    Downloads an mp3 file from the given URL and saves it to the specified filename.

    Args:
        url (str): The URL of the mp3 file to download.
        filename (str): The filename to save the mp3 file to.

    Returns:
        None

    Raises:
        Any exceptions raised by the requests module if the download fails.
    """
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)

def normalize_program(program):
    """
    Extract metadata from a given program object for normalization.

    Args:
        program (object): The program object to extract metadata from.

    Returns:
        dict: A dictionary containing the extracted metadata, including the program's title,
        link, format, published date, summary, description, author, and image (if available).
    """
    metadata = {}
    # get metadata from program
    metadata['title'] = program.title.replace('/', '-')
    if len(program.enclosures) == 0:
       metadata['link'] = program.link
       metadata['format'] = 'youtube'
    else:
        metadata['link'] = program.enclosures[0].href
        metadata['format'] = metadata['link'].split('.')[-1]
    metadata['published'] = program.published
    metadata['summary'] = program.summary
    metadata['description'] = program.description
    metadata['author'] = program.author
    metadata['image'] = None
    try:
        if 'image' in program:
            metadata['image'] = program.image.href
    except:
        pass

    return metadata


def chunk_text(t_ext, limit=2500):
    """
    Tokenizes the input text and splits it into chunks of up to `limit` words.

    Args:
        t_ext (str): The input text to be chunked.
        limit (int): The maximum number of words allowed in each chunk. Defaults to 2500.

    Returns:
        list: A list of strings, where each string is a chunk of up to `limit` words.
    """
    # Tokenize the text into words
    tokens = nltk.word_tokenize(t_ext)

    # Initialize variables
    chunks = []
    current_chunk = []
    current_chunk_size = 0

    # Iterate over the tokens
    for token in tokens:
        # Check if adding the token to the current chunk would exceed the limit
        if current_chunk_size + 1 > limit:
            # Add the current chunk to the list of chunks if it's not empty
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            # Start a new chunk with the current token
            current_chunk = [token]
            current_chunk_size = 1
        else:
            # Add the token to the current chunk
            current_chunk.append(token)
            current_chunk_size += 1

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def divide_audio(name_audio, file_save, dir_save_program, format='mp3'):
    """
    Divides an audio file into segments of 10 minutes each and saves them as separate files.

    Args:
    - name_audio (str): name of the audio file to be divided.
    - file_save (str): path to the audio file to be divided.
    - dir_save_program (str): path to the directory where the divided audio files will be saved.
    - format (str): format of the audio file. Default is 'mp3'.

    Returns:
    - files_div (list): a list of paths to the divided audio files.
    """

     # ffprobe for divide audio
    pydub.AudioSegment.ffprobe =config['whisper']['address'] # type: ignore
    # User whisper openai api to convert mp3 to text
    load_program = pydub.AudioSegment.from_mp3(file_save)

    # segments
    ten_minutes = 10 * 60 * 1000
    # Inicializar variables
    start = 0
    end = ten_minutes
    counter = 1

    # Iterar a través del archivo de audio y cortarlo en segmentos de 10 minutos
    files_div = []
    while start < len(load_program):
        # Cortar segmento de 10 minutos
        segment = load_program[start:end]

        # Exportar segmento a archivo separado
        name_div = f"{counter}_{name_audio}.{format}"
        file_save_div = os.path.join(dir_save_program,name_div)
        files_div.append(file_save_div)

        segment.export(file_save_div, format=format)

        # Actualizar variables
        start += ten_minutes
        end += ten_minutes
        counter += 1
    return files_div



