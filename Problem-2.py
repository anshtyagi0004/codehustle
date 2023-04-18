#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:\\Users\\anush\\Downloads\\you-tube-api-key-384106-af5d3a918520.json"


# In[2]:


import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from urllib.parse import urlparse, parse_qs

# Set up the YouTube API client
creds, project_id = google.auth.default()
youtube = build('youtube', 'v3', credentials=creds)


# In[3]:



def get_video_id(url):
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com'}:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None


# In[4]:


# Function to get the tags for a video
def get_video_tags(video_id):
    response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    tags = response['items'][0]['snippet']['tags']
    return tags


# In[5]:


# Function to get the top-performing videos related to a given video
def get_top_related_videos(video_id):
    response = youtube.search().list(
        part='id',
        relatedToVideoId=video_id,
        type='video',
        maxResults=10,
        order='viewCount'
    ).execute()

    related_video_ids = [item['id']['videoId'] for item in response['items']]
    return related_video_ids


# In[6]:


# Function to compare tags of two videos
def compare_tags(video1_tags, video2_tags):
    video1_tags = set(video1_tags)
    video2_tags = set(video2_tags)

    common_tags = video1_tags & video2_tags
    only_video1_tags = video1_tags - video2_tags
    only_video2_tags = video2_tags - video1_tags

    return common_tags, only_video1_tags, only_video2_tags


# In[7]:


# Function to suggest tag changes for a given video
def suggest_tag_changes(video_id):
    video_tags = get_video_tags(video_id)
    related_video_ids = get_top_related_videos(video_id)

    suggested_tags = set(video_tags)
    for related_video_id in related_video_ids:
        related_video_tags = get_video_tags(related_video_id)
        common_tags, only_video1_tags, only_video2_tags = compare_tags(video_tags, related_video_tags)

        suggested_tags |= common_tags
        suggested_tags |= only_video2_tags

    return list(suggested_tags)


# In[8]:


# Function to update the tags for a video
def update_video_tags(video_id, new_tags):
    video = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    video['items'][0]['snippet']['tags'] = new_tags

    youtube.videos().update(
        part='snippet',
        body=video
    ).execute()


# In[9]:


# Example usage
video_url = 'https://www.youtube.com/watch?v=AgyTHzjBS-c'


# In[10]:


video_id = get_video_id(video_url)
video_id


# In[11]:


suggested_tags = suggest_tag_changes(video_id)
suggested_tags


# In[12]:


update_video_tags(video_id, suggested_tags)
print('Updated tags:', suggested_tags)


# In[ ]:





# In[ ]:





# In[ ]:




