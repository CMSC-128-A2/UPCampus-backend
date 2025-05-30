# Generated by Django 5.1.1 on 2025-05-24 12:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0005_adminuser_is_superuser_alter_adminuser_department'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room', models.CharField(max_length=50)),
                ('floor', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['room'],
                'unique_together': {('room', 'floor')},
            },
        ),
        migrations.AlterField(
            model_name='classsection',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_sections', to='schedules.room'),
        ),
    ]
