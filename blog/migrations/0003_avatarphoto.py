# Generated by Django 2.2.1 on 2020-07-28 10:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0002_profile_cover_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvatarPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(blank=True, default='photo.jpg', null=True, upload_to='bg_image')),
                ('avatar_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'avatarPhoto',
                'verbose_name_plural': 'avatarPhotos',
            },
        ),
    ]
