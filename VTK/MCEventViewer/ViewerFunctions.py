import vtk
import math
class LArSoftToVtkCoord():
    
    # x_vtk is  y larsoft
    # y_vtk is  z larsoft
    # z_vtk is  x larsoft
    #vtk units are in mm while larsoft (geant) are in cm
    #larsoft origin is at the center of the 1 m side of the TPC
    #vtk origin (inported from CAD) is at the center of the CRP

    def GetXVTK(self,x_larsoft,y_larsoft,z_larsoft):
        return y_larsoft*10
    def GetYVTK(self,x_larsoft,y_larsoft,z_larsoft):
        return z_larsoft*10-1500
    def GetZVTK(self,x_larsoft,y_larsoft,z_larsoft):
        return x_larsoft*10-500
    def LArSoftOrigin(self):
        return [0.0, -1500.0, -500.0]
    def VTKOrigin(self):
        return [0.0, 0.0, 0.0]
    def VTKCenterTPC(self): 
        return [0.0, 0.0, -500.0]#returns center of TPC volume in VTK coordinates
    def ReturnAxesActor(self):
        AxesTransform = vtk.vtkTransform()
        AxesTransform.Translate(self.LArSoftOrigin())
        AxesTransform.Scale(1.5, 1.5, 1.5)
        axes = vtk.vtkAxesActor()
        axes.SetUserTransform(AxesTransform)
        axes.GetZAxisTipProperty().SetLineWidth(400)

        axes.SetXAxisLabelText("Y")
        axes.SetYAxisLabelText("Z")
        axes.SetZAxisLabelText("X")

        axes.SetTotalLength(500.0, 2500.0, 500.0)
        axes.SetNormalizedShaftLength(1.0, 1.0, 1.0)
        axes.SetNormalizedTipLength(0.05, 0.05*5/25, 0.05)

        xAxesLabel= axes.GetXAxisCaptionActor2D()
        xAxisLabel=axes.GetXAxisCaptionActor2D()
        xAxisLabel.GetTextActor().SetTextScaleModeToNone()
        xAxisLabel.GetCaptionTextProperty().SetFontSize(50)
        xAxisLabel.GetCaptionTextProperty().SetColor(1,0,0)
        xAxisLabel.GetCaptionTextProperty().ItalicOff

        yAxesLabel=axes.GetYAxisCaptionActor2D()
        yAxisLabel = axes.GetYAxisCaptionActor2D()
        yAxisLabel.GetTextActor().SetTextScaleModeToNone()
        yAxisLabel.GetCaptionTextProperty().SetFontSize(50)
        yAxisLabel.GetCaptionTextProperty().SetColor(0,1,0)
        yAxisLabel.GetCaptionTextProperty().ItalicOff

        zAxesLabel=axes.GetZAxisCaptionActor2D()
        zAxisLabel = axes.GetZAxisCaptionActor2D()
        zAxisLabel.GetTextActor().SetTextScaleModeToNone()
        zAxisLabel.GetCaptionTextProperty().SetFontSize(50)
        zAxisLabel.GetCaptionTextProperty().SetColor(0,0,1)
        zAxisLabel.GetCaptionTextProperty().ItalicOff
        return axes


class MCPoints():
    @staticmethod
    def FillHitsMC(first_hit, last_hit, mydata_mc,iev):
        LineSource=vtk.vtkLineSource()
        inputPoints=vtk.vtkPoints()
#        print"------************************************------------", first_hit, last_hit
        for istp in range (first_hit,last_hit):
            MC_hit_x=mydata_mc.MCTruth_GEANT4_TrajectoryStep_Point_X[iev][istp]
            MC_hit_y=mydata_mc.MCTruth_GEANT4_TrajectoryStep_Point_Y[iev][istp]
            MC_hit_z=mydata_mc.MCTruth_GEANT4_TrajectoryStep_Point_Z[iev][istp]
#            print istp, mydata_mc.MCTruth_GEANT4_PDGCode[iev][istp], "pid:", mydata_mc.MCTruth_GEANT4_ParticleID[iev][istp]
#            step_pid=mydata_mc.MCTruth_GEANT4_TrajectoryStep_ParticleID[iev][istp]
#            step_pdg=mydata_mc.MCTruth_GEANT4_TrajectoryStep_PDGCode[iev][istp]
#            print 
#            print "***", istp, step_pid, step_pdg, MC_hit_x, MC_hit_y, MC_hit_z
            if MC_hit_x<-100 : continue
            if MC_hit_x>100 :continue # don't show track points one meter above center of TPC
            if MC_hit_y>100 :continue # don't show track points one meter to the left of center of TPC
            if MC_hit_y<-100 :continue # don't show track points one meter to the right of center of TPC
            if MC_hit_z>300 :continue # don't show track points one meter to the left of center of TPC
            if MC_hit_z<-100 :continue # don't show track points one meter to the right of center of TPC 
#            print ".----", istp, step_pid, step_pdg, MC_hit_x, MC_hit_y, MC_hit_z, 
            if math.isnan(MC_hit_z): continue
            MC_hit_x_vtk=LArSoftToVtkCoord().GetXVTK(MC_hit_x,MC_hit_y,MC_hit_z)
            MC_hit_y_vtk=LArSoftToVtkCoord().GetYVTK(MC_hit_x,MC_hit_y,MC_hit_z)
            MC_hit_z_vtk=LArSoftToVtkCoord().GetZVTK(MC_hit_x,MC_hit_y,MC_hit_z)
            inputPoints.InsertNextPoint(MC_hit_x_vtk, MC_hit_y_vtk, MC_hit_z_vtk)
        if not inputPoints.GetNumberOfPoints()==0:
            LineSource.SetPoints(inputPoints)
            return LineSource
        
        
class PointsToGlyph():
    def ReturnGlyphActorFromPoints(self, MyPoints , View, SphereRadius, color):
        inputDataGlyph= vtk.vtkPolyData()
        glyphMapper = vtk.vtkPolyDataMapper()
        glyphPoints = vtk.vtkGlyph3D()
        balls = vtk.vtkSphereSource()
        inputDataGlyph.SetPoints(MyPoints)
        balls.SetRadius(SphereRadius)
        balls.SetPhiResolution(10)
        balls.SetThetaResolution(10)
        glyphPoints.SetInputData(inputDataGlyph)
        glyphPoints.SetSourceConnection(balls.GetOutputPort())
        glyphMapper.SetInputConnection(glyphPoints.GetOutputPort())
        glyphActor = vtk.vtkActor()
        glyphActor.SetMapper(glyphMapper)
        glyphActor.GetProperty().SetDiffuseColor(color)        
        glyphActor.GetProperty().SetSpecular(.3)
        glyphActor.GetProperty().SetSpecularPower(30)
        return glyphActor
    
    def ReturnTubeGlyphActorFromPoints(self, MyPoints , MyLines, TubeRadius, color):
        inputDataGlyph= vtk.vtkPolyData()
        glyphMapper = vtk.vtkPolyDataMapper()
#        glyphPoints = vtk.vtkGlyph3D()
        tubes = vtk.vtkTubeFilter()
        inputDataGlyph.SetPoints(MyPoints)
        inputDataGlyph.SetLines(MyLines)
        tubes.SetInputData(inputDataGlyph)
        tubes.SetRadius(TubeRadius)

#        glyphPoints.SetSourceConnection(tubes.GetOutputPort())
        glyphMapper.SetInputConnection(tubes.GetOutputPort())
        glyphActor = vtk.vtkActor()
        glyphActor.SetMapper(glyphMapper)
        glyphActor.GetProperty().SetDiffuseColor(color)        
        glyphActor.GetProperty().SetSpecular(.3)
        glyphActor.GetProperty().SetSpecularPower(30)
        return glyphActor

    def ReturnGlyphActorFromLineSource(self, LineSource, TubeRadius, color):
        inputDataGlyph= vtk.vtkPolyData()
        glyphMapper = vtk.vtkPolyDataMapper()
        glyphMapper.SetInputConnection(LineSource.GetOutputPort())
        glyphActor = vtk.vtkActor()
        glyphActor.SetMapper(glyphMapper)
        glyphActor.GetProperty().SetDiffuseColor(color)        
        glyphActor.GetProperty().SetLineWidth(TubeRadius)
        glyphActor.GetProperty().SetSpecularPower(30)
        return glyphActor
    

class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):
 
    def __init__(self,parent=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
 
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
 
    def leftButtonPressEvent(self,obj,event):
        clickPos = self.GetInteractor().GetEventPosition()
 
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
 
        # get the new
        self.NewPickedActor = picker.GetActor()
#        print self.NewPickedActor.GetProperty().GetOpacity()
        # If something was selected
        if self.NewPickedActor:
            if  self.NewPickedActor.GetProperty().GetOpacity()>.9: # temporary fix to avoid selecting the TPC geometry (it is currently the only transparent geomtry)
                # If we picked something before, reset its property
                if self.LastPickedActor:
                    self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
 
 
                # Save the property of the picked actor so that we can
                # restore it next time
                self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())
                # Highlight the picked actor by changing its properties
                self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                self.NewPickedActor.GetProperty().SetDiffuse(1.0)
                self.NewPickedActor.GetProperty().SetSpecular(0.0)
 
                # save the last picked actor
                self.LastPickedActor = self.NewPickedActor
    
            self.OnLeftButtonDown()
        return
#class ComputeAxes():
    
