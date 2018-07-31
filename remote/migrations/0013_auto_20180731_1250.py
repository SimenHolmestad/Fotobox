# Generated by Django 2.0.6 on 2018-07-31 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remote', '0012_auto_20180726_2220'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='description',
            field=models.TextField(default='Dette albumet har ingen beskrivelse', verbose_name='Beskrivelse'),
        ),
        migrations.AlterField(
            model_name='album',
            name='name',
            field=models.CharField(max_length=30, verbose_name='Navn'),
        ),
    ]