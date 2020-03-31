import numpy as np
from matplotlib import pyplot as plt
import math

def SeparateList(List2Sep,data):
    TotNum = len(List2Sep)
    xComponent = List2Sep[1::2].tolist()
    yComponent = List2Sep[::2].tolist()

    xComponent = np.reshape(xComponent,(data['nx'].item() ,data['ny'].item() ))
    yComponent = np.reshape(yComponent,(data['nx'].item() ,data['ny'].item() ))
    return xComponent,yComponent

def GetProfileData(LocIni,LocEnd,NumPoints, SplineFunction):
    x0,y0,x1,y1 = LocIni[0], LocIni[1], LocEnd[0], LocEnd[1]
    x, y = np.linspace(x0, x1, NumPoints),   np.linspace(y0, y1, NumPoints)

    CompX = [SplineFunction[0](x[i], y[i])[0][0] for i in range(NumPoints)]
    CompY = [SplineFunction[1](x[i], y[i])[0][0] for i in range(NumPoints)]

    Dist = math.sqrt((x1 - x0)**2.0 + (y1 - y0)**2.0)
    ArrayDist = np.linspace(0, Dist, NumPoints)

    return ArrayDist, CompX, CompY


#------------- for Plotting all together DEPRECATED -------------#
def FigSetupAndPlotImage(LCoorX,LCoorY,Field):
    fig = plt.figure(figsize = (10,5) ,constrained_layout=True)
    gs = fig.add_gridspec(2, 4)
    ax1 = fig.add_subplot(gs[0:2, 0:2])
    ax1.set_aspect('equal', 'box')
    axList= [fig.add_subplot(gs[i,2:4]) for i in range(2)]

    img = ax1.pcolormesh(LCoorX,LCoorY,Field)

    return img, axList

def PlotProfiles(ArrayDist, CompX, CompY, axList):
    axList[0].plot(ArrayDist,CompX)
    axList[1].plot(ArrayDist,CompY)
#-----------------------------------------------------#


def PlotLocLine(img,LocIni,LocEnd):
    img.axes.annotate("",
                    xy = (LocIni[0], LocIni[1]),
                    xycoords = 'data',
                    xytext = (LocEnd[0], LocEnd[1]), 
                    textcoords = 'data',
                    arrowprops = dict(
                        arrowstyle = "<-",
                        connectionstyle = "arc3", 
                        color = 'white',
                        alpha = 1,
                        linewidth = 1
                        ),
                    )

def PlotDomain(CoorX, CoorY, Field, FieldName):
    fig = plt.figure(figsize = (6, 5), constrained_layout = True)
    gs = fig.add_gridspec(1, 1)
    ax = fig.add_subplot(gs[:, :])
    ax.set_title("Domain:\n{FName}".format(FName = FieldName[:-4]))
    ax.set_xlabel("X-Coordinate [m]"), ax.set_ylabel("Y-Coordinate [m]")
    ax.set_aspect('equal', 'box')

    img = ax.pcolormesh(CoorX, CoorY, Field)
    cbar = fig.colorbar(img, ax = ax)
    cbar.ax.set_ylabel(FieldName)
    
    return fig, img


def BuildAndSaveDomainFig(CoorX, CoorY, Field, LocIni, LocEnd, FieldName,FileName):
    fig, img = PlotDomain(CoorX, CoorY, Field, FieldName)
    PlotLocLine(img, LocIni, LocEnd)

    print("Saving figure: {}".format(FileName))
    fig.savefig(FileName, dpi = 300)
    print("\rSaved figure! {}".format(FileName))

def PlotProfileInter(Dist, ProfileData, PlotTitle, Filename):
    fig = plt.figure(figsize = (10,5) ,constrained_layout=True)
    gs = fig.add_gridspec(1, 1)
    ax = fig.add_subplot(gs[:, :])
    
    ax.set(xlabel='Distance [m]', ylabel='Displacement [m]',
       title='Profile Plot:\n{}'.format(PlotTitle))
    ax.grid()
    
    plt.plot(Dist, ProfileData, 'b')
    
    print("Saving figure: {}".format(Filename))
    fig.savefig(Filename, dpi=300)
    print("\rSaved figure: {}".format(Filename))

#------------ GUI Functions -----------

class LineSlice:    
    def __init__(self, img, axList, SplineFunction, NumPoints=1000):
        self.img = img
        self.ax = axList

        self.SplineFunctionX = SplineFunction[0]
        self.SplineFunctionY = SplineFunction[1]
        self.NumPoints = NumPoints

        self.cidclick = img.figure.canvas.mpl_connect('button_press_event', self)
        self.cidrelease = img.figure.canvas.mpl_connect('button_release_event', self)

        self.markers, self.arrow = None, None  
        self.lineX = None
        self.lineY = None
    #end __init__

    def __call__(self, event):
        if event.inaxes != self.img.axes: return     # exit if clicks weren't within the `img` axes
        if self.img.figure.canvas.manager.toolbar._active is not None: return   # exit if pyplot toolbar (zooming etc.) is active

        if event.name == 'button_press_event':
            self.p1 = (event.xdata, event.ydata, event.x, event.y)  
        elif event.name == 'button_release_event':
            self.p2 = (event.xdata, event.ydata, event.x, event.y)  
            self.drawLineSlice() 
    #end __call__

    def drawLineSlice( self ):

        x0,y0,dx0,dy0 = self.p1[0], self.p1[1], self.p1[2], self.p1[3]  
        x1,y1,dx1,dy1 = self.p2[0], self.p2[1], self.p2[2], self.p2[3] 

        print(self.p1,self.p2)

        x, y = np.linspace(x0, x1, self.NumPoints),   np.linspace(y0, y1, self.NumPoints)
        dx, dy = np.linspace(dx0, dx1, self.NumPoints),   np.linspace(dy0, dy1, self.NumPoints)

        
        zxi = [self.SplineFunctionX(x[i], y[i])[0][0] for i in range(self.NumPoints)]
        zyi = [self.SplineFunctionY(x[i], y[i])[0][0] for i in range(self.NumPoints)]
        

        Dist = math.sqrt((x1 - x0)**2.0 + (y1 - y0)**2.0)
        ZDist = np.linspace(0, Dist, self.NumPoints)

        # if plots exist, delete them:
        if self.markers != None:
            if isinstance(self.markers, list):
                self.markers[0].remove()
            else:
                self.markers.remove()
        if self.arrow != None:
            self.arrow.remove()

        # plot the endpoints
        self.markers = self.img.axes.plot([x0, x1], [y0, y1], 'wo')   
        # plot an arrow:
        self.arrow = self.img.axes.annotate("",
                    xy = (x0, y0),    # start point
                    xycoords = 'data',
                    xytext = (x1, y1),    # end point
                    textcoords = 'data',
                    arrowprops = dict(
                        arrowstyle = "<-",
                        connectionstyle = "arc3", 
                        color = 'white',
                        alpha = 0.7,
                        linewidth = 3
                        ),
                    )
        if self.lineX != None:
            self.lineX[0].remove()
            self.lineY[0].remove()      
        self.lineX = self.ax[0].plot(ZDist,zxi)
        self.lineY = self.ax[1].plot(ZDist,zyi)


def PlotImage_GUI(LCoorX,LCoorY,Field, SplineFunction):
    plt.ion()

    fig = plt.figure(figsize = (10,5) ,constrained_layout=True)
    gs = fig.add_gridspec(2, 4)
    ax1 = fig.add_subplot(gs[0:2, 0:2])
    ax1.set_aspect('equal', 'box')
    axList= [fig.add_subplot(gs[i,2:4]) for i in range(2)]

    img = ax1.pcolormesh(LCoorX,LCoorY,Field)

    LnTr = LineSlice(img, axList, SplineFunction) 
    plt.show(block = True)