# Generated by Django 3.2 on 2023-04-10 22:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Имя категории')),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название жанра')),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название произведения')),
                ('year', models.IntegerField(verbose_name='Год выпуска')),
                ('description', models.CharField(max_length=256, null=True, verbose_name='Описание')),
                ('category', models.ForeignKey(default='default', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='categories', to='api.category')),
                ('genre', models.ForeignKey(default='default', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='genres', to='api.genre')),
            ],
        ),
    ]
