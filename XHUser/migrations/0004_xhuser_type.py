# Generated by Django 4.0.3 on 2022-04-11 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('XHUser', '0003_remove_xhuser_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='xhuser',
            name='type',
            field=models.IntegerField(default=0),
        ),
    ]
