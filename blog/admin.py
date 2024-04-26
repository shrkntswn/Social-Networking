from django.contrib import admin
from .models import Post, Profile, Comment, Photo, AvatarPhoto, Notification

"""
customize the admin panel
"""
'''class PostAdmin(admin.ModelAdmin):
	list_display = ('author', 'status')
	list_filter  = ('status', 'created', 'updated')
	search_fields = ('author_username', 'title')
	#prepopulated_fields = {'slug':('title',)}
	#list_editable = ('status',)
	date_hierarchy = 'created'''

class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'birthday', 'avatar')

admin.site.register(Post)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Comment)
admin.site.register(Photo)
admin.site.register(AvatarPhoto)
admin.site.register(Notification)
