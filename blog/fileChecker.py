from django.core.exceptions import ValidationError


def file_size(value): # add this to some file where you can import it from
	limit = 5 * 1024 * 1024
	if value.size > limit:
		raise ValidationError('File too large. Size should not exceed 5 MiB.')

class File_type():
	def image_type():
		image_list = ['image/jpeg','image/jpx','image/png','image/gif','image/webp','image/x-canon-cr2','image/tiff','image/bmp','image/vnd.ms-photo','image/vnd.adobe.photoshop','image/x-icon','image/heic']
		return image_list
	def video_type():
		video_list = ['video/mp4','video/x-m4v','video/x-matroska','video/webm','video/quicktime','video/x-msvideo','video/x-ms-wmv', 'video/mpeg','video/x-flv']
		return video_list