/*=========================================================================

  Program:   Visualization Toolkit
  Module:    vtkGDAL.h

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/
// .NAME vtkGDAL - Shared data for GDAL classes
// .SECTION Description
// .SECTION See Also

#ifndef __vtkGDAL_h
#define __vtkGDAL_h

#include "vtkObject.h"
#include <vtkIOGDALModule.h> // For export macro

class vtkInformationStringKey;

class VTKIOGDAL_EXPORT vtkGDAL : public vtkObject
{
 public:
  // Key used to put GDAL map projection string in the output information
  // by readers.
  static vtkInformationStringKey* MAP_PROJECTION();

 protected:

 private:
  vtkGDAL();  // Static class
  ~vtkGDAL();
  vtkGDAL(const vtkGDAL&); // Not implemented.
  void operator=(const vtkGDAL&); // Not implemented
};

#endif // __vtkGDAL_h
// VTK-HeaderTest-Exclude: vtkGDAL.h
