from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	pass

class Profile(models.Model):

	user = models.ForeignKey("User", on_delete=models.CASCADE, related_name= "profile_user")
	followers = models.ManyToManyField('User', symmetrical=False, related_name = "followers", blank = True)

	def user_return(self):
		return {
			"id": self.id,
			"email": self.user.email,
			"followers": [user.username for user in self.followers.all()]
		}
    

class Post(models.Model):
	author = models.ForeignKey("User", on_delete= models.CASCADE, related_name = "author")
	content = models.TextField()
	likes = models.ManyToManyField('User', related_name = "likes", blank = True)
	timestamp = models.DateTimeField(auto_now_add=True)
	

	def post_return(self):
		return {
			"author": self.author,
			"content": self.content,
			"likes": [user.username for user in self.likes.all()],
			"timestamp": self.timestamp,
			"modtimestamp": self.modtimestamp,
		}
