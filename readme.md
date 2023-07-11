**Welcome to the Demo of the graph editor Phase 4.**

This project is a demo of the term project for the course CENG445:Software Development With Scripting Languages.

We created an app which contains a backend Server which communicates to the Django App through websockets.
It contains all the necessary components as nodes which provided to us.
    
    1 Load Image
    2 Crop
    3 Get Dimensions
    4 Rotate
    5 Stack
    6 HStack
    7 Scale
    8 Fit
    9 Stretch
    10 Save Image
    11 View Image
    12 Dup Image
        
You can apply above operations as a Graph Based Structure to Images.

We created Server and Django App communication along with the components and necessary commands for the project. These are:

    Serverweb.py and The Django App


All components and methods are implemented in Server-App communication level which is websockets.

new - list - open - close commands are implemented in the described way and works fine.

new : Creates a new Graph.

list : Lists all the available Graphs in the system.

open : opens the Graph, set active_graph for User to desired Graph.

close : closes the Graph in active_graph, set active_graph to None.

We use a hybrid system that uses the powers of Django and websockets.

`Django views.py` handles authentication with session handling.

`Serverweb.py` includes the Server side of the system.

`Front end` does the job for a user which wants to use the application. When a Client connects localhost port 8000, a new thread begins from `Serverweb.py` to handle its requests.

We used all the methods that we created in the Phase 1. All the components is runnable and exists in the Server side.

** Usage **

First, run 'Serverweb.py', then run The Django App using 'python3 manage.py runserver' command.

In the Server side you will see a 'connection successful' message whenever a User connects.

**Authentication** is also handled by our Django App,
whenever a user reach to our server, he/she needs to login before doing any operation. He/She can not
reach to any other page in our application without logging in.

There is also **Notification System** which notifies the Users attached to that Graph whenever
a change is made.
And when a new graph is added, all the users can see the new graphs immediately.
Also same logic applies for the nodes of the opened graph, namely, if new nodes are added to the graph, users that opened that graph can see the current list of nodes immediately.

_By stating immediately, we mean that without need a page reload_

**As a User**

Your first request can be either '**login**' or '**signup**' **(you are not allowed to do anything else without logging in)**, since you can not create a graph without logged in.


**Specifications:**

* While arranging the connections, be careful; The first Node should be Load Image, and the last Node should be either Save Image or View Image ! (You should at least provide one these two.)
* Otherwise, the Execute Button **will not** work or give an error.

Ali Kömürcü

Emre Can Koparal
