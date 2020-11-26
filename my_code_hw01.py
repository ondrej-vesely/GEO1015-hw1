#-- my_code_hw01.py
#-- hw01 GEO1015.2020
#-- Guilherme Spinoza Andreo
#-- 5383994 
#-- Ondrej Vesely
#-- 5162130


#-- import outside the standard Python library are not allowed, just those:
import math
import numpy
import scipy.spatial
import startin 
#-----


class BoundingBox:
    """A 2D bounding box"""
    
    def __init__(self, points):       
        self.minx, self.miny = float("inf"), float("inf")
        self.maxx, self.maxy = float("-inf"), float("-inf")
        for x, y, *_ in points:
            # Set min coords
            if x < self.minx:
                self.minx = x
            if y < self.miny:
                self.miny = y
            # Set max coords
            if x > self.maxx:
                self.maxx = x
            elif y > self.maxy:
                self.maxy = y
    @property
    def width(self):
        return self.maxx - self.minx
    @property
    def height(self):
        return self.maxy - self.miny


class Raster:
  """Simple raster based on ESRI ASCII schema"""
  
  def __init__(self, bbox, cell_size, no_data=-9999):
    self.ncols = math.ceil(bbox.width / cell_size)
    self.nrows = math.ceil(bbox.height / cell_size)
    self.xllcorner = bbox.minx
    self.yllcorner = bbox.miny
    self.cell_size = cell_size
    self.no_data = no_data
    
    # initialize list of values with no_data
    self.values = [self.no_data] * self.ncols * self.nrows
    
  @property
  def centers(self):
    """Cell center coordinates"""
    xulcenter = self.xllcorner + self.cell_size/2
    yulcenter = self.yllcorner + self.cell_size/2 + self.cell_size*self.nrows
    for i in range(self.ncols):
      for j in range(self.nrows):
        x = xulcenter + j * self.cell_size
        y = yulcenter - i * self.cell_size
        yield (x,y)
    
  def to_ascii(self):
    rows = [
      "NCOLS %d" % self.ncols,
      "NROWS %d" % self.nrows,
      "XLLCORNER %s" % self.xllcorner,
      "YLLCORNER %s" % self.yllcorner,
      "CELLSIZE %s" % self.cell_size,
      "NODATA_VALUE %s" % self.no_data,
      ' '.join( (str(x) for x in self.values) )
    ]
    return '\n'.join(rows)


def nn_interpolation(list_pts_3d, j_nn):
    """ 
    Function that writes the output raster with nearest neighbour interpolation
     
    Input:
        list_pts_3d: the list of the input points (in 3D)
        j_nn:        the parameters of the input for "nn"
    Output:
        returns the value of the area
 
    """  
    bbox = BoundingBox(list_pts_3d)
    raster = Raster(bbox, j_nn['cellsize'])

    list_pts_2d = [(x,y) for x,y,z in list_pts_3d]
    list_pts_z = [(z) for x,y,z in list_pts_3d]
    kdtree = scipy.spatial.KDTree(list_pts_2d)
    dt = startin.DT()
    dt.insert(list_pts_2d)

    raster.values = []
    for center in raster.centers:
        # catch outside on convex hull case
        if not dt.locate(*center):
            raster.values.append(raster.no_data)
            continue
        # get nearest neighbour
        _, i = kdtree.query(center)
        raster.values.append(list_pts_z[i])

    with open(j_nn["output-file"], 'w') as output:
        output.write(raster.to_ascii())

    print("File written to", j_nn['output-file'])


def idw_interpolation(list_pts_3d, j_idw):
    """
    Function that writes the output raster with IDW
     
    Input:
        list_pts_3d: the list of the input points (in 3D)
        j_idw:       the parameters of the input for "idw"
    Output:
        returns the value of the area

    """  
    bbox = BoundingBox(list_pts_3d)
    raster = Raster(bbox, j_idw['cellsize'])

    list_pts_2d = [(x,y) for x,y,z in list_pts_3d]
    list_pts_z = [(z) for x,y,z in list_pts_3d]
    kdtree = scipy.spatial.KDTree(list_pts_2d)
    dt = startin.DT()
    dt.insert(list_pts_2d)

    raster.values = []
    for center in raster.centers:
        # catch outside on convex hull case
        if not dt.locate(*center):
            raster.values.append(raster.no_data)
            continue
        # get samples in radius
        samples = kdtree.query_ball_point(center, j_idw['radius'])
        coords = [list_pts_2d[i] for i in samples]
        values = [list_pts_z[i] for i in samples]
        dists = [math.sqrt( (center[0]-c[0])**2 + (center[1]-c[1])**2 ) 
                for c in coords]
        # catch no sample in radius case
        if not samples:
            raster.values.append(raster.no_data)
            continue
        # catch zero distance case
        if 0 in dists:
            i = dists.index(0)
            raster.values.append(values[i])
            continue 
        # calculate the weighted average
        weights = [1/d**j_idw['power'] for d in dists]
        weights_norm = [w/sum(weights) for w in weights]
        result = sum([norm*z for norm, z in zip(weights_norm, values)])
        raster.values.append(result)

    with open(j_idw["output-file"], 'w') as output:
        output.write(raster.to_ascii())
    
    print("File written to", j_idw['output-file'])


def tin_interpolation(list_pts_3d, j_tin):
    """
    Function that writes the output raster with linear in TIN interpolation
     
    Input:
        list_pts_3d: the list of the input points (in 3D)
        j_tin:       the parameters of the input for "tin"
    Output:
        returns the value of the area
 
    """  
    bbox = BoundingBox(list_pts_3d)
    raster = Raster(bbox, j_tin['cellsize'])
    
    dt = startin.DT()
    dt.insert(list_pts_3d)

    raster.values = []
    for center in raster.centers:
        triangle = dt.locate(*center)
        # catch outside on convex hull case
        if not triangle:
            raster.values.append(raster.no_data)
            continue
        # interpolate the triangle verts
        v1, v2, v3 = [dt.get_point(i) for i in triangle]
        # using barycentric coordinate weights 
        # https://codeplea.com/triangular-interpolation
        w1top = (v2[1]-v3[1])*(center[0]-v3[0]) + (v3[0]-v2[0])*(center[1]-v3[1])
        w2top = (v3[1]-v1[1])*(center[0]-v3[0]) + (v1[0]-v3[0])*(center[1]-v3[1])
        bot = (v2[1]-v3[1])*(v1[0]-v3[0]) + (v3[0]-v2[0])*(v1[1]-v3[1])
        w1 = w1top / bot
        w2 = w2top / bot
        w3 = 1 - w1 - w2
        result = v1[2]*w1 + v2[2]*w2 + v3[2]*w3
        raster.values.append(result)

    with open(j_tin["output-file"], 'w') as output:
        output.write(raster.to_ascii())

    print("File written to", j_tin['output-file'])


def kriging_interpolation(list_pts_3d, j_kriging):
    """
    !!! TO BE COMPLETED !!!
     
    Function that writes the output raster with ordinary kriging interpolation
     
    Input:
        list_pts_3d: the list of the input points (in 3D)
        j_kriging:       the parameters of the input for "kriging"
    Output:
        returns the value of the area
 
    """  
    
    
    print("File written to", j_kriging['output-file'])
