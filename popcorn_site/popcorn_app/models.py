from django.db import models

class Actor(models.Model):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)

	def __unicode__(self):
		return self.first_name + ' ' + self.last_name

class Film(models.Model):
	title = models.CharField(max_length=100)
	actor_id = models.ForeignKey(Actor)
	genre = models.CharField(max_length=100)
	keyword = models.CharField(max_length=100)
	description = models.CharField(max_length=500)

	def __unicode__(self):
		return self.title
	
