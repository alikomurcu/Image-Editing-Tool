import os
import pickle
import socket
import logging
import sys
import threading
import json
import struct
import time
from websockets.sync.server import serve
import websockets
from Graph import *
from Component import *
import queue

class Server:
	def __init__(self):
		self.userList = []     # TODO: database
		self.graphList = []    # TODO: database
		self.lock_user = threading.Lock()
		self.lock_graph = threading.Lock()
		self.lock_notifier = threading.Lock()
		self.cond_user = threading.Condition(self.lock_user)
		self.cond_graph = threading.Condition(self.lock_graph)
		self.cond_notifier = threading.Condition(self.lock_notifier)

	def add_user(self, user):
		with self.lock_user:
			for u in self.userList:
				if u.get_username() == user.get_username():
					print("User already exists")
					return False
			self.userList.append(user)
			return True

	def add_graph(self, graph): # TODO: dict
		with self.lock_graph:
			for g in self.graphList:
				if g.name == graph.name:
					print("Graph already exists")
					return False
			self.graphList.append(graph)
			self.cond_graph.notify_all()


	def remove_user(self, user):
		with self.lock_user:
			if user in self.userList:
				self.userList.remove(user)
			else:
				print("User not found")

	def remove_graph(self, graph):
		with self.lock_graph:
			if graph in self.graphList:
				self.graphList.remove(graph)
				self.cond_graph.notify_all()
			else:
				print("Graph not found")

	def get_user(self, username):   # TODO: dictionary
		with self.lock_user:
			for user in self.userList:
				if user.get_username() == username:
					return user
			return None

	def get_graph(self, name):   # TODO: dictionary
		with self.lock_graph:
			for graph in self.graphList:
				if graph.name == name:
					return graph
			return None

	def authenticate_user(self, username, password):
		user = self.get_user(username)
		if user is None:
			return False
		return user.auth(password)

	def create_node(self, graph, num, msg, username):
		num = int(num)
		if num == 1:
			component = LoadImage("Load Image")
			component.set_parameters(msg)
		elif num == 2:
			component = Crop("Crop")
			component.set_parameters(msg)
		elif num == 3:
			component = GetDimensions("Get Dimensions")
		elif num == 4:
			component = Rotate("Rotate")
			component.set_parameters(msg)
		elif num == 5:
			component = Stack("Stack")
		elif num == 6:
			component = HStack("HStack")
		elif num == 7:
			component = Scale("Scale")
			component.set_parameters(msg)
		elif num == 8:
			component = Fit("Fit")
			component.set_parameters(msg)
		elif num == 9:
			component = Stretch("Stretch")
			component.set_parameters(msg)
		elif num == 10:
			component = SaveImage("Save Image")
		elif num == 11:
			component = ViewImage("View Image")
		elif num == 12:
			component = DupImage("Dup Image")
		else:
			print("Invalid input")
			return
		graph.newnode(component, username)


	def handle_client(self, client_socket, request):
		print('Client connected')
		# print('Client authenticated')
		# serve the client requests
		# request = self.receive_message(client_socket)
		status, response = self.handle_request(request)
		# self.send_message(client_socket, response)
		client_socket.send(response)
		print("Request handled")

	def receive_message(self, socket):
		# read the size of the message (as a 4-byte integer)
		size_bytes = socket.recv(4)
		size = struct.unpack('!I', size_bytes)[0]

		# read the message data (as a JSON-encoded string)
		message_bytes = socket.recv(size)
		message = json.loads(message_bytes)

		return message


	def send_message(self, socket, message):
		# encode the message as a JSON string
		message_bytes = json.dumps(message).encode('utf-8')

		# send the size of the message (as a 4-byte integer), followed by the message data
		size_bytes = struct.pack('!I', len(message_bytes))
		socket.send(size_bytes)
		socket.send(message_bytes)

	def handle_request(self, request, suser):
		# print(request)
		username = suser.username
		# TODO: edit this section wrt demo.py methods
		# handle the request based on its type
		if request['type'] == 'logout':
			self.get_user(username).logout()
			return False, {'type': 'logout_result', 'success': True}

		elif request['type'] == 'exit':
			print('Client {} disconnected'.format(username))
			sys.exit()

		elif request['type'] == 'new':
			graph_name = request['graphname']
			graph = Graph(name=graph_name)
			self.add_graph(graph)
			return True, {'type': 'new_result', 'success': True}

		elif request['type'] == 'list':
			nameList = []
			for graph in self.graphList:
				nameList.append(graph.name)
			return True, {'type': 'list_result', 'success': True, 'graph_list': nameList}

		elif request['type'] == 'attachments':
			attachments = []
			for graph in self.graphList:
				if suser.username in graph.users:
					attachments.append(graph.name)
			suser.attachments = attachments
			return True, {'type': 'attachments_result', 'success': True, 'attachment_list': attachments}

		elif request['type'] == 'attach':
			graph_name = request['graphname']
			graph = self.get_graph(graph_name)
			mode = request['mode']
			if graph is None:
				return True, {'type': 'attach_result', 'success': False}
			with self.lock_graph:
				graph.attach(suser.username, mode)
				self.cond_graph.notify_all()
			return True, {'type': 'attach_result', 'success': True}

		elif request['type'] == 'detach':
			graph_name = request['graphname']
			graph = self.get_graph(graph_name)
			if graph is None:
				return True, {'type': 'detach_result', 'success': False}
			graph.detach(suser.username)
			return True, {'type': 'detach_result', 'success': True}

		elif request['type'] == 'open':
			graph_name = request['graphname']
			graph = self.get_graph(graph_name)
			if graph is None:
				return True, {'type': 'open_result', 'success': False}
			if suser.username in graph.users: # if attached
				suser.active_graph = graph_name
				return True, {'type': 'open_result', 'graphname': graph_name, 'success': True}
			return True, {'type': 'open_result', 'success': False}

		elif request['type'] == 'close':
			suser.active_graph = None
			return True, {'type': 'close_result', 'success': True}

		elif request['type'] == 'newnode':
			nodenum = request['nodenum']
			msg = request['msg'] # parameters
			graph = self.get_graph(suser.active_graph)
			if graph is None:
				return True, {'type': 'newnode_result', 'success': False}

			n = {'1': "Load Image", '2': 'Crop', '3': 'Get Dimensions', '4': 'Rotate', '5': 'Stack',
				 '6': 'Hstack', '7': 'Scale', '8': 'Fit', '9': 'Strectch',
				 '10': 'Save Image', '11': 'View Image', '12': 'Dup Image'}
			notification = n[nodenum] + " node created  with ID: " + str(graph.node_id)
			self.create_node(graph, nodenum, msg, suser.username)
			with self.lock_notifier:
				message_queue.append((graph.name, graph.users, notification))
				self.cond_notifier.notify_all()
			with self.lock_graph:
				self.cond_graph.notify_all()
			# print("Node created", nodenum, msg)
			return True, {'type': 'newnode_result', 'success': True}

		elif request['type'] == 'nodes':
			graphname = suser.active_graph
			graph = self.get_graph(graphname)
			if graph is None:
				return True, {'type': 'nodes_result', 'success': False}
			node_id_names = {}
			for node in graph.nodes:
				node_id_names[node.node_id] = node.name
			return True, {'type': 'nodes_result', 'success': True, 'node_id_names':node_id_names }

		elif request['type'] == 'connect':
			node1_id = request['node1_id']
			node2_id = request['node2_id']
			graphname = suser.active_graph
			graph = self.get_graph(graphname)
			if graph is None:
				return True, {'type': 'connect_result', 'success': False}
			msg = node1_id + " connected to " + node2_id
			with self.lock_notifier:
				message_queue.append((graphname, graph.users, msg))
				self.cond_notifier.notify_all()
			node1 = graph.get_node(int(node1_id))
			node2 = graph.get_node(int(node2_id))
			# print("NODE1", node1, "NODE2", node2)

			graph.connect(node1, {}, node2, {}, suser.username)
			return True, {'type': 'connect_result', 'success': True}
		elif request['type'] == 'execute':
			graphname = suser.active_graph
			graph = self.get_graph(graphname)
			if graph is None:
				return True, {'type': 'execute_result', 'success': False, 'image': None}
			retval = graph.execute()
			img_str, method = retval[-1]
			img_str = img_str.decode('utf-8')
			return True, {'type': 'execute_result', 'success': True, 'method': method, 'image': img_str}
		elif request['type'] == 'connection_establish':
			return True, {'type': 'connection_establish_result', 'success': True}
		else:
			return True, {'type': 'error', 'message': 'Unknown request type'}

	class User:
		def __init__(self):
			self.username = None
			self.active_graph = None
			self.attachments = []

	def serveconnection(self, cr, sc):
		wrtr = WRAgent(sc, cr)
		wrtr.start()
		notifier = NotifyAgent(sc, cr)
		notifier.start()
		try:
			inp = sc.recv(1024)
			inp = json.loads(inp)
			suser = self.User()
			suser.username = inp['username']
			print("started as ", suser.username)
			while inp:
				# print('received', inp)
				with open('graphs.txt', 'wb') as file:
					pickle.dump(self.graphList, file)
				# parse received message to json
				if(type(inp) == str):
					request = json.loads(inp)
				else:
					request = inp
				status, response = self.handle_request(request, suser)
				print(response)
				sc.send(json.dumps(response))
				# wrtr.chat.newmess.notify()
				cr.newmessage(request)
				# print('waiting next')
				inp = sc.recv(1024)
				# write self to file as json
			print('client is terminating')
			# wrtr.conn.close()
		except websockets.exceptions.ConnectionClosed:
			print(suser.username, 'disconnected with socket error')
			pass
			# wrtr.conn.close()
			# wrtr.terminate()

	def start(self):
		# create a socket object
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# bind the socket to a specific port on the server
		HOST = 'localhost'
		PORT = 1423
		chatroom = Chat()
		if os.path.exists('graphs.txt'):
			with open('graphs.txt', 'rb') as file:
				self.graphList = pickle.load(file)

		with serve(lambda nc: self.serveconnection(chatroom, nc), host=HOST, port=PORT,
				   logger=logging.getLogger("chatsrv")) as server:
			print("serving")
			server.serve_forever()





class NotifyAgent(threading.Thread):
	def __init__(self, conn, chat):
		self.conn = conn
		self.chat = chat
		self.current = 0
		threading.Thread.__init__(self)

	def run(self):
		notexit = True
		it = 0
		tmplist = []
		while notexit:
			try:
				with server.lock_notifier:
					server.cond_notifier.wait()
					attachments = {}
					if it >= len(message_queue):
						continue
					msg = message_queue[it]
					if msg in tmplist:
						it += 1
						continue
					tmplist.append(msg)
					it += 1
					attachments[msg[0]] = list(msg[1].keys()) + [msg[2]]
					msg = {
						'attachments': attachments,
						'type': 'notify',
						'success': True
					}
					msg = json.dumps(msg)
					self.conn.send(msg)
			except Exception as e:
				notexit = False
				print("sender thread is dead", e)
class WRAgent(threading.Thread):
	def __init__(self, conn, chat):
		self.conn = conn
		self.chat = chat
		self.current = 0
		threading.Thread.__init__(self)

	def run(self):
		global count
		global thread_number
		# oldmess = self.chat.getmessages()
		# self.current += len(oldmess)
		# self.conn.send('\n'.join([i for i in oldmess]))
		notexit = True
		# print("thread started", server.graphList)
		while notexit:
			try:
				# self.conn.send('\n'.join([i for i in oldmess]))
				with server.lock_graph:
					server.cond_graph.wait()


					nameList = []
					for graph in server.graphList:
						nameList.append(graph.name)
					graph_name_nodes = {}
					for graph in server.graphList:
						graph_name_nodes[graph.name] = []
						for node in graph.nodes:
							graph_name_nodes[graph.name].append(node.name)

					msg = {
						'graph_list': nameList,
						'graph_node_names': graph_name_nodes,
						'type': 'update',
						'success': True
					}
					msg = json.dumps(msg)
					# print("hala olmedim ecan")
					self.conn.send(msg)
			except Exception as e:
				notexit = False
				print("sender thread is dead", e)

class Chat:
	def __init__(self):
		self.buf = []
		self.lock = threading.Lock()
		self.newmess = threading.Condition(self.lock)
	def newmessage(self,mess):
		self.lock.acquire()
		self.buf.append(mess)
		self.newmess.notify_all()
		self.lock.release()
	def getmessages(self,after=0):
		self.lock.acquire()
		if len(self.buf) < after:
			a = []
		else:
			a = self.buf[after:]
		self.lock.release()
		return a

count = 0
message_queue = []
thread_number = 0
server = Server()
server.start()
