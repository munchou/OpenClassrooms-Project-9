# Generated by Django 3.2.9 on 2023-05-25 14:20

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0033_userfollow'),
    ]

    operations = [
        migrations.CreateModel(
            name='Followers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='profile',
            name='follows',
        ),
        migrations.AddField(
            model_name='profile',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, verbose_name=django.contrib.auth.models.User),
        ),
        migrations.DeleteModel(
            name='UserFollow',
        ),
        migrations.AddField(
            model_name='followers',
            name='another_user',
            field=models.ManyToManyField(related_name='another_user', to='authentication.Profile'),
        ),
        migrations.AddField(
            model_name='followers',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='authentication.profile'),
        ),
    ]
