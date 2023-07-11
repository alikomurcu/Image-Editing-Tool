from django.db import models

# Create your models here.
class Graph(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	name = models.CharField(max_length=128)
	def __str__(self):
		return self.name

class Nodes(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	component = models.CharField(max_length=512)	# component type: LoadImage, Crop, ...
	graph = models.ForeignKey(Graph, on_delete=models.CASCADE)	# one to many
	def __str__(self):
		return self.component

class User(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	username = models.CharField(max_length=128, primary_key=True)
	password = models.CharField(max_length=128)
	def __str__(self):
		return self.username

class GraphUser(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	graph = models.ForeignKey(Graph, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	def __str__(self):
		return self.graph.name + ' ' + self.user.username