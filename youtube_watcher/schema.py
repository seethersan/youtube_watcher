import json
import typing
import strawberry
from gqlauth.core.middlewares import JwtSchema
from gqlauth.core.utils import get_user
from gqlauth.user import arg_mutations
from gqlauth.user.arg_mutations import Captcha
from gqlauth.user.queries import UserQueries
from strawberry.types import Info
from strawberry_django_plus import gql
from strawberry_django_plus.directives import SchemaDirectiveExtension
from strawberry_django_plus.permissions import IsAuthenticated


from playlists.models import Playlist, Video
from playlists.producers import (
    producer,
    delivery_playlist_report,
)
from users.models import Profile
from receivers.models import Receiver, Message


@gql.django.type(Profile)
class ProfileType:
    id: strawberry.ID
    username: str
    email: str
    google_api_key: str


@gql.django.type(Receiver)
class ReceiverType(gql.Node):
    type: str
    profile: ProfileType
    token: str
    channel: str
    isActive: bool


@gql.django.input(Receiver)
class ReceiverFilter:
    type: typing.Optional[str]
    profile: typing.Optional[int]
    channel: typing.Optional[int]
    isActive: typing.Optional[bool]


@gql.django.input(Receiver)
class ReceiverInput:
    type: gql.auto
    token: str
    channel: int
    isActive: bool


@gql.django.type(Message)
class MessageType(gql.Node):
    receiver: ReceiverType
    body: str
    sent: bool
    error: str


@gql.django.input(Message)
class MessageFilter:
    receiver: typing.Optional[int]
    sent: typing.Optional[bool]


@gql.django.type(Video)
class VideoType(gql.Node):
    title: str
    video_id: str
    description: str
    views: int
    likes: int
    dislikes: int
    comments: int
    isActive: bool


@gql.django.input(Video)
class VideoInput:
    title: str
    video_id: str
    description: str
    views: int
    likes: int
    dislikes: int
    comments: int
    isActive: bool


@gql.django.type(Playlist)
class PlaylistType(gql.Node):
    name: gql.auto
    playlist_id: gql.auto
    description: gql.auto
    isActive: gql.auto
    playlist_videos: typing.List[VideoType]
    owner: ProfileType


@gql.django.input(Playlist)
class PlaylistInput:
    name: gql.auto
    playlist_id: gql.auto
    description: gql.auto
    isActive: gql.auto


@gql.django.input(Playlist)
class PlaylistFilter:
    name: typing.Optional[str]
    playlist_id: typing.Optional[str]
    isActive: typing.Optional[bool]


@gql.type
class Mutation:
    @gql.mutation(directives=[IsAuthenticated])
    def createReceiver(self, info: Info, input: ReceiverInput) -> ReceiverType:
        data = vars(input)
        data["profile"] = get_user(info)
        return Receiver.objects.create(**data)

    @gql.mutation(directives=[IsAuthenticated])
    def createPlaylist(self, info: Info, input: PlaylistInput) -> PlaylistType:
        data = vars(input)
        data["owner"] = get_user(info)
        playlist = Playlist.objects.create(**data)
        content = playlist.to_dict()
        producer.produce(
            "youtube-watcher-playlists",
            key=str(content.pop("id")),
            value=json.dumps(content),
            on_delivery=delivery_playlist_report,
        )
        producer.flush()
        return playlist

    @gql.django.field(directives=[IsAuthenticated])
    def activatePlaylist(self, playlist_id: int, info: Info) -> "PlaylistType":
        playlist = Playlist.objects.get(id=playlist_id)
        if playlist.profile.user == get_user(info):
            playlist.is_active = True
            playlist.save(update_fields=["is_active"])
            return playlist

    @gql.django.field(directives=[IsAuthenticated])
    def deactivatePlaylist(self, playlist_id: int, info: Info) -> "PlaylistType":
        playlist = Playlist.objects.get(id=playlist_id)
        if playlist.profile.user == get_user(info):
            playlist.is_active = False
            playlist.save(update_fields=["is_active"])
            return playlist

    @gql.django.field(directives=[IsAuthenticated])
    def activateVideo(self, video_id: int, info: Info) -> "VideoType":
        video = Video.objects.get(id=video_id)
        if video.profile.user == get_user(info):
            video.is_active = True
            video.save(update_fields=["is_active"])
            return video

    @gql.django.field(directives=[IsAuthenticated])
    def deactivateVideo(self, video_id: int, info: Info) -> "VideoType":
        video = Video.objects.get(id=video_id)
        if video.profile.user == get_user(info):
            video.is_active = False
            video.save(update_fields=["is_active"])
            return video

    @gql.django.field(directives=[IsAuthenticated])
    def setGoogleApikey(self, api_key: str, info: Info) -> "ProfileType":
        profile = get_user(info)
        profile.google_api_key = api_key
        profile.save()
        return profile

    verify_token = arg_mutations.VerifyToken.field
    update_account = arg_mutations.UpdateAccount.field
    archive_account = arg_mutations.ArchiveAccount.field
    delete_account = arg_mutations.DeleteAccount.field
    password_change = arg_mutations.PasswordChange.field

    captcha = Captcha.field
    token_auth = arg_mutations.ObtainJSONWebToken.field
    register = arg_mutations.Register.field
    verify_account = arg_mutations.VerifyAccount.field
    resend_activation_email = arg_mutations.ResendActivationEmail.field
    send_password_reset_email = arg_mutations.SendPasswordResetEmail.field
    password_reset = arg_mutations.PasswordReset.field
    password_set = arg_mutations.PasswordSet.field
    refresh_token = arg_mutations.RefreshToken.field
    revoke_token = arg_mutations.RevokeToken.field


@strawberry.type
class Query(UserQueries):
    @gql.django.field(
        directives=[
            IsAuthenticated(),
        ]
    )
    def user(self, info: Info) -> ProfileType:
        return get_user(info)

    @gql.django.field(
        directives=[
            IsAuthenticated(),
        ]
    )
    def getPlaylists(
        self, info: Info, input: PlaylistFilter
    ) -> typing.List[PlaylistType]:
        data = vars(input)
        if profile := data.get("profile"):
            if profile != info.context.request.user.id:
                raise PermissionError("Not allowed")
        playlists = Playlist.objects.filter(owner=get_user(info))
        if name := data.get("name"):
            playlists = playlists.filter(name=name)
        if playlist_id := data.get("playlist_id"):
            playlists = playlists.filter(playlist_id=playlist_id)
        if isActive := data.get("isActive"):
            playlists = playlists.filter(isActive__in=[isActive])
        return Playlist.objects.filter(owner=get_user(info))

    @gql.django.field(
        directives=[
            IsAuthenticated(),
        ]
    )
    def getReceivers(
        self, info: Info, input: ReceiverFilter
    ) -> typing.List[ReceiverType]:
        data = vars(input)
        if profile := data.get("profile"):
            if profile != info.context.request.user.id:
                raise PermissionError("Not allowed")
        receivers = Receiver.objects.filter(profile=get_user(info))
        if receiver_type := data.get("type"):
            receivers = receivers.filter(type=receiver_type)
        return receivers

    @gql.django.field(
        directives=[
            IsAuthenticated(),
        ]
    )
    def getMessages(self, info: Info, input: MessageFilter) -> typing.List[MessageType]:
        data = vars(input)
        if profile := data.get("profile"):
            if profile != info.context.request.user.id:
                raise PermissionError("Not allowed")
        messages = Message.objects.filter(receiver__profile=get_user(info))
        if receiver := data.get("receiver"):
            messages = messages.filter(receiver__id=receiver)
        if sent := data.get("sent"):
            messages = messages.filter(sent__in=[sent])
        return messages


schema = JwtSchema(
    query=Query, mutation=Mutation, extensions=[SchemaDirectiveExtension]
)
