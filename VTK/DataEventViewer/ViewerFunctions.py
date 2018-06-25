import vtk

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

#class ComputeAxes():
    
