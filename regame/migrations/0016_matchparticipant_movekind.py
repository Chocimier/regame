# Generated by Django 2.1.7 on 2019-04-03 15:02

from django.db import migrations
import enumfields.fields
import regame.models


class Migration(migrations.Migration):

    dependencies = [
        ('regame', '0015_auto_20190402_1847'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchparticipant',
            name='movekind',
            field=enumfields.fields.EnumField(default='a', enum=regame.models.MoveKind, max_length=1),
        ),
    ]
