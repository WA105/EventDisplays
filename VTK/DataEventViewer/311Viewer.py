import vtk
import math
from vtk.util.colors import tomato, banana, mint, peacock
import pandas as pd
from ViewerFunctions import *
import argparse
import os  
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
#run_path="/Users/sebastienmurphy/311Data/HDF5/Run840_subrun0.h5"
ADC2CHARGE = 67.
N_MAX_EVENT_PER_FILE=400
import os  
inputPoints_View0 = vtk.vtkPoints()
inputPoints_View1 = vtk.vtkPoints()
CoordTranform=LArSoftToVtkCoord() # from ViewerFunctions, init the coord transform from LArSoft to VTK


VTKGeomFileName = "3x1x1-full.vtk"

parser = argparse.ArgumentParser()
parser.add_argument("-file", help="specify the full run file name and path")
parser.add_argument("-ev", help="specify the event number")
parser.add_argument("-trk_length", help="cut on on track length in cm (show only tracks with length greater than cut)")
parser.add_argument("-ev_range", nargs=2, help="specify a range of events example -ev 10 100 returns all events between 10 and 100") # not implement yet
parser.add_argument("-ev_all", action="store_true")
parser.add_argument("--verbosity", help="increase output verbosity")
args=parser.parse_args()
if args.ev and args.ev_range:
    parser.error('please chose! either one event (-ev option) or event range (-ev_range option).')
if not args.ev and not args.ev_range and not args.ev_all:
    parser.error('please provide either event number (-ev option) or event range (-ev_range option).')
    
if not args.file:
    parser.error('please provide full run file path (-file option)')
else: this_run=args.file

if (not os.path.isfile(this_run)): # test existence of file
    print bcolors.FAIL+ " run:"+this_run+ " not found"+ bcolors.ENDC
    sys.exit()

if (not os.path.isfile(VTKGeomFileName)): # test existence of VTK geometry file
    print bcolors.FAIL+"VTK geometry file: "+VTKGeomFileName+ " not found"+ bcolors.ENDC
    sys.exit()
    
if args.ev:
    first_event=int(args.ev)
    last_event=first_event+1
    print bcolors.HEADER +"-------------------Running viewer on run:", this_run, "and event number:", first_event,"-------------------------"+ bcolors.ENDC

if args.ev_range:
    first_event=int(args.ev_range[0])
    last_event=int(args.ev_range[1])
    print bcolors.HEADER +"-------------------Running viewer on run:", this_run, ". Between event number:", first_event,"and event number:", last_event, "-------------------------"+ bcolors.ENDC

if args.ev_all:
    first_event=0
    last_event=N_MAX_EVENT_PER_FILE
    print bcolors.OKBLUE +"-------------------Running viewer on run:", this_run, "and ALL events:", last_event,"-------------------------"+ bcolors.ENDC

if args.trk_length:
    trk_length_cut=float(args.trk_length)
    print bcolors.HEADER +"-------------------Will display only tracks with length greater than:", trk_length_cut," cm  -------------------------"+ bcolors.ENDC

verbose=0
if args.verbosity:
    verbose=int(args.verbosity)

mydata = pd.read_hdf(this_run, "table", mode = "r")
print bcolors.OKBLUE +"-------------------Succesfuly read data from file:", this_run, "-------------------------"+ bcolors.ENDC

for iev in range(first_event,last_event) :
    NTracks=mydata.NumberOfTracks_pmtrack[iev]
    if(verbose): print("-------- Event:",iev,"number of tracks:",NTracks, "--------------")
#    if NTracks>5: continue
    for itrk in range(0, NTracks) :
        Nhits=mydata.Track_NumberOfHits_pmtrack[iev][itrk]
        TrkLength=mydata.Track_Length_pmtrack[iev][itrk]
        if verbose:print("\n-------------- track number:",itrk, "Length:", TrkLength, "--- Nhits:",Nhits)
        if args.trk_length and TrkLength< trk_length_cut : continue
        for ihit in range(0,Nhits) :
            hit_x= mydata.Track_Hit_X_pmtrack[iev][ihit]
            hit_y= mydata.Track_Hit_Y_pmtrack[iev][ihit]
            hit_z= mydata.Track_Hit_Z_pmtrack[iev][ihit]
            hit_charge=mydata.Hit_ChargeIntegral[iev][ihit]/ADC2CHARGE
            if math.isnan(hit_charge): continue
            hit_x_vtk=CoordTranform.GetXVTK(hit_x,hit_y,hit_z)
            hit_y_vtk=CoordTranform.GetYVTK(hit_x,hit_y,hit_z)
            hit_z_vtk=CoordTranform.GetZVTK(hit_x,hit_y,hit_z)
            iview= mydata.Track_Hit_View_pmtrack[iev][ihit]
            if iview==0 : pointID=inputPoints_View0.InsertNextPoint(hit_x_vtk, hit_y_vtk, hit_z_vtk)
            if iview==1 : pointID=inputPoints_View1.InsertNextPoint(hit_x_vtk, hit_y_vtk, hit_z_vtk)


#set vtk glyphs to points ( make spheres from the points and give them colors)
MyGlyphPoints=PointsToGlyph()
glyphActor_View0=MyGlyphPoints.ReturnGlyphActorFromPoints(inputPoints_View0 , 0, 10,peacock)
glyphActor_View1=MyGlyphPoints.ReturnGlyphActorFromPoints(inputPoints_View1 , 1, 3,tomato)

mapper = vtk.vtkPolyDataMapper()


#open the geometry
print bcolors.HEADER +"-------------------now loading the vtk geometry file:", VTKGeomFileName, "-------------------------"+ bcolors.ENDC
reader= vtk.vtkPolyDataReader()
reader.SetFileName(VTKGeomFileName)
reader.Update();
imageDataGeometryFilter = vtk.vtkGeometryFilter()
imageDataGeometryFilter.SetInputConnection(reader.GetOutputPort())
imageDataGeometryFilter.Update()
mapper.SetInputConnection(imageDataGeometryFilter.GetOutputPort())
GeomActor = vtk.vtkActor()
GeomActor.SetMapper(mapper)
GeomActor.GetProperty().SetPointSize(10)
GeomActor.GetProperty().SetOpacity(.1) 
print bcolors.OKBLUE +"-------------------DONE loading the vtk geometry file:"+ bcolors.ENDC

#ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.SetSize(3000, 1500) 
iren = vtk.vtkRenderWindowInteractor()
iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
iren.SetRenderWindow(renWin)
#imageStyle=vtk.vtkInteractorStyleImage() # remove 3D interaction and only zoom, this would be ideal for the projection views (but at the moment cannot set only this style for one window)
#iren.SetInteractorStyle(imageStyle)
#compute and add axes
axes=CoordTranform.ReturnAxesActor()

# Define viewport ranges
X_divide=.6
Y_divide=.4
xmins=[0 , X_divide, X_divide]
xmaxs=[X_divide , 1 ,1]
ymins=[0, Y_divide, 0]
ymaxs=[1, 1 ,Y_divide]

renderer=[]
camera=[]
for i in range(3):
        renderer.append(vtk.vtkRenderer())
        camera.append(vtk.vtkCamera())
        renderer[i].SetViewport(xmins[i],ymins[i],xmaxs[i],ymaxs[i])
        renderer[i].AddActor(GeomActor)
        renderer[i].AddActor(glyphActor_View0)
        renderer[i].AddActor(glyphActor_View1)
        renderer[i].GradientBackgroundOn()
        renderer[i].SetBackground(1,1,1)
        renderer[i].SetBackground2(0,0,0)
        renderer[i].AddActor(axes)
        renWin.AddRenderer(renderer[i])
        camera[i]=renderer[i].GetActiveCamera()
        camera[i].SetFocalPoint(CoordTranform.VTKCenterTPC() )
        if i==0:
            renderer[i].ResetCamera()
        if i==2:
            camera[i].ParallelProjectionOn()
            camera[i].SetParallelScale(1500.0) # camera is 1500 mm away from the focal point
            camera[i].SetPosition(500.0, 0.0,-500.0)
            camera[i].SetViewUp(0.0, 0.0, 1.0)
            
        if i==1:
            camera[i].ParallelProjectionOn()
            camera[i].SetParallelScale(1000.0) # distance of camera  from the focal point
            camera[i].SetPosition(0.0, 1.0,-500.0)
            camera[i].SetViewUp(0.0, 0.0, 1.0)

renWin.Render()
renWin.SetWindowName('3x1x1 Detector')
iren.Initialize()
iren.Start()




