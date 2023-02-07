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


from channels.models import Channel, Video
from users.models import Profile
from receivers.models import Receiver, Message
from receivers.receivers import TelegramReceiver

app = faust.App("youtube_watcher", broker=f"kafka://{settings.KAFKA_BOOTSTRAP_SERVERS}")


channel_topic = app.topic("youtube-watcher-channels")
channel_update_topic = app.topic("youtube-watcher-channels-updates")
video_changes_topic = app.topic("youtube-watcher-videos-changes")


def fetch_playlist_items_page(google_api_key, youtube_channel_id, page_token=None):
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "contentDetails",
        "key": google_api_key,
        "playlistId": youtube_channel_id,
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
def get_channel(channel_id, owner_id):
    return Channel.objects.get(channel_id=channel_id, owner__id=owner_id)


@sync_to_async
def get_receivers(profile_id):
    return Receiver.objects.filter(profile__id=profile_id)


@sync_to_async
def get_video(channel_id, video_id):
    try:
        video = Video.objects.get(channel_id=channel_id, video_id=video_id)
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
def create_messages(messages):
    return Message.objects.bulk_create(messages)


@sync_to_async
def update_channel(channel, total_views, total_comments, total_likes):
    channel.total_views = total_views
    channel.total_comments = total_comments
    channel.total_likes = total_likes
    channel.save()


@app.agent(channel_topic)
async def process_channel(stream):
    async for record in stream:
        instance = await get_channel(record["channel_id"], record["owner"])
        videos_ids = []
        videos = []
        google_api_key = await get_google_api_key(record["owner"])
        payload = fetch_playlist_items_page(google_api_key, record["channel_id"])
        videos_ids.extend(
            [item.get("contentDetails").get("videoId") for item in payload.get("items")]
        )
        while page_token := payload.get("nextPageToken"):
            payload = fetch_playlist_items_page(
                google_api_key, record["channel_id"], page_token
            )
            videos_ids.extend(
                [
                    item.get("contentDetails").get("videoId")
                    for item in payload.get("items")
                ]
            )
        for video_id in videos_ids:
            payload = fetch_videos_page(google_api_key, video_id)
            videos.extend(payload.get("items"))
            if page_token := payload.get("nextPageToken"):
                payload = fetch_videos_page(google_api_key, video_id, page_token)
                videos.extend(payload.get("items"))
            videos_objs = []
            total_views = 0
            total_likes = 0
            total_comments = 0
            for item in videos:
                total_views += int(item.get("statistics").get("viewCount", 0))
                total_likes += int(item.get("statistics").get("likeCount", 0))
                total_comments += int(item.get("statistics").get("commentCount", 0))
                videos_objs.append(
                    Video(
                        title=item.get("snippet").get("title"),
                        video_id=item.get("id"),
                        description=item.get("snippet").get("description"),
                        views=item.get("statistics").get("viewCount", 0),
                        likes=item.get("statistics").get("likeCount", 0),
                        comments=item.get("statistics").get("commentCount", 0),
                        thumbnail=item.get("snippet")
                        .get("thumbnails")
                        .get("maxres")
                        .get("url"),
                        channel=instance,
                    )
                )
            await create_videos(videos_objs)
            await update_channel(instance, total_views, total_comments, total_likes)


@app.agent(channel_update_topic)
async def process_channel_updates(stream):
    async for record in stream:
        instance = await get_channel(record["channel_id"], record["owner"])
        videos_ids = []
        videos = []
        google_api_key = await get_google_api_key(record["owner"])
        payload = fetch_playlist_items_page(google_api_key, record["channel_id"])
        videos_ids.extend(
            [item.get("contentDetails").get("videoId") for item in payload.get("items")]
        )
        while page_token := payload.get("nextPageToken"):
            payload = fetch_playlist_items_page(
                google_api_key, record["channel_id"], page_token
            )
            videos_ids.extend(
                [
                    item.get("contentDetails").get("videoId")
                    for item in payload.get("items")
                ]
            )
        for video_id in videos_ids:
            payload = fetch_videos_page(google_api_key, video_id)
            videos.extend(payload.get("items"))
            if page_token := payload.get("nextPageToken"):
                payload = fetch_videos_page(google_api_key, video_id, page_token)
                videos.extend(payload.get("items"))
            videos_objs = []
            total_views = 0
            total_likes = 0
            total_comments = 0
            for item in videos:
                total_views += int(item.get("statistics").get("viewCount", 0))
                total_likes += int(item.get("statistics").get("likeCount", 0))
                total_comments += int(item.get("statistics").get("commentCount", 0))
                video = await get_video(record["channel_id"], item.get("id"))
                if not video:
                    videos_objs.append(
                        Video(
                            title=item.get("snippet").get("title"),
                            video_id=item.get("id"),
                            description=item.get("snippet").get("description"),
                            views=item.get("statistics").get("viewCount", 0),
                            likes=item.get("statistics").get("likeCount", 0),
                            comments=item.get("statistics").get("commentCount", 0),
                            thumbnail=item.get("snippet")
                            .get("thumbnails")
                            .get("maxres")
                            .get("url"),
                            channel=instance,
                        )
                    )
                else:
                    video_data = {
                        "title": item.get("snippet").get("title"),
                        "description": item.get("snippet").get("description"),
                        "views": item.get("statistics").get("viewCount", 0),
                        "likes": item.get("statistics").get("likeCount", 0),
                        "comments": item.get("statistics").get("commentCount", 0),
                        "thumbnail": item.get("snippet")
                        .get("thumbnails")
                        .get("maxres")
                        .get("url"),
                    }
                    await update_video(video, video_data)
            if videos_objs:
                await create_videos(videos_objs)
            await update_channel(instance, total_views, total_comments, total_likes)


@app.agent(video_changes_topic)
async def process_video_changes(stream):
    async for record in stream:
        receiver = await get_receivers(record["owner_id"])
        messages_objs = []
        for receiver in receiver:
            if receiver.type == "telegram":
                telegram = TelegramReceiver(receiver)
                sent, error = telegram.send(record["message"])
                messages_objs.append(
                    Message(
                        receiver=receiver,
                        body=record["message"],
                        sent=sent,
                        error=error or "",
                    )
                )
        if messages_objs:
            await create_messages(messages_objs)
