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
# import startin 
#-----


class BoundingBox:
    """A 2D bounding box"""
    
    def __init__(self, points):
        if len(points) == 0:
            raise ValueError("Can't compute bounding box of empty list")
        
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
    def __repr__(self):
        return "BoundingBox(X: {} - {}, Y: {} - {})".format(
            self.minx, self.maxx, self.miny, self.maxy)


class Raster:
  """Simple raster based on ESRI ASCII schema"""
  
  def __init__(self, bbox, cell_size, no_data=-9999):
    self.ncols = int(bbox.width // cell_size + 1)
    self.nrows = int(bbox.height // cell_size + 1)
    self.xllcenter = bbox.minx
    self.yllcenter = bbox.miny
    self.cell_size = cell_size
    self.no_data = no_data
    
    # initialize list of values with no_data
    self.values = [self.no_data] * self.ncols * self.nrows
    
  @property
  def coords(self):
    """Cell center coordinates"""
    for i in range(self.ncols):
      for j in range(self.nrows):
        x = self.xllcenter + i * self.cell_size
        y = self.yllcenter + j * self.cell_size
        yield (x,y)
    
  def to_ascii(self):
    rows = [
      "NCOLS %d" % self.ncols,
      "NROWS %d" % self.nrows,
      "XLLCENTER %s" % self.xllcenter,
      "YLLCENTER %s" % self.yllcenter,
      "CELLSIZE %s" % self.cell_size,
      "NODATA_VALUE %s" % self.no_data,
      ' '.join( (str(x) for x in self.values) )
    ]
    return '\n'.join(rows)


def nn_interpolation(list_pts_3d, j_nn):
    """
    !!! TO BE COMPLETED !!!
     
    Function that writes the output raster with nearest neighbour interpolation
     
    Input:
        list_pts_3d: the list of the input points (in 3D)
        j_nn:        the parameters of the input for "nn"
    Output:
        returns the value of the area
 
    """  
    # print("cellsize:", j_nn['cellsize'])

    #-- to speed up the nearest neighbour us a kd-tree
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.html#scipy.spatial.KDTree
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.query.html#scipy.spatial.KDTree.query
    # kd = scipy.spatial.KDTree(list_pts)
    # d, i = kd.query(p, k=1)

    bbox = BoundingBox(list_pts_3d)
    raster = Raster(bbox, j_nn['cellsize'])

    list_points_2d = [(x,y) for x,y,z in list_pts_3d]
    list_points_z = [(z) for x,y,z in list_pts_3d]
    kdtree = scipy.spatial.KDTree(list_points_2d)

    for i, coord in enumerate(raster.coords):
        _, index = kdtree.query(coord)
        raster.values[i] = list_points_z[index]

    with open(j_nn["output-file"], 'w') as output:
        output.write(raster.to_ascii())

    print("File written to", j_nn['output-file'])


def idw_interpolation(list_pts_3d, j_idw):
    """
    !!! TO BE COMPLETED !!!
     
    Function that writes the output raster with IDW
     
    Input:
        list_pts_3d: the list of the input points (in 3D)
        j_idw:       the parameters of the input for "idw"
    Output:
        returns the value of the area
 
    """  
    # print("cellsize:", j_idw['cellsize'])
    # print("radius:", j_idw['radius'])

    #-- to speed up the nearest neighbour us a kd-tree
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.html#scipy.spatial.KDTree
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.query.html#scipy.spatial.KDTree.query
    # kd = scipy.spatial.KDTree(list_pts)
    # i = kd.query_ball_point(p, radius)
    
    print("File written to", j_idw['output-file'])


def tin_interpolation(list_pts_3d, j_tin):
    """
    !!! TO BE COMPLETED !!!
     
    Function that writes the output raster with linear in TIN interpolation
     
    Input:
        list_pts_3d: the list of the input points (in 3D)
        j_tin:       the parameters of the input for "tin"
    Output:
        returns the value of the area
 
    """  
    #-- example to construct the DT with scipy
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html#scipy.spatial.Delaunay
    # dt = scipy.spatial.Delaunay([])

    #-- example to construct the DT with startin
    # minimal docs: https://github.com/hugoledoux/startin_python/blob/master/docs/doc.md
    # how to use it: https://github.com/hugoledoux/startin_python#a-full-simple-example
    # you are *not* allowed to use the function for the tin linear interpolation that I wrote for startin
    # you need to write your own code for this step
    # but you can of course read the code [dt.interpolate_tin_linear(x, y)]
    
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
