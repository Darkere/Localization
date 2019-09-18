import paho.mqtt.client as mqtt
import time
import json
import tkinter
import _thread  
anchornames = ['81a9','c032','cc8a','5bad',] 
tagnames  =  ['9631','8033','cf81']

"""Point and Rectangle classes.

This code is in the public domain.

Point  -- point with (x,y) coordinates
Rect  -- two points, forming a rectangle
"""

import math

class Point:
    
    """A point identified by (x,y) coordinates.
    
    supports: +, -, *, /, str, repr
    
    length  -- calculate length of vector to point from origin
    distance_to  -- calculate distance between two points
    as_tuple  -- construct tuple (x,y)
    clone  -- construct a duplicate
    integerize  -- convert x & y to integers
    floatize  -- convert x & y to floats
    move_to  -- reset x & y
    slide  -- move (in place) +dx, +dy, as spec'd by point
    slide_xy  -- move (in place) +dx, +dy
    rotate  -- rotate around the origin
    rotate_about  -- rotate around another point
    """
    
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
    
    def __add__(self, p):
        """Point(x1+x2, y1+y2)"""
        return Point(self.x+p.x, self.y+p.y)
    
    def __sub__(self, p):
        """Point(x1-x2, y1-y2)"""
        return Point(self.x-p.x, self.y-p.y)
    
    def __mul__( self, scalar ):
        """Point(x1*x2, y1*y2)"""
        return Point(self.x*scalar, self.y*scalar)
    
    def __div__(self, scalar):
        """Point(x1/x2, y1/y2)"""
        return Point(self.x/scalar, self.y/scalar)
    
    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)
    
    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def distance_to(self, p):
        """Calculate the distance between two points."""
        return (self - p).length()
    
    def as_tuple(self):
        """(x, y)"""
        return (self.x, self.y)
    
    def clone(self):
        """Return a full copy of this point."""
        return Point(self.x, self.y)
    
    def integerize(self):
        """Convert co-ordinate values to integers."""
        self.x = int(self.x)
        self.y = int(self.y)
    
    def floatize(self):
        """Convert co-ordinate values to floats."""
        self.x = float(self.x)
        self.y = float(self.y)
    
    def move_to(self, x, y):
        """Reset x & y coordinates."""
        self.x = x
        self.y = y
    
    def slide(self, p):
        '''Move to new (x+dx,y+dy).
        
        Can anyone think up a better name for this function?
        slide? shift? delta? move_by?
        '''
        self.x = self.x + p.x
        self.y = self.y + p.y
    
    def slide_xy(self, dx, dy):
        '''Move to new (x+dx,y+dy).
        
        Can anyone think up a better name for this function?
        slide? shift? delta? move_by?
        '''
        self.x = self.x + dx
        self.y = self.y + dy
    
    def rotate(self, rad):
        """Rotate counter-clockwise by rad radians.
        
        Positive y goes *up,* as in traditional mathematics.
        
        Interestingly, you can use this in y-down computer graphics, if
        you just remember that it turns clockwise, rather than
        counter-clockwise.
        
        The new position is returned as a new Point.
        """
        s, c = [f(rad) for f in (math.sin, math.cos)]
        x, y = (c*self.x - s*self.y, s*self.x + c*self.y)
        return Point(x,y)
    
    def rotate_about(self, p, theta):
        """Rotate counter-clockwise around a point, by theta degrees.
        
        Positive y goes *up,* as in traditional mathematics.
        
        The new position is returned as a new Point.
        """
        result = self.clone()
        result.slide(-p.x, -p.y)
        result.rotate(theta)
        result.slide(p.x, p.y)
        return result


class Rect:

    """A rectangle identified by two points.

    The rectangle stores left, top, right, and bottom values.

    Coordinates are based on screen coordinates.

    origin                               top
       +-----> x increases                |
       |                           left  -+-  right
       v                                  |
    y increases                         bottom

    set_points  -- reset rectangle coordinates
    contains  -- is a point inside?
    overlaps  -- does a rectangle overlap?
    top_left  -- get top-left corner
    bottom_right  -- get bottom-right corner
    expanded_by  -- grow (or shrink)
    """

    def __init__(self, pt1, pt2):
        """Initialize a rectangle from two points."""
        self.set_points(pt1, pt2)

    def set_points(self, pt1, pt2):
        """Reset the rectangle coordinates."""
        (x1, y1) = pt1.as_tuple()
        (x2, y2) = pt2.as_tuple()
        self.left = min(x1, x2)
        self.top = min(y1, y2)
        self.right = max(x1, x2)
        self.bottom = max(y1, y2)

    def contains(self, pt):
        """Return true if a point is inside the rectangle."""
        x,y = pt.as_tuple()
        return (self.left <= x <= self.right and
                self.top <= y <= self.bottom)

    def overlaps(self, other):
        """Return true if a rectangle overlaps this rectangle."""
        return (self.right > other.left and self.left < other.right and
                self.top < other.bottom and self.bottom > other.top)
    
    def top_left(self):
        """Return the top-left corner as a Point."""
        return Point(self.left, self.top)
        """Return the bottom-right corner as a Point."""
        return Point(self.right, self.bottom)
    
    def expanded_by(self, n):
        """Return a rectangle with extended borders.

        Create a new rectangle that is wider and taller than the
        immediate one. All sides are extended by "n" points.
        """
        p1 = Point(self.left-n, self.top-n)
        p2 = Point(self.right+n, self.bottom+n)
        return Rect(p1, p2)
    
    def __str__( self ):
        return "<Rect (%s,%s)-(%s,%s)>" % (self.left,self.top,
                                           self.right,self.bottom)
    
    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__,
                               Point(self.left, self.top),
                               Point(self.right, self.bottom))
class Location:
    def __str__(self):
        return ("x: "+str(self.x) +" y: "+ str(self.y) +" z: "+ str(self.z) +" t: "+ str(self.t))
    
    def __repr__(self):
        return ("x: "+str(self.x) +" y: "+ str(self.y) +" z: "+ str(self.z) +" t: "+ str(self.t))
    
    def __init__(self,x,y,z,t):
        self.x = round(x,2)
        self.y = round(y,2)
        self.z = round(z,2)
        self.t = t   
    def getVP(self,i):
        if i == 0:
            return self.x*20
        if i == 1:
            return self.y*20
    def getTime(self):
        return self.t
    
warning = False       
softwarning = False
tagpositions = {}
anchorpositions = {}
streetzone = Rect(Point(-1,10),Point(1,-10))
canvastags = []
canvasanchors = []
currenttags = 0
currrentanchors = 0
warn = 0
timer = 10
tags = []
anchors = []
for n in tagnames:
    tags.append('dwm/node/'+n+'/uplink/location')
for n in anchornames:
    anchors.append('dwm/node/' +n+ '/uplink/config')
    
def on_connect(client, userdata, flags, rc):
    x = []
    for n in tags:
        x.append((n,0))

    client.subscribe(x) 
    x = []
    for n in anchors:
        x.append((n,0))
    client.subscribe(x) 
    
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
            #check speed
    print(str(payload)+str(msg.topic))
    global time
    if msg.topic in tags:
        global softwarning
        global warning
        label = msg.topic[9:13]
        position = payload["position"]
        x = position["x"]
        y = position["y"]
        z = position["z"]
        if streetzone.contains(Point(x,y)):
            softwarning = True
    
        if label in tagpositions:
            deltax = tagpositions[label].x-x
            deltatime = time.time() - tagpositions[label].getTime()
            speed = deltax/deltatime
            if speed > 1:
                warning = True
        if(type(x) is str or type(y) is str or type(z) is str):
            return 
        tagpositions[label] = Location(x,y,z , time.time())
        f = open("Postion.data","a")
        f.write(label+',' + str(x)+',' +str(y)+',' +str(z)+',' +str(time.time())+'\n')
        f.close()
        
    elif msg.topic in anchors:
        config = payload["configuration"]
        position = config["anchor"]["position"]
        x = position["x"]
        y = position["y"]
        z = position["z"]
        if(type(x) is str or type(y) is str or type(z) is str):
            return
        anchorpositions[config["label"]] = Location(x,y,z, time.time()) 
        f = open("anchor.data","a")
        f.write(config["label"]+',' + str(x)+',' +str(y)+',' +str(z)+',' +str(time.time())+'\n')
        f.close()
        
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.43.222", 1883, 60)

client.loop_start()
center = 500
size = 10
root = tkinter.Tk()
root.geometry('1000x1000')

    

C = tkinter.Canvas(root, height=1000, width=1000)
def refresh():
    global currenttags 
    global currrentanchors
    global warn
    global canvasanchors
    global canvastags
    currenttags = tagpositions.__len__()
    currrentanchors= anchorpositions.__len__()
    C.delete("all")
    canvastags.clear()
    canvasanchors.clear()
    for tag,loc in tagpositions.items():
        canvastags.append( C.create_oval(center+loc.getVP(0),center+loc.getVP(1),center+loc.getVP(0)+size,center+loc.getVP(1)+size,fill="green"))
        canvastags.append( C.create_oval(center+loc.getVP(0),center+loc.getVP(1),center+loc.getVP(0)+size,center+loc.getVP(1)+size,fill="green"))
    for tag,loc in anchorpositions.items():
        canvasanchors.append( C.create_rectangle(center+loc.getVP(0),center+loc.getVP(1),center+loc.getVP(0)+size,center+loc.getVP(1)+size,fill="red"))
        canvasanchors.append( C.create_rectangle(center+loc.getVP(0),center+loc.getVP(1),center+loc.getVP(0)+size,center+loc.getVP(1)+size,fill="red"))
    warn = C.create_text(center,50,text="WARNING",fill="red",font=("Times New Roman",50))
    print("refreshed")
refresh()

C.pack()
def task():
    global timer
    global warning
    global softwarning
    refresh()
    C.create_rectangle(center+streetzone.left*50,center+streetzone.top*50,center+streetzone.right*50,center+streetzone.bottom*50)
    if (currenttags != tagpositions.__len__() or currrentanchors != anchorpositions.__len__()):
        refresh()
    if warning:
        C.itemconfig(warn,text="TOO FAST")
        if timer <1:
            warning = False
            timer = 10
        else:
            timer = timer-1
    elif softwarning:
        C.itemconfig(warn,text="IN STREETZONE")
        if timer <1:
            softwarning = False
            timer = 10
        else:
            timer = timer-1
    else:
        C.itemconfig(warn,text="zzz")
    i =0
    for tag,loc in tagpositions.items():
        if canvastags:        
            C.coords(canvastags[i],center+loc.getVP(0),center+loc.getVP(1),center+loc.getVP(0)+size,center+loc.getVP(1)+size)
            ++i
    i= 0
    for tag,loc in anchorpositions.items():
        if canvasanchors:
            C.coords(canvasanchors[i],center+loc.getVP(0),center+loc.getVP(1),center+loc.getVP(0)+size,center+loc.getVP(1)+size)
            ++i
    root.after(100, task)
root.after(100, task)
root.mainloop()
