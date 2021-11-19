from tkinter import *
from tkinter import ttk
from Frames import ToggledFrame, ScrollableFrame
import colorsys

nPoint = 5 #no. of points
Points = [ [901, 36], [780, 450], [385, 152], [273, 214], [200, 450] ] #default points
daPoints = [] #instance of daPoint class
Bezt = 0.28 #defalut t in bezier curve

bezt = None
beztslider = None

cplabel = [] #control point label
entryP = [] #control point input field (Entry)

Ch = 1000 #canvas height
Cw = 1500 #canvas width
Fh = 500 #frame height
Fw = 1200 #frame width

root = Tk()
root.title('bezier curve')
frame = Frame(root)
frame.pack(expand=True, fill='both', side='left')

sideframe = ScrollableFrame(frame)
sideframe.canvas.configure(width=150)
sideframe.pack(expand=True, fill='y', side='right')

C = Canvas(frame, bg='#f5f9ff', width = Fw, height = Fh, scrollregion=(0,0,Cw,Ch))
hbar = Scrollbar(frame, orient=HORIZONTAL, command= C.xview)
hbar.pack(side='bottom', fill='x')
vbar = Scrollbar(frame, orient='vertical', command= C.yview)
vbar.pack(side='right', fill='y')
C.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
C.pack(side='left', expand=True, fill='both')

#collapsable frame for control point
cpointframe = None
#collapsable frame for intermidate point
ipointframe = None

def create_grid(event=None):
    """config grid on canvas"""
    global C, Cw, Ch
    w = Cw # Get current width of canvas
    h = Ch # Get current height of canvas
    C.delete('grid_line') # Will only remove the grid_line

    # Creates all vertical lines at intevals of 100
    for i in range(0, w, 100):
        C.create_line([(i, 0), (i, h)], tag='grid_line')

    # Creates all horizontal lines at intevals of 100
    for i in range(0, h, 100):
        C.create_line([(0, i), (w, i)], tag='grid_line')


class daPoint:
    """drag able point"""
    rad = 10 #radius of point
    _drag_data = {"x": 0, "y": 0, "item": None} #drag data of current object

    def __init__(self,C, p, extoken):
        """canvas object, point, extoken = f'P{i}'"""
        rad = daPoint.rad
        self.extag = extoken
        self.canvas_obj =  C.create_oval(p[0]-rad, p[1]-rad, p[0]+rad, p[1]+rad, 
                            width = 1, tags=('token',extoken), outline='blue', fill='red')
    
    def remove(self):
        """remove this point from screen"""
        global nPoint, C
        i = nPoint - 1
        C.delete(self.extag)

    def get_coords(self):
        """get coords (x, y) by equating bounding box of tinkter object"""
        global C
        loc = C.coords(self.canvas_obj)
        return [int((loc[0]+loc[2])/2), int((loc[1]+loc[3])/2)]
    
    def move(self, p):
        """move point to given point"""
        global C
        curr_pos = self.get_coords()
        C.move(self.canvas_obj, p[0] - curr_pos[0], p[1] - curr_pos[1])
    
    def drag_start(event):
        """Begining drag of an object"""
        global C
        # record the item and its location
        item = C.find_closest(C.canvasx(event.x), C.canvasy(event.y))[0]
        if 'token' not in C.gettags(item):
            return
        daPoint._drag_data["item"] = item
        daPoint._drag_data["x"] = event.x
        daPoint._drag_data["y"] = event.y

    def drag_stop(event):
        """End drag of an object"""
        global C
        # reset the drag information
        daPoint._drag_data["item"] = None
        daPoint._drag_data["x"] = 0
        daPoint._drag_data["y"] = 0

    def drag(event):
        """Handle dragging of an object"""
        global C
        if daPoint._drag_data["item"] == None:
            return
        # compute how much the mouse has moved
        delta_x = event.x - daPoint._drag_data["x"]
        delta_y = event.y - daPoint._drag_data["y"]
        # move the object the appropriate amount
        C.move(daPoint._drag_data["item"], delta_x, delta_y)
        # record the new position
        daPoint._drag_data["x"] = event.x
        daPoint._drag_data["y"] = event.y
        recompute_gui()


def add_ctrl_point():
    """add new ctrl point label and entry in toggled frame"""
    global entryP, cplabel, sideframe, Points, cpointframe
    i = len(entryP)
    parentframe = cpointframe.sub_frame
    cplabel.append(Label(parentframe, text=f'P{i}'))
    cplabel[-1].pack()
    entryP.append(Entry(parentframe))
    entryP[-1].insert(0, f'{Points[i][0]} {Points[i][1]}')
    entryP[-1].pack()

def pop_ctrl_point():
    """remove last ctrl point from toggle frame"""
    global entryP, cplabel
    i = len(entryP)-1
    cplabel[i].destroy()
    cplabel.pop()
    entryP[i].destroy()
    entryP.pop()

def clear_all_ipoint():
    """clear all intermidate point in collapsable frame"""
    global ipointframe
    parentframe = ipointframe.sub_frame
    for child in parentframe.winfo_children():
        child.destroy()

def add_ipoint(q):
    """add intermidate point q to collapsable frame"""
    global ipointframe
    parentframe = ipointframe.sub_frame
    Label(parentframe, text=f'( {q[0]:.2f} , {q[1]:.2f} )').pack()

def add_ipoint_label(k, color):
    """add intermidate point label representing level of subdivison"""
    global ipointframe
    parentframe = ipointframe.sub_frame
    Label(parentframe, text=f'Subdivision {k}').pack()
    Label(parentframe, text=f'::::', bg=color).pack(side='top')
    

def slidercallback(val):
    """callback function when slider is moved, whole bezier curve is redrawn"""
    global Bezt
    val = float(val)
    Bezt = val
    bezt.delete(0, 'end')
    bezt.insert(0, f'{val}')
    draw_bezier()


def recompute_gui():
    """sync data by copying dragable points location to input fields,
        called by dragable point when control point is moved
    """
    global nPoint, daPoints, Points, entryP, Bezt, bezt
    #take user input from GUI (red draggable points)
    for i in range(nPoint):

        Points[i] = daPoints[i].get_coords()
        entryP[i].delete(0, 'end')
        entryP[i].insert(0, f'{Points[i][0]} {Points[i][1]}')
    
    Bezt = float(bezt.get())
    #draw bezier curve
    draw_bezier()


def compute():
    """sync data by copying data from input fields,
        called on compute button press
    """
    global nPoint, Points, entryP, Bezt, bezt, beztslider
    #take user input from input fields
    for i in range(nPoint):
        Points[i] = list(map(int, entryP[i].get().split()))
        daPoints[i].move(Points[i])
    Bezt = float(bezt.get())
    beztslider.set(Bezt)
    #draw bezier curve
    draw_bezier()

def draw_point(C, x, y, color = 'black'):
    """draw point on canvas"""
    C.create_oval(x-4, y-4, x+4, y+4, width = 1, outline = 'black', fill = color)

def draw_intermediate_point(a, b, t, color='black'):
    """draw intermidate point on line defined by point a to b with t"""
    x = (1-t)*a[0]+t*b[0]
    y = (1-t)*a[1]+t*b[1]
    draw_point(C, x, y, color)
    return [x,y]

def hsv_to_hex(h, s, v):
    """translates an hsv value in range[0,1] to a hexadecimal color code"""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r, g, b = int(255*r), int(255*g), int(255*b)
    return f'#{r:02x}{g:02x}{b:02x}'


def draw_bezier():
    """computes and draw bezier curve on canvas"""
    global C, nPoint, Points, Bezt
    #clear canvas
    C.delete("!token&&!grid_line") #remove all except daPoint and grid_lines
    
    #init control polygon points
    p = Points
    deg = nPoint - 1 #degree of curve

    #draw control polygon
    for i in range(deg):
        C.create_line(*p[i], *p[i+1], fill='black', width=1)
    
    #subdivide at t
    t = Bezt
    #init intermidiate points for subdivision at t
    clear_all_ipoint()
    q = [p,[]] #two buffers swapped alternatively
    for j in range(deg):
        q0 = q[j&1] #q0 is for read
        q1 = q[1-(j&1)] = [] #assign new list

        sub_color = hsv_to_hex((j+1)/deg, 0.9, 0.9) if j!=0 else 'grey'
        
        add_ipoint_label(j+1, sub_color)

        for i in range(len(q0)-1):
            ipoint = draw_intermediate_point(q0[i], q0[i+1], t, sub_color)
            add_ipoint(ipoint)
            q1.append(ipoint)
        
        for i in range(len(q1)-1):
            C.create_line(*q1[i], *q1[i+1], fill= sub_color, width=2)

    #draw curve
    # Start x and y coordinates from t = 0 to t = 1
    x_start, y_start = p[0]
    n = 100
    for i in range(n+1):
        t = i / n
        x, y = 0, 0
        coff = 1 #cofficient
        for i in range(nPoint):
            coff *= (deg-i+1)/i if i!=0 else 1
            comm = coff*((1-t)**(deg-i))*(t**i)
            x += comm*p[i][0]
            y += comm*p[i][1]
        x = int(x)
        y = int(y)
        C.create_line(x, y, x_start, y_start, fill='red', width=3)
        
        # updates initial values
        x_start = x
        y_start = y
    #raise daPoint
    C.tag_raise('token')


def raise_degree():
    """degree elevation on curve"""
    global nPoint, Points, daPoints, entryP, C, root
    old_point = [x.copy() for x in Points] #make deep copy

    for i in range(1, nPoint): #skip first point
        Points[i][0] = int((i/nPoint)*old_point[i-1][0] + ((nPoint-i)/nPoint)*old_point[i][0])
        Points[i][1] = int((i/nPoint)*old_point[i-1][1] + ((nPoint-i)/nPoint)*old_point[i][1])
        daPoints[i].move(Points[i])
    Points.append(old_point[-1])
    daPoints.append(daPoint(C, old_point[-1], f'P{nPoint}'))
    daPoints[-1].move(old_point[-1])
    
    add_ctrl_point()
    nPoint += 1
    recompute_gui()

def helper_reduce_degree_approx(newPoint):
    """takes list of new reduced degree Points and set all variable"""
    global nPoint, Points, daPoints, entryP, C, root
    if nPoint == 2:
        return
    Points = newPoint
    daPoints[-1].remove()
    daPoints.pop()
    for i in range(len(Points)):
        daPoints[i].move(Points[i])

    pop_ctrl_point()
    nPoint -= 1
    recompute_gui()

def reduce_degree():
    """remove last point from curve, 
    TODO: curve approximation can be implemented
    """
    global nPoint, Points, daPoints, entryP, C, root
    if nPoint == 2:
        return
    Points.pop()
    daPoints[-1].remove()
    daPoints.pop()
    
    pop_ctrl_point()
    nPoint -= 1
    recompute_gui()

def approx_reduce():
    """reduce degree by formula"""
    global nPoint, Points
    if nPoint == 2:
        return

    n = nPoint-1 #degree = n = total_control_points - 1
    e = [[0.0, 0.0]] #stores ei for i = [0, n-1]
    nCi = [1] #stores nCi for i = [0, n]
    
    #compute nCi
    for i in range(1, n+1): #i = [1, n]
        nCi.append((nCi[-1]*(n-i+1))//i)
    
    sumnCi2 = 0 #stores summation((nCi)**2) for i = [1, n-1]
    for i in range(1, n):
        sumnCi2 += nCi[i]**2
    
    sumSnCiPi = [0.0, 0.0] #stores summation((-1)**(n-i)*(nCi)*Pi) for i = [0, n]
    for i in range(0, n+1):
        sign = -1 if (n-i)&1 else 1 #(-1)**(n-i)
        coff = sign*nCi[i]
        sumSnCiPi = [coff*Points[i][0]+sumSnCiPi[0], coff*Points[i][1]+sumSnCiPi[1]]
        
    #compute ei = -((-1)**(n-i))*(nCi)*(sumSnCiPi/sumnCi2)
    for i in range(1, n):
        sign = -1 if (n-i)&1 else 1 #(-1)**(n-i)
        ei = -(sign*nCi[i])/sumnCi2
        e.append([sumSnCiPi[0]*ei, sumSnCiPi[1]*ei])
    
    #compute new reduced points
    newPoint = [Points[0]]
    for i in range(1, n): #for i = [1, n-1]
        f1 = n/(n-i)
        f2 = i/(n-i)
        f1 = [f1*(Points[i][0]+e[i][0]), f1*(Points[i][1]+e[i][1])]
        
        f2 = [f2*newPoint[i-1][0], f2*newPoint[i-1][1]]
        newPoint.append([int(f1[0]-f2[0]), int(f1[1]-f2[1])])
    
    helper_reduce_degree_approx(newPoint)

def init_window():
    """init widgets and configure canvas"""
    global C, sideframe, nPoint, Points, Bezt, daPoints, bezt, beztslider, cpointframe, ipointframe
    
    #button to raise degree
    Button(sideframe.scrollable_frame, text='Raise Degree', command=raise_degree).pack(pady = 10)

    #button to approx reduce degree
    Button(sideframe.scrollable_frame, text='Reduce Degree Approx', command=approx_reduce).pack(pady = 10)

    #button to reduce degree by removing last point
    Button(sideframe.scrollable_frame, text='Remove Last Point', command=reduce_degree).pack(pady = 10)

    #constructing slider
    Label(sideframe.scrollable_frame, text="t[0,1]").pack()
    bezt = Entry(sideframe.scrollable_frame)
    bezt.insert(0, f'{Bezt}')
    bezt.pack()

    beztslider = Scale(sideframe.scrollable_frame, from_=0.0, to=1.0,orient='horizontal',
                        resolution=0.001, variable=Bezt, command=slidercallback)
    beztslider.set(Bezt)
    beztslider.pack(fill='both', expand=True)

    #compute button
    Button(sideframe.scrollable_frame, text='Compute', command=compute).pack(pady=10)

    cpointframe = ToggledFrame(sideframe.scrollable_frame, text='Control Point', relief="raised", borderwidth=1)
    cpointframe.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

    for i in range(nPoint):
        add_ctrl_point()

    ipointframe = ToggledFrame(sideframe.scrollable_frame, text='Intermidate Point', relief="raised", borderwidth=1)
    ipointframe.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

    #create drag able point
    for i in range(nPoint):
        daPoints.append(daPoint(C, Points[i], f'P{i}'))

    C.tag_bind("token", "<ButtonPress-1>", daPoint.drag_start)
    C.tag_bind("token", "<ButtonRelease-1>", daPoint.drag_stop)
    C.tag_bind("token", "<B1-Motion>", daPoint.drag)
    C.bind('<Configure>', create_grid)



def main():
    #driver code
    frm = ttk.Frame(root, padding=10)
    frm.pack()

    init_window()

    #init curve
    compute()
    
    root.mainloop()
    
    
if __name__ == '__main__':
    main()