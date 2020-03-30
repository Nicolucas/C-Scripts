import importlib.util
spec = importlib.util.spec_from_file_location("PetscBinaryIO", "/home/nico/Documents/TEAR/Codes_TEAR/plot-utils_se2wave/se2wave/utils/python/PetscBinaryIO.py")
pio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pio)

import numpy as np
from matplotlib import pyplot as plt
import math

from scipy.interpolate import RectBivariateSpline


def se2wave_load_coordinates(filename):
  debug = True
  io = pio.PetscBinaryIO()
  data = dict()
  with open(filename) as fp:
    v = io.readInteger(fp)
    data['mx'] = v
    
    v = io.readInteger(fp)
    data['my'] = v
    
    v = io.readInteger(fp)
    data['nx'] = v
    
    v = io.readInteger(fp)
    data['ny'] = v
    
    objecttype = io.readObjectType(fp)
    v = io.readVec(fp)
    data['coor'] = v
  
  if debug:
    print('#elements-x',data['mx'])
    print('#elements-y',data['my'])
    print('#basis-x',data['nx'])
    print('#basis-y',data['ny'])

  return data

def se2wave_load_wavefield(filename,has_displacement,has_velocity):
  debug = True
  io = pio.PetscBinaryIO()
  data = dict()
  with open(filename) as fp:
    v = io.readInteger(fp)
    data['mx'] = v
    
    v = io.readInteger(fp)
    data['my'] = v
    
    v = io.readInteger(fp)
    data['nx'] = v
    
    v = io.readInteger(fp)
    data['ny'] = v

    v = io.readInteger(fp)
    data['step'] = v

    v = io.readReal(fp)
    data['time'] = v

    if has_displacement:
      objecttype = io.readObjectType(fp)
      v = io.readVec(fp)
      data['displ'] = v

    if has_velocity:
      objecttype = io.readObjectType(fp)
      v = io.readVec(fp)
      data['vel'] = v

  if debug:
    print('#elements-x',data['mx'])
    print('#elements-y',data['my'])
    print('#basis-x',data['nx'])
    print('#basis-y',data['ny'])
    print('step',data['step'])
    print('time',data['time'])
  
  return data



def SeparateList(List2Sep):
    TotNum = len(List2Sep)
    xComponent = [List2Sep[i] for i in range(TotNum) if i%2==1]
    yComponent = [List2Sep[i] for i in range(TotNum) if i%2==0]
    
    xComponent = np.reshape(xComponent,(385,385))
    yComponent = np.reshape(yComponent,(385,385))
    return xComponent,yComponent


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


filename = "/home/nico/Documents/TEAR/Codes_TEAR/plot-utils_se2wave/se2wave/default_mesh_coor.pbin"
se2_coor = se2wave_load_coordinates(filename);


w_filename = "/home/nico/Documents/TEAR/Codes_TEAR/plot-utils_se2wave/se2wave/step-1400_wavefield.pbin"
se2_field = se2wave_load_wavefield(w_filename,True,True);

LCoorX, LCoorY = SeparateList(se2_coor['coor'])
LFieldX, LFieldY = SeparateList(se2_field['displ'])

SplineFunction = [RectBivariateSpline(LCoorX[:,0], LCoorY[0,:], LFieldX), 
                  RectBivariateSpline(LCoorX[:,0], LCoorY[0,:], LFieldY)]


PlotImage_GUI(LCoorX, LCoorY, LFieldY, SplineFunction)