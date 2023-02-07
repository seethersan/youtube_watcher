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


from channels.models import Channel, Video
from channels.producers import (
    producer,
    delivery_channel_report,
)
from users.models import Profile


@gql.django.type(Profile)
class ProfileType:
    id: strawberry.ID
    username: str
    email: str
    google_api_key: str


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


@gql.django.partial(Video)
class VideoPartial(gql.NodeInput):
    title: str
    video_id: str
    description: str
    views: int
    likes: int
    dislikes: int
    comments: int
    isActive: bool


@gql.django.type(Channel)
class ChannelType(gql.Node):
    name: gql.auto
    channel_id: gql.auto
    description: gql.auto
    isActive: gql.auto
    channel_videos: typing.List[VideoType]
    owner: ProfileType


@gql.django.input(Channel)
class ChannelInput:
    name: gql.auto
    channel_id: gql.auto
    description: gql.auto
    isActive: gql.auto


@gql.django.input(Channel)
class ChannelPartial(gql.NodeInput):
    name: gql.auto
    channel_id: gql.auto
    description: gql.auto
    isActive: gql.auto


@gql.type
class Mutation:
    @gql.mutation
    def create_channel(self, info: Info, input: ChannelInput) -> ChannelType:
        data = vars(input)
        data["owner"] = get_user(info)
        channel = Channel.objects.create(**data)
        content = channel.to_dict()
        producer.produce(
            "youtube-watcher-channels",
            key=str(content.pop("id")),
            value=json.dumps(content),
            on_delivery=delivery_channel_report,
        )
        producer.flush()
        return channel

    @gql.django.field(directives=[IsAuthenticated])
    def activateChannel(self, channel_id: int, info: Info) -> "ChannelType":
        channel = Channel.objects.get(id=channel_id)
        if channel.profile.user == get_user(info):
            channel.is_active = True
            return channel

    @gql.django.field(directives=[IsAuthenticated])
    def deactivateChannel(self, channel_id: int, info: Info) -> "ChannelType":
        channel = Channel.objects.get(id=channel_id)
        if channel.profile.user == get_user(info):
            channel.is_active = False
            return channel

    @gql.django.field(directives=[IsAuthenticated])
    def activateVideo(self, video_id: int, info: Info) -> "VideoType":
        video = Video.objects.get(id=video_id)
        if video.profile.user == get_user(info):
            video.is_active = True
            return video

    @gql.django.field(directives=[IsAuthenticated])
    def deactivateVideo(self, video_id: int, info: Info) -> "VideoType":
        video = Video.objects.get(id=video_id)
        if video.profile.user == get_user(info):
            video.is_active = False
            return video

    @gql.django.field(directives=[IsAuthenticated])
    def set_google_api_key(self, api_key: str, info: Info) -> "ProfileType":
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
    def getChannels(self, info: Info) -> typing.List[ChannelType]:
        return Channel.objects.filter(owner=get_user(info))


schema = JwtSchema(
    query=Query, mutation=Mutation, extensions=[SchemaDirectiveExtension]
)
