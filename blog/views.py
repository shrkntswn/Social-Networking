from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Profile, Comment, Photo, AvatarPhoto, Notification
from django.urls import reverse 
from .forms import PostCreationForm, UserLoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm, PostEditForm, UserCommentForm, PhotoForm, AvatarPhotoForm
from datetime import datetime
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import re
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
import filetype
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from blog.fileChecker import File_type
import random

#=====================================POST RELATED========================================================
# HOME
@login_required(login_url='blog:user_login')
def post_list(request, newContext={}):

	user=request.user
	profile_user = get_object_or_404(Profile, user=request.user)
	follow_list = user.following.all()
	form = PostCreationForm()
	comment_form = UserCommentForm()
	people_u_may_know = list(Profile.objects.all())
	people_u_may_know=random.sample(people_u_may_know, 3)
	print(profile_user)
	print(people_u_may_know)
	
	def loop_author(request):
		temp = Q(author = request.user)
		for f in follow_list:
			temp = temp|Q(author = f.user)
		return temp

	posts = Post.objects.filter(loop_author(request)).order_by('-updated')
	post_list = posts

	posts_likes = list()
	#for likes
	for post in posts:
		is_liked = False
		if post.likes.filter(id=request.user.id).exists():
			is_liked = True
		posts_likes.append(is_liked)

	posts_comments=list()
	for post in posts:
		comments = Comment.objects.filter(post=post, reply=None)
		posts_comments.append(comments)

	#for query
	query = request.GET.get('term')
	if query:
		profiles = Profile.objects.filter(Q(user__username__icontains = query)|
			Q(user__first_name__icontains = query)|
			Q(user__last_name__icontains = query))
		post_list = Post.objects.filter(
			Q(author__username = query)|Q(body__icontains = query)
			).order_by('-created')
		if profiles is not None or post_list is not None:
			query_user = True
		
		#FOR QUERY POST LIKES
		posts_likes = list()	
		for post in post_list:
			is_liked = False
			if post.likes.filter(id=request.user.id).exists():
				is_liked = True
			posts_likes.append(is_liked)

		posts_comments=list()
		for post in post_list:
			comments = Comment.objects.filter(post=post, reply=None)
			posts_comments.append(comments)
		context = {'profile_user':profile_user, 'profiles':profiles, 'form':form, 'query_user':query_user, 'query':query, 'comment_form':comment_form, 'zipped_posts':zip(post_list,posts_likes), 'posts_comments':posts_comments,'total_followers':profile_user.total_followers,'total_following':profile_user.total_following(),'people_u_may_know':people_u_may_know}
	else:
		context = {'profile_user':profile_user, 'form':form,'comment_form':comment_form, 'zipped_posts':zip(post_list,posts_likes,), 'posts_comments':posts_comments,'total_followers':profile_user.total_followers,'total_following':profile_user.total_following(),'people_u_may_know':people_u_may_know}
	context.update(newContext)
	return render(request, 'blog/post_list.html', context)


# auto complete
def auto_search(request):
	if request.is_ajax():
		q = request.GET.get('term')
		qs = Profile.objects.filter(Q(user__username__icontains = q)|
			Q(user__first_name__icontains = q)|
			Q(user__last_name__icontains = q))
		results = []
		for profile in qs:
			profile_json ={}
			profile_json['label'] = profile.user.username
			profile_json['image'] = profile.avatar.url
			profile_json['url'] = profile.get_absolute_url()
			results.append(profile_json)
			print(results)	
		data = json.dumps(results)
	else:
		data = 'fail'
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)


# for post details
@login_required(login_url='blog:user_login')
def post_detail(request, id):
	
	post = get_object_or_404(Post, id=id)
	user_post = PostEditForm(instance = post)
	comments = Comment.objects.filter(post=post, reply=None).order_by('-id')

	is_liked = False
	if post.likes.filter(id=request.user.id).exists():
		is_liked = True

	if request.method == 'POST':
		comment_form = UserCommentForm(request.POST or None)
		if comment_form.is_valid():
			content = request.POST.get('content')
			reply_id = request.POST.get('comment_id')
			comment_qs = None
			if reply_id:
				comment_qs = Comment.objects.get(id=reply_id)	
			body_list=content.split(' ')
			new_list=[]
			for body in body_list:
				if body.startswith('@'):
					body=body.strip('@')
					new_list.append(body)
			profiles=Profile.objects.filter(user__username__in=new_list)
			profile_dict = {}
			for profile in profiles:
				profile_dict.update({'@'+profile.user.username:profile.get_absolute_url()})
			for key, value in profile_dict.items():
				content = content.replace(key, '<a href="%s">%s</a>' % (value,key))
			comment = Comment.objects.create(post=post, user=request.user, content=content, reply=comment_qs)
			comment.save()
			return HttpResponseRedirect(post.get_absolute_url())
	else:
		comment_form = UserCommentForm()
	context = {'post':post,
			  'is_liked':is_liked,
			  'total_likes': post.total_likes,
			  'comments':comments,
			  'comment_form':comment_form, 
			  'user_post': user_post,
			  }

	if request.is_ajax():
		html = render_to_string('blog/comments.html', context, request=request)
		return JsonResponse({'form':html})
	return render(request, 'blog/post_detail.html', context)



@login_required(login_url='blog:user_login')
def comment_delete(request, post_id, id):
	comment = get_object_or_404(Comment, id=id)
	post = get_object_or_404(Post, id = post_id)
	if request.user== comment.user or request.user==post.author:
		comment.delete()
	else:
		raise Http404()
	return redirect(post)


def reply_delete(request, reply_id, post_id, comment_id):
	reply = get_object_or_404(Comment, id=reply_id)
	comment = get_object_or_404(Comment, id=comment_id)
	post = Post.objects.get(id = post_id)
	if (request.user != post.author) and (request.user != reply.user) and (request.user != comment.user):
		raise Http404()
	reply.delete()
	return redirect(post)


#for post likes
def like_post(request):
	post =get_object_or_404(Post, id=request.POST.get('id'))
	is_liked=False
	if post.likes.filter(id=request.user.id).exists():
		post.likes.remove(request.user)
		is_liked = False
	else:
		post.likes.add(request.user)
		is_liked = True
	context = {'post':post, 'is_liked':is_liked, 'total_likes': post.total_likes,}
	if request.is_ajax():
		html = render_to_string('blog/like.html', context, request=request)
		return JsonResponse({'form':html})

#for tagging someone
def parsing_tag(form):
	post=form.save(commit=False)
	body_list=post.body.split(' ')
	new_list=[]
	for body in body_list:
		if body.startswith('@'):
			body=body.strip('@')
			new_list.append(body)
	profiles=Profile.objects.filter(user__username__in=new_list)
	profile_dict = {}
	for profile in profiles:
		profile_dict.update({'@'+profile.user.username:profile.get_absolute_url()})
	for key, value in profile_dict.items():
		post.body = post.body.replace(key, '<a href="%s">%s</a>' % (value,key))
	post.created=datetime.now()
	return post.save()

# for creating posts
@login_required(login_url='blog:user_login')
def post_create(request):
	form=PostCreationForm()

	if request.method=="POST":
		is_media = request.FILES.get('media', False)
		if is_media != False:
			kind = filetype.guess(request.FILES['media'])
			if kind is not None and (kind.mime in File_type.image_type() or kind.mime in File_type.video_type()):
				form=PostCreationForm(data = request.POST, files = request.FILES)
				if form.is_valid():
					parsing_tag(form)	
					return redirect('blog:post_list')
				else:
					message = "The file you are trying to upload has size greater than 5 MB"
					context={'message':message}
					response = post_list(request, context)
					return response
			else:
				message = "The file you are trying to upload is not supported"
				context={'message':message}
				response = post_list(request, context)
				return response
		else:
			form=PostCreationForm(data = request.POST, files = None)
			if form.is_valid():
				parsing_tag(form)
	return redirect('blog:post_list')


# for post editting
@login_required(login_url='blog:user_login')
def post_edit(request, id):
	post = get_object_or_404(Post, id=id)
	
	if request.method == 'POST':
		is_media = request.FILES.get('media', False)
		if is_media != False:
			kind = filetype.guess(request.FILES['media'])
			if kind is not None and (kind.mime in File_type.image_type() or kind.mime in File_type.video_type()):
				form = PostEditForm(data = request.POST, instance = post, files=request.FILES)
				if form.is_valid():
					parsing_tag(form)
					messages.success(request, 'Post updated successfully.')
					return HttpResponseRedirect(post.get_absolute_url())
				else:
					messages.warning(request, 'The file you are trying to upload has size greater than 5 MB.')
					return HttpResponseRedirect(post.get_absolute_url())
			else:
				messages.warning(request, 'The file you are trying to upload is not supported.')
				return HttpResponseRedirect(post.get_absolute_url())
		else:
			form=PostCreationForm(data = request.POST, instance = post, files=request.FILES or None)
			if form.is_valid():
				parsing_tag(form)
				messages.success(request, 'Post updated successfully.')
	return HttpResponseRedirect(post.get_absolute_url())


# for post delete
@login_required(login_url='blog:user_login')
def post_delete(request, id):
	post = get_object_or_404(Post, id=id)
	if request.user != post.author:
		raise Http404()
	post.delete()
	return redirect('blog:post_list')


# To update post date-time
@receiver(post_save, sender=Comment)
def someone_commented(sender, instance, **kwargs):
	instance.post.updated = datetime.now()
	instance.post.save()
	print('signal received')


#====================================================== Account RELATED ==================================================
# for login
def user_login(request):
	if request.method == 'POST':
		form =UserLoginForm(request.POST)
		if form.is_valid():
			username = request.POST['username'].lower()
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				if request.POST.get('rememberMeCheck', None) == None:
					request.session.set_expiry(0)
				return redirect('blog:post_list')
			else:
				message = "User does not exists or password not correct. Please try again."
				context = {'form': form, 'message':message}
				return render(request, 'blog/login.html', context)
	else:
		form = UserLoginForm()
		context = {'form': form}
		return render(request, 'blog/login.html', context)


# for logout
def user_logout(request):
	logout(request)
	request.session.clear_expired()
	return redirect('blog:user_login')


# for registration
def user_registration(request):
	if request.method == "POST":
		form = UserRegistrationForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username'].lower() #Input the data from html
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			password = form.cleaned_data['password1']
			email = form.cleaned_data['email']
			user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
			user.save()
			Profile.objects.create(user = user, avatar='default/default_avatar.jpg', cover_image='default/default_cover.jpg')
			login(request, user)
			return HttpResponseRedirect(reverse('blog:edit_profile'))
	else:
		form=UserRegistrationForm()
		print(form)
	return render(request, 'blog/registration.html', {'form':form})



#====================================================== PROFILE RELATED =======================================================

# for profile
@login_required(login_url='blog:user_login')
def profile(request, username, id):

	posts = Post.objects.filter(author__id=id).order_by('-created')

	profile = get_object_or_404(Profile, user__id=id)

	comment_form = UserCommentForm()

	posts_likes = list()	
	for post in posts:
		is_liked = False
		if post.likes.filter(id=request.user.id).exists():
			is_liked = True
		posts_likes.append(is_liked)

	posts_comments=list()
	for post in posts:
		comments = Comment.objects.filter(post=post, reply=None)
		posts_comments.append(comments)

# TO RESTRICT OTHER'S PROFILE EDITTING
	if profile.user.id == request.user.id:
		access = True
	else: 
		access = False

# FOR FOLLOWERS
	is_followed=False
	if profile.follow.filter(id=request.user.id).exists():
		is_followed = True

	context = {'posts':posts,'profile':profile, 'is_followed': is_followed,
			  'total_followers': profile.total_followers, 'access':access, 'posts_comments':posts_comments,'comment_form':comment_form, 'zipped_posts':zip(posts,posts_likes,), 'total_following':profile.total_following()}
	
	# print(len(profile.user.following.all()))
	# print(profile.total_following())
	return render(request, 'blog/profile.html', context)



# for editting the profile
@login_required(login_url='blog:user_login')
def edit_profile(request):
	if request.method == 'POST':
		user_form = UserEditForm(data = request.POST or None, instance = request.user)
		profile_form = ProfileEditForm(data = request.POST or None, instance = request.user.profile, files = request.FILES) 
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			messages.success(request, 'Profile details updated successfully.')
			return HttpResponseRedirect(reverse("blog:edit_profile"))

	else:
		user_form = UserEditForm(instance = request.user)
		profile_form = ProfileEditForm(instance = request.user.profile)

	context = {
		'user_form': user_form,
		'profile_form': profile_form
	}
	return render(request, 'blog/edit_profile.html', context)



# for profile follow
def follow(request):
	profile = get_object_or_404(Profile, id=request.POST.get('id'))
	is_followed=False
	if profile.follow.filter(id=request.user.id).exists():
		profile.follow.remove(request.user)
		is_followed = False
	else:
		profile.follow.add(request.user)
		is_followed = True
	context = {'profile':profile, 'is_followed':is_followed, 'total_followers': profile.total_followers,'total_following':profile.total_following()}
	if request.is_ajax():
		html = render_to_string('blog/follow.html', context, request=request)
		return JsonResponse({'form':html})



#=================================== FOR PHOTO RELATED ================================================

# for cover photo
def photo_list(request):
	photos = Photo.objects.filter(profile_user=request.user)
	profile = get_object_or_404(Profile, user=request.user)
	
	if request.method == 'POST':
		
		form = PhotoForm(data=request.POST, files=request.FILES , instance=Photo(profile_user=request.user))
		if form.is_valid():
			form.save()
		
		photo = Photo.objects.all().last()
		Profile.objects.filter(user=request.user).update(cover_image=photo.file)
			
		return redirect(profile)

	else:
		form = PhotoForm()
	return render(request, 'blog/photo_list.html', {'form': form, 'photos': photos, 'profile':profile})


# for cover photo update
def coverUpdate(request, username, id, photo_id):
	photo = get_object_or_404(Photo, id=photo_id)
	image = photo.file 
	if request.method=='GET':
		Profile.objects.filter(user=request.user).update(cover_image=image)
		profile = get_object_or_404(Profile, user=request.user)
	return redirect(profile)

# for cover photo remove
def coverRemove(request, username, id):
	profile = get_object_or_404(Profile, user=request.user)
	image = profile.cover_image 
	if request.method=='GET':
		Profile.objects.filter(user=request.user).update(cover_image='default/default_cover.jpg')
	return redirect(profile)

# for cover photo delete
def coverDelete(request, id):
	photo = get_object_or_404(Photo, profile_user=request.user, id=id)
	if request.method == 'POST':
		photo.delete()
	return redirect('blog:photo_list')


# for profile photo
def avatar_list(request):
	avatarPhotos = AvatarPhoto.objects.filter(avatar_user=request.user)
	profile = get_object_or_404(Profile, user=request.user)
	
	if request.method == 'POST':	
		form = AvatarPhotoForm(data=request.POST, files=request.FILES, instance=AvatarPhoto(avatar_user=request.user))
		if form.is_valid():
			form.save()
		
		avatarPhoto = AvatarPhoto.objects.all().last()
		Profile.objects.filter(user=request.user).update(avatar=avatarPhoto.file)			
		return redirect(profile)
	else:
		form = PhotoForm()
	return render(request, 'blog/avatar.html', {'form': form, 'photos': avatarPhotos, 'profile':profile})

# for profile pic update
def avatarUpdate(request, username, id):
	photo = get_object_or_404(AvatarPhoto, id=id)
	image = photo.file 
	if request.method=='GET':
		Profile.objects.filter(user=request.user).update(avatar=image)
		profile = get_object_or_404(Profile, user=request.user)
	return redirect(profile)

# for profile pic delete
def avatarRemove(request, username, id):
	profile = get_object_or_404(Profile, user=request.user)
	image = profile.avatar 
	if request.method=='GET':
		Profile.objects.filter(user=request.user).update(avatar='default/default_avatar.jpg')
	return redirect(profile)

def avatarDelete(request, id):
	avatar_photo = get_object_or_404(AvatarPhoto, avatar_user=request.user, id=id)
	if request.method == 'POST':
		avatar_photo.delete()
	return redirect('blog:avatar')


def gallery(request, username):
	profile = get_object_or_404(Profile, user__username=username)
	posts = Post.objects.filter(author__username=username).order_by('-updated')
	context={'posts':posts, 'profile':profile}
	return render(request, 'blog/gallery.html', context)



#======================================= SETTINGS RELATED ================================================

#SETTINGS
def settings(request, username):
	
	return render(request, 'blog/settings.html')


def delete_profile(request):
	user = User.objects.get(username=request.user.username)
	if request.method == "POST":
		user.delete()
		return redirect('blog:user_login')


# password change
def change_password(request):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  # Important!
			messages.success(request, 'Your password is successfully updated!')
			return redirect('blog:change_password')
		else:
			messages.warning(request, 'Please correct the error below.')
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'settings/password-change.html', {
		'form': form})







