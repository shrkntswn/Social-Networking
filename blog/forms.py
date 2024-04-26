from django import forms
from .models import Post, User, Profile, Comment, Photo, AvatarPhoto
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from PIL import Image
from django.core.files import File
from blog.fileChecker import file_size

class PostCreationForm(forms.ModelForm):	
	body = forms.CharField(label="Content", widget=forms.Textarea(attrs={'class': 'form-control border-info ', 'rows':5, 'placeholder':'Write Something Here...'}))
	media = forms.FileField(label="media", widget=forms.ClearableFileInput(attrs={'class': 'media-form','accept': {'image/*', 'video/*'}}),required=False, validators=[file_size])

	class Meta():
		model = Post
		fields= ('body', 'media') 



class PostEditForm(forms.ModelForm):
	body = forms.CharField(label="Content", widget=forms.Textarea(attrs={'class': 'form-control', 'rows':3}), required=False)
	
	class Meta():
		model = Post
		fields= ('body', 'media')


class UserLoginForm(forms.Form):
	username= forms.CharField(label="Username",max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
	password = forms.CharField(label="Password", max_length=100, min_length=8, widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserRegistrationForm(UserCreationForm):
	first_name = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control form-control', 'placeholder':'Fist Name'}))
	last_name = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control form-control','placeholder':'Last Name'}))
	username = forms.CharField(label="Username",max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Username'}))
	email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Email'}))
	password1 = forms.CharField(label="Password", max_length=100, min_length=8, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Password'}))
	password2 = forms.CharField(label="Confirm Password", max_length=100, min_length=8, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Confirm Password'}))

	def clean_username(self):
		username = self.cleaned_data['username']
		qs = User.objects.filter(username=username.lower())
		if qs.exists():
			raise ValidationError('Username is already taken.')
		elif len(qs)>15:
			raise ValidationError("Number of characters can't be more than 15.")
		else:
			return username
		

	def clean_email(self):
		email = self.cleaned_data['email']
		qs = User.objects.filter(email=email)
		if qs.exists():
			raise ValidationError('Email is already registered.')
		else: 
			return email
		

	def clean(self):
		cleaned_data = super().clean()
		p1 = cleaned_data.get('password1')
		p2 = cleaned_data.get('password2')
		if p1 and p2:
			if p1 != p2:
				raise ValidationError('Passwords do not match')
		
class UserEditForm(forms.ModelForm):
	username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm','readonly':'readonly'}))
	email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
	first_name = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
	last_name = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
	class Meta:
		model = User
		fields = {
			'username', 'email', 'first_name', 'last_name',
		}	

class ProfileEditForm(forms.ModelForm):
	birthday = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control form-control-sm'}))
	country = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), required=False)
	current_City = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), required=False)
	about_Myself = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), required=False)
	profession = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), required=False)
	class Meta:
		model = Profile
		exclude = ['user', 'follow', 'avatar', 'cover_image']

		

class UserCommentForm(forms.ModelForm):
	content = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'form-control border border-info', 'rows':1,}))

	class Meta:
		model = Comment
		fields = {'content',}
		

class PhotoForm(forms.ModelForm):
	
	x = forms.FloatField(widget=forms.HiddenInput())
	y = forms.FloatField(widget=forms.HiddenInput())
	width = forms.FloatField(widget=forms.HiddenInput())
	height = forms.FloatField(widget=forms.HiddenInput())

	class Meta:
		model = Photo
		fields = ('file', 'x', 'y', 'width', 'height')
		widgets = {
			'file': forms.FileInput(attrs = {
				'accept': 'image/*'  # this is not an actual validation! don't rely on that!
			})
		}


	def save(self):
		photo = super(PhotoForm, self).save()
		
		x = self.cleaned_data.get('x')
		y = self.cleaned_data.get('y')
		w = self.cleaned_data.get('width')
		h = self.cleaned_data.get('height')

		image = Image.open(photo.file)
		cropped_image = image.crop((x, y, w+x, h+y))
		resized_image = cropped_image.resize((1600, 300), Image.ANTIALIAS)
		resized_image.save(photo.file.path)

		return photo


class AvatarPhotoForm(forms.ModelForm):
	
	x = forms.FloatField(widget=forms.HiddenInput())
	y = forms.FloatField(widget=forms.HiddenInput())
	width = forms.FloatField(widget=forms.HiddenInput())
	height = forms.FloatField(widget=forms.HiddenInput())

	class Meta:
		model = AvatarPhoto
		fields = ('file', 'x', 'y', 'width', 'height')
		widgets = {
			'file': forms.FileInput(attrs = {
				'accept': 'image/*'  # this is not an actual validation! don't rely on that!
			})
		}


	def save(self):
		avatarPhoto = super(AvatarPhotoForm, self).save()
		
		x = self.cleaned_data.get('x')
		y = self.cleaned_data.get('y')
		w = self.cleaned_data.get('width')
		h = self.cleaned_data.get('height')

		image = Image.open(avatarPhoto.file)
		cropped_image = image.crop((x, y, w+x, h+y))
		resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
		resized_image.save(avatarPhoto.file.path)

		return avatarPhoto
