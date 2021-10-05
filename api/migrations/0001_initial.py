# Generated by Django 3.2.7 on 2021-10-04 13:23

import api.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_name', models.CharField(max_length=20)),
                ('google_image_url', models.URLField()),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to=api.models.upload_profile_path)),
                ('self_introduction', models.CharField(blank=True, max_length=200, null=True)),
                ('github_username', models.CharField(blank=True, max_length=30, null=True)),
                ('twitter_username', models.CharField(blank=True, max_length=30, null=True)),
                ('website_url', models.URLField(blank=True, null=True)),
                ('following_users', models.ManyToManyField(blank=True, default=[], related_name='following_users', to=settings.AUTH_USER_MODEL)),
                ('related_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='related_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]