# Generated by Django 3.2.9 on 2023-05-31 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_auto_20230530_2307'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='reply',
            field=models.BooleanField(default=False),
        ),
    ]
