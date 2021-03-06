# Generated by Django 3.2.7 on 2021-10-05 23:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20211006_0821'),
    ]

    operations = [
        migrations.RenameField(
            model_name='thred',
            old_name='comment_target_type',
            new_name='thread_target_type',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='target_thred',
        ),
        migrations.AddField(
            model_name='comment',
            name='target_thread',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='target_thread', to='api.thred'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(default='', max_length=100),
        ),
    ]
