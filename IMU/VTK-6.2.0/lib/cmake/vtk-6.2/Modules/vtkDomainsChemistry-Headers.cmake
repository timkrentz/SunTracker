set(vtkDomainsChemistry_HEADERS_LOADED 1)
set(vtkDomainsChemistry_HEADERS "vtkCMLMoleculeReader;vtkMoleculeAlgorithm;vtkMoleculeMapper;vtkMoleculeToAtomBallFilter;vtkMoleculeToBondStickFilter;vtkMoleculeToPolyDataFilter;vtkPeriodicTable;vtkProgrammableElectronicData;vtkProteinRibbonFilter;vtkSimpleBondPerceiver")

foreach(header ${vtkDomainsChemistry_HEADERS})
  set(vtkDomainsChemistry_HEADER_${header}_EXISTS 1)
endforeach()

set(vtkDomainsChemistry_HEADER_vtkMoleculeToPolyDataFilter_ABSTRACT 1)



