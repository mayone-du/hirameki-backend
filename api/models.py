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


class UserManager(BaseUserManager):
    def create_user(
        self,
        **kwargs,
    ):
        try:
            email = kwargs.get('email')
            username = kwargs.get('username')
            password = kwargs.get('password')
            print(kwargs)
            if not email:
                raise ValueError('email is must')
            user = self.model(email=self.normalize_email(email))
            if not username:
                user.username = ''
            user.set_password(password)
            user.save(using=self._db)
            # ユーザー作成時にメールを送信 superuser作成時はコメントアウト
            send_mail(subject='サンプルアプリ | 本登録のお知らせ',
                      message=f'ユーザー作成時にメール送信しています' + email,
                      from_email="sample@email.com",
                      recipient_list=[email],
                      fail_silently=False)
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
                                default="")
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
    google_image_url = models.URLField()
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

    # # フォロー機能 自分がフォローしているユーザーはプロフィールモデルから、フォローされているユーザーはユーザーモデルから逆参照で取得
    # following_users = models.ManyToManyField(
    #     settings.AUTH_USER_MODEL,
    #     related_name='following_users',
    #     blank=True,
    #     default=[],
    # )

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
    is_following = models.BooleanField(default=False)


# アイデアのトピック
class Topic(models.Model):
    name = models.CharField(max_length=10,
                            unique=True,
                            null=False,
                            blank=False)


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


# タイトルだけのメモ
class Memo(models.Model):
    memo_creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     related_name='memo_creator',
                                     on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)


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
                                    related_name='target_idea',
                                    on_delete=models.CASCADE)
    target_memo = models.ForeignKey(Memo,
                                    null=True,
                                    related_name='target_memo',
                                    on_delete=models.CASCADE)


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


# 投稿に良いねしたときの中間テーブル
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
                                   related_name='liked_idea',
                                   on_delete=models.CASCADE)
    liked_memo = models.ForeignKey(Memo,
                                   null=True,
                                   related_name='liked_memo',
                                   on_delete=models.CASCADE)
    liked_comment = models.ForeignKey(Comment,
                                      null=True,
                                      related_name='liked_comment',
                                      on_delete=models.CASCADE)
    # いいねをしているかのフラグ
    is_liked = models.BooleanField(default=False)


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
    # 通知が確認済みか
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


# 全体へのお知らせ
class Announce(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
