import asyncio

import graphene
import graphql_social_auth
from django.contrib.auth import get_user_model
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphene_file_upload.scalars import Upload
from graphql_relay import from_global_id

from api.validation import validate_token

from .models import (Announce, Comment, Follow, Idea, Like, Memo, Notification,
                     Profile, Thread, Topic, User)


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
        model = Thred
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
            'is_checked': ['exact'],
        }
        interfaces = (relay.Node, )


class AnnounceNode(DjangoObjectType):
    class Meta:
        model = Announce
        filter_fields = {
            'title': ['exact', 'icontains'],
            'content': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )


class UpdateProfileMutation(relay.ClientIDMutation):
    class Input:
        profile_id = graphene.ID(required=True)
        profile_name = graphene.String(required=False)

    profile = graphene.Field(ProfileNode)

    def mutate_and_get_payload(root, info, **input):
        try:
            profile_id = input.get('profile_id')
            profile_name = input.get('profile_name')

            profile: Profile = Profile.objects.get(
                id=from_global_id(profile_id)[1])

            if profile_name is not None:
                profile.profile_name = profile_name

            profile.save()

            return UpdateProfileMutation(profile=profile)
        except:
            raise


# アイデア
class CreateIdeaMutation(relay.ClientIDMutation):
    class Input:
        title = graphene.String(required=True)
        content = graphene.String(required=True)

    idea = graphene.Field(IdeaNode)

    @validate_token
    def mutate_and_get_payload(root, info, **input):
        try:
            user = get_user_model().objects.get(email=info.context.user.email)

            title = input.get('title')
            content = input.get('content')
            idea = Idea(idea_creator=user, title=title, content=content)
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
            target_idea_id = input.get('target_idea_id')
            target_memo_id = input.get('target_memo_id')

            if target_idea_id and target_memo_id is None:
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
            return CreateCommentMutation(comment=comment)
        except:
            raise


# # タスクの作成
# class CreateTaskMutation(relay.ClientIDMutation):
#     class Input:
#         title = graphene.String(required=True)
#         content = graphene.String(required=False)
#         task_image = Upload(required=False)

#     task = graphene.Field(TaskNode)

#     @validate_token
#     def mutate_and_get_payload(root, info, **input):
#         try:
#             current_user = get_user_model().objects.get(email=input.get('login_user_email'))
#             task = Task(
#                 create_user=current_user.id,
#                 title=input.get('title'),
#             )
#             if input.get('content') is not None:
#                 task.content = input.get('content')
#             return CreateTaskMutation(task=task)
#         except:
#             raise ValueError('create task error')

# # タスクの更新
# class UpdateTaskMutation(relay.ClientIDMutation):
#     class Input:
#         id = graphene.ID(required=True)
#         title = graphene.String(required=True)

#     task = graphene.Field(TaskNode)

#     @validate_token
#     def mutate_and_get_payload(root, info, **input):
#         id = input.get('id')
#         title = input.get('title')
#         content = input.get('content')
#         is_done = input.get('is_done')

#         task = Task.objects.get(id=from_global_id(id)[1])

#         if title is not None:
#             task.title = title
#         if content is not None:
#             task.content =content
#         if is_done is not None:
#             task.is_done =is_done

#         task.save()
#         return UpdateTaskMutation(task=task)

# # タスクの削除
# class DeleteTaskMutation(relay.ClientIDMutation):
#     class Input:
#         id = graphene.ID(required=True)

#     task = graphene.Field(TaskNode)

#     @validate_token
#     def mutate_and_get_payload(root, info, **input):
#         task = Task.objects.get(id=from_global_id(id)[1])
#         task.delete()
#         return DeleteTaskMutation(task=task)


class Mutation(graphene.ObjectType):
    social_auth = graphql_social_auth.SocialAuth.Field()

    # create_task = CreateTaskMutation.Field()
    # update_task = UpdateTaskMutation.Field()
    # delete_task = DeleteTaskMutation.Field()


class Query(graphene.ObjectType):
    user = graphene.Field(UserNode, id=graphene.NonNull(graphene.ID))
    all_users = DjangoFilterConnectionField(UserNode)
    request_user = graphene.Field(UserNode)

    # task = graphene.Field(TaskNode, id=graphene.NonNull(graphene.ID))

    def resolve_user(self, info, **kwargs):
        id = kwargs.get('id')
        return get_user_model().objects.get(id=from_global_id(id)[1])

    def resolve_all_users(self, info, **kwargs):
        return get_user_model().objects.all()

    @validate_token
    def resolve_user(self, info):
        # ↓デコレーターで追加されたemailにアクセス
        email = info.context.user.email
        return get_user_model().objects.get(email=email)

    # @validate_token
    # def resolve_task(self, info, **kwargs):
    #     id = kwargs.get('id')
    #     return Task.objects.get(id=from_global_id(id)[1])


class Subscription(graphene.ObjectType):
    count_seconds = graphene.Float(up_to=graphene.Int())

    async def resolve_count_seconds(root, info, up_to):
        for i in range(up_to):
            yield i
            await asyncio.sleep(1.)
        yield up_to
