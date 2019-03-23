# Generated by Django 2.1.7 on 2019-03-23 13:24

from django.conf import settings
from django.contrib.auth.models import User
from django.db import migrations, models
import django.db.models.deletion

def createprofiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('regame', 'UserProfile')
    for user in User.objects.all():
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('regame', '0007_match_score_to_win'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temporary', models.BooleanField(default=False)),
                ('sound', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RunPython(createprofiles),
    ]