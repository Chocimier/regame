# Generated by Django 2.1.7 on 2019-03-25 13:37

from django.db import migrations, models
import enumfields.fields
import regame.models


class Migration(migrations.Migration):

    dependencies = [
        ('regame', '0010_userprofile_hidden'),
    ]

    operations = [
        migrations.RenameField(
            model_name='match',
            old_name='score_to_win',
            new_name='winconditionnumber',
        ),
        migrations.AddField(
            model_name='match',
            name='turnspassed',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='winconditiontype',
            field=enumfields.fields.EnumField(default='g', enum=regame.models.WinConditionType, max_length=1),
        ),
    ]
