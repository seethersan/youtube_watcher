import os
import faust
from django.conf import settings
from asgiref.sync import sync_to_async
import requests
import django

os.environ.setdefault("FAUST_LOOP", "eventlet")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "youtube_watcher.settings")
django.setup()

from django.conf import settings


from playlists.models import Playlist, Video
from users.models import Profile
from receivers.models import Receiver, Message
from receivers.receivers import TelegramReceiver

app = faust.App("youtube_watcher", broker=f"kafka://{settings.KAFKA_BOOTSTRAP_SERVERS}")


playlist_topic = app.topic("youtube-watcher-playlists")
playlist_update_topic = app.topic("youtube-watcher-playlists-updates")
video_changes_topic = app.topic("youtube-watcher-videos-changes")


def fetch_playlist_items_page(google_api_key, youtube_playlist_id, page_token=None):
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "contentDetails",
        "key": google_api_key,
        "playlistId": youtube_playlist_id,
        "pageToken": page_token,
    }
    response = requests.get(url, params=params)
    payload = response.json()
    return payload


def fetch_videos_page(google_api_key, video_id, page_token=None):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "key": google_api_key,
        "id": video_id,
        "pageToken": page_token,
    }
    response = requests.get(url, params=params)
    payload = response.json()
    return payload


@sync_to_async
def get_playlist(playlist_id, owner_id):
    return Playlist.objects.get(playlist_id=playlist_id, owner__id=owner_id)


@sync_to_async
def process_receivers(profile_id, message):
    receivers = Receiver.objects.filter(profile__id=profile_id)
    messages_objs = []
    for receiver in receivers:
        if receiver.type == "telegram":
            telegram = TelegramReceiver(receiver)
            sent, error = telegram.send(message)
            messages_objs.append(
                Message(
                    receiver=receiver,
                    body=message,
                    sent=sent,
                    error=error or "",
                )
            )
    if messages_objs:
        Message.objects.bulk_create(messages_objs)


@sync_to_async
def get_video(playlist_id, video_id):
    try:
        video = Video.objects.get(playlist__playlist_id=playlist_id, video_id=video_id)
    except Video.DoesNotExist:
        return None
    return video


@sync_to_async
def get_google_api_key(owner_id):
    profile = Profile.objects.get(id=owner_id)
    return profile.google_api_key


@sync_to_async
def update_video(video, video_data):
    video.title = video_data.get("title")
    video.description = video_data.get("description")
    video.views = video_data.get("views")
    video.comments = video_data.get("comments")
    video.likes = video_data.get("likes")
    video.thumbnail = video_data.get("thumbnail")
    video.save()


@sync_to_async
def create_videos(videos):
    return Video.objects.bulk_create(videos)


@sync_to_async
def update_playlist(playlist, total_views, total_comments, total_likes):
    playlist.total_views = total_views
    playlist.total_comments = total_comments
    playlist.total_likes = total_likes
    playlist.save()


@app.agent(playlist_topic)
async def process_playlist(stream):
    async for record in stream:
        instance = await get_playlist(record["playlist_id"], record["owner"])
        videos_ids = []
        videos_objs = []
        page_token = None

        total_views = 0
        total_likes = 0
        total_comments = 0

        google_api_key = await get_google_api_key(record["owner"])

        while True:
            payload = fetch_playlist_items_page(
                google_api_key, record["playlist_id"], page_token
            )
            page_token = payload.get("nextPageToken")
            if page_token is None:
                break
            for video in payload.get("items"):
                video_id = video.get("contentDetails").get("videoId")
                videos_ids.append(video_id)

        print(videos_ids)
        videos_ids = list(set(videos_ids))
        print(videos_ids)

        page_token = None

        while True:
            payload = fetch_videos_page(
                google_api_key, ",".join(videos_ids), page_token
            )
            page_token = payload.get("nextPageToken")
            for video in payload.get("items"):
                video_id = video.get("id")
                thumbnail = video.get("snippet").get("thumbnails").get("high")
                video_data = {
                    "title": video.get("snippet").get("title"),
                    "description": video.get("snippet").get("description"),
                    "views": video.get("statistics").get("viewCount", 0),
                    "likes": video.get("statistics").get("likeCount", 0),
                    "comments": video.get("statistics").get("commentCount", 0),
                    "thumbnail": thumbnail.get("url") if thumbnail else "",
                }
                total_views += int(video_data.get("views"))
                total_likes += int(video_data.get("likes"))
                total_comments += int(video_data.get("comments"))
                video_obj = await get_video(record["playlist_id"], video_id)
                if video_obj:
                    await update_video(video_obj, video_data)
                else:
                    videos_objs.append(
                        Video(
                            title=video_data.get("title"),
                            video_id=video_id,
                            description=video_data.get("description"),
                            views=video_data.get("views"),
                            likes=video_data.get("likes"),
                            comments=video_data.get("comments"),
                            thumbnail=video_data.get("thumbnail"),
                            playlist=instance,
                        )
                    )
            if page_token is None:
                break
        await create_videos(videos_objs)
        await update_playlist(instance, total_views, total_comments, total_likes)


@app.agent(playlist_update_topic)
async def process_playlist_updates(stream):
    async for record in stream:
        instance = await get_playlist(record["playlist_id"], record["owner"])
        videos_ids = []
        videos_objs = []

        total_views = 0
        total_likes = 0
        total_comments = 0
        page_token = None

        google_api_key = await get_google_api_key(record["owner"])

        while True:
            payload = fetch_playlist_items_page(
                google_api_key, record["playlist_id"], page_token
            )
            page_token = payload.get("nextPageToken")
            if page_token is None:
                break
            for video in payload.get("items"):
                video_id = video.get("contentDetails").get("videoId")
                videos_ids.append(video_id)

        print(videos_ids)
        videos_ids = list(set(videos_ids))
        print(videos_ids)
        page_token = None

        while True:
            payload = fetch_videos_page(
                google_api_key, ",".join(videos_ids), page_token
            )
            page_token = payload.get("nextPageToken")
            for video in payload.get("items"):
                total_views += int(video.get("statistics").get("viewCount", 0))
                total_likes += int(video.get("statistics").get("likeCount", 0))
                total_comments += int(video.get("statistics").get("commentCount", 0))
                thumbnail = video.get("snippet").get("thumbnails").get("high")

                video = await get_video(record["playlist_id"], video.get("id"))
                if not video:
                    videos_objs.append(
                        Video(
                            title=video.get("snippet").get("title"),
                            video_id=video.get("id"),
                            description=video.get("snippet").get("description"),
                            views=video.get("statistics").get("viewCount", 0),
                            likes=video.get("statistics").get("likeCount", 0),
                            comments=video.get("statistics").get("commentCount", 0),
                            thumbnail=thumbnail.get("url") if thumbnail else None,
                            playlist=instance,
                        )
                    )
                else:
                    video_data = {
                        "title": video.get("snippet").get("title"),
                        "description": video.get("snippet").get("description"),
                        "views": video.get("statistics").get("viewCount", 0),
                        "likes": video.get("statistics").get("likeCount", 0),
                        "comments": video.get("statistics").get("commentCount", 0),
                        "thumbnail": thumbnail.get("url") if thumbnail else None,
                    }
                    await update_video(video, video_data)
            if page_token is None:
                break
        if videos_objs:
            await create_videos(videos_objs)
        await update_playlist(instance, total_views, total_comments, total_likes)


@app.agent(video_changes_topic)
async def process_video_changes(stream):
    async for record in stream:
        await process_receivers(record["owner"], record["message"])
