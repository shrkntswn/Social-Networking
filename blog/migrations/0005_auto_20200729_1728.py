# Generated by Django 2.2.1 on 2020-07-29 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_remove_photo_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avatarphoto',
            name='file',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='file',
            field=models.ImageField(blank=True, null=True, upload_to='bg_image'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='default/avatar_default.jpg', null=True, upload_to='profile_pics'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cover_image',
            field=models.ImageField(blank=True, default='default/defalt_cover.jpg', null=True, upload_to='bg_image'),
        ),
    ]