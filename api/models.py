from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.mail import send_mail
from django.db import models


def upload_profile_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(
        ['profiles',
         str(instance.related_user.id) + str(".") + str(ext)])


LIKE_CHOICES = (
    ('Idea', 'アイデア'),
    ('Memo', 'メモ'),
    ('Comment', 'コメント'),
)

THREAD_CHOICES = (
    ('Idea', 'アイデア'),
    ('Memo', 'メモ'),
)

# 通知の種類
NOTIFICATION_CHOICES = (
    ('Comment', 'コメント'),
    ('Follow', 'フォロー'),
    ('Like', 'いいね'),
    ('Announce', 'お知らせ'),
)
# 通知を受けたアイテムの種類
NOTIFIED_ITEM_CHOICES = (
    ('Idea', 'アイデア'),
    ('Memo', 'メモ'),
    ('Comment', 'コメント'),
    ('FollowedUser', 'フォローされたユーザー'),
    ('Announce', 'お知らせ'),
)

# 通報の種類
REPORT_CHOICES = (('', ''))


class UserManager(BaseUserManager):
    def create_user(
        self,
        **kwargs,
    ):
        try:
            email = kwargs.get('email')
            username = kwargs.get('username')
            password = kwargs.get('password')

            if not email:
                raise ValueError('email is must')
            user: User = self.model(email=self.normalize_email(email))
            user.username = username
            user.set_password(password)

            user.save(using=self._db)

            # ユーザー作成時にメールを送信 superuser作成時はコメントアウト
            # send_mail(subject='サンプルアプリ | 本登録のお知らせ',
            #           message=f'ユーザー作成時にメール送信しています' + email,
            #           from_email="sample@email.com",
            #           recipient_list=[email],
            #           fail_silently=False)
            return user
        except:
            raise

    def create_superuser(self, email, password):
        user = self.create_user(**{'email': email, 'password': password})
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# ユーザー
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100,
                                null=False,
                                blank=False,
                                default='')
    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


# ユーザーに1対1で紐づくプロフィール
class Profile(models.Model):
    # 紐付いているユーザー
    related_user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                        related_name='related_user',
                                        on_delete=models.CASCADE)
    # 表示名
    profile_name = models.CharField(max_length=20)
    # もとのGoogleアカウントのデフォルトの画像URL
    google_image_url = models.URLField(null=True, blank=True)
    # プロフィール画像
    profile_image = models.ImageField(blank=True,
                                      null=True,
                                      upload_to=upload_profile_path)
    # 自己紹介
    self_introduction = models.CharField(max_length=200, null=True, blank=True)
    # GitHubとTwitterのユーザーネーム
    github_username = models.CharField(max_length=30, null=True, blank=True)
    twitter_username = models.CharField(max_length=30, null=True, blank=True)
    # 自分のWebサイトのURL
    website_url = models.URLField(null=True, blank=True)

    def __str__(self) -> str:
        return self.profile_name


# フォローの中間テーブル
class Follow(models.Model):
    # フォローした人
    following_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       related_name='following_user',
                                       on_delete=models.CASCADE)
    # フォローされた人
    followed_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      related_name='followed_user',
                                      on_delete=models.CASCADE)
    # フォローしているかの判定フラグ
    is_following = models.BooleanField(default=True)

    def __str__(self) -> str:
        str = self.following_user.related_user.profile_name + ' -> ' + self.followed_user.related_user.profile_name + ' : '
        if self.is_following:
            return str + 'true'
        else:
            return str + 'false'


# アイデアのトピック
class Topic(models.Model):
    name = models.CharField(max_length=10,
                            unique=True,
                            null=False,
                            blank=False)
    display_name = models.CharField(max_length=20,
                                    unique=True,
                                    null=False,
                                    blank=False)

    def __str__(self) -> str:
        return self.name


# しっかりしたアイデア
class Idea(models.Model):
    idea_creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     related_name='idea_creator',
                                     on_delete=models.CASCADE)
    # 関連するトピックを配列形式で保存
    topics = models.ManyToManyField(
        Topic,
        related_name='topics',
        blank=True,
        default=[],
    )
    title = models.CharField(max_length=30)
    content = models.TextField(max_length=3000)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


# タイトルだけのメモ
class Memo(models.Model):
    memo_creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     related_name='memo_creator',
                                     on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title


# 対象の投稿ごとにスレッドを作れる
class Thread(models.Model):
    # 対象の投稿のモデルタイプ
    thread_target_type = models.CharField(null=False,
                                          blank=False,
                                          max_length=50,
                                          choices=THREAD_CHOICES)
    # 投稿タイプによって外部参照キーを変更
    target_idea = models.ForeignKey(Idea,
                                    null=True,
                                    blank=True,
                                    related_name='target_idea',
                                    on_delete=models.CASCADE)
    target_memo = models.ForeignKey(Memo,
                                    null=True,
                                    blank=True,
                                    related_name='target_memo',
                                    on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.thread_target_type


# スレッドに付随するコメント
class Comment(models.Model):
    commentor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='commentor',
                                  on_delete=models.CASCADE)
    target_thread = models.ForeignKey(Thread,
                                      related_name='target_thread',
                                      on_delete=models.CASCADE)
    content = models.TextField(max_length=300)
    # 変更されたかのフラグ
    is_modified = models.BooleanField(default=False)
    # 公開されているか(デフォルトでは普通に公開されている)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.commentor.email + ' : ' + self.content


# 投稿にいいねしたときの中間テーブル
class Like(models.Model):
    liked_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name='liked_user',
                                   on_delete=models.CASCADE)
    # いいねの対象の投稿タイプ
    like_target_type = models.CharField(max_length=50,
                                        choices=LIKE_CHOICES,
                                        null=False,
                                        blank=False)
    # 投稿タイプによって外部参照キーを変更
    liked_idea = models.ForeignKey(Idea,
                                   null=True,
                                   blank=True,
                                   related_name='liked_idea',
                                   on_delete=models.CASCADE)
    liked_memo = models.ForeignKey(Memo,
                                   null=True,
                                   blank=True,
                                   related_name='liked_memo',
                                   on_delete=models.CASCADE)
    liked_comment = models.ForeignKey(Comment,
                                      null=True,
                                      blank=True,
                                      related_name='liked_comment',
                                      on_delete=models.CASCADE)
    # いいねをしているかのフラグ
    is_liked = models.BooleanField(default=True)

    def __str__(self) -> str:
        if self.like_target_type == 'Idea':
            str = self.liked_user.related_user.profile_name + ' -> ' + self.liked_idea.title + ' : '
            if self.is_liked:
                return str + 'true'
            else:
                return str + 'false'

        if self.like_target_type == 'Memo':
            str = self.liked_user.related_user.profile_name + ' -> ' + self.liked_memo.title + ' : '
            if self.is_liked:
                return str + 'true'
            else:
                return str + 'false'

        if self.like_target_type == 'Comment':
            str = self.liked_user.related_user.profile_name + ' -> ' + self.liked_comment.content + ' : '
            if self.is_liked:
                return str + 'true'
            else:
                return str + 'false'
        return self.like_target_type


# ユーザーからユーザーへの通知
class Notification(models.Model):
    # 通知を作成した人
    notificator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    related_name='notificator',
                                    on_delete=models.CASCADE)
    # 通知を受けた人
    notification_reciever = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notification_reciever',
        on_delete=models.CASCADE)
    # 通知の種類
    notification_type = models.CharField(choices=NOTIFICATION_CHOICES,
                                         max_length=50,
                                         null=False,
                                         blank=False)
    # 通知を受けたアイテムの種類
    notified_item_type = models.CharField(choices=NOTIFIED_ITEM_CHOICES,
                                          max_length=50,
                                          null=False,
                                          blank=False)
    # 通知を受けたアイテムのID（遷移するために必要）
    notified_item_id = models.PositiveBigIntegerField()
    # 通知が確認済みか
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.notificator.related_user.profile_name + ' : ' + self.notification_type


# 全体へのお知らせ
class Announce(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    # 重要なお知らせかどうか
    is_important = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


# ユーザーからの通報
class Report(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 related_name='reporter',
                                 on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=False, blank=False)
    content = models.CharField(max_length=1000, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title
