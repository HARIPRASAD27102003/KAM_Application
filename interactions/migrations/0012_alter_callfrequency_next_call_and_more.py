# Generated by Django 5.1.3 on 2024-12-26 09:42

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactions', '0011_alter_callfrequency_next_call'),
        ('profiles', '0004_alter_kam_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callfrequency',
            name='next_call',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 26, 9, 42, 53, 445909), help_text='The next scheduled call'),
        ),
        migrations.AlterField(
            model_name='callfrequency',
            name='restaurant',
            field=models.ForeignKey(help_text='The restaurant this call frequency is associated with', on_delete=django.db.models.deletion.CASCADE, related_name='call_frequencies', to='profiles.restaurant', unique=True),
        ),
    ]
