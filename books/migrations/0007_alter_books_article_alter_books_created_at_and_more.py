# Generated by Django 5.0.1 on 2024-02-02 01:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_alter_books_article_alter_books_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='books',
            name='article',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='books',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 2, 1, 31, 50, 380373, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='books',
            name='unique_url',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='users',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 2, 1, 31, 50, 380009, tzinfo=datetime.timezone.utc)),
        ),
    ]