#from usr.local.lib.python2.7.site-packages import vtk
import vtk
import math
from vtk.util.colors import tomato, banana, mint, peacock, raspberry, flesh, lavender, salmon, black
import pandas as pd
from ViewerFunctions import *
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib 

import h5py
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

ProcessMC=False

CoordTranform=LArSoftToVtkCoord() # from ViewerFunctions, init the coord transform from LArSoft to VTK
MyMCPoints=MCPoints()

VTKGeomFileName = "3x1x1-full.vtk"

parser = argparse.ArgumentParser()
parser.add_argument("-file", help="specify the full run file name and path (either data or reconstructed MC)")
parser.add_argument("-MCfile", help="specify the full run file name and path of MC file")
parser.add_argument("-ev", help="specify the event number")
parser.add_argument("-trk_length", help="cut on on track length in cm (show only tracks with length greater than cut)")
parser.add_argument("-ev_range", nargs=2, help="specify a range of events example -ev 10 100 returns all events between 10 and 100") # not implement yet
parser.add_argument("-ev_all", action="store_true")
parser.add_argument("-no_neutrons", action="store_true")
parser.add_argument("-no_gammas", action="store_true")
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

if args.MCfile:
    ProcessMC=True
    this_MC_run=args.MCfile
    if (not os.path.isfile(this_MC_run)): # test existence of file
        print bcolors.FAIL+ "Monte Carlo run:"+this_MC_run+ " not found"+ bcolors.ENDC
        sys.exit()
    else:
        print bcolors.HEADER +"-------------------Running viewer on MC run:", this_MC_run,"-------------------------"+ bcolors.ENDC
        mydata_mc = pd.read_hdf(this_MC_run, "table", mode = "r")
        print bcolors.OKBLUE +"-------------------Succesfuly read data from file:",this_MC_run, "---- All OK! -----------------------"+ bcolors.ENDC
    
if args.ev:
    first_event=int(args.ev)
    last_event=first_event+1
    print bcolors.HEADER +"-------------------Running viewer on event number:", first_event,"-------------------------"+ bcolors.ENDC

if args.ev_range:
    first_event=int(args.ev_range[0])
    last_event=int(args.ev_range[1])
    print bcolors.HEADER +"-------------------Running viewer between event number:", first_event," and event number:", last_event, "-------------------------"+ bcolors.ENDC

if args.ev_all:
    first_event=0
    last_event=N_MAX_EVENT_PER_FILE
    print bcolors.OKBLUE +"-------------------Running viewer on  ALL events:", last_event,"-------------------------"+ bcolors.ENDC

if args.trk_length:
    trk_length_cut=float(args.trk_length)
    print bcolors.HEADER +"-------------------Will display only Reco tracks with length greater than:", trk_length_cut," cm  -------------------------"+ bcolors.ENDC

verbose=0
if args.verbosity:
    verbose=int(args.verbosity)

mydata = pd.read_hdf(this_run, "table", mode = "r")
print bcolors.OKBLUE +"-------------------Succesfuly read data from file:", this_run, "-------------------------"+ bcolors.ENDC


ListRecPointsView0=[]
ListRecPointsView1=[]

ListRecoInfoView0=[]
ListRecoInfoView1=[]


ListLineSourceNeutron=[]
ListLineSourceMuon=[]
ListLineSourcePion=[]
ListLineSourceProton=[]
ListLineSourceGamma=[]
ListLineSourceElectron=[]

ListNeutronInfo=[]
ListMuonInfo=[]
ListPionInfo=[]
ListProtonInfo=[]
ListGammaInfo=[]
ListElectronInfo=[]

glyphActor_MC_neutron=[]
glyphActor_MC_muon=[]
glyphActor_MC_pion=[]
glyphActor_MC_proton=[]
glyphActor_MC_gamma=[]
glyphActor_MC_electron=[]

MyGlyphPoints=PointsToGlyph()
mapper = vtk.vtkPolyDataMapper()

glyphActor_RecView0=[]
glyphActor_RecView1=[]


for iev in range(first_event,last_event) :
    #------------------ RECO LOOP -------------------#
    index_hit_inside_track = 0
    NTracks=mydata.NumberOfTracks[iev]
    for itrk in range(0, NTracks) :
        NhitView0=0
        NhitView1=0
        Nhits=mydata.Track_NumberOfHits[iev][itrk]
        TrkLength=mydata.Track_Length_Trajectory[iev][itrk]
        if args.trk_length and TrkLength< trk_length_cut : continue
        inputPoints_View0 = vtk.vtkPoints()
        inputPoints_View1 = vtk.vtkPoints()
        for ihit in range(index_hit_inside_track,Nhits+index_hit_inside_track) :
            hit_x= mydata.Track_Hit_X[iev][ihit]
            hit_y= mydata.Track_Hit_Y[iev][ihit]
            hit_z= mydata.Track_Hit_Z[iev][ihit]
            hit_charge=mydata.Hit_ChargeIntegral[iev][ihit]/ADC2CHARGE
            if math.isnan(hit_charge): continue
            hit_x_vtk=CoordTranform.GetXVTK(hit_x,hit_y,hit_z)
            hit_y_vtk=CoordTranform.GetYVTK(hit_x,hit_y,hit_z)
            hit_z_vtk=CoordTranform.GetZVTK(hit_x,hit_y,hit_z)
            iview= mydata.Track_Hit_View[iev][ihit]
            ListRecPointsView0
            if iview==0 :
                inputPoints_View0.InsertNextPoint(hit_x_vtk, hit_y_vtk, hit_z_vtk)
                NhitView0+=1
            if iview==1 :
                inputPoints_View1.InsertNextPoint(hit_x_vtk, hit_y_vtk, hit_z_vtk)
                NhitView1+=1

        ListRecPointsView0.append(inputPoints_View0)
        text="view 0, iev:"+str(iev)+" trk: "+str(itrk)+" Nhits:"+str( NhitView0)+" length:"+str(TrkLength)
        ListRecoInfoView0.append(text)
        print text
        
        ListRecPointsView1.append(inputPoints_View1)
        text="view 1, iev:"+str(iev)+" trk: "+str(itrk)+" Nhits:"+str(NhitView1)+" length:"+str(TrkLength)
        ListRecoInfoView1.append(text)
        print text
        
        index_hit_inside_track+=Nhits
         #------------------ END RECO LOOP -------------------#
    if not ProcessMC : continue
         #------------------ GO ON TO PROCESS MC DATA ONLY if ASKED -------------------#
         
    
    NPrimaries=mydata_mc.MCTruth_GEANT4_NumberOfParticles[iev]
    NPrimariesInTPC=mydata_mc.MCTruth_GEANT4_InTPCAV_NumberOfParticles[iev]
    print("-------- Event:",iev,"number of tracks:",NTracks, "--------------")
    NStepsTotal = mydata_mc.MCTruth_GEANT4_TotalNumberOfTrajectoryStepsForAllParticles[iev]
    TotPart=mydata_mc.MCTruth_GEANT4_NumberOfParticles[iev]
    mc_index_hit_inside_track = 0
    for i in range(0, TotPart):
        pid=mydata_mc.MCTruth_GEANT4_ParticleID[iev][i]
        pdg=mydata_mc.MCTruth_GEANT4_PDGCode[iev][i]
        NSteps=mydata_mc.MCTruth_GEANT4_NumberOfTrajectoryStepsPerParticle[iev][i]
        IsInTPC=mydata_mc.MCTruth_GEANT4_IsInTPCAV[iev][i]
        Pstart=round(mydata_mc.MCTruth_GEANT4_StartMomentum[iev][i],1)
        Pstart_3dec=round(mydata_mc.MCTruth_GEANT4_StartMomentum[iev][i],3)
     #   StartTimeInTPC=mydata_mc.MCTruth_GEANT4_InTPCAV_StartTime[iev][i] #something wrong with this one
        StartTime=round(mydata_mc.MCTruth_GEANT4_StartTime[iev][i]/1000.,1) #convert ns to us
        if not IsInTPC: # only show track that have hits in TPC
            mc_index_hit_inside_track += NSteps
            continue
        
        if pdg==2112:
            LineSourceNeutron=MyMCPoints.FillHitsMC(mc_index_hit_inside_track,NSteps+mc_index_hit_inside_track,mydata_mc,iev)
            if LineSourceNeutron:
                ListLineSourceNeutron.append(LineSourceNeutron)
                text="neutron, ev:"+str(iev)+"p= "+str(Pstart)+" GeV/c"
                ListNeutronInfo.append(text)
                
        elif pdg==13 or pdg==-13:
            LineSourceMuon=MyMCPoints.FillHitsMC(mc_index_hit_inside_track,NSteps+mc_index_hit_inside_track,mydata_mc,iev)
            if LineSourceMuon:
                ListLineSourceMuon.append(LineSourceMuon)
                if pdg==13: text="muon, ev:"+str(iev)+" p= "+str(Pstart)+" GeV/c"+" t="+str(StartTime)+"us"
                if pdg==-13: text="anti-muon, ev:"+str(iev)+" p= "+str(Pstart)+" GeV/c"+" t="+str(StartTime)+"us"
                ListMuonInfo.append(text)
                
        elif pdg==211 or pdg==-211:
            LineSourcePion=MyMCPoints.FillHitsMC(mc_index_hit_inside_track,NSteps+mc_index_hit_inside_track,mydata_mc,iev)
            if LineSourcePion:
                ListLineSourcePion.append(LineSourcePion)
                if pdg==211: text="pi+, ev:"+str(iev)+" p= "+str(Pstart)+" GeV/c"
                if pdg==-211: text="pi-, ev:"+str(iev)+" p= "+str(Pstart)+" GeV/c"
                ListPionInfo.append(text)
                
        elif pdg==11 or pdg==-11:
            LineSourceElectron=MyMCPoints.FillHitsMC(mc_index_hit_inside_track,NSteps+mc_index_hit_inside_track,mydata_mc,iev)
            if LineSourceElectron:
                ListLineSourceElectron.append(LineSourceElectron)
                if pdg==11: text="e-, ev:"+str(iev)+" p= "+str(Pstart_3dec)+" GeV/c"
                if pdg==-11: text="e+, ev:"+str(iev)+" p= "+str(Pstart_3dec)+" GeV/c"
                ListElectronInfo.append(text)
                
        elif pdg==22:
            LineSourceGamma=MyMCPoints.FillHitsMC(mc_index_hit_inside_track,NSteps+mc_index_hit_inside_track,mydata_mc,iev)
            if LineSourceGamma:
                ListLineSourceGamma.append(LineSourceGamma)
                text="gamma, ev:"+str(iev)+" p= "+str(Pstart_3dec)+" GeV/c"
                ListGammaInfo.append(text)
                
        mc_index_hit_inside_track += NSteps



#Assign glyphs to points for Reconstructed points
for i in range(len(ListRecPointsView0)):
    glyphActor_RecView0.append(MyGlyphPoints.ReturnGlyphActorFromPoints(ListRecPointsView0[i] , 0, 7,peacock))

for i in range(len(ListRecPointsView1)):
    glyphActor_RecView1.append(MyGlyphPoints.ReturnGlyphActorFromPoints(ListRecPointsView1[i] , 0, 6,tomato))


#Assign glyphs to points for MC points
if(ProcessMC):  
    for i in range(len(ListLineSourceNeutron)):
        glyphActor_MC_neutron.append(MyGlyphPoints.ReturnGlyphActorFromLineSource(ListLineSourceNeutron[i] , 7, black))

    for i in range(len(ListLineSourceMuon)):
        glyphActor_MC_muon.append(MyGlyphPoints.ReturnGlyphActorFromLineSource(ListLineSourceMuon[i] , 7, raspberry))

    for i in range(len(ListLineSourcePion)):
        glyphActor_MC_pion.append(MyGlyphPoints.ReturnGlyphActorFromLineSource(ListLineSourcePion[i] , 7, lavender))

    for i in range(len(ListLineSourceElectron)):
        glyphActor_MC_electron.append(MyGlyphPoints.ReturnGlyphActorFromLineSource(ListLineSourceElectron[i] , 7, banana))

    for i in range(len(ListLineSourceGamma)):
        glyphActor_MC_gamma.append(MyGlyphPoints.ReturnGlyphActorFromLineSource(ListLineSourceGamma[i] , 7, mint))


    
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


renWin = vtk.vtkRenderWindow()
renWin.SetSize(3000, 1500) 
iren = vtk.vtkRenderWindowInteractor()
iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
iren.SetRenderWindow(renWin)
#imageStyle=vtk.vtkInteractorStyleImage() # remove 3D interaction and only zoom, this would be ideal for the projection views (but at the moment cannot set only this style for one window)
#iren.SetInteractorStyle(imageStyle)
#compute and add axes
axes=CoordTranform.ReturnAxesActor()

balloonRep = vtk.vtkBalloonRepresentation()
balloonRep.SetBalloonLayoutToImageRight()
balloonRep.GetTextProperty().SetFontSize(30)
 
balloonWidget = vtk.vtkBalloonWidget()
balloonWidget.SetInteractor(iren)
balloonWidget.SetRepresentation(balloonRep)


# Define viewport ranges
X_divide=.65
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

        for ireco in range(len(glyphActor_RecView0)):
            renderer[i].AddActor(glyphActor_RecView0[ireco])
            balloonWidget.AddBalloon(glyphActor_RecView0[ireco],str(ListRecoInfoView0[ireco]))
            
        for ireco in range(len(glyphActor_RecView1)):
            renderer[i].AddActor(glyphActor_RecView1[ireco])
            balloonWidget.AddBalloon(glyphActor_RecView1[ireco],str(ListRecoInfoView1[ireco]))

        if(ProcessMC):
                for ipart in range(len(glyphActor_MC_muon)):
                    renderer[i].AddActor(glyphActor_MC_muon[ipart])
                    balloonWidget.AddBalloon(glyphActor_MC_muon[ipart],str(ListMuonInfo[ipart]))

                for ipart in range(len(glyphActor_MC_pion)):
                    renderer[i].AddActor(glyphActor_MC_pion[ipart])
                    balloonWidget.AddBalloon(glyphActor_MC_pion[ipart],str(ListPionInfo[ipart]))

                for ipart in range(len(glyphActor_MC_electron)):
                    renderer[i].AddActor(glyphActor_MC_electron[ipart])
                    balloonWidget.AddBalloon(glyphActor_MC_electron[ipart],str(ListElectronInfo[ipart]))

                if not args.no_gammas:
                        for ipart in range(len(glyphActor_MC_gamma)):
                                renderer[i].AddActor(glyphActor_MC_gamma[ipart])
                                balloonWidget.AddBalloon(glyphActor_MC_gamma[ipart],str(ListGammaInfo[ipart]))

                if not args.no_neutrons:
                    for ipart in range(len(glyphActor_MC_neutron)): 
                        renderer[i].AddActor(glyphActor_MC_neutron[ipart])
                        balloonWidget.AddBalloon(glyphActor_MC_neutron[ipart],str(ListNeutronInfo[ipart]))
            
        renderer[i].GradientBackgroundOn()
        renderer[i].SetBackground(1,1,1)
        renderer[i].SetBackground2(0,0,0)
        renderer[i].AddActor(axes)
        renWin.AddRenderer(renderer[i])
        camera[i]=renderer[i].GetActiveCamera()
        camera[i].SetFocalPoint(CoordTranform.VTKCenterTPC() )

        if i==0:
            renderer[i].ResetCamera()
            
        if i==1:
            camera[i].ParallelProjectionOn()
            camera[i].SetParallelScale(1500.0) 
            camera[i].SetClippingRange(0.1,3000)# depth of parrellel integration  from the parralel scale
            camera[i].SetPosition(0.0, -1500.0, -500.0)
            camera[i].SetViewUp(0.0, 0.0, 1.0)
        
        if i==2:
            camera[i].ParallelProjectionOn()
            camera[i].SetParallelScale(1000.0) # camera is 1500 mm away from the focal point
            camera[i].SetClippingRange(0.1,3000)
            camera[i].SetPosition(500.0, 0.0,-500.0)
            camera[i].SetViewUp(0.0, 0.0, 1.0)
            
        

balloonWidget.EnabledOn()
renWin.Render()
renWin.SetWindowName('3x1x1 Detector')

style = MouseInteractorHighLightActor()
style.SetDefaultRenderer(renderer[0])
#style.SetDefaultRenderer(renderer[1])
iren.SetInteractorStyle(style)

iren.Initialize()
iren.Start()




