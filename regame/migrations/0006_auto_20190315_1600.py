# Generated by Django 2.1.7 on 2019-03-15 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regame', '0005_auto_20190314_2053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='patternbit',
            field=models.CharField(max_length=12),
        ),
        migrations.AlterField(
            model_name='card',
            name='text',
            field=models.CharField(max_length=12),
        ),
    ]