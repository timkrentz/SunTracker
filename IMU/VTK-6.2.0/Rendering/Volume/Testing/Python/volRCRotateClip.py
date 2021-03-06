#!/usr/bin/env python
import vtk
from vtk.test import Testing
from vtk.util.misc import vtkGetDataRoot
VTK_DATA_ROOT = vtkGetDataRoot()

# Simple volume rendering example.
reader = vtk.vtkImageReader()
reader.SetDataByteOrderToLittleEndian()
reader.SetDataExtent(0,63,0,63,1,93)
reader.SetFilePrefix("" + str(VTK_DATA_ROOT) + "/Data/headsq/quarter")
reader.SetDataMask(0x7fff)
reader.SetDataSpacing(2,2,1)
reader.SetDataScalarTypeToUnsignedShort()
reader.Update()
readerOutput = reader.GetOutput()
readerOutput.SetOrigin(-63,-63,-46)
# Disconnect the output from its reader.  First get an extra reference.
readerOutput.Register(None)
# Create transfer functions for opacity and color
opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction.AddPoint(600,0.0)
opacityTransferFunction.AddPoint(2000,1.0)
colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.ClampingOff()
colorTransferFunction.AddHSVPoint(0.0,0.01,1.0,1.0)
colorTransferFunction.AddHSVPoint(1000.0,0.50,1.0,1.0)
colorTransferFunction.AddHSVPoint(2000.0,0.99,1.0,1.0)
colorTransferFunction.SetColorSpaceToHSV()
# Create properties, mappers, volume actors, and ray cast function
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorTransferFunction)
volumeProperty.SetScalarOpacity(opacityTransferFunction)
volumeProperty.SetInterpolationTypeToLinear()
f = vtk.vtkVolumeRayCastCompositeFunction()
volumeMapper = vtk.vtkVolumeRayCastMapper()
volumeMapper.SetInputData(readerOutput)
volumeMapper.SetVolumeRayCastFunction(f)
volumeMapper.SetSampleDistance(0.3)
# The data object is now referenced by the connection.
readerOutput.UnRegister(None) # not needed in python
volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)
# Create geometric sphere
sphereSource = vtk.vtkSphereSource()
sphereSource.SetRadius(65)
sphereSource.SetThetaResolution(20)
sphereSource.SetPhiResolution(40)
def colorCells (__vtk__temp0=0,__vtk__temp1=0):
    randomColorGenerator = vtk.vtkMath()
    input = randomColors.GetInput()
    output = randomColors.GetOutput()
    numCells = input.GetNumberOfCells()
    colors = vtk.vtkFloatArray()
    colors.SetNumberOfTuples(numCells)
    i = 0
    while i < numCells:
        colors.SetValue(i,randomColorGenerator.Random(0,1))
        i = i + 1

    output.GetCellData().CopyScalarsOff()
    output.GetCellData().PassData(input.GetCellData())
    output.GetCellData().SetScalars(colors)
    del colors
    #reference counting - it's ok
    del randomColorGenerator

# Compute random scalars (colors) for each cell
randomColors = vtk.vtkProgrammableAttributeDataFilter()
randomColors.SetInputConnection(sphereSource.GetOutputPort())
randomColors.SetExecuteMethod(colorCells)
sphereMapper = vtk.vtkPolyDataMapper()
sphereMapper.SetInputConnection(randomColors.GetOutputPort())
sphereActor = vtk.vtkActor()
sphereActor.SetMapper(sphereMapper)
# Set up the planes
plane1 = vtk.vtkPlane()
plane1.SetOrigin(0,0,-10)
plane1.SetNormal(0,0,1)
plane2 = vtk.vtkPlane()
plane2.SetOrigin(0,0,10)
plane2.SetNormal(0,0,-1)
plane3 = vtk.vtkPlane()
plane3.SetOrigin(-10,0,0)
plane3.SetNormal(1,0,0)
plane4 = vtk.vtkPlane()
plane4.SetOrigin(10,0,0)
plane4.SetNormal(-1,0,0)
sphereMapper.AddClippingPlane(plane1)
sphereMapper.AddClippingPlane(plane2)
volumeMapper.AddClippingPlane(plane3)
volumeMapper.AddClippingPlane(plane4)
# Okay now the graphics stuff
ren1 = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren1)
renWin.SetSize(256,256)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
ren1.GetCullers().InitTraversal()
culler = ren1.GetCullers().GetNextItem()
culler.SetSortingStyleToBackToFront()
ren1.AddViewProp(sphereActor)
ren1.AddViewProp(volume)
ren1.SetBackground(0.1,0.2,0.4)
renWin.Render()
ren1.GetActiveCamera().Azimuth(45)
ren1.GetActiveCamera().Elevation(15)
ren1.GetActiveCamera().Roll(45)
ren1.GetActiveCamera().Zoom(2.0)
iren.Initialize()
i = 0
while i < 5:
    volume.RotateY(17)
    volume.RotateZ(13)
    sphereActor.RotateX(13)
    sphereActor.RotateY(17)
    i = i + 1

renWin.Render()
# --- end of script --
