# Generated by Django 2.0.6 on 2018-06-18 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remote', '0003_auto_20180618_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image_lowres',
            field=models.ImageField(upload_to=''),
        ),
    ]