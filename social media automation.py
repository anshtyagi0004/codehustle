import pandas as pd
import os
from datetime import datetime
import requests
import json

# YouTube API
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# LinkedIn API
from linkedin_api import Linkedin
from linkedin_api.client import ClientAuth

# Facebook Graph API
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.abstractcrudobject import AbstractCrudObject
from facebook_business.adobjects.video import Video

# Step 1: Read Excel Sheet
def read_excel_sheet(excel_path):
    df = pd.read_excel(excel_path, parse_dates=['Date and time of upload'])
    return df

# Step 2: Upload to YouTube
def upload_to_youtube(title, description, file_path, date_time, tags=None, thumbnail=None, privacy=None, comments=None):
    credentials = Credentials.from_authorized_user_file("you-tube-api-key-384106-d1c364e63364.json", scopes=["https://www.googleapis.com/auth/youtube.upload"])
    youtube = build("youtube", "v3", credentials=credentials)

    # Step 2.2: Upload Video
    try:
        request_body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags.split(',') if tags else [],
                "categoryId": 22
            },
            "status": {
                "privacyStatus": privacy if privacy else 'public',
                "publishAt": date_time.isoformat() + 'Z',
                "selfDeclaredMadeForKids": False,
                "commentModerationSetting": 'heldForReview' if comments == 'yes' else 'moderate'
            }
        }
        if thumbnail:
            request_body["snippet"]["thumbnails"] = {"default": {"url": thumbnail}}
        media_file = MediaFileUpload(file_path)
        response_upload = youtube.videos().insert(
            part=",".join(request_body.keys()),
            body=request_body,
            media_body=media_file
        ).execute()
        video_id = response_upload.get('id')
        print(f"Video {title} uploaded successfully to YouTube with ID {video_id}.")
        return video_id
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None

# Step 3: Upload to LinkedIn
def upload_to_linkedin(title, description, file_path, date_time, tags=None, thumbnail=None, privacy=None, comments=None):
    auth = ClientAuth("1015283970851-9u2avt2nn8a617cdms6l4v63srt3822u.apps.googleusercontent.com", "yGOCSPX-s4TXyNbUu095WGJsZsTtehT4sMnd")
    linkedin = Linkedin(auth) 
    try:
        response_upload = linkedin.video_upload(file_path, title, description)
        video_id = response_upload['id']
        linkedin.video_update(
            video_id,
            comment_disabled=True if comments == 'no' else False,
            description=description,
            title=title,
            public_visibility=True if privacy == 'public' else False,
            publish_time=int(date_time.timestamp())
        )
        print(f"Video {title} uploaded successfully to LinkedIn with ID {video_id}.")
        return video_id
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

