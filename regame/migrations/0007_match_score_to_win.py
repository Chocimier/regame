# Generated by Django 2.1.7 on 2019-03-22 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regame', '0006_auto_20190315_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='score_to_win',
            field=models.PositiveSmallIntegerField(default=40),
        ),
    ]
