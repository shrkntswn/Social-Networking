from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
import filetype
from django.conf import settings
from blog.fileChecker import File_type


class Post(models.Model):
	author = models.ForeignKey(User, related_name='blog_posts', on_delete=models.CASCADE)
	body = models.TextField(null=True, blank=True)
	media = models.FileField(upload_to='post_pics', null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	likes = models.ManyToManyField(User, related_name='likes', blank=True)
	user_tagged = models.ManyToManyField(User, related_name="user_tagged", null=True, blank=True)
	
	def __str__(self):
		return '{} - {} - {}'.format(str(self.author.username), self.body[:20], str(self.created))

	def total_likes(self):
		return self.likes.count()

	def get_absolute_url(self):
		return reverse('blog:post_detail', args=[self.id,])

	def media_kind(self):
		if settings.DEBUG:
			media_path = settings.BASE_DIR + self.media.url
		else:
			media_path = self.media.url
		
		kind = filetype.guess(media_path)
		
		if kind.mime in File_type.image_type():
			return "image"
		elif kind.mime in File_type.video_type():
			return "video"
		else:
			return "Media type not supported"


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	birthday = models.DateField(null=True, blank=True)
	avatar = models.ImageField(default='default/avatar_default.jpg', upload_to='profile_pics', null=True, blank=True)
	cover_image = models.ImageField(default='default/defalt_cover.jpg', upload_to='bg_image', null=True, blank=True)
	follow = models.ManyToManyField(User, related_name='following', blank=True)
	country = models.CharField(max_length=100, blank=True, null=True)
	current_City =  models.CharField(max_length=100, blank=True, null=True)
	about_Myself = models.CharField(max_length=200, blank=True, null=True)
	profession = models.CharField(max_length=200, blank=True, null=True)

	def profile_url(self):
		return reverse('blog:profile', args=[self.user.username, self.user.id])

	def total_followers(self):
		return self.follow.count()
	
	def total_following(self):
		return self.user.following.count()

	def __str__(self):
		return self.user.username

	def get_absolute_url(self):
		return reverse('blog:profile', args=[self.user.username, self.user.id])


class Photo(models.Model):
	profile_user = models.ForeignKey(User, on_delete = models.CASCADE)
	file = models.ImageField(upload_to='bg_image', null=True, blank=True)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = 'photo'
		verbose_name_plural = 'photos'

	def __str__(self):
		return self.profile_user.username


class AvatarPhoto(models.Model):
	avatar_user = models.ForeignKey(User, on_delete = models.CASCADE)
	file = models.ImageField(upload_to='profile_pics', null=True, blank=True)

	class Meta:
		verbose_name = 'avatarPhoto'
		verbose_name_plural = 'avatarPhotos'

	def __str__(self):
		return self.avatar_user.username


class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete = models.CASCADE )
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='replies')
	content = models.TextField(max_length=100)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return '{}-{}'.format(self.content[:20], str(self.user.username))


class Notification(models.Model):
	receiver_user = models.ForeignKey(User, on_delete = models.CASCADE)
	message = models.TextField(max_length=100)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.message



