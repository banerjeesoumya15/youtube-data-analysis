'''
All the user functions are defined here
'''

import re
import pandas as pd

# to get all the required stats of channels
def get_channel_stats(youtube, channel_ids):

    all_data = []
    
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    )
    response = request.execute()
    
    
    # loop through items
    for item in response['items']:
        data = {
            'channelName':item['snippet']['title'],
            'subscribers':item['statistics']['subscriberCount'],
            'views':item['statistics']['viewCount'],
            'totalVids':item['statistics']['videoCount'],
            'playlistId':item['contentDetails']['relatedPlaylists']['uploads']
        }
        all_data.append(data)
        
    df = pd.DataFrame(all_data)
    return df

# to get all video ids from a playlist
def get_vid_ids(youtube, playlist_id):
    
    vid_ids = []
    
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        playlistId=playlist_id
    )
    response = request.execute()
    
    for item in response['items']:
        vid_ids.append(item['contentDetails']['videoId'])
    
    next_page_token = response.get('nextPageToken')
    while next_page_token is not None:
        request = youtube.playlistItems().list(
            part="contentDetails",
            maxResults=50,
            playlistId=playlist_id,
            pageToken = next_page_token)
        response = request.execute()
        
        for item in response['items']:
            vid_ids.append(item['contentDetails']['videoId'])
            
        next_page_token = response.get('nextPageToken')
        
    return vid_ids

# to get video details from list of video ids
def get_vid_Details(youtube, vid_ids):
    
    all_vid_info = []
    
    for i in range(0, len(vid_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(vid_ids[i:i+50])
        )
        response = request.execute()

        for video in response['items']:
            stats_to_keep = {'snippet':['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
                             'statistics':['viewCount', 'likeCount', 'favouriteCount', 'commentCount'],
                             'contentDetails':['duration', 'definition', 'caption']
                            }
            vid_info = {}
            vid_info['vid_id'] = video['id']
            
            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    try:
                        vid_info[v] = video[k][v]
                    except:
                        vid_info[v] = None
                        
            all_vid_info.append(vid_info)
            
    return pd.DataFrame(all_vid_info)

# to get all the comments from a list of video ids
def get_comments_in_videos(youtube, vid_ids):
    
    all_comments = []
    
    for i in range(0, len(vid_ids)):
        request = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=vid_ids[i]
            )
        response = request.execute()
            
        comment_txt = [comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in response['items']]
        all_comments.append({'vid_id':vid_ids[i], 'comment':comment_txt})
            
    return pd.DataFrame(all_comments)


# To convert duration into seconds
#https://stackoverflow.com/questions/16742381/how-to-convert-youtube-api-duration-to-seconds
def YTDurationToSeconds(duration):
    match = re.match('PT(\d+H)?(\d+M)?(\d+S)?', duration).groups()
    hours = _js_parseInt(match[0]) if match[0] else 0
    minutes = _js_parseInt(match[1]) if match[1] else 0
    seconds = _js_parseInt(match[2]) if match[2] else 0
    return hours * 3600 + minutes * 60 + seconds

# js-like parseInt
# https://gist.github.com/douglasmiranda/2174255
def _js_parseInt(string):
    return int(''.join([x for x in string if x.isdigit()]))

# example output 
YTDurationToSeconds(u'PT12M3S')