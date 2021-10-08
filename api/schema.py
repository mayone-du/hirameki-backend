import asyncio

import graphene
import graphql_social_auth
from django.contrib.auth import get_user_model
from django.db import models
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql_relay import from_global_id

from api.validation import validate_token

from .models import (LIKE_CHOICES, THREAD_CHOICES, Announce, Comment, Follow,
                     Idea, Like, Memo, Notification, Profile, Report, Thread,
                     Topic, User)


# ユーザー
class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            'username': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'is_staff': ['exact'],
            'is_superuser': ['exact'],
        }
        interfaces = (relay.Node, )


class ProfileNode(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = {
            'profile_name': ['exact', 'icontains'],
            'self_introduction': ['exact', 'icontains'],
            'github_username': ['exact', 'icontains'],
            'twitter_username': ['exact', 'icontains'],
            'website_url': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )


class FollowNode(DjangoObjectType):
    class Meta:
        model = Follow
        filter_fields = {
            'following_user': ['exact'],
            'followed_user': ['exact'],
            'is_following': ['exact'],
        }
        interfaces = (relay.Node, )


class TopicNode(DjangoObjectType):
    class Meta:
        model = Topic
        filter_fields = {
            'name': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )


class IdeaNode(DjangoObjectType):
    class Meta:
        model = Idea
        filter_fields = {
            'idea_creator': ['exact'],
            'title': ['exact', 'icontains'],
            'content': ['exact', 'icontains'],
            'is_published': ['exact'],
        }
        interfaces = (relay.Node, )


class MemoNode(DjangoObjectType):
    class Meta:
        model = Memo
        filter_fields = {
            'memo_creator': ['exact'],
            'title': ['exact', 'icontains'],
            'is_published': ['exact'],
        }
        interfaces = (relay.Node, )


class ThreadNode(DjangoObjectType):
    class Meta:
        model = Thread
        filter_fields = {
            'thread_target_type': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )


class CommentNode(DjangoObjectType):
    class Meta:
        model = Comment
        filter_fields = {
            'commentor': ['exact'],
            'target_thread': ['exact'],
        }
        interfaces = (relay.Node, )


class LikeNode(DjangoObjectType):
    class Meta:
        model = Like
        filter_fields = {
            'liked_user': ['exact'],
            'like_target_type': ['exact'],
            'is_liked': ['exact'],
        }
        interfaces = (relay.Node, )


class NotificationNode(DjangoObjectType):
    class Meta:
        model = Notification
        filter_fields = {
            'notificator': ['exact'],
            'notification_reciever': ['exact'],
            'notification_type': ['exact'],
            'is_checked': ['exact'],
        }
        interfaces = (relay.Node, )


class AnnounceNode(DjangoObjectType):
    class Meta:
        model = Announce
        filter_fields = {
            'title': ['exact', 'icontains'],
            'content': ['exact', 'icontains'],
            'is_important': ['exact'],
        }
        interfaces = (relay.Node, )


class ReportNode(DjangoObjectType):
    class Meta:
        model = Report
        filter_fields = {
            'title': ['exact', 'icontains'],
            'content': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )


# プロフィール
class UpdateProfileMutation(relay.ClientIDMutation):
    class Input:
        profile_id = graphene.ID(required=True)
        profile_name = graphene.String(required=False)
        google_image_url = graphene.String(required=False)
        profile_image = Upload(required=False)
        self_introduction = graphene.String(required=False)
        github_username = graphene.String(required=False)
        twitter_username = graphene.String(required=False)
        website_url = graphene.String(required=False)

    profile = graphene.Field(ProfileNode)

    def mutate_and_get_payload(root, info, **input):
        try:
            profile_id = input.get('profile_id')
            profile_name = input.get('profile_name')
            google_image_url = input.get('google_image_url')
            self_introduction = input.get('self_introduction')

            profile: Profile = Profile.objects.get(
                id=from_global_id(profile_id)[1])
            print(profile)

            if profile_name is not None:
                profile.profile_name = profile_name
            if google_image_url is not None:
                profile.google_image_url = google_image_url

            profile.save()

            return UpdateProfileMutation(profile=profile)
        except:
            raise


# フォロー
class CreateFollowMutation(relay.ClientIDMutation):
    class Input:
        followed_user_id = graphene.ID(required=True)

    follow = graphene.Field(FollowNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            followed_user_id = input.get('followed_user_id')
            following_user = get_user_model().objects.get(
                email=info.context.user.email)
            followed_user = get_user_model().objects.get(
                id=from_global_id(followed_user_id)[1])
            follow = Follow(following_user=following_user,
                            followed_user=followed_user)
            follow.save()
            return CreateFollowMutation(follow=follow)
        except:
            raise


class UpdateFollowMutation(relay.ClientIDMutation):
    class Input:
        follow_id = graphene.ID(required=True)
        is_following = graphene.Boolean(required=True)

    follow = graphene.Field(FollowNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            follow_id = input.get('follow_id')
            is_following = input.get('is_following')
            follow: Follow = Follow.objects.get(
                id=from_global_id(follow_id)[1])
            follow.is_following = is_following
            follow.save()
            return UpdateFollowMutation(follow=follow)
        except:
            raise


# アイデア
class CreateIdeaMutation(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        topic_ids = graphene.List(graphene.ID)

    idea = graphene.Field(IdeaNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            user = get_user_model().objects.get(email=info.context.user.email)

            title = input.get('title')
            content = input.get('content')
            topic_ids = input.get('topic_ids')
            idea = Idea(idea_creator=user, title=title, content=content)
            # TODO
            # for topic_id in topic_ids:
            #     pass
            idea.save()
            return CreateIdeaMutation(idea=idea)
        except:
            raise


class UpdateIdeaMutation(relay.ClientIDMutation):
    class Input:
        idea_id = graphene.ID(required=True)
        title = graphene.String(required=False)
        content = graphene.String(required=False)

    idea = graphene.Field(IdeaNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            idea_id = input.get('idea_id')
            title = input.get('title')
            content = input.get('content')
            idea: Idea = Idea.objects.get(id=from_global_id(idea_id)[1])
            if title is not None:
                idea.title = title
            if content is not None:
                idea.content = content
            idea.save()
            return CreateIdeaMutation(idea=idea)
        except:
            raise


class DeleteIdeaMutation(relay.ClientIDMutation):
    class Input:
        idea_id = graphene.ID(required=True)

    idea = graphene.Field(IdeaNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            idea_id = input.get('idea_id')
            idea: Idea = Idea.objects.get(id=from_global_id(idea_id)[1])
            idea.delete()
            return DeleteIdeaMutation(idea=idea)
        except:
            raise


# メモ
class CreateMemoMutation(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)

    memo = graphene.Field(MemoNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            title = input.get('title')
            memo = Memo(title=title)
            memo.save()
            return
        except:
            raise


class UpdateMemoMutation(relay.ClientIDMutation):
    class Input:
        memo_id = graphene.ID(required=True)
        title = graphene.String(required=False)

    memo = graphene.Field(MemoNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            memo_id = input.get('memo_id')
            title = input.get('title')
            memo: Memo = Memo.objects.get(id=from_global_id(memo_id)[1])
            if title is not None:
                memo.title = title
            memo.save()
            return UpdateMemoMutation(memo=memo)
        except:
            raise


class DeleteMemoMutation(relay.ClientIDMutation):
    class Input:
        memo_id = graphene.ID(required=True)

    memo = graphene.Field(MemoNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            memo_id = input.get('memo_id')
            memo: Memo = Memo.objects.get(id=from_global_id(memo_id)[1])
            memo.delete()
            return DeleteMemoMutation(memo=memo)
        except:
            raise


# スレッド
class CreateThreadMutation(relay.ClientIDMutation):
    class Input:
        thread_target_type = graphene.String(required=True)
        target_idea_id = graphene.ID(required=False)
        target_memo_id = graphene.ID(required=False)

    thread = graphene.Field(ThreadNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            thread_target_type = input.get('thread_target_type')
            # thread_target_typeは指定された値のみに限定する
            if not thread_target_type in THREAD_CHOICES:
                raise ValueError('thread_target_type error')

            # どちらか片方は必須にする
            target_idea_id = input.get('target_idea_id')
            target_memo_id = input.get('target_memo_id')
            if (target_idea_id and target_memo_id) is None:
                raise ValueError('Either id is required')

            thread = Thread(thread_target_type=thread_target_type)

            if target_idea_id is not None:
                idea: Idea = Idea.objects.get(
                    id=from_global_id(target_idea_id)[1])
                thread.target_idea = idea

            if target_memo_id is not None:
                memo: Memo = Memo.objects.get(
                    id=from_global_id(target_memo_id)[1])
                thread.target_memo = memo

            thread.save()
            return CreateThreadMutation(thread=thread)
        except:
            raise


# コメント
class CreateCommentMutation(relay.ClientIDMutation):
    class Input:
        target_thread_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    comment = graphene.Field(CommentNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            target_thread_id = input.get('target_thread_id')
            content = input.get('content')

            user: User = User.objects.get(email=info.context.user.email)
            thread: Thread = Thread.objects.get(
                id=from_global_id(target_thread_id)[1])

            comment = Comment(commentor=user,
                              target_thread=thread,
                              content=content)
            comment.save()
            return CreateCommentMutation(comment=comment)
        except:
            raise


class UpdateCommentMutation(relay.ClientIDMutation):
    class Input:
        comment_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    comment = graphene.Field(CommentNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            comment_id = input.get('comment_id')
            content = input.get('content')
            comment: Comment = Comment.objects.get(
                id=from_global_id(comment_id)[1])

            comment.content = content
            comment.is_modified = True
            comment.save()
            return UpdateCommentMutation(comment=comment)
        except:
            raise


class DeleteCommentMutation(relay.ClientIDMutation):
    class Input:
        comment_id = graphene.ID(required=True)

    comment = graphene.Field(CommentNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            comment_id = input.get('comment_id')
            comment: Comment = Comment.objects.get(
                id=from_global_id(comment_id)[1])
            comment.delete()
            return DeleteCommentMutation(comment=comment)
        except:
            raise


# いいね
class CreateLikeMutation(relay.ClientIDMutation):
    class Input:
        like_target_type = graphene.String(required=True)
        liked_idea_id = graphene.ID(required=False)
        liked_memo_id = graphene.ID(required=False)
        liked_comment_id = graphene.ID(required=False)

    like = graphene.Field(LikeNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            like_target_type = input.get('like_target_type')
            if not like_target_type in LIKE_CHOICES:
                raise ValueError('like_target_type error')

            liked_idea_id = input.get('liked_idea_id')
            liked_memo_id = input.get('liked_memo_id')
            liked_comment_id = input.get('liked_comment_id')
            if (liked_idea_id and liked_memo_id and liked_comment_id) is None:
                raise ValueError('Either id is required')

            user = get_user_model().objects.get(email=info.context.user.email)
            like = Like(liked_user=user, like_target_type=like_target_type)

            if liked_idea_id is not None:
                idea = Idea.objects.get(id=from_global_id(liked_idea_id)[1])
                like.liked_idea = idea
            if liked_memo_id is not None:
                memo = Memo.objects.get(id=from_global_id(liked_memo_id)[1])
                like.liked_memo = memo
            if liked_comment_id is not None:
                comment = Comment.objects.get(
                    id=from_global_id(liked_comment_id)[1])
                like.liked_comment = comment

            like.save()
            return CreateLikeMutation(like=like)
        except:
            raise


class UpdateLikeMutation(relay.ClientIDMutation):
    class Input:
        like_id = graphene.ID(required=True)
        is_liked = graphene.Boolean(required=True)

    like = graphene.Field(LikeNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            like_id = input.get('like_id')
            is_liked = input.get('is_liked')

            like: Like = Like.objects.get(id=from_global_id(like_id)[1])
            like.is_liked = is_liked
            like.save()
            return UpdateLikeMutation(like=like)
        except:
            raise


# 通知
class CreateNotificationMutation(relay.ClientIDMutation):
    class Input:
        notification_reciever_id = graphene.ID(required=True)
        notification_type = graphene.String(required=True)
        notified_item_type = graphene.String(required=True)
        notified_item_id = graphene.Int(required=True)

    notification = graphene.Field(NotificationNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            notificator = get_user_model().objects.get(
                email=info.context.user.email)

            notification_reciever_id = input.get('notification_reciever_id')
            notification_reciever = get_user_model().objects.get(
                id=from_global_id(notification_reciever_id)[1])

            notification_type = input.get('notification_type')
            notified_item_type = input.get('notified_item_type')
            notified_item_id = input.get('notified_item_id')

            notification = Notification(
                notificator=notificator,
                notification_reciever=notification_reciever,
                notification_type=notification_type,
                notified_item_type=notified_item_type,
                notified_item_id=from_global_id(notified_item_id)[1])
            notification.save()
            return CreateNotificationMutation(notification=notification)
        except:
            raise


class UpdateNotificationMutation(relay.ClientIDMutation):
    class Input:
        notification_id = graphene.ID(required=True)
        is_checked = graphene.Boolean(required=True)

    notification = graphene.Field(NotificationNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            notification_id = input.get('notification_id')
            is_checked = input.get('is_checked')

            notification: Notification = Notification(
                id=from_global_id(notification_id)[1])
            notification.is_checked = is_checked
            notification.save()
            return UpdateNotificationMutation(notification=notification)
        except:
            raise


class CreateReportMutation(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)
        content = graphene.String(required=True)

    report = graphene.Field(ReportNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            title = input.get('title')
            content = input.get('content')
            user = get_user_model().objects.get(email=info.context.user.email)
            report = Report(reporter=user, title=title, content=content)
            return CreateReportMutation(report=report)
        except:
            raise


class Mutation(graphene.ObjectType):
    social_auth = graphql_social_auth.SocialAuth.Field()

    # profile
    update_profile = UpdateProfileMutation.Field()

    # follow
    create_follow = CreateFollowMutation.Field()
    udpate_follow = UpdateFollowMutation.Field()

    # idea
    create_idea = CreateIdeaMutation.Field()
    update_idea = UpdateIdeaMutation.Field()
    delete_idea = DeleteIdeaMutation.Field()

    # memo
    create_memo = CreateMemoMutation.Field()
    update_memo = UpdateMemoMutation.Field()
    delete_memo = DeleteMemoMutation.Field()

    # thread
    create_thread = CreateThreadMutation.Field()

    # comment
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()

    # like
    create_like = CreateLikeMutation.Field()
    update_like = UpdateLikeMutation.Field()

    # notification
    create_notification = CreateNotificationMutation.Field()
    update_notification = UpdateNotificationMutation.Field()

    # report
    create_report = CreateReportMutation.Field()


class Query(graphene.ObjectType):
    user = graphene.Field(UserNode, id=graphene.NonNull(graphene.ID))
    all_users = DjangoFilterConnectionField(UserNode)
    my_user_info = graphene.Field(UserNode)

    def resolve_user(self, info, **kwargs):
        id = kwargs.get('id')
        return get_user_model().objects.get(id=from_global_id(id)[1])

    def resolve_all_users(self, info, **kwargs):
        return get_user_model().objects.all()

    @validate_token
    def resolve_my_user_info(self, info):
        email = info.context.user.email
        return get_user_model().objects.get(email=email)

    # idea
    def resolve_idea(self, info, **kwargs):
        id = kwargs.get('id')
        return Idea.objects.get(id=from_global_id(id)[1])

    def resolve_all_publised_ideas(self, info, **kwargs):
        ideas = Idea.objects.filter(is_published=True)
        return ideas


class Subscription(graphene.ObjectType):
    count_seconds = graphene.Float(up_to=graphene.Int())

    async def resolve_count_seconds(root, info, up_to):
        for i in range(up_to):
            yield i
            await asyncio.sleep(1.)
        yield up_to
