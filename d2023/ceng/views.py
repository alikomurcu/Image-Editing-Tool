from django.shortcuts import render, redirect
from django.http import HttpResponse
from ceng.models import *

import socket
import json
import struct

import hashlib as hl
import secrets
import uuid

import sys
# Create your views here.
# def hello(request):
# 	# return HttpResponse("<body> <h1> Hello World </h1> </body>")
# 	questions = Question.objects.all()
# 	return render(request, "hello.html", {'name': 'Ecan', 'surname': 'kops',
# 										 'questions': questions,
# 										 'post': request.POST,
# 										 'tasks':
# 											['odevyap',
# 											'projeyap']})

# def newquestion(request):
# 	q = Question()
# 	q.text = request.POST['text']
# 	q.name = request.POST['name']
# 	q.surname = request.POST['surname']
# 	q.save()
# 	return redirect("/")
#
# def newanswer(request):
# 	qid = request.POST['question']
# 	q = Question.objects.get(id=qid)
# 	a = Answer()
# 	a.text = request.POST['text']
# 	a.name = request.POST['name']
# 	a.surname = request.POST['surname']
# 	a.question = q
# 	a.save()
# 	return redirect("/")

def connect_socket():
	# create a socket object and connect to the server
	global client_socket
	server_address = ('localhost', 1423)
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect(server_address)
	return client_socket

def receive_message(socket):
	# read the size of the message (as a 4-byte integer)
	size_bytes = socket.recv(4)
	size = struct.unpack('!I', size_bytes)[0]

	# read the message data (as a JSON-encoded string)
	message_bytes = socket.recv(size)
	message = json.loads(message_bytes)

	return message

def send_message(socket, message):
	# encode the message as a JSON string
	message_bytes = json.dumps(message).encode('utf-8')

	# send the size of the message (as a 4-byte integer), followed by the message data
	size_bytes = struct.pack('!I', len(message_bytes))
	socket.send(size_bytes)
	socket.send(message_bytes)

def websocket(request):
	return render(request, "websocket.html", {'username': request.session['username']})


def nodeparams(request):
	global client_socket
	global active_graph

	# set node_id to last created Node object in database
	node_id = Nodes.objects.last().id
	msg = ""
	for key in request.POST:
		if key not in ['csrfmiddlewaretoken', 'cid']:
			msg += request.POST[key] + " "
	send_message(client_socket, {'type': 'newnode', 'node_id':node_id, 'nodenum': request.POST['cid'], 'graphname': activegraph.name, 'msg': msg})	# TODO: active graph
	response = receive_message(client_socket)
	if response['type'] == 'newnode_result' and response['success']:
		print('Node created successfully')
	else:
		print('Failed to create node')
	return render(request, "hello.html")


def newnode(request):
	global activegraph
	n = Nodes()
	graphs = Graph.objects.all()

	n.component = request.POST['components']
	n.graph = Graph.objects.get(name=activegraph.name)	# TODO: active graph
	n.save()

	component_dict = {'1': ["image"],
					  '2': ['x', 'y', 'w', 'h'],
					  '3': [],
					  '4': ['angle'],
					  '5': ['image1', 'image2'],
					  '6': ['image1', 'image2'],
					  '7': ['scale'],
					  '8': ['width', 'height'],
					  '9': ['width', 'height'],
					  '10': ['path'],
					  '11': ['image'],
					  '12': ['image'],
					  }

	return render(request, "hello.html", {'post': request.POST,
										  'cid': n.component,
										  'inputs': component_dict[n.component]})

def newgraph(request):
	global client_socket
	g = Graph()
	g.name = request.POST['name']
	g.save()
	username = request.session['username']

	gU = GraphUser()
	gU.graph = g
	gU.user = User.objects.get(username=username)
	gU.save()

	print("username: ", username)
	print("mode: ", request.POST['graphtype'].strip())
	send_message(client_socket, {'type': 'new', 'graphname': g.name, 'mode': request.POST['graphtype']})
	response = receive_message(client_socket)
	return render(request, "hello.html")

def connect(request):
	global client_socket
	global activegraph
	id1 = request.POST['node1']
	id2 = request.POST['node2']

	send_message(client_socket, {'type': 'connect', 'graphname': activegraph.name, 'node1_id': id1, 'node2_id': id2})
	response = receive_message(client_socket)
	if response['type'] == 'connect_result' and response['success']:
		print('Connected successfully')
	else:
		print('Failed to connect')
	return render(request, "hello.html")

def opengraph(request):
	global client_socket
	global activegraph
	activegraph = Graph.objects.get(name=request.POST['graphname'])
	send_message(client_socket, {'type': 'open', 'graphname': activegraph.name})
	response = receive_message(client_socket)
	if response['type'] == 'open_result' and response['success']:
		print('Graph opened successfully')
	else:
		print('Failed to open graph')
	return render(request, "hello.html")


def listnodes(request):
	nodes = Nodes.objects.all()
	return render(request, "hello.html", {'nodes': nodes})

def list(request):
	graphs = Graph.objects.all()
	return render(request, "hello.html", {'graphs': graphs})

def homepage(request):
	if 'username' not in request.session:
		return redirect("/")
	global client_socket
	client_socket = connect_socket()
	# check if user is authanticated
	return render(request, "websocket.html", {'username': request.session['username']})

def handle_login(request):
	username = request.POST['username']
	password = request.POST['password']
	try:
		user = User.objects.get(username=username)
	except:
		return render(request, "login.html", {'error': 'Username or password is wrong'})
	if user.password == hash_password(username, password):
		# set username to session
		request.session['username'] = username
		# set session cookie to expire in 5 minutes
		return redirect("/home")

	else:
		return redirect("/login")
		# return render(request, "login.html", {'error': 'Username or password is wrong'})

def login(request):
	return render(request, "login.html")

def handle_register(request):
	username = request.POST['username']
	password = request.POST['password']
	try:
		user = User.objects.get(username=username)
	except:
		user = User()
		user.username = username
		user.password = hash_password(username, password)
		user.save()
		return render(request, "login.html")
	return render(request, "register.html", {'error': 'Username already exists'})

def register(request):
	return render(request, "register.html")

def auth(request):
	return render(request, "auth.html")


def hash_password(username, password):
	password = password + username  # stronger by concatenating the plainpwd with the username
	return hl.sha256(password.encode()).hexdigest()

def logout(request):
	request.session.flush()
	return render(request, "auth.html")

def execute(request):
	global client_socket
	global activegraph
	send_message(client_socket, {'type': 'execute', 'graphname': activegraph.name})
	response = receive_message(client_socket)
	if response['type'] == 'execute_result' and response['success']:
		print('Graph executed successfully')
	else:
		print('Failed to execute graph')
	return render(request, "hello.html")