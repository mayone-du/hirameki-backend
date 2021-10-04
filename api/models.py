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
            user = self.model(email=self.normalize_email(email),
                              username=username)
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
            raise ValueError('create_user_error')

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# ユーザー
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100)
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
    # フォロー機能 自分がフォローしているユーザーはプロフィールモデルから、フォローされているユーザーはユーザーモデルから逆参照で取得
    following_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='following_users',
        blank=True,
        default=[],
    )

    def __str__(self) -> str:
        return self.profile_name


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
    # topics = models.ManyToManyField()
    title = models.CharField(max_length=30)
    content = models.TextField(max_length=3000)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # アイデアにいいねしたユーザー
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='likes',
                                   blank=True)


# タイトルだけのメモ
class Memo(models.Model):
    memo_creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     related_name='memo_creator',
                                     on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)


# アイデアに良いねしたときの中間テーブル
class IdeaLike(models.Model):
    like_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='like_user',
                                  on_delete=models.CASCADE)
    target_idea = models.ForeignKey(Idea,
                                    related_name='target_post',
                                    on_delete=models.CASCADE)


# TODO: アイデアやメモ、コメントのためのコメント
class Comment(models.Model):
    commentor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='commentor',
                                  on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)


# 通知
class Notification(models.Model):
    notificator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    related_name='notificator',
                                    on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
