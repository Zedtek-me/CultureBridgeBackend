# Generated by Django 5.1.2 on 2024-10-19 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
            ],
            options={
                'verbose_name': 'blog',
                'verbose_name_plural': 'blogs',
                'db_table': 'blogs',
                'ordering': ('-created_at',),
                'get_latest_by': 'created_at',
            },
        ),
    ]
