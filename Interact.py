class GaussAdjuster:
    # Messages to show during the lifetime of the adjuster
    messages = {
        "left_point" : "Seleccione el punto izquierdo",
        "right_point" : "Seleccione el punto derecho",
        "ready" : "Listo para hacer el ajuste"
        }
 
    # Initialization of object, set variables needed to calculate adjustment and
    # bind THIS object to the "button_press_event" event, making this object the
    # "event handler"
    def __init__(self, figure):
        self.figure = figure
        self.left_point = None
        self.right_point = None
        self.center_point = None
        self.message =  GaussAdjuster.messages["left_point"]
        print self.message
        self.ready = False
        self.connection_id = self.figure.canvas.mpl_connect('button_press_event', self)

    # this function is called whenever the event connected on __init__ is called
    def __call__(self, event):
        if self.left_point == None:
            self.left_point = {"x": event.xdata, "y" : event.ydata}
            self.message = GaussAdjuster.messages["right_point"]
            print self.message

        elif self.right_point == None:
            self.right_point = {"x": event.xdata, "y" : event.ydata}
            self.message = GaussAdjuster.messages["ready"]
            print self.message
 
#        elif self.center_point == None:
#            self.center_point = {"x": event.xdata, "y" : event.ydata}
#            self.message = GaussAdjuster.messages["ready"]
#            print self.message

            if self.validates():
                #all data is correct, ready to make adjustment
                self.ready = True
                self.figure.canvas.mpl_disconnect(self.connection_id)
                self.makeAdjustment()
            else:
                #user entered invalid data, reset internal state
                self.reset()

    # returns true or false, set validation rules here
    def validates(self):
        # TODO: return messages for each validation
        if self.left_point["x"] >= self.right_point["x"]:
            return False
#        elif self.center_point["x"] <= self.left_point["x"] or self.center_point["x"] >= self.right_point["x"]:
#            return False
        else:
            return True

    # makes gaussian adjustment
    def makeAdjustment(self):
        message = "Ajuste hecho con: \n lp(x:%f, y:%.4E) \n rp(x:%f, y:%.4E)"
        params = (self.left_point["x"], self.left_point["y"], self.right_point["x"], self.right_point["y"])
        print message % params

    # resets internal state
    def reset(self):
        self.left_point = None
        self.right_point = None
#        self.center_point = None
        self.message = GaussAdjuster.messages["left_point"]
        self.ready = False
        #TODO: ver si es necesario
        self.connection_id = self.figure.canvas.mpl_connect('button_press_event', self)

class LineAdjuster:
    # Messages used throught the lifespan of the adjuster
    messages = {
        "initial" : "Listo para comenzar seleccion de puntos",
        "lp" : "Seleccione el punto izquierdo",
        "rp" : "Seleccione el punto derecho",
        "p_defined" : "Punto %s definido en (x:%f, y:%.5E)",
        "val_init" : "Validando los datos ingresados...",
        "val_fail" : "Puntos definidos inconsistentes, vuelva a ingresarlos",
        "val_success" : "Datos ingresados correctos"
    }

    # Initialization method
    def __init__(self, figure):
        self.figure = figure
        self.lp = None
        self.rp = None
        self.message = LineAdjuster.messages["initial"]
        self.ready = False
        self.connection_id = None

    # Event handling method, only works when object is attached
    def __call__(self,event):
        if not self.isAttached(): return
        #if event.inaxes != self.line.axes: return
        e_point = { "x": event.xdata , "y" : event.ydata }

        if self.lp == None:
            #Set lp
            #self.bindPoint(self.lp, e_point)
            self.lp = e_point            
            print LineAdjuster.messages["p_defined"] % ("lp", self.lp["x"], self.lp["y"])
            self.message = LineAdjuster.messages["rp"]
            print self.message
            return
        elif self.rp == None:
            #Set rp
            #self.bindPoint(self.rp, e_point)
            self.rp = e_point
            print LineAdjuster.messages["p_defined"] % ("rp", self.rp["x"], self.rp["y"])
            self.message = LineAdjuster.messages["val_init"]
            print self.message
            #both points set, validate consitency
            if self.validates():
                print LineAdjuster.messages["val_success"]
                self.setReady()
                self.detach()
                self.adjust()
            else:
                print LineAdjuster.messages["val_fail"]
                self.reset()
                self.message = LineAdjuster.messages["lp"]
                print self.message

    # Method to capture point definitions (mouse clicks)
    def startPointSelection(self):
        self.message = LineAdjuster.messages["lp"]
        print self.message
        self.attach()

    # Method to bind selected point to the adjuster
    def bindPoint(self, point, event_point):
        point = event_point

    # Method to "attach" to a given event, button_press_event is default
    def attach(self, event_name = "button_press_event"):
        self.connection_id = self.figure.canvas.mpl_connect(event_name, self)

    # Method to "detach" from the event that this instance is connected to
    def detach(self):
        self.figure.canvas.mpl_disconnect(self.connection_id)
        self.connection_id == None

    # Return true of false if this instance is attached to a event
    def isAttached(self):
        return self.connection_id != None

    # Method to check consitency of the adjuster internal state
    def validates(self):
        if self.lp["x"] > self.rp["x"]:
            return False
        else:
            return True

    # Method to reset adjuster internal state
    def reset(self):
        self.lp = None
        self.rp = None
        self.message = LineAdjuster.messages["initial"]
        self.ready = False

    def setReady(self):
        self.ready = True

    def adjust(self):
        print " "
