from pytube import YouTube
import pytube
from sys import argv
from moviepy import *
from yt_dlp import YoutubeDL
from moviepy.video.fx import MirrorX
import ffmpeg

import json
import os

def download_video_and_audio(link, title):
    """Télécharge la vidéo et l'audio, puis les fusionne."""
    folder_path = "Videos"
    video_path = f"{folder_path}/{title}.mp4"

    # Créer le dossier s'il n'existe pas
    os.makedirs(folder_path, exist_ok=True)

    # Options de téléchargement pour la vidéo et l'audio
    video_options = {
        "format": "bestvideo[ext=mp4]/bestaudio",
        "outtmpl": video_path,
    }

    try:
        # Télécharger la vidéo
        with YoutubeDL(video_options) as ydl:
            link = link.strip()
            ydl.download([link])
        print(f"Vidéo téléchargée : {video_path}")

        return video_path
    except Exception as e:
        print(f"Erreur : {e}")



def cutVideo(downloaded_file_path, title, start, end) :
  """Utilisation de moviepy pour découper la vidéo"""

  print("Début cutVideo")
  
  with VideoFileClip(downloaded_file_path) as clip:
    clip = clip.subclipped(start, end) #Couper la vidéo
    clip = MirrorX().apply(clip) #Mettre la vidéo en mirroir

    file_path = f'Videos\\{title}_mirror.mp4' #Définir le chemin de sortie pour la vidéo découpée

    clip.write_videofile(file_path) #Met la vidéo dans le dossier souhaité

  print("Fin cutVideo")
  return file_path

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle

# SCOPES nécessaires pour l'upload vidéo
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Fonction pour obtenir les identifiants d'authentification
def get_authenticated_service():
    credentials = None
    # Si un fichier token.pickle existe, chargez-le
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # Si aucun token, procédez à l'authentification
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
              'credentials/client_secrets.json', SCOPES)

            credentials = flow.run_local_server()
        # Sauvegardez les identifiants pour la prochaine fois
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build('youtube', 'v3', credentials=credentials)


def videoToYoutube(file_path, title):
    """Publier la vidéo sur YouTube"""
    try:
        # Authentification avec l'API YouTube
        youtube = get_authenticated_service()

        # Préparer les métadonnées de la vidéo
        request_body = {
            'snippet': {
                'title': title.upper() + " CHOREO MIRROR",
            },
            'status': {
                'privacyStatus': 'private'
            }
        }

        # Charger le fichier vidéo
        media_file = MediaFileUpload(file_path, mimetype='video/mp4', resumable=True)

        # Envoi de la requête pour télécharger la vidéo
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media_file
        )

        # Exécution de la requête
        response = request.execute()
        print("Vidéo en cours de publication...")

        print("Vidéo publiée avec succès! Link :", response["link"])

    except Exception as e:
        print("Une erreur s'est produite lors de la publication de la vidéo:", str(e))


def mirrorVideo(link, title, start, end) :
  video = download_video_and_audio(link, title)
  video_cut = cutVideo(video, title, start, end)
  os.remove(video) #Efface la vidéo entière téléchargée auparavant
  videoToYoutube(video_cut, title)
  

link = input("Lien : ")
title = input("Titre (sans espace): ")
start = input("Début de la vidéo : ")
end = input("Fin de la vidéo : ")

mirrorVideo(link, title, start, end)