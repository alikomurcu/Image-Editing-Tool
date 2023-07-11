class Node:
    def __init__(self, name, componenttype, node_id, params):
        self.name = name
        self.componenttype = componenttype #pointer to component
        self.params = params
        self.node_id = node_id

    def __str__(self):
        return str(self.name)


class Graph:
    node_id = 0

    def __init__(self, name="", callback=None):
        self.nodes = {}
        self.connections = {}
        self.name = name    # name of the graph
        self.users = {}    # relationship between user and graph is many to many TODO: database
        self.callback = None
        self.edited = None
        # TODO: callback bir liste olur, her biri bir user olur bunlari degisiklik olunca notify eder

    def attach(self, username, mode, callback=None):
        if username not in self.users:
            self.users[username] = mode     # append user to graph's users
            self.callback = callback
        else:
            print("User is already attached to this graph")

    def detach(self, user):
        if user in self.users:
            self.users.remove(user)     # remove user from graph's users
            self.callback = None
        else:
            print("User is not attached to this graph")

    def newnode(self, componenttype, username):
        if self.users[username] == 'rw':
            print("I am here nwnode")
            newnode = Node(componenttype.name, componenttype, self.node_id, {})        # ISSUE: how to create a new node?
            self.node_id += 1
            print("newnode: ", newnode)
            if newnode not in self.nodes:
                self.nodes[newnode] = []  # nodes[node] is a adjacency list
            print("selfnodes", self.nodes)
            # self.callback()
        else:
            print("You don't have permission to do this operation")

    def connect(self, node1, outport, node2, inport, username):
        if self.users[username] == 'rw':
            # if there is no nodes, create
            # if node1 not in self.nodes:
            #     self.newnode(node1)
            # if node2 not in self.nodes:
            #     self.newnode(node2)

            self.nodes[node1].append(node2)     # add node2 to node1's adjacency list
            self.connections[(node1, node2)] = (outport, inport)    # add directed edge to connections

            # self.callback()
        else:
            print("You don't have permission to do this operation")

    def disconnect(self, node1, outport, node2, inport, username):
        if self.users[username] == 'rw':
            if node1 not in self.nodes:
                print("Node1 does not exist")
                return
            if node2 not in self.nodes:
                print("Node2 does not exist")
                return
            self.nodes[node1].remove(node2)     # remove node2 from node1's adjacency list
            del self.connections[(node1, node2)]    # remove directed edge from connections

            # self.callback()
        else:
            print("You don't have permission to do this operation")

    def get_node(self, node_id):
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    def isvalid(self):
        # check if graph is valid
        # check if there is a cycle
        # TODO: check if the graph is connected
        visited = {}
        for component in self.nodes:
            visited[component] = False
        for component in self.nodes:
            if not visited[component]:
                if self.is_cyclic_util(component, visited, -1):
                    return False
        return True

    def is_cyclic_util(self, v, visited, parent):       # ISSUE: test this function
        visited[v] = True
        for i in self.nodes[v]:
            if not visited[i]:
                if self.is_cyclic_util(i, visited, v):
                    return True
            elif i != parent:
                return True
        return False

    def runparams(self):
        # TODO: check here
        queue = []
        # traverse all nodes
        for node1,node2 in self.connections.keys():
            queue.append(node1)

        queue.append(list(self.connections.keys())[-1][1])

        if not queue[0].name == "Load Image":
            print("Load Image Component is needed and should be the first component")
            return False
        if not (queue[-1].name == "Save Image" or queue[-1].name == "View Image") :
            print("Save Image or View Image Component is needed and should be the last component")
            return False

        for node in queue:
            print("For the",node.name,"node;",node.componenttype.inputs_types,"are the needed inputs")

        return True

    def execute(self):
        # traverse the graph and execute each component
        visited = {}
        result = []
        # traverse with BFS
        queue = []
        for node in self.nodes:
            if node.componenttype.name == "Load Image":
                queue.append(node)
        while queue:
            node = queue[0]
            del queue[0]
            if node not in visited:
                visited[node] = True
                if node.componenttype.name in ["Stack", "HStack"]:
                    if "Image" not in node.componenttype.inports.keys() and "Image2" not in node.componenttype.inports.keys():
                        print("Stack Component needs two images")
                        # queue.append(node)
                        continue
                result.append(node.componenttype.execute())
                for i in self.nodes[node]:
                    if i.componenttype.name in ["Stack", "HStack"]:
                        if "Image" not in i.componenttype.inports.keys():
                            i.componenttype.inports["Image"] = node.componenttype.outports["Image"]
                        else:
                            i.componenttype.inports["Image2"] = node.componenttype.outports["Image"]
                    else:
                        i.componenttype.inports = node.componenttype.outports
                    if i not in queue:
                        queue.append(i)

        return tuple(result)

    def getcomponenttypes(self):
        #traverse nodes and print component types with their descriptions
        for node in self.nodes:
            try:
                print(node.componenttype.name, node.componenttype.description)
            except:
                print("Component type is not defined for this node", node.name)

    def __str__(self):
        return str(self.graph)
