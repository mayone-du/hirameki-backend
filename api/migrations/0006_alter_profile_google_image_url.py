# Generated by Django 3.2.7 on 2021-10-08 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_report_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='google_image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
