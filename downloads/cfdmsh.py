"""
++++++++++ 
+ CFDMSH +
++++++++++ 

Python Library for CFD Meshing with Salome Platform

Author: Tougeron W. (www.tougeron-cfd.com)

Licence: GNU General Public License
"""

version = "4.0"

import salome, salome.geom.geomtools

import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New(salome.myStudy)

import SMESH, SALOMEDS
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New(salome.myStudy)
from salome.StdMeshers import StdMeshersBuilder

#import numpy
import time
import random
import ast
import csv
import os
import math

#### Here are internal functions ####

def ListComponentShapes( comp = "GEOM", output = "name", rec = True ):
	"""
	
	
Description:
	Gives the list of all objects published in a Salome component, being GEOM or SMESH.
	

Arguments:
	# comp 
		Description:       The name of the component : "GEOM" or "SMESH". 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "GEOM"  

	# output 
		Description:       Defines if the returned values should be the "name" or the "id" of the found shapes. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "name"  

	# rec 
		Description:       If equals False, the function will only iterate over the first level of the study tree. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           String 
	Number:         n 
	Name:           -  

Conditions of use:
	-
	

"""
	
	# Make this function recursive
	
	if isinstance(comp, list):
		
		return_list = []
		
		for sub_object in comp:
			
			return_list.append(ListComponentShapes(sub_object, output, rec))
			
		
		return return_list
		
	
	#-
	
	if comp not in ["GEOM", "SMESH"]:
		
		return []
		
	
	component = salome.myStudy.FindComponent(comp)
	
	sub_shape_list = []
	
	try:
		
		child_iterator = salome.myStudy.NewChildIterator(component)
		
		child_iterator.InitEx(rec)
		
		while(child_iterator.More()):
			
			sub_object = child_iterator.Value()
			
			if sub_object.GetAllAttributes():
				
				if output == "name":
					
					sub_shape = sub_object.GetName()
					
				
				elif output in ["id", "ID"]:
					
					sub_shape = salome.ObjectToID(sub_object.GetObject())
					
				
				else:
					
					sub_shape = None
					
				
				sub_shape_list.append(sub_shape)
				
			
			child_iterator.Next()
			
		
	
	except:
		
		pass
		
	
	return sub_shape_list
	

lcs = ListComponentShapes

def CheckObjectExistence( name, comp = "GEOM" ):
	"""
	
	
Description:
	Checks if an object is already published in the study tree, according to its name and component.
	

Arguments:
	# name 
		Description:       The name of the shape. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# comp 
		Description:       The name of the component : "GEOM" or "SMESH". 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "GEOM"  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Boolean 
	Number:         1 
	Name:           -  

Conditions of use:
	-
	

"""
	
	# Make this function recursive
	
	if isinstance(name, list):
		
		return_list = []
		
		for sub_object in name:
			
			return_list.append(CheckObjectExistence(sub_object, comp))
			
		
		return return_list
		
	
	#-
	
	else:
		
		# Get the existing names
		
		name_list = ListComponentShapes(comp)
		
		#-
		
		# Check the object existence
		
		if name == None:
			
			return None
			
		
		elif name in name_list:
			
			return True
			
		
		else:
			
			return False
			
		
		#-
		
	

coe = CheckObjectExistence

def GetNextNameIndex( name, comp = "GEOM" ):
	"""
	
	
Description:
	Gives the next name index of a given name to be published in the study tree.
	

Arguments:
	# name 
		Description:       The name of the shape. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# comp 
		Description:       The name of the component : "GEOM" or "SMESH". 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "GEOM"  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Integer 
	Number:         1 
	Name:           -  

Conditions of use:
	-
	

"""
	
	# Get the existing names
	
	name_list = ListComponentShapes(comp)
	
	#-
	
	name += "_"
	
	# Get the existing indexes
	
	existing_indexes = []
	
	for existing_name in name_list:
		
		if existing_name.find(name) != -1:
			
			name_ending = existing_name.split(name)[1]
			
			try:
				
				index = int(name_ending)
				
				existing_indexes.append(index)
				
			
			except:
				
				pass
				
			
		
	
	#-
	
	# Sort the existing indexes list
	
	existing_indexes = list(set(existing_indexes))
	
	existing_indexes.sort()
	
	#-
	
	# Get the next index
	
	i = 1
	
	for existing_index in existing_indexes:
		
		if existing_index != i:
			
			break
			
		
		i += 1
		
	
	next_index = str(i)
	
	#-
	
	# Return the index
	
	return next_index
	
	#-
	

gnni = GetNextNameIndex

def AddToStudy( object, name = "Geometrical Object", father = None, suffix = True, disp = True, refresh = True ):
	"""
	
	
Description:
	Flexibly publishes an object in the study tree.
	

Arguments:
	# object 
		Description:       The object to publish. 
		Type:              Any geometrical object 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         yes 
		Default value:     -  

	# name 
		Description:       The name to give to the shape in the study tree. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "Geometrical Object"  

	# father 
		Description:       The geometrical shape in which to add the published shape. 
		Type:              Any geometrical object 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     None  

	# suffix 
		Description:       Determines if a suffix (eg. "_1") as to be added to the name of the shape to publish. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# disp 
		Description:       Determines if the shape has to be displayed in the 3D window after publication. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# refresh 
		Description:       Determines if the study tree has to be refreshed after publication. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	-
	

"""
	
	if isinstance(object, list):
		
		for sub_object in object:
			
			AddToStudy(sub_object, name, father, suffix, disp, refresh)
			
		
	
	else:
		
		if not isinstance(name, str):
			
			name = str(name)
			
		
		if suffix == True:
			
			index = GetNextNameIndex(name)
			
			name += "_"
			
			name += index
			
		
		if father == None:
			
			id = geompy.addToStudy(object, name)
			
		
		else:
			
			id = geompy.addToStudyInFather(father, object, name)
			
		
		if refresh == True:
			
			if disp == True:
				
				gg = salome.ImportComponentGUI("GEOM")
				
				gg.createAndDisplayGO(id)
				
			
			else:
				
				if salome.sg.hasDesktop():
					
					salome.sg.updateObjBrowser(1)
					
				
			
		
	

ats = AddToStudy

def GetObject( object = None, comp = "GEOM", silent = False ):
	"""
	
	
Description:
	Gets a published object, according to its name in the study tree and its component.
	

Arguments:
	# object 
		Description:       The name of the object to get. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# comp 
		Description:       The name of the component : "GEOM" or "SMESH". 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "GEOM"  

	# silent 
		Description:       Determines if the error message, in case no object was found, has to be hidden or not. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Any object 
	Number:         1 
	Name:           -  

Conditions of use:
	-
	

"""
	
	# Make this function recursive
	
	if isinstance(object, list):
		
		return_list = []
		
		for sub_object in object:
			
			return_list.append(GetObject(sub_object, comp, silent))
			
		
		return return_list
		
	
	#-
	
	if isinstance(object, str):
		
		if CheckObjectExistence(object, comp):
			
			object = salome.myStudy.FindObjectByName(object, comp)[0].GetObject()
			
		
		else:
			
			if silent == False:
				
				print "[X] The object", object, "doesn't exist in the study tree."
				
			
			return "error"
			
		
	
	return object
	

go = GetObject

def GetSubShapes( shape ):
	"""
	
	
Description:
	Gets all sub-vertexes, sub-edges, sub-faces and sub-solids of a geometrical shape.
	

Arguments:
	# shape 
		Description:       The shape from which to get sub shapes. 
		Type:              Any geometrical object 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Geometrical object or List of Geometrical objects (see the "Additional Information") 
	Number:         5 
	Name:           -  

Conditions of use:
	-
	

"""
	
	# Make this function recursive
	
	if isinstance(shape, list):
		
		return_list = []
		
		for sub_shape in shape:
			
			return_list.append(GetSubShapes(sub_shape))
			
		
		return return_list
		
	
	#-
	
	shape_vertexes = geompy.SubShapeAll(shape, geompy.ShapeType["VERTEX"])
	shape_edges = geompy.SubShapeAll(shape, geompy.ShapeType["EDGE"])
	shape_faces = geompy.SubShapeAll(shape, geompy.ShapeType["FACE"])
	shape_solids = geompy.SubShapeAll(shape, geompy.ShapeType["SOLID"])
	
	return [shape_vertexes, shape_edges, shape_faces, shape_solids, shape]
	

gss = GetSubShapes

def GetGUISelection( shape = None, uniq = False ):
	"""
	
	
Description:
	Gets the objects selected in the GUI.
	

Arguments:
	# shape 
		Description:       The input shape. If different that None, this shape is returned instead of the GUI selection. 
		Type:              Any object 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     None  

	# uniq 
		Description:       Allows to restrict the number of returned objects to one. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Any object 
	Number:         n 
	Name:           -  

Conditions of use:
	-
	

"""
	
	if shape == None or shape == [None]:
		
		selected_object_ids = salome.sg.getAllSelected()
		
		if len(selected_object_ids) > 0:
			
			selected_objects = []
			
			for selected_object_id in selected_object_ids:
				
				selected_objects.append(salome.myStudy.FindObjectID(selected_object_id).GetObject())
				
			
			if (shape == None and len(selected_objects) == 1) or (uniq == True):
				
				shape = selected_objects[0]
				
				if len(selected_objects) > 1 and uniq == True:
					
					print "[i] Only one object processed over " + str(len(selected_object_ids)) + "."
					
				
			
			else:
				
				shape = selected_objects
				
			
		
	
	return shape
	

ggs = GetGUISelection

def PrintDefinedFunctions( cond = False ):
	"""
	
	
Description:
	Displays the list of all available cfdmsh functions.
	

Arguments:
	# cond 
		Description:       Allows to display the function names in condensed mode. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	-
	

"""
	
	if cond == True:
		
		print """ListComponentShapes
CheckObjectExistence
GetNextNameIndex
AddToStudy
GetObject
GetSubShapes
GetGUISelection
PrintDefinedFunctions
PrintVersion
GetBoundaryVertexes
GetReorderedEdges
GetNormalizedVector
GetCrossProduct
GetDotProduct
GetTurnAngle
GeometricalEquality
GetBoundaryFaces
GetTriEdgeFaces
RebuildSpline
SplitEdge
DiscretizeEdgeByCurvature
FuseSplines
ExtendSpline
ExtendSplinesToIntersection
FuseSplineSets
UnrefineSplineSet
SwitchSplineSet
RebuildFace
FuseCoplanarFaces
FuseShellFaces
FuseGroupFaces
RemoveFaceExtraEdges
MakeFoilTrailingFillets
MakeMiddleSpline
MakeCurveFromUnsortedVertexes
MakeEllipticalFilling
MakeFillingFromUnsortedEdges
MakeFoilFromUnsortedVertexes
MakeEdgeOffset
MakePlanarWireOffset
CloseViscousLayer
ExtendViscousLayer
PropagateViscousLayerIntersection
MakeTipViscousLayer
CloseTipViscousLayer
ExtendTipViscousLayer
MakeLinkingSolids
CopyGeometricalGroups
ExportGeometricalGroups
ImportGeometricalGroups
PutAllSubShapesInAGroup
SetRandomColors
ExportCSVFile
ImportCSVFile
MakeVirtualOffsetEdgeSubmeshes
MakeTriEdgeFaceSubmeshes
ProjectEdgeSubmesh
MakeNetgenRefinement
SetNetgenRefinement
ClearNetgenRefinement
ProjectMeshGroupOnFace
MakeVertexesFromMeshGroup
RotateFlapGenerateAndExportMeshInAmshFormat
ViscousLayerScaleFactor
ExportMeshConfiguration
ImportMeshConfiguration
ExportHypotheses
ImportHypotheses
ExportAmshFile
ExportSU2File"""
		
	
	else:
		
		print """
Defined Functions:

Internal Functions
==================

	List Component Shapes
	Check Object Existence
	Get Next Name Index
	Add To Study
	Get Object
	Get Sub Shapes
	Get GUI Selection
	Print Defined Functions
	Print Version

Geometry Module
===============

Measurement
...........

Edges

	Get Boundary Vertexes
	Get Reordered Edges

Vectors

	Get Normalized Vector
	Get Cross Product
	Get Dot Product
	Get Turn Angle

Any Shape

	Geometrical Equality
	Get Boundary Faces
	Get Tri Edge Faces

Repair
......

Splines or Edges

	Rebuild Spline
	Split Edge
	Discretize Edge By Curvature
	Fuse Splines
	Extend Spline
	Extend Splines To Intersection

Spline Sets

	Fuse Spline Sets
	Unrefine Spline Set
	Switch Spline Set

Faces

	Rebuild Face
	Fuse Coplanar Faces
	Fuse Shell Faces
	Fuse Group Faces
	Remove Face Extra Edges

Foils

	Make Foil Trailing Fillets

Basic Geometry Generation
.........................

Splines

	Make Middle Spline
	Make Curve From Unsorted Vertexes

Faces

	Make Elliptical Filling
	Make Filling From Unsorted Edges

Foils

	Make Foil From Unsorted Vertexes

Viscous Layer Generation
........................

2D

	Make Edge Offset
	Make Planar Wire Offset
	Extend Viscous Layer
	Close Viscous Layer
	Propagate Viscous Layer Intersection

3D

	Make Tip Viscous Layer
	Extend Tip Viscous Layer
	Close Tip Viscous Layer
	Make Linking Solids

Group Management
................

	Copy Geometrical Groups
	Export Geometrical Groups
	Import Geometrical Groups
	Put All Sub Shapes In A Group

Rendering
.........

	Set Random Colors

Import / Export
...............

	Export CSV File
	Import CSV File

Geometry + Mesh modules
=======================

Viscous Layer Meshing
.....................

	Make Virtual Offset Edge Submesh
	Make Tri Edge Face Submeshes
	Project Edge Submesh

Netgen Refinement
.................

	Make Netgen Refinement
	Set Netgen Refinement
	Clear Netgen Refinement

Mesh Repair
...........

	Project Mesh Group On Face

Mesh to Geometry Conversion
...........................

	Make Vertexes From Mesh Group 

Parametric Meshing
..................

	Rotate Flap Generate And Export Mesh In Amsh Format

Mesh Module
===========

Viscous Layer Meshing
.....................

	Viscous Layer Scale Factor

Mesh Management
...............

	Export Mesh Configuration
	Import Mesh Configuration

Hypothesis Management
.....................

	Export Hypotheses
	Import Hypotheses

Mesh Export
...........

	Export Amsh File
	Export SU2 File
"""
	

pdf = PrintDefinedFunctions

def PrintVersion(  ):
	"""
	
	
Description:
	Displays the cfdmsh version.
	

Arguments:
	# - 
		Description:       - 
		Type:              - 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	-
	

"""
	
	print "Version:"
	
	print version
	

pv = PrintVersion

#### - ####

#### Here are beta cfdmsh functions ####

#### - ####

def GetBoundaryVertexes( wire = None, tol = 1e-7, single = True, add = True, infa = True ):
	"""
	
	
Description:
	Gets boundary vertexes from a wire and put them into a group.
	

Arguments:
	# wire 
		Description:       The input wire. 
		Type:              Wire 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: False 
	Type:           Vertex 
	Number:         2 
	Name:           "BoundaryVertex"  

	"dim" value:    - 
	"single" value: True 
	Type:           Compound or Group of Vertexes 
	Number:         1 
	Name:           "BoundaryVertexes"  

Conditions of use:
	-
	

"""
	
	input_shape = wire
	
	# Get the input shape(s)
	
	input_shape = GetGUISelection(input_shape)
	
	input_shape = GetObject(input_shape)
	
	#-
	
	# Make this function recursive
	
	if isinstance(input_shape, list):
		
		return_list = []
		
		for sub_object in input_shape:
			
			return_list.append(GetBoundaryVertexes(sub_object, tol, single, add, infa))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [input_shape] or None in [input_shape]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = input_shape
	
	#-
	
	wire = input_shape
	
	if False: pass
	
	else:# All checks done
		
		# Get the sub-shapes
		
		wire_edge_list = geompy.SubShapeAll(wire, geompy.ShapeType["EDGE"])
		
		wire_vertex_list = geompy.SubShapeAll(wire, geompy.ShapeType["VERTEX"])
		
		#-
		
		# Get the boundary vertexes
		
		boundary_vertex_list = []
		for vertex in wire_vertex_list:
			
			nb_touching_edges = 0
			for edge in wire_edge_list:
				
				distance = geompy.MinDistance(edge, vertex)
				
				if distance < tol:
					
					nb_touching_edges += 1
					
				
			
			if nb_touching_edges == 1:
				
				boundary_vertex_list.append(vertex)
				
			
		
		#-
		
		# Detect closed wire
		
		if len(boundary_vertex_list) < 2:
			
			boundary_vertex_list = []
			
		
		#-
		
		if len(boundary_vertex_list) == 0:
			
			return
			
		
		to_return = boundary_vertex_list
		to_return_name = "BoundaryVertexes"
		
		if single == True:
			
			to_return_name = "BoundaryVertex"
			
			if infa == True:
				
				# Create the boundary vertex group
				
				boundary_vertex_group = geompy.CreateGroup(father, geompy.ShapeType["VERTEX"])
				
				#-
				
				for boundary_vertex in boundary_vertex_list:# For each boundary vertex...
					
					# Get the boundary vertex ID
					
					boundary_vertex_id = geompy.GetSubShapeID(father, boundary_vertex)
					
					#-
					
					# Put the boundary vertex in the group
					
					geompy.AddObject(boundary_vertex_group, boundary_vertex_id)
					
					#-
					
				
				to_return = boundary_vertex_group
				
			
			else:
				
				compound = geompy.MakeCompound(boundary_vertex_list)
				
				to_return = compound
				
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(to_return, to_return_name, father)
			
		
		return to_return
		
		#-
		
	

gbv = GetBoundaryVertexes

def GetReorderedEdges( wire = None, tol = 1e-9, add = True, infa = False ):
	"""
	
	
Description:
	Gets reordered edges from a wire, starting from one of its boundaries if open.
	

Arguments:
	# wire 
		Description:       The input wire. 
		Type:              Wire 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Edge 
	Number:         n 
	Name:           "ReorderedEdge"  

Conditions of use:
	-
	

"""
	
	input_shape = wire
	
	# Get the input shape(s)
	
	input_shape = GetGUISelection(input_shape)
	
	input_shape = GetObject(input_shape)
	
	#-
	
	# Make this function recursive
	
	if isinstance(input_shape, list):
		
		return_list = []
		
		for sub_object in input_shape:
			
			return_list.append(GetReorderedEdges(sub_object, tol, add, infa))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [input_shape] or None in [input_shape]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = input_shape
	
	#-
	
	wire = input_shape
	
	if False: pass
	
	else:# All checks done
		
		resting_edges = geompy.SubShapeAll(wire, geompy.ShapeType["EDGE"])
		nb_edges = len(resting_edges)
		
		# Get boundary vertexes
		
		boundary_vertexes = GetBoundaryVertexes(wire, add = False, single = False)
		
		#-
		
		# Check if the wire is closed
		
		wire_is_closed = False
		if boundary_vertexes == None:
			
			wire_is_closed = True
			
		
		#-
		
		# Detect the first edge
		
		found = False
		
		if wire_is_closed == False:
			
			boundary_vertex = boundary_vertexes[0]
			
			for i in range(nb_edges):
				
				the_edge = resting_edges[i]
				
				distance = geompy.MinDistance(the_edge, boundary_vertex)
				
				if distance <= tol:
					
					first_edge = resting_edges.pop(i)
					
					found = True
					
					break
				
			
			
		
		if found == False:
			
			first_edge = resting_edges.pop()
			
		
		#-
		
		first_edge_vertexes = geompy.SubShapeAll(first_edge, geompy.ShapeType["VERTEX"])
		first_edge_vertex_compound = geompy.MakeCompound(first_edge_vertexes)
		
		# Sort the resting edges
		
		sorted_edges = [first_edge]
		n = 0
		while len(resting_edges) > 0:
			
			i = 0
			for edge in resting_edges:
				
				edge_vertexes = geompy.SubShapeAll(edge, geompy.ShapeType["VERTEX"])
				edge_vertex_compound = geompy.MakeCompound(edge_vertexes)
				
				distance = geompy.MinDistance(first_edge_vertex_compound, edge_vertex_compound)
				
				if distance <= tol:
					
					first_vertex = geompy.MakeVertexOnCurve(edge, 0.0)
					last_vertex = geompy.MakeVertexOnCurve(first_edge, 1.0)
					
					distance = geompy.MinDistance(first_vertex, last_vertex)
					
					first_edge = resting_edges.pop(i)
					
					if distance > tol:
						first_edge = geompy.ChangeOrientation(first_edge)
						
					first_edge_vertexes = geompy.SubShapeAll(first_edge, geompy.ShapeType["VERTEX"])
					first_edge_vertex_compound = geompy.MakeCompound(first_edge_vertexes)
					
					sorted_edges.append(first_edge)
					
					break
				i += 1
			
			if n >= 9999:
				
				print "[X] Infinite loop during edge reordering."
				
				break
				
			
			n += 1
			
		
		#-
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(sorted_edges, "ReorderedEdge", father)
			
		
		return sorted_edges
		
		#-
		
	

gre = GetReorderedEdges

def GetNormalizedVector( vector = None, add = True, infa = False ):
	"""
	
	
Description:
	Normalizes a 3D vector.
	

Arguments:
	# vector 
		Description:       The input vector. 
		Type:              Vector 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Vector 
	Number:         1 
	Name:           "NormalizedVector"  

Conditions of use:
	-
	

"""
	
	input_shape = vector
	
	# Get the input shape(s)
	
	input_shape = GetGUISelection(input_shape)
	
	input_shape = GetObject(input_shape)
	
	#-
	
	# Make this function recursive
	
	if isinstance(input_shape, list):
		
		return_list = []
		
		for sub_object in input_shape:
			
			return_list.append(GetNormalizedVector(sub_object, add, infa))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [input_shape] or None in [input_shape]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = input_shape
	
	#-
	
	vector = input_shape
	
	if False: pass
	
	else:# All checks done
		
		base_vertex = geompy.MakeVertexOnCurve(vector, 0)
		
		magnitude = geompy.BasicProperties(vector)[0]
		
		normalized_vector = geompy.MakeScaleTransform(vector, base_vertex, 1.0 / magnitude)
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(normalized_vector, "NormalizedVector")
			
		
		return normalized_vector
		
		#-
		
	

gnv = GetNormalizedVector

def GetCrossProduct( vector_1, vector_2, tol = 1e-7, add = True ):
	"""
	
	
Description:
	Computes the cross product between two 3D vectors.
	

Arguments:
	# vector_1 
		Description:       The first vector. 
		Type:              Vector 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# vector_2 
		Description:       The second vector. 
		Type:              Vector 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Vector 
	Number:         1 
	Name:           "CrossProduct"  

Conditions of use:
	-
	

"""
	
	input_shapes = [vector_1, vector_2]
	
	# Get the input shape(s)
	
	input_shapes = GetObject(input_shapes)
	
	#-
	
	# Check the input shape existence
	
	if "error" in input_shapes or None in input_shapes: return
	
	#-
	
	[vector_1, vector_2] = input_shapes
	
	if False: pass
	
	else:# All checks done
		
		base_vertex = geompy.MakeVertexOnCurve(vector_1, 0)
		origin = geompy.MakeVertex(0, 0, 0)
		
		c1 = geompy.VectorCoordinates(vector_1)
		c2 = geompy.VectorCoordinates(vector_2)
		
		x = c1[1] * c2[2] - c1[2] * c2[1]
		y = c1[2] * c2[0] - c1[0] * c2[2]
		z = c1[0] * c2[1] - c1[1] * c2[0]
		
		vector_product_norm = math.sqrt(pow(x,2) + pow(y,2) + pow(z,2))
		
		if vector_product_norm > tol:
			
			vector_product = geompy.MakeVectorDXDYDZ(x, y, z)
			
			vector_product = geompy.MakeTranslationTwoPoints(vector_product, origin, base_vertex)
			
		
		else:
			
			vector_product = None
			
		
		# Add and return the resulting shape(s)
		
		if add == True and vector_product != None:
			
			AddToStudy(vector_product, "CrossProduct")
			
		
		return vector_product
		
		#-
		
	

gcp = GetCrossProduct

def GetDotProduct( vectors = [None] ):
	"""
	
	
Description:
	Computes the dot product between two 3D vectors.
	

Arguments:
	# vectors 
		Description:       The input vectors. 
		Type:              List of 2 Vectors 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Float 
	Number:         1 
	Name:           -  

Conditions of use:
	-
	

"""
	
	if isinstance(vectors, list) == False: print "[X] The first argument (vectors) should be an array."; return
	
	input_shapes = vectors
	
	# Get the input shape(s)
	
	input_shapes = GetGUISelection(input_shapes)
	
	input_shapes = GetObject(input_shapes)
	
	#-
	
	# Check the input shape existence
	
	if "error" in input_shapes or None in input_shapes: return
	
	#-
	
	# Check the number of selected objects
	
	if len(input_shapes) != 2:
		
		print "[X] Two shapes should be selected."
		
		return
		
	
	#-
	
	vectors = input_shapes
	
	if False: pass
	
	else:# All checks done
		
		c1 = geompy.VectorCoordinates(vectors[0])
		c2 = geompy.VectorCoordinates(vectors[1])
		
		dot_product = c1[0] * c2[0] + c1[1] * c2[1] + c1[2] * c2[2]
		
		return dot_product
		
	

gdp = GetDotProduct

def GetTurnAngle( vector_1, vector_2, normal, unit = "rad" ):
	"""
	
	
Description:
	Gets the "turn angle" between two vectors.
	

Arguments:
	# vector_1 
		Description:       The first vector. 
		Type:              Vector 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# vector_2 
		Description:       The second vector. 
		Type:              Vector 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# normal 
		Description:       The reference vector indicating the angle orientation, being normal to other input vectors. 
		Type:              Vector 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# unit 
		Description:       Defines the return unit. Can equal "rad" or "deg". 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "rad"  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Float 
	Number:         1 
	Name:           -  

Conditions of use:
	-
	

"""
	
	input_shapes = [vector_1, vector_2, normal]
	
	# Get the input shape(s)
	
	input_shapes = GetObject(input_shapes)
	
	#-
	
	# Check the input shape existence
	
	if "error" in input_shapes or None in input_shapes: return
	
	#-
	
	[vector_1, vector_2, normal] = input_shapes
	
	if False: pass
	
	else:# All checks done
		
		vector_1 = GetNormalizedVector(vector_1, add = False)
		vector_2 = GetNormalizedVector(vector_2, add = False)
		
		dot_product = GetDotProduct([vector_1, vector_2])
		
		vector_product = GetCrossProduct(vector_1, vector_2, add = False)
		
		if vector_product == None:
			
			coord_1 = geompy.VectorCoordinates(vector_1)
			coord_2 = geompy.VectorCoordinates(vector_2)
			
			vertex_1 = geompy.MakeVertex(coord_1[0], coord_1[1], coord_1[2])
			vertex_2 = geompy.MakeVertex(coord_2[0], coord_2[1], coord_2[2])
			
			distance = geompy.MinDistance(vertex_1, vertex_2)
			
			tol = 0.1
			if distance < tol:
				
				angle = 0.0
				
			
			else:
				
				angle = math.pi
				
			
		
		else:
			
			angle = math.acos(dot_product)
			
			if GetDotProduct([vector_product, normal]) < 0:
				
				angle = 2 * math.pi - angle
				
			
		
		if unit != "rad":
			
			angle = angle / math.pi * 180.0
		
		return angle
		
	

gta = GetTurnAngle

def GeometricalEquality( shapes = [None], tol = 1e-7 ):
	"""
	
	
Description:
	Compares the shapes of two geometrical objects.
	

Arguments:
	# shapes 
		Description:       Geometrical objects to be compared. 
		Type:              List of 2 Geometrical objects 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# tol 
		Description:       Maximum difference allowed between all the shape parameters. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Boolean 
	Number:         1 
	Name:           -  

Conditions of use:
	-
	

"""
	
	if isinstance(shapes, list) == False: print "[X] The first argument (shapes) should be an array."; return
	
	# Get the input shape(s)
	
	shapes = GetGUISelection(shapes)
	
	shapes = GetObject(shapes)
	
	#-
	
	# Check the input shape existence
	
	if "error" in shapes or None in shapes: return
	
	#-
	
	# Check the number of selected objects
	
	if len(shapes) != 2:
		
		print "[X] Two shapes should be selected."
		
		return
		
	
	#-
	
	else:# All checks done
		
		is_equal = False
		
		# Check the centers of mass
		
		centers_of_mass = [
			geompy.MakeCDG(shapes[0]), 
			geompy.MakeCDG(shapes[1])
		]
		
		distance = geompy.MinDistance(centers_of_mass[1], centers_of_mass[0])
		
		#-
		
		if distance <= tol:# If they are equals...
			
			# Check the basic properties
			
			basic_properties = [
				geompy.BasicProperties(shapes[0]), 
				geompy.BasicProperties(shapes[1])
			]
			
			for i in range(len(basic_properties[0])):
				
				difference = abs(basic_properties[1][i] - basic_properties[0][i])
				
				if difference > tol:
					
					break
					
				
			
			#-
			
			if i == len(basic_properties[0]) - 1:# If they are equal...
			
				# Check the inertia matrices
				
				inertia_matrices = [
				geompy.Inertia(shapes[0]), 
				geompy.Inertia(shapes[1])
				]
				
				for i in range(len(inertia_matrices[0])):
					
					difference = abs(inertia_matrices[1][i] - inertia_matrices[0][i])
					
					if difference > tol:
						
						break
						
					
				
				#-
				
				if i == len(inertia_matrices[0]) - 1:# If they are equal...
					
					# Say the shapes are equal
					
					is_equal = True
					
					#-
					
				
			
		
		# Return the result
		
		return is_equal
		
		#-
		
	

ge = GeometricalEquality

def GetBoundaryFaces( compound = None, single = True, add = True, infa = True ):
	"""
	
	
Description:
	Get the boundary faces of a solid compound and put them in a group.
	

Arguments:
	# compound 
		Description:       The input compound of solids. 
		Type:              Compound of Solids 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: False 
	Type:           Face 
	Number:         n 
	Name:           "BoundaryVertex"  

	"dim" value:    - 
	"single" value: True 
	Type:           Compound or Group of Faces 
	Number:         1 
	Name:           "BoundaryVertexes"  

Conditions of use:
	-
	

"""
	
	# Get the input shape(s)
	
	compound = GetGUISelection(compound)
	
	compound = GetObject(compound)
	
	#-
	
	# Make this function recursive
	
	if isinstance(compound, list):
		
		return_list = []
		
		for sub_object in compound:
			
			return_list.append(GetBoundaryFaces(sub_object, single, add, infa))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [compound] or None in [compound]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = compound
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the sub-shapes
		
		compound = GetSubShapes(compound)
		
		#-
		
		# Get the boundary face IDs
		
		boundary_face_ids = geompy.GetFreeFacesIDs(compound[-1])
		
		#-
		
		# Create the boundary face group
		
		boundary_face_group = geompy.CreateGroup(compound[-1], geompy.ShapeType["FACE"])
		
		#-
		
		boundary_face_list = []
		for face in compound[2]:# For each face of the compound...
			
			# Get the face ID
			
			face_id = geompy.GetSubShapeID(compound[-1], face)
			
			#-
			
			# Put the face in the group
			
			if face_id in boundary_face_ids:
				
				geompy.AddObject(boundary_face_group, face_id)
				boundary_face_list.append(face)
				
			
			#-
			
		
		to_return = boundary_face_list
		to_return_name = "BoundaryFace"
		
		if single == True:
			
			to_return_name = "BoundaryFaces"
			
			if infa == True:
				
				to_return = boundary_face_group
				
			
			else:
				
				compound = geompy.MakeCompound(boundary_face_list)
				
				to_return = compound
				
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, father, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
	

gbf = GetBoundaryFaces

def GetTriEdgeFaces( shape = None, tol = 1e-7, add = True ):
	"""
	
	
Description:
	Get all the surfaces having three edges and put them in separated groups.
	

Arguments:
	# shape 
		Description:       The shape in which to look for tri-edge faces. 
		Type:              Any geometrical object 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Group of Faces 
	Number:         n 
	Name:           "TriEdgeFace"  

Conditions of use:
	-
	

"""
	
	# Get the input shape(s)
	
	shape = GetGUISelection(shape)
	
	shape = GetObject(shape)
	
	#-
	
	# Make this function recursive
	
	if isinstance(shape, list):
		
		return_list = []
		
		for sub_object in shape:
			
			return_list.append(GetTriEdgeFaces(sub_object, tol, add))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [shape] or None in [shape]: return
	
	#-
	
	else:# All checks done
		
		# Get the sub-shapes
		
		shape = GetSubShapes(shape)
		
		#-
		
		# Get the triangles
		
		shape_triangles = []
		
		for shape_face in shape[2]:
			
			shape_face_description = geompy.WhatIs(shape_face)
			
			if "EDGE : 3" in shape_face_description:
				
				shape_triangles.append(shape_face)
				
			
		
		#-
		
		# Create groups
		
		shape_triangle_groups = []
		
		for shape_triangle in shape_triangles:# For each list of adjacent triangles...
			
			# Create a group
			
			new_group = geompy.CreateGroup(shape[-1], geompy.ShapeType["FACE"])
			
			#-
			
			# Get the ID of the triangle
			
			shape_triangle_id = geompy.GetSubShapeID(shape[-1], shape_triangle)
			
			#-
			
			# Add the triangle to the group
			
			geompy.AddObject(new_group, shape_triangle_id)
			
			#-
			
			# Add the group to the list
			
			shape_triangle_groups.append(new_group)
			
			#-
			
		
		#-
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			for shape_triangle_group in shape_triangle_groups:
				
				AddToStudy(shape_triangle_group, "TriEdgeFace", father = shape[-1])
				
			
		
		return shape_triangle_groups
		
		#-
		
	

gtef = GetTriEdgeFaces

def RebuildSpline( np = 20, edge = None, single = True, add = True, infa = False, dim = 1 ):
	"""
	
	
Description:
	Rebuilds an edge with a spline.
	

Arguments:
	# np 
		Description:       See here. In addition, the value of this argument can be a list of parameters (from 0.0 to 1.0) which will be used to create the internal list of vertexes. 
		Type:              Integer or List of Floats 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     20  

	# edge 
		Description:       The edge to rebuild. 
		Type:              Edge 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

Returned Values:
	"dim" value:    0 
	"single" value: False 
	Type:           Vertex 
	Number:         n 
	Name:           "RebuiltSpline (Vertex)"  

	"dim" value:    0 
	"single" value: True 
	Type:           Compound of Vertexes 
	Number:         1 
	Name:           "RebuiltSpline (Vertexes)"  

	"dim" value:    1 
	"single" value: - 
	Type:           Edge 
	Number:         1 
	Name:           "RebuiltSpline"  

Conditions of use:
	-
	

"""
	
	#if isinstance(np, str): print "[X] The first argument (np) should be an integer."; return
	
	if dim not in [0, 1]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	edge = GetGUISelection(edge)
	
	edge = GetObject(edge)
	
	#-
	
	# Make this function recursive
	
	if isinstance(edge, list):
		
		return_list = []
		
		for sub_object in edge:
			
			return_list.append(RebuildSpline(np, sub_object, single, add, infa, dim))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [edge] or None in [edge]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = edge
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the list of positions where to create vertexes
		
		if isinstance(np, list):
			
			parameter_list = np
			
		
		else:
			
			parameter_list = [float(i) / (np - 1) for i in range(np)]
			
		
		#-
		
		# Create the points
		
		points = []
		
		for parameter in parameter_list:
			
			points.append(geompy.MakeVertexOnCurve(edge, parameter))
			
		
		#-
		
		if dim == 0:# If the output dimension is 0...
			
			to_return = points
			to_return_name = "RebuiltSpline (Vertex)"
			
			if single == True:
				
				compound = geompy.MakeCompound(to_return)
				
				to_return = compound
				to_return_name = "RebuiltSpline (Vertexes)"
				
			
		
		else:
			
			# Create the edge
			
			rebuilt_spline = geompy.MakeInterpol(points)
			
			#-
			
			to_return = rebuilt_spline
			to_return_name = "RebuiltSpline"
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, father, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
	

rs = RebuildSpline

def SplitEdge( np = 20, edge = None, single = True, add = True, infa = False, dim = 1 ):
	"""
	
	
Description:
	Splits an edge into a discretized wire.
	

Arguments:
	# np 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     20  

	# edge 
		Description:       The edge to split. 
		Type:              Edge 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

Returned Values:
	"dim" value:    0 
	"single" value: False 
	Type:           Vertex 
	Number:         n 
	Name:           "SplitEdge (Vertex)"  

	"dim" value:    0 
	"single" value: True 
	Type:           Compound of Vertexes 
	Number:         1 
	Name:           "SplitEdge (Vertexes)"  

	"dim" value:    1 
	"single" value: - 
	Type:           Wire 
	Number:         1 
	Name:           "SplitEdge" 

Conditions of use:
	-
	

"""
	
	if dim not in [0, 1]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	edge = GetGUISelection(edge)
	
	edge = GetObject(edge)
	
	#-
	
	# Make this function recursive
	
	if isinstance(edge, list):
		
		return_list = []
		
		for sub_object in edge:
			
			return_list.append(SplitEdge(np, sub_object, single, add, infa, dim))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [edge] or None in [edge]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = edge
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the list of positions where to create vertexes
		
		if isinstance(np, list):
			
			parameter_list = np
			
		
		else:
			
			parameter_list = [float(i) / (np - 1) for i in range(np)]
			
		
		#-
		
		# Create the points
		
		points = []
		
		for parameter in parameter_list:
			
			points.append(geompy.MakeVertexOnCurve(edge, parameter))
			
		
		#-
		
		if dim == 0:# If the output dimension is 0...
			
			to_return = points
			to_return_name = "SplitEdge (Vertex)"
			
			if single == True:
				
				compound = geompy.MakeCompound(to_return)
				
				to_return = compound
				to_return_name = "SplitEdge (Vertexes)"
				
			
		
		else:
			
			# Partition the edge
			
			partition = geompy.MakePartition([edge], points)
			
			#-
			
			# Explode the partition in edges
			
			edges = geompy.SubShapeAll(partition, geompy.ShapeType["EDGE"])
			
			#-
			
			# Create the wire
			
			wire = geompy.MakeWire(edges)
			
			#-
			
			to_return = wire
			to_return_name = "SplitEdge"
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, father, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
	

se = SplitEdge

def DiscretizeEdgeByCurvature( edge = None, np = 20, fine = 1e3, it_max = 10, single = True, add = True, infa = False, dim = 1 ):
	"""
	
	
Description:
	Discretizes an edge into a wire made of straight edges taking into account the local curvature.
	

Arguments:
	# edge 
		Description:       The edge to discretize. 
		Type:              Edge 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# np 
		Description:       See here. In this case, corresponds to the number of vertexes used for the first iteration. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     20  

	# fine 
		Description:       The desired fineness. Higher it is, finer is the discretization. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e3  

	# it_max 
		Description:       The maximum number of iterations. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     10  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

Returned Values:
	"dim" value:    0 
	"single" value: False 
	Type:           Vertex 
	Number:         n 
	Name:           "EdgeDiscretizedByCurvature (Vertex)"  

	"dim" value:    0 
	"single" value: True 
	Type:           Compound of Vertexes 
	Number:         1 
	Name:           "EdgeDiscretizedByCurvature (Vertexes)"  

	"dim" value:    1 
	"single" value: False 
	Type:           Edge 
	Number:         n 
	Name:           "EdgeDiscretizedByCurvature (Edge)"  

	"dim" value:    1 
	"single" value: True 
	Type:           Wire 
	Number:         1 
	Name:           "EdgeDiscretizedByCurvature"  

Conditions of use:
	-
	

"""
	
	input_shape = edge
	
	# Check the "dim" value
	
	if dim not in [ - 1, 0, 1]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	#-
	
	# Get the input shape(s)
	
	input_shape = GetGUISelection(input_shape)
	
	input_shape = GetObject(input_shape)
	
	#-
	
	# Make this function recursive
	
	if isinstance(input_shape, list):
		
		return_list = []
		
		for sub_object in input_shape:
			
			return_list.append(DiscretizeEdgeByCurvature(sub_object, np, fine, it_max, single, add, infa, dim))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [input_shape] or None in [input_shape]: return
	
	#-
	
	# Check the input shape type
	
	if geompy.NumberOfEdges(input_shape) != 1:
		
		print "[X] The first argument (edge) should be a single edge."; return
		
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = input_shape
	
	#-
	
	edge = input_shape
	
	if False: pass
	
	else:# All checks done
		
		if np < 2:
			
			np = 2
			
		
		# Get the edge length
		
		edge_length = geompy.BasicProperties(edge)[0]
		
		#-
		
		# Deduce the max distance above which to refine
		
		dist = edge_length / fine
		
		#-
		
		# Create a first set of equidistqnt vertexes
		
		parameter_list = [n / float(np - 1) for n in range(np)]
		vertex_list = [geompy.MakeVertexOnCurve(edge, parameter) for parameter in parameter_list]
		
		#-
		
		for j in range(it_max):# For each iteration...
			
			# Get segments to refine
			
			nb_vertexes = len(vertex_list)
			segment_to_refine_index_list = []
			for i in range(nb_vertexes - 2):
				
				p0 = parameter_list[i]
				p1 = parameter_list[i + 1]
				p2 = parameter_list[i + 2]
				
				v0 = vertex_list[i]
				v1 = vertex_list[i + 1]
				v2 = vertex_list[i + 2]
				
				straight_edge = geompy.MakeEdge(v0, v2)
				distance = geompy.MinDistance(v1, straight_edge)
				
				if distance > dist:
					
					segment_to_refine_index_list.extend([i, i + 1])
					
				
			
			segment_to_refine_index_list = list(set(segment_to_refine_index_list))
			segment_to_refine_index_list.sort()
			
			#-
			
			if len(segment_to_refine_index_list) == 0:
				
				break
				
			
			# Refine segments
			
			new_parameter_list = list(parameter_list)
			new_vertex_list = list(vertex_list)
			for segment_to_refine_index in reversed(segment_to_refine_index_list):
				
				index = segment_to_refine_index
				
				p0 = parameter_list[index]
				p1 = parameter_list[index + 1]
				
				p01 = (p0 + p1) / 2.0
				
				new_parameter_list.insert(index + 1, p01)
				
				v01 = geompy.MakeVertexOnCurve(edge, p01)
				
				new_vertex_list.insert(index + 1, v01)
				
			
			parameter_list = list(new_parameter_list)
			vertex_list = list(new_vertex_list)
			
			#-
			
		
		if dim == -1:
			
			# Add and return the resulting shape(s)
			
			to_return = parameter_list
			
			return to_return
			
			#-
			
		
		elif dim == 0:
			
			to_return = vertex_list
			to_return_name = "EdgeDiscretizedByCurvature (Vertex)"
			
			if single == True:
				
				compound = geompy.MakeCompound(vertex_list)
				
				to_return = compound
				to_return_name = "EdgeDiscretizedByCurvature (Vertexes)"
				
			
		
		else:
			
			# Create a polyline from vertexes
			
			nb_vertexes = len(vertex_list)
			segment_list = []
			for i in range(nb_vertexes - 1):
				
				v1 = vertex_list[i]
				v2 = vertex_list[i + 1]
				
				segment = geompy.MakeEdge(v1, v2)
				segment_list.append(segment)
				
			
			#-
			
			to_return = segment_list
			to_return_name = "EdgeDiscretizedByCurvature (Edge)"
			
			if single == True:
				
				wire = geompy.MakeWire(segment_list)
				
				to_return = wire
				to_return_name = "EdgeDiscretizedByCurvature"
				
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, father, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
		
	

debc = DiscretizeEdgeByCurvature

def FuseSplines( edges = [None], np = 20, curv = True, tol = 1e-7, single = True, add = True, dim = 1 ):
	"""
	
	
Description:
	Fuses two edges.
	

Arguments:
	# edges 
		Description:       The edges to fuse. 
		Type:              List of 2 Edges 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# np 
		Description:       See here. In this case, the number of points is divided up between input edges according to their lenght. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     20  

	# curv 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

Returned Values:
	"dim" value:    0 
	"single" value: False 
	Type:           Vertex 
	Number:         n 
	Name:           "FusedSpline (Vertex)"  

	"dim" value:    0 
	"single" value: True 
	Type:           Compound of Vertexes 
	Number:         1 
	Name:           "FusedSpline (Vertexes)"  

	"dim" value:    1 
	"single" value: - 
	Type:           Edge 
	Number:         1 
	Name:           "FusedSpline"  

Conditions of use:
	For better results, if coincident, both splines has to be as tangential as possible.
	

"""
	
	if isinstance(np, str): print "[X] The first argument (np) should be an integer ."; return
	if isinstance(edges, list) == False: print "[X] The second argument (edges) should be an array."; return
	
	if dim not in [0, 1]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	edges = GetGUISelection(edges)
	
	edges = GetObject(edges)
	
	#-
	
	# Check the input shape existence
	
	if "error" in edges or None in edges: return
	
	#-
	
	# Check the number of selected objects
	
	if len(edges) != 2:
		
		print "[X] Two shapes should be selected."
		
		return
		
	
	#-
	
	else:# All checks done
		
		# Get the number of points on each edge
		
		length_1 = geompy.BasicProperties(edges[0])[0]
		length_2 = geompy.BasicProperties(edges[1])[0]
		
		total_lenght = length_1 + length_2
		
		np_1 = int(round(float(np) * length_1 / total_lenght))
		np_2 = int(round(float(np) * length_2 / total_lenght))
		
		#-
		
		# Extract the edge vertexes
		
		#### Here the extremum vertexes are created on curve
		#### and not exploded to be sure the vertex order
		#### respects the edge orientation
		
		edge_vertexes = [
		geompy.MakeVertexOnCurve(edges[0], 0), 
		geompy.MakeVertexOnCurve(edges[0], 1), 
		geompy.MakeVertexOnCurve(edges[1], 0), 
		geompy.MakeVertexOnCurve(edges[1], 1)
		]
		
		#### -
		
		#-
		
		# Determine the edge directions
		
		min_distances = [
		geompy.MinDistance(edge_vertexes[0], edges[1]), 
		geompy.MinDistance(edge_vertexes[1], edges[1]), 
		geompy.MinDistance(edges[0], edge_vertexes[2]), 
		geompy.MinDistance(edges[0], edge_vertexes[3])
		]
		
		reverse_edges = [False, False]
		
		if min_distances[0] < min_distances[1]:
			
			reverse_edges[0] = True
			
		
		if min_distances[2] > min_distances[3]:
			
			reverse_edges[1] = True
			
		
		#-
		
		# Check if splines are touching each other
		
		edges_are_coincident = False
		if min(min_distances) <= tol:
			
			edges_are_coincident = True
			
		
		#-
		
		# Split edge_1
		
		if curv == True:
			
			parameter_list = DiscretizeEdgeByCurvature(edges[0], np_1, dim = -1)
			
		
		else:
			
			parameter_list = [n / float(np_1) for n in range(np_1 + 1)]
			
		
		if edges_are_coincident:
			
			del parameter_list[-1]
			
		
		fused_spline_vertexes = []
		for parameter in parameter_list:
			
			if reverse_edges[0] == True:
				
				parameter = 1 - parameter
				
			
			edge_1_vertex = geompy.MakeVertexOnCurve(edges[0], parameter)
			
			fused_spline_vertexes.append(edge_1_vertex)
		
		#-
		
		# Split edge_2
		
		if curv == True:
			
			parameter_list = DiscretizeEdgeByCurvature(edges[1], np_2, dim = -1)
			
		
		else:
			
			parameter_list = [n / float(np_2) for n in range(np_2 + 1)]
			
		
		for parameter in parameter_list:
			
			if reverse_edges[1] == True:
				
				parameter = 1 - parameter
				
			
			edge_2_vertex = geompy.MakeVertexOnCurve(edges[1], parameter)
			
			fused_spline_vertexes.append(edge_2_vertex)
		
		#-
		
		if dim == 0:# If the output dimension is 0...
			
			to_return = fused_spline_vertexes
			to_return_name = "FusedSpline (Vertex)"
			
			if single == True:
				
				compound = geompy.MakeCompound(fused_spline_vertexes)
				
				to_return = compound
				to_return_name = "FusedSpline (Vertexes)"
				
			
		
		else:
			
			# Create the fused edge
			
			fused_spline = geompy.MakeInterpol(fused_spline_vertexes, False, False)
			
			#-
			
			to_return = fused_spline
			to_return_name = "FusedSpline"
			
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
	

fs = FuseSplines

def ExtendSpline( edge_and_vertex = [None], np = 20, pos = "auto", strat = "flex", curv = True, tol = 1e-7, single = True, add = True, infa = False, dim = 1 ):
	"""
	
	
Description:
	Extends an edge to a vertex position.
	

Arguments:
	# edge_and_vertex 
		Description:       The edge to extend and the target vertex. 
		Type:              List of 1 Edge + 1 Vertex 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# np 
		Description:       See here. In this case, correspond to the number of vertexes created on the input edge. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     10  

	# pos 
		Description:       If equals "before" or "after", the edge  is extended from it start or its end respectively (according to its orientation). If equals "auto", the function decides itself. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "auto"  

	# strat 
		Description:       Defines the extension strategy. If equals "rigid" or "flex", the edge  is respectively extended with or without a constrain on the straightness of the extension. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "flex"  

	# curv 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True 

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

Returned Values:
	"dim" value:    0 
	"single" value: False 
	Type:           Vertex 
	Number:         n 
	Name:           "ExtendedSpline (Vertex)"  

	"dim" value:    0 
	"single" value: True 
	Type:           Compound of Vertexes 
	Number:         1 
	Name:           "ExtendedSpline (Vertexes)"  

	"dim" value:    1 
	"single" value: - 
	Type:           Edge 
	Number:         1 
	Name:           "ExtendedSpline"  

Conditions of use:
	-
	

"""
	
	if isinstance(edge_and_vertex, list) == False: print "[X] The first argument (edge_and_vertex) should be an array."; return
	
	if dim not in [0, 1]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	edge_and_vertex = GetGUISelection(edge_and_vertex)
	
	edge_and_vertex = GetObject(edge_and_vertex)
	
	#-
	
	# Check the input shape existence
	
	if "error" in edge_and_vertex or None in edge_and_vertex: return
	
	#-
	
	# Check the number of selected objects
	
	if len(edge_and_vertex) != 2:
		
		print "[X] Two shapes should be selected."
		
		return
		
	
	#-
	
	# Distinguish input shapes
	
	edge = None
	vertex = None
	
	for object in edge_and_vertex:
		
		nb_vertexes = len(geompy.SubShapeAll(object, geompy.ShapeType["VERTEX"]))
		
		if nb_vertexes == 1: vertex = object
		if nb_vertexes == 2: edge = object
		
	
	if None in [edge, vertex]:
		
		print "[X] Only an edge and a vertex should be selected."
		
		return
		
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = edge
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the sub-shapes
		
		[edge, vertex] = GetSubShapes([edge, vertex])
		
		#-
		
		# Check if the edge and vertex are not coincident
		
		vertex_is_coincident = False
		for edge_vertex in edge[0]:
			
			distance = geompy.MinDistance(edge_vertex, vertex[-1])
			
			if distance <= tol:
				
				vertex_is_coincident = True
				
			
		
		#-
		
		# Check the position
		
		if pos not in ["auto", "before", "after"]:
			
			pos = "auto"
			
		
		#-
		
		# Get the pos of the user vertex
		
		if pos == "auto":
			
			vertex_distances = [
			geompy.MinDistance(vertex[-1], edge[0][0]), 
			geompy.MinDistance(vertex[-1], edge[0][1])
			]
			
			pos = "after"
			
			if vertex_distances[0] < vertex_distances[1]:
				
				pos = "before"
				
			
		
		#-
		
		# Create the spline vertexes
		
		if curv == True:
			
			np_or_params = DiscretizeEdgeByCurvature(edge[-1], np, dim = -1)
			
		else:
			
			np_or_params = np
			
		
		spline_vertexes = RebuildSpline(np_or_params, edge[-1], dim = 0, single = False, add = False)
		
		if not vertex_is_coincident:
			
			if strat == "rigid":
				
				if pos == "before":
					
					extension = geompy.MakeEdge(vertex[-1], edge[0][0])
					
				
				if pos == "after":
					
					extension = geompy.MakeEdge(edge[0][1], vertex[-1])
					
				
				spline_vertexes = FuseSplines([edge[-1], extension], np = np, dim = 0, add = False)
				spline_vertexes = geompy.SubShapeAll(spline_vertexes, geompy.ShapeType["VERTEX"])
				
			
			else:# strat = "flex"
				
				if pos == "before":
					
					spline_vertexes.insert(0, vertex[-1])
					
				
				#for parameter in [n / float(np) for n in range(np + 1)]:
					
					#splineVertex = geompy.MakeVertexOnCurve(edge[-1], parameter)
					
					#splineVertexes.append(spline_vertex)
				
				if pos == "after":
					
					spline_vertexes.append(vertex[-1])
					
				
		
		#-
		
		if dim == 0:# If the output dimension is 0...
			
			to_return = spline_vertexes
			to_return_name = "ExtendSpline (Vertex)"
			
			if single == True:
				
				# Create the vertex compound
				
				spline_vertex_compound = geompy.MakeCompound(spline_vertexes)
				
				#-
				
				to_return = spline_vertex_compound
				to_return_name = "ExtendSpline (Vertexes)"
				
			
		
		else:
			
			# Create the extended spline
			
			extended_spline = geompy.MakeInterpol(spline_vertexes, False, False)
			
			#-
			
			to_return = extended_spline
			to_return_name = "ExtendSpline"
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
			
		
	

es = ExtendSpline

def ExtendSplinesToIntersection( edges = [None], np = 20, curv = True, tol = 1e-4, single = True, add = True ):
	"""
	
	
Description:
	Extends two splines to intersection points.
	

Arguments:
	# edges 
		Description:       The edges to extend. 
		Type:              List of 2 Edges 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# np 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     20  

	# curv 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-4  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: False 
	Type:           Edge 
	Number:         2 
	Name:           "SplineExtendedToIntersection"  

	"dim" value:    - 
	"single" value: True 
	Type:           Wire or Compound of Edges 
	Number:         1 
	Name:           "SplinesExtendedToIntersection"  

Conditions of use:
	To detect intersection, both input splines must be as coplanar as possible.
	

"""
	
	if isinstance(np, str): print "[X] The first argument (np) should be an integer."; return
	if isinstance(edges, list) == False: print "[X] The second argument (edges) should be an array."; return
	
	input_shapes = edges
	
	# Get the input shape(s)
	
	input_shapes = GetGUISelection(input_shapes)
	
	input_shapes = GetObject(input_shapes)
	
	#-
	
	# Check the input shape existence
	
	if "error" in input_shapes or None in input_shapes: return
	
	#-
	
	# Check the number of selected objects
	
	if len(input_shapes) != 2:
		
		print "[X] Two shapes should be selected."
		
		return
		
	
	#-
	
	edges = input_shapes
	
	if False: pass
	
	else:# All checks done
		
		small_value = 1e-3
		
		length_1 = geompy.BasicProperties(edges[0])[0]
		length_2 = geompy.BasicProperties(edges[1])[0]
		
		infinite_distance = (length_1 + length_2) * 1e2
		
		# Create boundary direction vectors
		
		direction_vectors = []
		boundary_vertexes = []
		for i in range(2):
			
			edge = edges[i]
			
			v11 = geompy.MakeVertexOnCurve(edge, 0.0 + small_value)
			v12 = geompy.MakeVertexOnCurve(edge, 0.0)
			
			v21 = geompy.MakeVertexOnCurve(edge, 1.0 - small_value)
			v22 = geompy.MakeVertexOnCurve(edge, 1.0)
			
			boundary_vertexes.append([v12, v22])
			
			direction_vector_1 = geompy.MakeVector(v11, v12)
			direction_vector_2 = geompy.MakeVector(v21, v22)
			
			direction_vectors.append([direction_vector_1, direction_vector_2])
			
		
		#-
		
		# Extend edges
		
		for i in range(2):# For each extremity of the first edge...
			
			direction_vector_1 = direction_vectors[0][i]
			vertex_1 = boundary_vertexes[0][i]
			
			extrusion_1 = geompy.MakePrismVecH(vertex_1, direction_vector_1, infinite_distance)
			
			# Get possible intersections with the second edge
			
			possible_intersections = []
			for j in range(2):
				
				direction_vector_2 = direction_vectors[1][j]
				vertex_2 = boundary_vertexes[1][j]
				
				extrusion_2 = geompy.MakePrismVecH(vertex_2, direction_vector_2, infinite_distance)
				
				distance = geompy.MinDistance(extrusion_1, extrusion_2)
				
				if distance < tol:
					
					[x, y, z] = geompy.ClosestPoints(extrusion_1, extrusion_2)[1][0:3]
					intersection = geompy.MakeVertex(x, y, z)
					
					possible_intersections.append(intersection)
					
				
			
			#-
			
			# Keep the closest intersection
			
			final_intersection = None
			nb_possible_intersections = len(possible_intersections)
			if nb_possible_intersections > 1:
				
				closest_intersection = None
				min_distance = infinite_distance
				for possible_intersection in possible_intersections:
					
					distance = geompy.MinDistance(vertex_1, possible_intersection)
					
					if distance < min_distance:
						
						closest_intersection = possible_intersection
						min_distance = distance
						
					
				
				final_intersection = closest_intersection
			
			elif nb_possible_intersections == 1:
				
				final_intersection = possible_intersections[0]
				
			
			#-
			
			# Extend edges
			
			if final_intersection != None:
				
				for j in range(2):
					
					edges[j] = ExtendSpline([edges[j], final_intersection], strat = "rigid", np = np, curv = curv, tol = tol, add = False)
					
				
			
			#-
			
		
		#-
		
		to_return = edges
		to_return_name = "SplineExtendedToIntersection"
		
		if single == True:
			
			try:
				wire = geompy.MakeWire(to_return)
			except:
				wire = geompy.MakeCompound(to_return)
			
			to_return = wire
			to_return_name = "SplinesExtendedToIntersection"
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(to_return, to_return_name)
			
		
		return edges
		
		#-
		
	

esti = ExtendSplinesToIntersection

def FuseSplineSets( compounds = [None], np = 20, curv = True, tol = 1e-7, add = True ):
	"""
	
	
Description:
	Fuses two sets of splines.
	

Arguments:
	# compounds 
		Description:       The spline sets to fuse. 
		Type:              List of 2 Compounds of Edges 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# np 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     20  

	# curv 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Compound of Edges 
	Number:         1 
	Name:           "FusedSplineSets"  

Conditions of use:
	Input spline sets must be coinciding, that is sharing boundary nodes or edge.
	

"""
	
	if isinstance(np, str): print "[X] The first argument (np) should be an integer ."; return
	if isinstance(compounds, list) == False: print "[X] The second argument (compounds) should be an array."; return
	
	# Get the input shape(s)
	
	compounds = GetGUISelection(compounds)
	
	compounds = GetObject(compounds)
	
	#-
	
	# Check the input shape existence
	
	if "error" in compounds or None in compounds: return
	
	#-
	
	# Check the number of selected objects
	
	if len(compounds) != 2:
		
		print "[X] Exactly two objects should be selected."
		
		return
		
	
	#-
	
	# Check the input shape characteritics
	
	for object in compounds:
		
		nb_edges = int(geompy.WhatIs(object).split("\n")[2].split(": ")[1])
		
		if nb_edges < 2:
			
			print "[X] Input objects should contain at least two edges"
			
			return
			
		
	
	#-
	
	else:# All checks done
		
		# Get the sub-shapes
		
		[compound1, compound2] = GetSubShapes(compounds)
		
		#-
		
		# Check compound position
		
		side_by_side = True
		
		n = 0
		
		for compound1_edge in compound1[1]:# For each edge of the first compound...
			
			compound1_edge_vertexes = geompy.SubShapeAll(compound1_edge, geompy.ShapeType["VERTEX"])
			
			for compound2_edge in compound2[1]:
				
				min_distance1 = geompy.MinDistance(compound2_edge, compound1_edge_vertexes[0])
				min_distance2 = geompy.MinDistance(compound2_edge, compound1_edge_vertexes[1])
				
				if min_distance1 <= tol and min_distance2 <= tol:
					
					side_by_side = False
					
					del compound1[1][n]
					
					break
				
			
			n += 1
			
		
		#-
		
		if side_by_side == True:
			
			# Check the number of edges
			
			nb_edges1 = int(geompy.WhatIs(compound1[-1]).split("\n")[2].split(": ")[1])
			nb_edges2 = int(geompy.WhatIs(compound2[-1]).split("\n")[2].split(": ")[1])
			
			if nb_edges1 != nb_edges2:
				
				print "[X] Input compounds should have a same number of edges"
				
				return
				
			
			#-
			
			fused_splines = []
			
			for compound1_edge in compound1[1]:# For each edge of the first compound...
				
				# Get the touching edge in the second compound
				
				closest_compound2_edge = None
				
				min_distance = 1e99
				
				for compound2_edge in compound2[1]:
					
					distance = geompy.MinDistance(compound2_edge, compound1_edge)
					
					if distance <= min_distance:
						
						min_distance = distance
						
						closest_compound2_edge = compound2_edge
						
					
				
				#-
				
				# Fuse edges
				
				fused_spline = FuseSplines([compound1_edge, closest_compound2_edge], np = np, curv = curv, tol = tol, add = False)
				
				#-
				
				# Add the fused spline to the list
				
				fused_splines.append(fused_spline)
				
				#-
				
			
			# Create the fused spline compound
			
			fused_spline_compound = geompy.MakeCompound(fused_splines)
			
			#-
			
		
		else:
			
			fused_spline_compound = geompy.MakeCompound(compound1[1] + compound2[1])
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(fused_spline_compound, "FusedSplineSets")
			
		
		return fused_spline_compound
		
		#-
		
	

fss = FuseSplineSets

def UnrefineSplineSet( fact = 2, compound = None, add = True, infa = False ):
	"""
	
	
Description:
	Unrefines a spline set.
	

Arguments:
	# fact 
		Description:       The unrefinement factor. For example, if equals 2, one spline over two is kept. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     2  

	# compound 
		Description:       The spline set to unrefine. 
		Type:              Compounds 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     false  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Compound of Edges 
	Number:         1 
	Name:           "UnrefinedSplineSet"  

Conditions of use:
	-
	

"""
	
	# Get the input shape(s)
	
	compound = GetGUISelection(compound)
	
	compound = GetObject(compound)
	
	#-
	
	# Make this function recursive
	
	if isinstance(compound, list):
		
		return_list = []
		
		for sub_object in compound:
			
			return_list.append(UnrefineSplineSet(fact, sub_object, add, infa))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [compound] or None in [compound]: return
	
	#-
	
	# Check the input shape characteritics
	
	nb_edges = int(geompy.WhatIs(compound).split("\n")[2].split(": ")[1])
	
	if nb_edges < 2:
		
		print "[X] The selected object should be a compound containing several edges."
		
		return
		
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = compound
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the sub-shapes
		
		compound = GetSubShapes(compound)
		
		#-
		
		# Unrefine the edge compound
		
		unrefined_edges = []
		
		for i in range(nb_edges - 1):
			
			if i%fact == 0 and nb_edges - i > fact:
				
				unrefined_edges.append(compound[1][i])
				
			
		
		unrefined_edges.append(compound[1][i + 1])
		
		#-
		
		# Create the unrefined edge compound
		
		unrefined_compound = geompy.MakeCompound(unrefined_edges)
		
		#-
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(unrefined_compound, "UnrefinedSplineSet")
			
		
		return unrefined_compound
		
		#-
		
	

uss = UnrefineSplineSet

def SwitchSplineSet( compound = None, np = "auto", add = True, infa = False ):
	"""
	
	
Description:
	Sitches the orientation of a spline set.
	

Arguments:
	# compound 
		Description:       The spline set to switch. 
		Type:              Compounds 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# np 
		Description:       See here. In this case, if equals "auto", the number of points is set equal to the number of splines in the input spline set. 
		Type:              Integer or String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "auto"  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     false  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Compound of Edges 
	Number:         1 
	Name:           "SwitchedSplineSet"  

Conditions of use:
	-
	

"""
	
	# Get the input shape(s)
	
	compound = GetGUISelection(compound)
	
	compound = GetObject(compound)
	
	#-
	
	# Make this function recursive
	
	if isinstance(compound, list):
		
		return_list = []
		
		for sub_object in compound:
			
			return_list.append(SwitchSplineSet(sub_object, np, add, infa))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [compound] or None in [compound]: return
	
	#-
	
	# Check the input shape characteritics
	
	nb_edges = int(geompy.WhatIs(compound).split("\n")[2].split(": ")[1])
	
	if nb_edges < 2:
		
		print "[X] The selected object should be a compound containing several edges."
		
		return
		
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = compound
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the sub-shapes
		
		compound = GetSubShapes(compound)
		
		#-
		
		if np == "auto":
			
			np = len(compound[1])
			
		
		# Create splines
		
		splines = []
		
		for parameter in [n / float(np - 1) for n in range(np)]:
			
			spline_vertexes = []
			for edge in compound[1]:
				
				spline_vertex = geompy.MakeVertexOnCurve(edge, parameter)
				spline_vertexes.append(spline_vertex)
				
			
			spline = geompy.MakeInterpol(spline_vertexes)
			splines.append(spline)
			
		
		#-
		
		# Put them into a compound
		
		switched_compound = geompy.MakeCompound(splines)
		
		#-
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(switched_compound, "SwitchedSplineSet")
			
		
		return switched_compound
		
		#-
		
	

sss = SwitchSplineSet

def RebuildFace( np = 30, face = None, rel = False, switch = False, tol = 1e-7, single = True, add = True, infa = False, dim = 2 ):
	"""
	
	
Description:
	Rebuilds a face using its iso-lines.
	

Arguments:
	# np 
		Description:       See here. In addition, if this argument is an list of 2 integers, the first number gives the number of  isolines created to rebuild the face and the second number gives the number of points used to create each isoline (see the above script example). 
		Type:              Integer or  List of 2 Integers 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     30  

	# face 
		Description:       The face to rebuild. 
		Type:              Face 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# rel 
		Description:       If equals True, the function try to relimit the rebuild face using the  source face edges. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# switch 
		Description:       If equals True, the iso-curves are switched from iso-u to iso-v. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     2  

Returned Values:
	"dim" value:    0 
	"single" value: False 
	Type:           Vertex 
	Number:         n 
	Name:           "RebuiltFace (Vertex)"  

	"dim" value:    0 
	"single" value: True 
	Type:           Compound of Vertexes 
	Number:         1 
	Name:           "RebuiltFace (Vertexes)"  

	"dim" value:    1 
	"single" value: False 
	Type:           Edge 
	Number:         n 
	Name:           "RebuiltFace (Edge)"  

	"dim" value:    1 
	"single" value: True 
	Type:           Compound of Edges 
	Number:         1 
	Name:           "RebuiltFace (Edges)"  

	"dim" value:    2 
	"single" value: - 
	Type:           Face 
	Number:         1 
	Name:           "RebuiltFace"  

Conditions of use:
	-
	

"""
	
	if isinstance(np, str): print "[X] The first argument (np) should be an integer ."; return
	
	if dim not in [0, 1, 2]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	face = GetGUISelection(face)
	
	face = GetObject(face)
	
	#-
	
	# Make this function recursive
	
	if isinstance(face, list):
		
		return_list = []
		
		for sub_object in face:
			
			return_list.append(RebuildFace(np, sub_object, rel, switch, tol, single, add, infa, dim))
			
		
		return return_list
		
	
	#-
	
	# Get input values
	
	if isinstance(np, list) == False:
		
		np = [np, np]
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [face] or None in [face]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = face
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the sub-shapes
		
		face = GetSubShapes(face)
		
		#-
		
		# Create the iso curves
		
		iso_curves = []
		
		if dim == 0: iso_curve_vertexes_all = []
		
		for i in [n / float(np[0]) for n in range(np[0] + 1)]:
			
			iso_curve_vertexes = []
			
			for j in [n / float(np[1]) for n in range(np[1] + 1)]:
				
				if switch == True:
					
					new_iso_curve_vertex = geompy.MakeVertexOnSurface(face[-1], j, i)
					
					
				
				else:
					
					new_iso_curve_vertex = geompy.MakeVertexOnSurface(face[-1], i, j)
					
				
				iso_curve_vertexes.append(new_iso_curve_vertex)
				
			
			if dim == 0: iso_curve_vertexes_all += iso_curve_vertexes
			if dim != 0:
				
				new_iso_curve = geompy.MakeInterpol(iso_curve_vertexes)
				
				iso_curves.append(new_iso_curve)
				
			
		
		#-
		
		if dim == 0:
			
			to_return = iso_curve_vertexes_all
			to_return_name = "RebuiltFace (Vertex)"
			
			if single == True:
				
				# Put them into a compound
				
				vertex_compound = geompy.MakeCompound(iso_curve_vertexes_all)
				
				#-
				
				to_return = vertex_compound
				to_return_name = "RebuiltFace (Vertexes)"
				
			
		
		else:
			# Put them into a compound
			
			iso_curve_compound = geompy.MakeCompound(iso_curves)
			
			#-
			
			if dim == 1:# If the output dimension is 1...
				
				to_return = iso_curves
				to_return_name = "RebuiltFace (Edge)"
				
				if single == True:
					
					to_return = iso_curve_compound
					to_return_name = "RebuiltFace (Edges)"
					
				
			
			else:# If the output dimension is 2...
				
				# Create the filling from this compound
				
				filling = geompy.MakeFilling(iso_curve_compound, theMinDeg = 10, theMaxDeg = 20, theTol2D = 1e-5, theTol3D = 1e-5)
				
				#-
				
				# Relimitate the filling
				# TODO improve that ?
				
				rebuild_face = filling
				
				if rel == True:
					
					#face_wire = geompy.SubShapeAll(face[-1], geompy.ShapeType["WIRE"])[0]
					
					#fused_face = geompy.MakeFaceFromSurface(filling, face_wire) 
					
					projected_edges = []
					
					for edge in face[1]:
						
						try:
							
							projected_edge = geompy.MakeProjection(edge, filling)
							
							projected_edges.append(projected_edge)
							
						
						except:
							
							pass
							
						
					
					if len(projected_edges) > 0:
						
						filling_partition = geompy.MakePartition([filling], projected_edges)
						
						filling_partition_faces = geompy.SubShapeAll(filling_partition, geompy.ShapeType["FACE"])
						
						for filling_partition_face in filling_partition_faces:
							
							filling_partition_face_vertexes = geompy.SubShapeAll(filling_partition_face, geompy.ShapeType["VERTEX"])
							
							match = True
							
							for filling_partition_face_vertex in filling_partition_face_vertexes:
								
								projected_edge_compound = geompy.MakeCompound(projected_edges)
								
								min_distance = geompy.MinDistance(filling_partition_face_vertex, projected_edge_compound)
								
								if min_distance > tol:
									
									match = False
									
								
							
							if match == True:
								
								rebuild_face = filling_partition_face
								
								break
								
							
						
					
				
				#-
				
				to_return = rebuild_face
				to_return_name = "RebuiltFace"
				
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, father, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
	

rf = RebuildFace

def FuseCoplanarFaces( faces = [None], add = True ):
	"""
	
	
Description:
	Completely fuses two coplanar faces.
	

Arguments:
	# faces 
		Description:       The faces to fuse. 
		Type:              List of 2 Faces 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Face 
	Number:         1 
	Name:           "FusedFace"  

Conditions of use:
	-
	

"""
	
	if isinstance(faces, list) == False: print "[X] The first argument (faces) should be an array."; return
	
	# Get the input shape(s)
	
	faces = GetGUISelection(faces)
	
	faces = GetObject(faces)
	
	#-
	
	# Check the input shape existence
	
	if "error" in faces or None in faces: return
	
	#-
	
	# Check the number of selected objects
	
	if len(faces) != 2:
		
		print "[X] Two shapes should be selected."
		
		return
		
	
	#-
	
	else:# All checks done
		
		# Get the plane normal
		
		normal = geompy.GetNormal(faces[0])
		
		#-
		
		# Extrude the faces
		
		extrusion_distance = 1e3
		
		cutting_plane_position = extrusion_distance / 2
		
		extruded_faces = [
		geompy.MakePrismVecH(faces[0], normal, extrusion_distance), 
		geompy.MakePrismVecH(faces[1], normal, extrusion_distance)
		]
		
		#-
		
		# Fuse the extruded faces
		
		fused_extension = geompy.MakeFuse(extruded_faces[0], extruded_faces[1])
		
		#-
		
		# Get the length of the cutting plane
		
		bounding_box = geompy.BoundingBox(fused_extension)
		
		dx = abs(bounding_box[1] - bounding_box[0])
		dy = abs(bounding_box[2] - bounding_box[1])
		dz = abs(bounding_box[3] - bounding_box[2])
		
		plane_length = 2 * dx + 2 * dy + 2 * dz
		
		#-
		
		# Create the cutting plane
		
		cutting_plane = geompy.MakePlaneFace(faces[0], plane_length)
		
		cutting_plane = geompy.MakeTranslationVectorDistance(cutting_plane, normal, cutting_plane_position)
		
		#-
		
		# Cut the fused extrusion with the plane
		
		fused_face = geompy.MakeCommon(fused_extension, cutting_plane)
		
		#-
		
		# Remove shells (optional)
		
		random_vertex = geompy.MakeVertex(0, 0, 0)# This vertex is only used to make the below partition possible
		
		fused_face = geompy.MakePartition([fused_face], [random_vertex], Limit = geompy.ShapeType["FACE"])
		
		#-
		
		# Move the face to the original position
		
		fused_face = geompy.MakeTranslationVectorDistance(fused_face, normal, - cutting_plane_position)
		
		#-
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(fused_face, "FusedFace")
			
		
		return fused_face
		
		#-
		
	

fcf = FuseCoplanarFaces

def FuseShellFaces( shell = None, np = 400, strat = "rigid", curv = True, add = True, infa = False, dim = 2 ):
	"""
	
	
Description:
	Creates a single face from a shell.
	

Arguments:
	# shell 
		Description:       The shell to fuse. 
		Type:              Shell 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     [None]  

	# np 
		Description:       See here. In this case, the number of point is approximatively respected. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     400  

	# strat 
		Description:       The strategy. If equals "flex", the function tries to insert smooth transitions between sub-faces of the input shell (the boundary wire is then modified). Equals "rigid" otherwise (necessitates the input sub-faces to be  as tangential as possible). 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "rigid"  

	# curv 
		Description:       See here. In this case, applies only for the boundary wire reconstruction when strat equals "flex". 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    0 
	"single" value: - 
	Type:           Compound of Vertexes 
	Number:         1 
	Name:           "FusedShell (Vertexes)"  

	"dim" value:    2 
	"single" value: - 
	Type:           Face 
	Number:         1 
	Name:           "FusedShell"  

Conditions of use:
	The shell should have only one boundary wire.
	
	Also, to be fused efficiently, the shell faces should have reasonable aspect ratio and local curvature. 

"""
	
	if isinstance(np, str): print "[X] The first argument (np) should be an integer ."; return
	
	if dim not in [0, 2]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	shell = GetGUISelection(shell)
	
	shell = GetObject(shell)
	
	#-
	
	# Make this function recursive
	
	if isinstance(shell, list):
		
		return_list = []
		
		for sub_object in shell:
			
			return_list.append(FuseShellFaces(sub_object, np, strat, curv, add, infa, dim))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [shell] or None in [shell]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = shell
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Check if the input shape is "shell-shaped"
		
		shell_faces = GetSubShapes(shell)[2]
		
		try:
			
			shell = geompy.MakeShell(shell_faces)
			
		except:
			
			print "[X] The input 2D shape should be \"shell-shaped\"."; return
			
		
		#-
		
		# Get the input shell boundary wire
		
		boundary_wire = geompy.GetFreeBoundary(shell)[1][0]
		
		#-
		
		# Get the input shell area
		
		area = geompy.BasicProperties(shell)[1]
		
		#-
		
		# Get the cell size
		
		cell_size = math.sqrt(area / np)
		
		#-
		
		# Mesh the input shell
		
		mesh = smesh.Mesh(shell)
		
		netgen_algo = mesh.Triangle(algo = smeshBuilder.NETGEN_1D2D)
		netgen_hypo = netgen_algo.Parameters()
		netgen_hypo.SetMinSize(cell_size)
		netgen_hypo.SetMaxSize(cell_size)
		netgen_hypo.SetFineness(2)
		
		mesh.Compute()
		
		#-
		
		# Remove internal vertexes
		
		if strat == "flex":# not "rigid"
			
			# Get the internal edges
			
			all_edges_group = PutAllSubShapesInAGroup(1, shell, add = False)
			
			internal_edge_compound = geompy.MakeCut(all_edges_group, boundary_wire)
			geompy.addToStudy(internal_edge_compound, "internal_edges")
			
			#-
			
			# Create the internal node mesh group
			
			internal_nodes_mesh_filter = smesh.GetFilterFromCriteria([smesh.GetCriterion(SMESH.NODE, SMESH.FT_BelongToGeom, SMESH.FT_Undefined, internal_edge_compound)])
			internal_nodes_mesh_filter.SetMesh(mesh.GetMesh())
			
			internal_nodes_mesh_group = mesh.GroupOnFilter(SMESH.NODE, "internal_nodes", internal_nodes_mesh_filter)
			
			#-
			
			# Delete the internal nodes
			
			mesh.RemoveGroupWithContents(internal_nodes_mesh_group)
			#mesh.RemoveGroupWithContents(edge_node_mesh_group)
			
			#-
			
			# Delete temporary geometrical shapes
			
			#http://www.salome-platform.org/forum/forum_10/366900504#419952388
			so = salome.ObjectToSObject(internal_edge_compound)
			sb = salome.myStudy.NewBuilder()
			sb.RemoveObjectWithChildren(so)
			
			#-
			
		
		#-
		
		# Create the node group
		
		node_group = mesh.CreateEmptyGroup( SMESH.NODE, "nodes" )
		node_group.AddFrom(mesh.GetMesh())
		
		#-
		
		# Create vertexes from nodes
		
		vertex_compound = MakeVertexesFromMeshGroup(node_group, add = False)
		
		#-
		
		# Delete the shell, mesh and hypos
		
		so = salome.ObjectToSObject(shell)
		sb = salome.myStudy.NewBuilder()
		sb.RemoveObjectWithChildren(so)
		
		a_study_builder = salome.myStudy.NewBuilder()
		SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(node_group))
		if SO: a_study_builder.RemoveObjectWithChildren(SO)
		SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(mesh.GetMesh()))
		if SO: a_study_builder.RemoveObjectWithChildren(SO)
		SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(netgen_hypo))
		if SO: a_study_builder.RemoveObjectWithChildren(SO)
		
		#-
		
		if dim == 0:# If the output dimension is 0...
			
			# Return the resulting shape(s)
			
			if add == True:
				
				AddToStudy(vertex_compound, "FusedShell (Vertexes)", father)
				
			
			return vertex_compound
			
			#-
			
		
		else:
			
			# Create the smoothing surface
			
			vertex_list = geompy.SubShapeAll(vertex_compound, geompy.ShapeType["VERTEX"])
			
			smoothing_surface = geompy.MakeSmoothingSurface(vertex_list, 100, 15)
			
			#-
			
			if strat == "flex":# not "rigid"
				
				zero_size = cell_size / 100.0
				
				# Get boundary vertexes to ignore
				
				boundary_vertexes = GetSubShapes(boundary_wire)[0]
				
				vertexes_to_ignore = []
				for boundary_vertex in boundary_vertexes:
					
					distance = geompy.MinDistance(boundary_vertex, vertex_compound)
					
					if distance > zero_size:
						
						vertexes_to_ignore.append(boundary_vertex)
						
					
				
				#-
				
				# Fuse boundary edges
				
				boundary_edges = GetSubShapes(boundary_wire)[1]
				
				new_boundary_edges = []
				for vertex_to_ignore in vertexes_to_ignore:# For each vertex to ignore...
					
					# Get touching boundary edges
					
					touching_edges = []
					
					for boundary_edge in boundary_edges:
						
						distance = geompy.MinDistance(boundary_edge, vertex_to_ignore)
						
						if distance < zero_size:
							
							touching_edges.append(boundary_edge)
							
						
					
					#-
					
					# Create new boundary edges
					
					max_nb_touching_vertexes = 0
					new_boundary_separated_edges = []
					for touching_edge in touching_edges:# For each touching edge...
						
						# Get touching vertexes
						
						touching_vertexes = []
						
						for vertex in vertex_list:
							
							distance = geompy.MinDistance(vertex, touching_edge)
							
							if distance < zero_size:
								
								touching_vertexes.append(vertex)
								
							
						
						#-
						
						nb_touching_vertexes = len(touching_vertexes)
						
						if nb_touching_vertexes > max_nb_touching_vertexes:
							
							max_nb_touching_vertexes = nb_touching_vertexes
							
						
						# Create a spline from them
						
						touching_vertex_compound = geompy.MakeCompound(touching_vertexes)
						
						new_boundary_separated_edge = MakeCurveFromUnsortedVertexes([touching_vertex_compound, vertex_to_ignore], add = False)
						
						new_boundary_separated_edges.append(new_boundary_separated_edge)
						
						#-
						
					
					#-
					
					# Fuse them together
					
					new_boundary_edge = FuseSplines(new_boundary_separated_edges, np = max_nb_touching_vertexes, curv = curv, add = False)
					
					new_boundary_edges.append(new_boundary_edge)
					
					#-
					
				
				#-
				
				# Replace the boundary wire
				
				boundary_wire = geompy.MakeWire(new_boundary_edges)
				
				#-
				
			
			# Relimitate the smoothing surface
			
			fused_face = geompy.MakeFaceFromSurface(smoothing_surface, boundary_wire) 
			
			#-
			
			# Add and return the resulting shape(s)
			
			if add == True:
			
				AddToStudy(fused_face, "FusedShell", father)
			
			return fused_face
			
			#-
	

fsf = FuseShellFaces

def FuseGroupFaces( group = None, np = 400, add = True ):
	"""
	
	
Description:
	Fuse faces inside a face group, be it in a solid or a shell.
	

Arguments:
	# group 
		Description:       The face group to fuse. 
		Type:              Group of Faces 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# np 
		Description:       See here. In this case, the number of point is approximatively respected. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     400  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Solid or Shell 
	Number:         1 
	Name:           "SolidWithFusedGroup" or "ShellWithFusedGroup"  

Conditions of use:
	-
	

"""
	
	if isinstance(np, str): print "[X] The first argument (np) should be an integer ."; return
	
	# Get the input shape(s)
	
	group = GetGUISelection(group, uniq = True)
	
	group = GetObject(group)
	
	#-
	
	# Check the input shape existence
	
	if "error" in [group] or None in [group]: return
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the parent shape
		
		main_shape = group.GetMainShape()
		
		#-
		
		# Get the main shape type
		
		nb_faces = geompy.NumberOfFaces(main_shape)
		nb_solids = geompy.NumberOfSolids(main_shape)
		
		main_shape_type = None
		
		if nb_solids == 1:
			
			main_shape_type = "solid"
			
		elif nb_solids == 0:
			
			if nb_faces > 0:
				
				main_shape_type = "shell"
				
			
		
		if main_shape_type == None:
			
			print "[X] The main shape should be a solid or a shell."; return
			
		
		#-
		
		# Fuse all faces in the group
		
		fused_face = FuseShellFaces(group, np, add = False)
		
		#-
		
		# Create a group of resting faces
		
		all_faces_group = geompy.CreateGroup(main_shape, geompy.ShapeType["FACE"])
		
		solid_face_list = geompy.SubShapeAll(main_shape, geompy.ShapeType["FACE"])
		
		for face in solid_face_list:
			
			face_id = geompy.GetSubShapeID(main_shape, face)
			geompy.AddObject(all_faces_group, face_id)
			
		
		resting_group = geompy.CutGroups(all_faces_group, group)
		
		#-
		
		# Create a new shell
		
		new_shell = geompy.MakeShell([resting_group, fused_face])
		
		#-
		
		if main_shape_type == "shell":
			
			# Add and return the resulting shape(s)
			
			if add == True:
			
				AddToStudy(new_shell, "ShellWithFusedGroup")
			
			return new_shell
			
			#-
			
		
		else:
			
			# Create a solid from the shell
			
			new_solid = geompy.MakeSolid([new_shell])
			
			#-
			
			# Add and return the resulting shape(s)
			
			if add == True:
			
				AddToStudy(new_solid, "SolidWithFusedGroup")
			
			return new_solid
			
			#-
			
		
		
	

fgf = FuseGroupFaces

def RemoveFaceExtraEdges( face = None, tol = 1e-7, add = True, infa = False ):
	"""
	
	
Description:
	Removes zero-length edges in a face.
	

Arguments:
	# face 
		Description:       The face from which to remove extra edges. 
		Type:              Face 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Face 
	Number:         1 
	Name:           "FaceWithoutExtraEdges"  

Conditions of use:
	-
	

"""
	
	# Get the input shape(s)
	
	face = GetGUISelection(face)
	
	face = GetObject(face)
	
	#-
	
	# Make this function recursive
	
	if isinstance(face, list):
		
		return_list = []
		
		for sub_object in face:
			
			return_list.append(RemoveFaceExtraEdges(sub_object, tol, add, infa))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [face] or None in [face]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = face
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the face normal
		
		normal = geompy.GetNormal(face)
		
		#-
		
		# Extrude the face_name
		
		extruded_face = geompy.MakePrismVecH(face, normal, 1000)
		
		#-
		
		# Remove the extra edges
		
		fixed_solid = geompy.RemoveExtraEdges(extruded_face)
		
		#-
		
		# Get the faces
		
		exploded_faces = geompy.SubShapeAll(fixed_solid, geompy.ShapeType["FACE"])
		
		#-
		
		# Get the fixed face
		
		for exploded_face in exploded_faces:
			
			vertexes = geompy.SubShapeAll(exploded_face, geompy.ShapeType["VERTEX"])
			
			match = True
			
			for vertex in vertexes:
				
				min_distance = geompy.MinDistance(vertex, face)
				
				if min_distance > tol:
					
					match = False
					
				
			
			if match == True:
				
				fixed_face = exploded_face
				
				break
				
			
		
		#-
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(fixed_face, "FaceWithoutExtraEdges", father)
			
		
		return fixed_face
		
		#-
		
	

rfee = RemoveFaceExtraEdges

def MakeFoilTrailingFillets( thick, wire = None, angle = 25, tol = 1e-7, add = True, infa = False ):
	"""
	
	
Description:
	Add a trailing fillet to a foil wire.
	

Arguments:
	# thick 
		Description:       The desired approximative trailing edge thickness. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# wire 
		Description:       The input foil. 
		Type:              Wire 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# angle 
		Description:       The angle in degrees between two touching sub-edges below which a fillet has to be done. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     25  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Face 
	Number:         1 
	Name:           "FoilWithTrailingFillet"  

Conditions of use:
	The input foil should be a planar closed wire having no trailing edge thickness, that is having (a) sharp trailing edge(s) ending by a vertex common to the upper and lower edges of the foil.
	

"""
	
	input_shape = wire
	
	# Get the input shape(s)
	
	input_shape = GetGUISelection(input_shape)
	
	input_shape = GetObject(input_shape)
	
	#-
	
	# Make this function recursive
	
	if isinstance(input_shape, list):
		
		return_list = []
		
		for sub_object in input_shape:
			
			return_list.append(MakeFoilTrailingFillets(thick, sub_object, angle, add, infa))
			
		
		return return_list
		
		#-
	
	# Check the input shape existence
	
	if "error" in [input_shape] or None in [input_shape]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = input_shape
	
	#-
	
	wire = input_shape
	
	if False: pass
	
	else:# All checks done
		
		small_value = 1e-3
		
		wire_length = geompy.BasicProperties(wire)[0]
		infinite_distance = 1e2 * wire_length
		cut_plane_size = 3 * thick
		
		wire_edges = GetSubShapes(wire)[1]
		
		try:
			
			wire = geompy.MakeWire(wire_edges)
			
		
		except:
			
			print "[X] The input shape should be \"wire-shaped\"."; return
			
		
		# Check the wire is closed
		
		if GetBoundaryVertexes(wire, add = False) != None:
			
			print "[X] The input wire should be closed."; return
			
		
		#-
		
		# Create a face from the wire
		
		wire_face = geompy.MakeFace(wire, isPlanarWanted = True)
		
		#-
		
		# Get vertexes
		
		wire_vertex_list = GetSubShapes(wire)[0]
		
		#-
		
		# Get trailing vertexes
		
		trailing_vertex_list = []
		cut_normal_list = []
		thickness_slope_list = []
		for vertex in wire_vertex_list:# For each vertex of the wire...
			
			# Get the edge(s) touching the vertex
			
			touching_edge_compound = geompy.GetShapesNearPoint(wire, vertex, geompy.ShapeType["EDGE"])
			
			touching_edge_list = geompy.SubShapeAll(touching_edge_compound, geompy.ShapeType["EDGE"])
			
			#-
			
			# Create local edge direction vectors
			
			direction_vector_list = []
			
			if len(touching_edge_list) == 1:
				
				touching_edge = touching_edge_list[0]
				
				direction_vector_tip_vertex_1 = geompy.MakeVertexOnCurve(touching_edge, 0.0 + small_value)
				direction_vector_tip_vertex_2 = geompy.MakeVertexOnCurve(touching_edge, 1.0 - small_value)
				
				direction_vector_1 = geompy.MakeVector(vertex, direction_vector_tip_vertex_1)
				direction_vector_2 = geompy.MakeVector(vertex, direction_vector_tip_vertex_2)
				
				direction_vector_list.append(direction_vector_1)
				direction_vector_list.append(direction_vector_2)
				
			
			else:
				
				for touching_edge in touching_edge_list:
					
					direction_vector_tip_vertex_parameter_1 = 0.0 + small_value
					direction_vector_tip_vertex_parameter_2 = 1.0 - small_value
					
					vertex_1 = geompy.MakeVertexOnCurve(touching_edge, 0.0)
					vertex_2 = geompy.MakeVertexOnCurve(touching_edge, 1.0)
					
					distance_1 = geompy.MinDistance(vertex_1, vertex)
					distance_2 = geompy.MinDistance(vertex_2, vertex)
					
					direction_vector_vertex_list = []
					if distance_2 > distance_1:
						
						direction_vector_tip_vertex = geompy.MakeVertexOnCurve(touching_edge, 0.0 + small_value)
						
					else:
						
						direction_vector_tip_vertex = geompy.MakeVertexOnCurve(touching_edge, 1.0 - small_value)
					
					direction_vector = geompy.MakeVector(vertex, direction_vector_tip_vertex)
					direction_vector_list.append(direction_vector)
				
			
			#-
			
			# Detect sharp angles
			
			[direction_vector_1, direction_vector_2] = direction_vector_list
			
			local_angle = geompy.GetAngle(direction_vector_1, direction_vector_2)
			
			if local_angle < angle:
				
				# Check if this is an open or closed angle
				
				tmp_vertex_1 = geompy.MakeVertexOnCurve(direction_vector_1, 1.0)
				tmp_vertex_2 = geompy.MakeVertexOnCurve(direction_vector_2, 1.0)
				tmp_edge = geompy.MakeEdge(tmp_vertex_1, tmp_vertex_2)
				tmp_vertex = geompy.MakeVertexOnCurve(tmp_edge, 0.5)
				
				distance = geompy.MinDistance(tmp_vertex, wire_face)
				
				if distance > tol:
					
					continue
					
				
				#-
				
				# Get the cut normal
				
				normalized_direction_vector_1 = GetNormalizedVector(direction_vector_1, add = False)
				normalized_direction_vector_2 = GetNormalizedVector(direction_vector_2, add = False)
				
				tip_vertex_1 = geompy.MakeVertexOnCurve(normalized_direction_vector_1, 1)
				tip_vertex_2 = geompy.MakeVertexOnCurve(normalized_direction_vector_2, 1)
				
				tmp_edge = geompy.MakeEdge(tip_vertex_1, tip_vertex_2)
				
				cut_normal_tip_vertex = geompy.MakeVertexOnCurve(tmp_edge, 0.5)
				
				cut_normal = geompy.MakeVector(vertex, cut_normal_tip_vertex)
				
				#-
				
				# Get the local thickness slope
				
				local_thickness = geompy.BasicProperties(tmp_edge)[0]
				
				delta_x = geompy.BasicProperties(cut_normal)[0]
				
				thickness_slope = local_thickness / delta_x
				
				thickness_slope_list.append(thickness_slope)
				
				#-
				
				trailing_vertex_list.append(vertex)
				cut_normal_list.append(cut_normal)
				
			
			#-
			
		
		#-
		
		final_wire = wire
		
		# Create trailing fillings
		
		for i in range(len(trailing_vertex_list)):# For each trailing vertex...
			
			trailing_vertex = trailing_vertex_list[i]
			cut_normal = cut_normal_list[i]
			thickness_slope = thickness_slope_list[i]
			
			# Create the cutting plane
			
			cutting_plane = geompy.MakePlane(trailing_vertex, cut_normal, cut_plane_size)
			
			#-
			
			# Cut the wire
			
			cut_position = thick / thickness_slope
			
			cutting_plane = geompy.MakeTranslationVectorDistance(cutting_plane, cut_normal, cut_position)
			
			extrusion = geompy.MakePrismVecH(cutting_plane, cut_normal, - infinite_distance)
			
			cut_wire = geompy.MakeCut(final_wire, extrusion)
			
			#-
			
			# Close the cut wire
			
			boundary_vertex_list = GetBoundaryVertexes(cut_wire, add = False, single = False)
			
			closing_edge = geompy.MakeEdge(boundary_vertex_list[0], boundary_vertex_list[1])
			
			try:
				closed_wire = geompy.MakeWire([cut_wire, closing_edge])
			except:
				
				print "[X] A \"make wire\" operation failed on a rebuilt wire."
				
				if add == True:
					
					AddToStudy([cut_wire, closing_edge], "ProblematicShapes")
					
				
				return [cut_wire, closing_edge]
				
			
			#-
			
			# Get the trailing vertexes IDs
			
			boundary_vertex_id_list = []
			
			for boundary_vertex in boundary_vertex_list:
				
				boundary_vertex_id = geompy.GetSubShapeID(closed_wire, boundary_vertex)
				boundary_vertex_id_list.append(boundary_vertex_id)
				
			
			#-
			
			# Make first fillets
			
			radius_1 = thick / 4.0
			radius_2 = thick / 3.0
			
			try:
				
				fillet_1 = geompy.MakeFillet1D(closed_wire, radius_1, boundary_vertex_id_list, doIgnoreSecantVertices = False)
				fillet_2 = geompy.MakeFillet1D(closed_wire, radius_2, boundary_vertex_id_list, doIgnoreSecantVertices = False)
				
			except:
				
				print "[X] Fillet operations failed on the cut wire."
				
				if add == True:
					
					AddToStudy(closed_wire, "ProblematicShape")
					
				
				return closed_wire
				
			
			#-
			
			# Get the fillets trailing edge lengths
			
			trailing_edge_middle_vertex = geompy.MakeVertexOnCurve(closing_edge, 0.5)
			
			trailing_edge_1 = geompy.GetShapesNearPoint(fillet_1, trailing_edge_middle_vertex, geompy.ShapeType["EDGE"])
			trailing_edge_2 = geompy.GetShapesNearPoint(fillet_2, trailing_edge_middle_vertex, geompy.ShapeType["EDGE"])
			
			trailing_edge_thickness_1 = geompy.BasicProperties(trailing_edge_1)[0]
			trailing_edge_thickness_2 = geompy.BasicProperties(trailing_edge_2)[0]
			
			#-
			
			# Deduce a better fillet radius
			
			trailing_edge_thickness_slope = (trailing_edge_thickness_2 - trailing_edge_thickness_1) / (radius_2 - radius_1)
			
			radius_3 = (radius_1 * trailing_edge_thickness_slope - trailing_edge_thickness_1) / trailing_edge_thickness_slope
			
			#-
			
			# Create the final fillet
			
			fillet_3 = geompy.MakeFillet1D(closed_wire, radius_3 * .99, boundary_vertex_id_list, doIgnoreSecantVertices = False)
			
			#-
			
			# Remove the fillet trailing edge
			
			trailing_edge_3 = geompy.GetShapesNearPoint(fillet_3, trailing_edge_middle_vertex, geompy.ShapeType["EDGE"])
			
			trailing_edge_thickness_3 = geompy.BasicProperties(trailing_edge_3)[0]
			
			final_wire = geompy.ProcessShape(fillet_3, ["DropSmallEdges"], ["DropSmallEdges.Tolerance3d"], [str(trailing_edge_thickness_3 * 1.1)])
			
			#-
		
		#-
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(final_wire, "FoilWithTrailingFillet")
			
		
		return final_wire
		
		#-
		
	

mftf = MakeFoilTrailingFillets

def MakeMiddleSpline( edges = [None], np = 20, cor = False, single = True, add = True, dim = 1 ):
	"""
	
	
Description:
	Creates a middle spline between two edges.
	

Arguments:
	# edges 
		Description:       The edges between which to build the middle edge. 
		Type:              List of 2 Edges 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# np 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     10  

	# cor 
		Description:       If equals True, the edge orientation is automatically corrected. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

Returned Values:
	"dim" value:    0 
	"single" value: False 
	Type:           Vertex 
	Number:         n 
	Name:           "MiddleSpline (Vertex)"  

	"dim" value:    0 
	"single" value: True 
	Type:           Compound of Vertexes 
	Number:         1 
	Name:           "MiddleSpline (Vertexes)"  

	"dim" value:    1 
	"single" value: - 
	Type:           Edge 
	Number:         1 
	Name:           "MiddleSpline"  

Conditions of use:
	Input edges should not touch each other.
	

"""
	
	if isinstance(np, str): print "[X] The first argument (np) should be an integer ."; return
	if isinstance(edges, list) == False: print "[X] The second argument (edges) should be an array."; return
	
	if dim > 1: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	edges = GetGUISelection(edges)
	
	edges = GetObject(edges)
	
	#-
	
	# Check the input shape existence
	
	if "error" in edges or None in edges: return
	
	#-
	
	# Check the number of selected objects
	
	if len(edges) != 2:
		
		print "[X] Two shapes should be selected."
		
		return
		
		
	#-
	
	else:# All checks done
		
		# Get the sub-shapes
		
		edges = GetSubShapes(edges)
		
		#-
		
		# Get the offset edge sense
		
		reverse_parameter = False
		
		if cor == True:
			
			linking_edges = [
			geompy.MakeEdge(edges[0][0][0], edges[1][0][0]), 
			geompy.MakeEdge(edges[0][0][0], edges[1][0][1])
			]
			
			linking_edge_lengths = [
			geompy.BasicProperties(linking_edges[0])[0], 
			geompy.BasicProperties(linking_edges[1])[0]
			]
			
			if linking_edge_lengths[0] > linking_edge_lengths[1]:
				
				reverse_parameter = True
				
			
		
		#-
		
		# Create the points
		
		edge_vertexes = [[], []]
		
		for parameter in [float(i) / (np - 1) for i in range(np)]:
			
			edge_vertexes[0].append(geompy.MakeVertexOnCurve(edges[0][-1], parameter))
			
			if reverse_parameter == True:
				
				parameter = 1.0 - parameter
				
			
			edge_vertexes[1].append(geompy.MakeVertexOnCurve(edges[1][-1], parameter))
			
		
		#-
		
		# Get the middle spline vertexes
		
		nb_vertexes = len(edge_vertexes[0])
		
		middle_vertexes = []
		
		for i in range(nb_vertexes):
			
			spline = geompy.MakeEdge(edge_vertexes[0][i], edge_vertexes[1][i])
			
			middle_vertexes.append(geompy.MakeVertexOnCurve(spline, 0.5))
			
		
		#-
		
		if dim == 0:# If the output dimension is 0...
			
			to_return = middle_vertexes
			to_return_name = "MiddleSpline (Vertex)"
			
			if single == True:
				
				# Create the vertex compound
				
				middle_vertex_compound = geompy.MakeCompound(middle_vertexes)
				
				#-
				
				to_return = middle_vertex_compound
				to_return_name = "MiddleSpline (Vertexes)"
				
			
			
		
		else:
			
			# Create the middle spline
			
			middle_spline = geompy.MakeInterpol(middle_vertexes)
			
			#-
			
			to_return = middle_spline
			to_return_name = "MiddleSpline"
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
	

mms = MakeMiddleSpline

def MakeCurveFromUnsortedVertexes( compound_and_start = [None], close = False, poly = False, single = True, add = True, infa = False, dim = 1):
	"""
	
	
Description:
	Creates a spline using a set of vertexes in random order, starting from a given vertex.
	

Arguments:
	# compound_and_start 
		Description:       The compound of vertexes describing the curve and the start vertex. For a closed curve, the start vertex is optional. 
		Type:              List of 1 Compound of Vertexes + 1 Vertex 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# close 
		Description:       Defines if the curve has to be closed or not. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# poly 
		Description:       If True, the output curve is a wire composed of straights edges. If False, the output curve is a single smooth edge. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

Returned Values:
	"dim" value:    0 
	"single" value: False 
	Type:           Vertex 
	Number:         n 
	Name:           "CurveFromUnstortedVertexes (Vertex)"  

	"dim" value:    0 
	"single" value: True 
	Type:           Compound or Vertexes 
	Number:         1 
	Name:           "CurveFromUnstortedVertexes (Vertexes)"  

	"dim" value:    1 
	"single" value: - 
	Type:           Edge or Wire 
	Number:         1 
	Name:           "CurveFromUnstortedVertexes"  

Conditions of use:
	-
	

"""
	
	if dim not in [0, 1]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	if isinstance(compound_and_start, list) == False: print "[X] The first argument (compound_and_start) should be an array."; return
	
	# Get the input shape(s)
	
	compound_and_start = GetGUISelection(compound_and_start)
	
	compound_and_start = GetObject(compound_and_start)
	
	#-
	
	# Check the input shape existence
	
	if "error" in compound_and_start or None in compound_and_start: return
	
	#-
	
	# Check the number of selected objects
	
	if len(compound_and_start) > 2: 
		
		print "[X] No more than two objects should be selected."
		
		return
		
	
	#-
	
	# Distinguish input shapes
	
	compound = None
	start = None
	
	for object in compound_and_start:
		
		nb_vertexes = int(geompy.WhatIs(object).split("\n")[1].split(": ")[1])
		
		if nb_vertexes == 1:
			
			start = object
		
		elif nb_vertexes > 1:
			
			compound = object
			
		
	
	if compound == None:
		
		print "[X] None of selected objects is a compound containing several vertexes."
		
		return
		
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = compound
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the sub-shapes
		
		compound = GetSubShapes(compound)
		
		resting_vertexes = compound[0]
		nb_vertexes = len(resting_vertexes)
		
		#-
		
		# Get the start vertex
		
		if start == None:
			
			vertex_index = 0
			
		
		else:
			
			min_distance = 1e99
			vertex_index = 0
			
			for i in range(nb_vertexes):
				
				vertex = resting_vertexes[i]
				
				distance = geompy.MinDistance(vertex, start)
				
				if distance < min_distance:
					
					min_distance = distance
					
					vertex_index = i
				
				i += 1
				
			
		
		#-
		
		# Sort the vertexes
		
		sorted_vertexes = []
		
		for i in range(nb_vertexes):
			
			vertex = resting_vertexes[vertex_index]
			
			sorted_vertexes.append(vertex)
			
			del resting_vertexes[vertex_index]
			
			min_distance = 1e99
			
			j = 0
			
			for resting_vertex in resting_vertexes:
				
				distance = geompy.MinDistance(resting_vertex, vertex)
				
				if distance < min_distance:
					
					min_distance = distance
					
					vertex_index = j
					
				
				j += 1
				
			
		
		#-
		
		if dim == 0:
			
			to_return = sorted_vertexes
			to_return_name = "CurveFromUnstortedVertexes (Vertex)"
			
			if single == True:
				
				compound = geompy.MakeCompound(to_return)
				
				to_return = compound
				to_return_name = "CurveFromUnstortedVertexes (Vertexes)"
				
			
		
		else:
			
			# Create the curve
			
			if poly == True:
				
				curve = geompy.MakePolyline(sorted_vertexes, close)
				
			
			else:
				
				curve = geompy.MakeInterpol(sorted_vertexes, close)
				
			
			#-
			
			to_return = curve
			to_return_name = "CurveFromUnstortedVertexes"
			
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, father, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
	

mcfuv = MakeCurveFromUnsortedVertexes

def MakeEllipticalFilling( center, guides = [None], np = 20, parallel = False, single = True, add = True, dim = 2 ):
	"""
	
	
Description:
	Creates a filling face having all its section being elliptical.
	

Arguments:
	# center 
		Description:       The central edge of the elliptical filling. 
		Type:              Edge 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# guides 
		Description:       The guiding edges. 
		Type:              List of 2 Edges 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# np 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     10  

	# parallel 
		Description:       If equals True, the elliptical sections of the filling are forced to be parallel. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     2  

Returned Values:
	"dim" value:    1 
	"single" value: False 
	Type:           Edge 
	Number:         n 
	Name:           "EllipticalFilling (Edge)"  

	"dim" value:    1 
	"single" value: True 
	Type:           Compound of Edges 
	Number:         1 
	Name:           "EllipticalFilling (Edges)"  

	"dim" value:    2 
	"single" value: - 
	Type:           Face 
	Number:         1 
	Name:           "EllipticalFilling"  

Conditions of use:
	Triangles formed by vertexes taken at a same position on the center and guiding edges should be always rectangle.
	

"""
	
	if isinstance(guides, list) == False: print "[X] The second argument (guides) should be an array."; return
	
	if dim not in [1, 2]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	guides = GetGUISelection(guides)
	
	guides = GetObject(guides)
	
	#-
	
	# Check the input shape existence
	
	if "error" in guides or None in guides: return
	
	#-
	
	# Check the number of selected objects
	
	if len(guides) != 2:
		
		print "[X] Two guiding edge should be selected."
		
		return
		
	
	#-
	
	# Get the input shape(s)
	
	[guide1, guide2, center] = GetObject(guides + [center], "GEOM")
	
	#-
	
	# Check the input shape characteritics
	
	for object in [guide1, guide2, center]:
		
		nb_edges = int(geompy.WhatIs(object).split("\n")[2].split(": ")[1])
		
		if nb_edges != 1:
			
			print "[X] Only edges should be selected."
			
			return
			
		
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Create ellipses
		
		ellipses = []
		
		if parallel == True:
			
			# Get the cutting plane
			
			center_edge_first_point = geompy.MakeVertexOnCurve(center, 0)
			center_edge_last_point = geompy.MakeVertexOnCurve(center, 1)
			
			cutting_plane = geompy.MakePlane(center_edge_first_point, center, 100000)
			
			#-
			
			for parameter in [n / float(np - 1) for n in range(np)]:
				
				if parameter == 0:
					
					local_guide1 = geompy.MakeVertexOnCurve(guide1, 0)
					local_guide2 = geompy.MakeVertexOnCurve(guide2, 0)
					local_center = center_edge_first_point
					
				
				elif parameter == 1:
					
					local_guide1 = geompy.MakeVertexOnCurve(guide1, 1)
					local_guide2 = geompy.MakeVertexOnCurve(guide2, 1)
					local_center = center_edge_last_point
					
				
				else:
					
					# Get the local center
					
					local_center = geompy.MakeVertexOnCurve(center, parameter)
					
					#-
					
					# Translate the cutting plane
					
					translated_cutting_plane = geompy.MakeTranslationTwoPoints(cutting_plane, center_edge_first_point, local_center)
					
					translated_cutting_plane_wire = geompy.SubShapeAll(translated_cutting_plane, geompy.ShapeType["WIRE"])[0]
					
					#-
					
					# Get the local guide point 1
					
					partition = geompy.MakePartition([translated_cutting_plane], [guide1], Limit = geompy.ShapeType["VERTEX"])
					
					vertexes = geompy.SubShapeAll(partition, geompy.ShapeType["VERTEX"])
					
					max_distance = 0
					
					local_guide1 = None
					
					for vertex in vertexes:
						
						distance = geompy.MinDistance(vertex, translated_cutting_plane_wire)
						
						if distance > max_distance:
							
							local_guide1 = vertex
							
							max_distance = distance
							
						
					
					#-
					
					# Get the local guide point 2
					
					partition = geompy.MakePartition([translated_cutting_plane], [guide2], Limit = geompy.ShapeType["VERTEX"])
					
					vertexes = geompy.SubShapeAll(partition, geompy.ShapeType["VERTEX"])
					
					max_distance = 0
					
					local_guide2 = None
					
					for vertex in vertexes:
						
						distance = geompy.MinDistance(vertex, translated_cutting_plane_wire)
						
						if distance > max_distance:
							
							local_guide2 = vertex
							
							max_distance = distance
							
						
					
					#-
					
				
				# Create the local ellipse
				
				ellipse = geompy.MakeArcOfEllipse(local_center, local_guide1, local_guide2)
				
				#-
				
				# Add the local ellipse to the list
				
				ellipses.append(ellipse)
				
				#-
				
			
			#-
			
		
		else:
			
			for parameter in [n / float(np - 1) for n in range(np)]:
				
				# Get the local points
				
				local_guide1 = geompy.MakeVertexOnCurve(guide1, parameter)
				local_guide2 = geompy.MakeVertexOnCurve(guide2, parameter)
				local_center = geompy.MakeVertexOnCurve(center, parameter)
				
				#-
				
				# Create the local ellipse
				
				ellipse = geompy.MakeArcOfEllipse(local_center, local_guide1, local_guide2)
				
				#-
				
				# Add the local ellipse to the list
				
				ellipses.append(ellipse)
				
				#-
			
		
		# Put the ellipses into a compound
		
		ellipse_compound = geompy.MakeCompound(ellipses)
		
		#-
		
		if dim == 1:
			
			to_return = ellipses
			to_return_name = "EllipticalFilling (Edge)"
			
			if single == True:
				
				to_return = ellipse_compound
				to_return_name = "EllipticalFilling (Edges)"
				
			
		
		else:
			
			# Create the filling
			
			elliptical_filling = geompy.MakeFilling(ellipse_compound, theMinDeg = 10, theMaxDeg = 15, theTol2D = 1e-5, theTol3D = 1e-5, theMethod = GEOM.FOM_AutoCorrect)
			
			#-
			
			to_return = elliptical_filling
			to_return_name = "EllipticalFilling"
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
	

mef = MakeEllipticalFilling

def MakeFillingFromUnsortedEdges( compound_and_start = [None], single = True, add = True, infa = False, dim = 2 ):
	"""
	
	
Description:
	Creates a filling face using a set of edges in a random order, starting from a given vertex position.
	

Arguments:
	# compound_and_start 
		Description:       The compound of edges and the start vertex. 
		Type:              List of 1 Compound of Edges+ 1 Vertex 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     2  

Returned Values:
	"dim" value:    1 
	"single" value: False 
	Type:           Edge 
	Number:         n 
	Name:           "FillingFromUnstortedEdges (Edge)"  

	"dim" value:    1 
	"single" value: True 
	Type:           Compound of Edges 
	Number:         1 
	Name:           "FillingFromUnstortedEdges (Edges)"  

	"dim" value:    2 
	"single" value: - 
	Type:           Face 
	Number:         1 
	Name:           "FillingFromUnstortedEdges"  

Conditions of use:
	-
	

"""
	
	if isinstance(compound_and_start, list) == False: print "[X] The first argument (compound_and_start) should be an array."; return
	
	if dim == 0 or dim == 3: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	compound_and_start = GetGUISelection(compound_and_start)
	
	compound_and_start = GetObject(compound_and_start)
	
	#-
	
	# Check the input shape existence
	
	if "error" in compound_and_start or None in compound_and_start: return
	
	#-
	
	# Check the number of selected objects
	
	if len(compound_and_start) > 2:
		
		print "[X] No more than two objects should be selected."
		
		return
		
	
	#-
	
	# Distinguish input shapes
	
	compound = None
	start = None
	
	for object in compound_and_start:
		
		nb_vertexes = int(geompy.WhatIs(object).split("\n")[1].split(": ")[1])
		nb_edges = int(geompy.WhatIs(object).split("\n")[2].split(": ")[1])
		
		if nb_vertexes == 1:
			
			start = object
		
		elif nb_edges > 1:
			
			compound = object
			
		
	
	compound = GetObject(compound, "GEOM")
	start = GetObject(start, "GEOM")
	
	if compound == None:
		
		print "[X] None of selected objects is a compound containing several edges."
		
		return
		
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = compound
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the sub-shapes
		
		compound = GetSubShapes(compound)
		
		resting_edges = compound[1]
		nb_edges = len(resting_edges)
		
		#-
		
		# Get the start edge
		
		if start == None:
			
			edge_index = 0
			
		
		else:
			
			min_distance = 1e99
			edge_index = 0
			
			for i in range(nb_edges):
				
				edge = resting_edges[i]
				
				distance = geompy.MinDistance(edge, start)
				
				if distance < min_distance:
					
					min_distance = distance
					
					edge_index = i
				
				i += 1
				
			
		
		#-
		
		# Sort the edges
		
		sorted_edges = []
		
		for i in range(nb_edges):
			
			edge = resting_edges[edge_index]
			
			sorted_edges.append(edge)
			
			del resting_edges[edge_index]
			
			min_distance = 1e99
			
			j = 0
			
			for resting_edge in resting_edges:
				
				distance = geompy.MinDistance(resting_edge, edge)
				
				if distance < min_distance:
					
					min_distance = distance
					
					edge_index = j
					
				
				j += 1
				
			
		
		#-
		
		# Create the edge compound
		
		filling_edge_compound = geompy.MakeCompound(sorted_edges)
		
		#-
		
		if dim == 1:
			
			to_return = sorted_edges
			to_return_name = "FillingFromUnstortedEdges (Edge)"
			
			if single == True:
				
				to_return = filling_edge_compound
				to_return_name = "FillingFromUnstortedEdges (Edges)"
				
			
		
		else:
			
			# Create the filling
			
			filling = geompy.MakeFilling(filling_edge_compound, theMinDeg = 10, theMaxDeg = 15, theTol2D = 1e-5, theTol3D = 1e-5, theMethod = GEOM.FOM_AutoCorrect)
			
			#-
			
			to_return = filling
			to_return_name = "FillingFromUnstortedEdges"
			
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, father, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
	


mffue = MakeFillingFromUnsortedEdges

def MakeFoilFromUnsortedVertexes( compound = None, coef = 1.5, coef2 = 0.02, strat = "grow", poly = False, angle = 60, add = True, infa = False ):
	"""
	
	
Description:
	Makes a foil wire from an unsorted compound of vertexes.
	

Arguments:
	# compound 
		Description:       The compound of vertexes describing the foil. 
		Type:              List of 1 Compound of Vertexes + 1 Vertex 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# coef 
		Description:       Coefficient influencing the search distance: search_distance = coef * mean_distance_between_vertexes 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1.5  

	# coef2 
		Description:       When the foil curvature is very low, some vertexes can be skipped. This coefficient has an influence on skipped vertex detection. Lower it is, finer is the detection. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     0.02  

	# strat 
		Description:       The search distance strategy. If equals "grow", the search distance  increases until at least one nearby vertex is seen. If equals "stop", the algorithm stops when no nearby vertex  is seen within the search distance. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "grow"  

	# poly 
		Description:       If True, the output wire is made of straights edges. If False, the output wire is made of smooth edge. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# angle 
		Description:       The feature angle in degrees. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     60  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Wire 
	Number:         1 
	Name:           "FoilFromUnsortedVertexes"  

Conditions of use:
	The input vertex compound must be planar.
	

"""
	
	input_shape = compound
	
	# Get the input shape(s)
	
	input_shape = GetGUISelection(input_shape)
	
	input_shape = GetObject(input_shape)
	
	#-
	
	# Make this function recursive
	
	if isinstance(input_shape, list):
		
		return_list = []
		
		for sub_object in input_shape:
			
			return_list.append(MakeFoilFromUnsortedVertexes(sub_object, coef, coef2, strat, poly, angle, add, infa))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [input_shape] or None in [input_shape]: return
	
	#-
	
	# Check the input shape type
	
	nb_vertexes = geompy.NumberOfSubShapes(input_shape, geompy.ShapeType["VERTEX"])
	if nb_vertexes < 2:
		
		print "[X] The first argument (compound) should contain more than one vertex."; return
		
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = input_shape
	
	#-
	
	compound = input_shape
	
	if False: pass
	
	else:# All checks done
		
		feature_angle = angle
		
		# Get the sub-shapes
		
		compound = GetSubShapes(compound)
		
		resting_vertexes = compound[0]
		nb_vertexes = len(resting_vertexes)
		
		#-
		
		# Get the biggest dimension of the compound
		
		[x_min, x_max, y_min, y_max, z_min, z_max ] = geompy.BoundingBox(compound[-1])
		
		x = (x_min + x_max) / 2.0
		y = (y_min + y_max) / 2.0
		z = (z_min + z_max) / 2.0
		
		center = geompy.MakeVertex(x, y, z)
		
		farest_vertex_1 = None
		farest_vertex_1_id = None
		max_distance = 0
		i = 0
		for vertex in resting_vertexes:
			distance = geompy.MinDistance(vertex, center)
			if distance > max_distance:
				farest_vertex_1 = vertex
				farest_vertex_1_id = i
				max_distance = distance
				
			i += 1
		
		farest_vertex_2 = None
		max_distance = 0
		for vertex in resting_vertexes:
			distance = geompy.MinDistance(vertex, farest_vertex_1)
			if distance > max_distance:
				farest_vertex_2 = vertex
				max_distance = distance
		
		biggest_dimension = geompy.MinDistance(farest_vertex_1, farest_vertex_2)
		
		#-
		
		# Define the search distance
		
		nb_profile_vertexes = len(resting_vertexes)
		
		mean_distance_between_vertexes = 2.0 * biggest_dimension / nb_profile_vertexes
		
		search_distance = coef * mean_distance_between_vertexes
		initial_search_distance = search_distance
		
		#-
		
		# Initialize the sorted vertex list
		
		sorted_vertexes = [resting_vertexes[farest_vertex_1_id]]
		
		del resting_vertexes[farest_vertex_1_id]
		
		#-
		
		# As long as there are non sorted vertexes...
		
		while len(resting_vertexes) > 0:
			
			last_vertex = sorted_vertexes[-1]
			
			vertex_to_delete_ids = []
			
			# Get vertexes being relatively close
			
			closest_vertexes = []
			closest_vertex_indexes = []
			
			i = 0
			for resting_vertex in resting_vertexes:
				
				distance = geompy.MinDistance(resting_vertex, last_vertex)
				
				if distance < search_distance:
					
					closest_vertexes.append(resting_vertex)
					closest_vertex_indexes.append(i)
					
				i += 1
			
			if len(closest_vertexes) == 0:
				
				if strat == "grow":
					
					search_distance *= 1.1
					
					continue
					
				
				else:# "stop"
					
					break
					
				
			
			search_distance = initial_search_distance
			
			#-
			
			# Get the next vertex
			
			best_vertex = None
			
			if len(sorted_vertexes) == 1:
				
				i = 0
				min_distance = 1e99
				for vertex in closest_vertexes:
					
					distance = geompy.MinDistance(vertex, last_vertex)
					
					if distance < min_distance:
						
						best_vertex = vertex
						best_vertex_index = i
						
						min_distance = distance
						
					
					i += 1
					
				
			
			else:
				
				previous_vertex = sorted_vertexes[ - 2]
				
				last_vector = geompy.MakeVector(previous_vertex, last_vertex)
				
				i = 0
				min_angle = 1e99
				for vertex in closest_vertexes:
					
					vector = geompy.MakeVector(last_vertex, vertex)
					
					angle = geompy.GetAngleVectors(last_vector, vector)
					
					
					
					if angle < min_angle:
						
						best_vertex = vertex
						best_vertex_index = i
						
						min_angle = angle
					
					i += 1
					
				
			
			#-
			
			# Remove it from the resting vertex list
			
			sorted_vertexes.append(best_vertex)
			
			vertex_to_delete_ids.append(closest_vertex_indexes[best_vertex_index])
			
			#-
			
			# Check if the segment covers other vertexes
			
			segment = geompy.MakeEdge(last_vertex, best_vertex)
			segment_length = geompy.BasicProperties(segment)[0]
			tol = segment_length * coef2
			
			i = 0
			for vertex in closest_vertexes:
				
				if i != best_vertex_index:
					
					distance = geompy.MinDistance(vertex, segment)
					
					if distance <= tol:
						
						vertex_to_delete_ids.append(closest_vertex_indexes[i])
						
					
				
				i += 1
				
			
			#-
			
			# Delete the suitable vertexes from the resting vertex list
			
			# http: / / stackoverflow.com / a / 28697246 / 2123808
			for vertex_to_delete_id in sorted(vertex_to_delete_ids, reverse = True):
				
				del resting_vertexes[vertex_to_delete_id]
				
			
			#-
			
		
		#-
		
		# Create the wire
		
		if poly == False:
			
			# Look for a feature angle
			
			v1 = sorted_vertexes[0]
			v2 = sorted_vertexes[1]
			
			[dx, dy, dz] = geompy.MinDistanceComponents(v1, v2)[1:4]
			last_vector = geompy.MakeVectorDXDYDZ(dx, dy, dz)
			
			first_vertex_indice = None
			nb_sorted_vertexes = len(sorted_vertexes)
			for i in range(nb_sorted_vertexes):
				
				if i > 0:
					
					next_i = i + 1
					if next_i == nb_sorted_vertexes:
						next_i = 0
					
					v1 = sorted_vertexes[i]
					v2 = sorted_vertexes[next_i]
					
					[dx, dy, dz] = geompy.MinDistanceComponents(v1, v2)[1:4]
					new_vector = geompy.MakeVectorDXDYDZ(dx, dy, dz)
					
					angle = geompy.GetAngle(last_vector, new_vector)
					
					if angle >= feature_angle:
						first_vertex_indice = i
						break
					
					last_vector = new_vector
				
			
			if first_vertex_indice == None:
				shift = 0
				first_vertex = sorted_vertexes[0]
			else:
				shift = first_vertex_indice
				first_vertex = sorted_vertexes[first_vertex_indice]
			
			#-
			
			# Create curves
			
			index_1 = shift
			if index_1 >= nb_sorted_vertexes:
				index_1 -= nb_vertexes
			
			index_2 = shift + 1
			if index_2 >= nb_sorted_vertexes:
				index_2 -= nb_vertexes
			
			v1 = sorted_vertexes[index_1]
			v2 = sorted_vertexes[index_2]
			
			[dx, dy, dz] = geompy.MinDistanceComponents(v1, v2)[1:4]
			last_vector = geompy.MakeVectorDXDYDZ(dx, dy, dz)
			
			curves = []
			curve_vertexes = [first_vertex]
			for i in range(nb_sorted_vertexes):
				
				i = i + shift
				
				if i > shift:
					
					if i >= nb_sorted_vertexes:
						i -= nb_sorted_vertexes
					
					next_i = i + 1
					if next_i == nb_sorted_vertexes:
						next_i = 0
					
					v1 = sorted_vertexes[i]
					v2 = sorted_vertexes[next_i]
					
					[dx, dy, dz] = geompy.MinDistanceComponents(v1, v2)[1:4]
					new_vector = geompy.MakeVectorDXDYDZ(dx, dy, dz)
					
					angle = geompy.GetAngle(last_vector, new_vector)
					
					if angle >= feature_angle:
						
						curve_vertexes.append(v1)
						
						curve = geompy.MakeInterpol(curve_vertexes)
						curves.append(curve)
						
						curve_vertexes = [v1]
						
					
					else:
						
						curve_vertexes.append(v1)
						
					
					last_vector = new_vector
					
				
			
			curve_vertexes.append(first_vertex)
			curve = geompy.MakeInterpol(curve_vertexes)
			curves.append(curve)
			
			wire = geompy.MakeWire(curves)
			
			#-
			
		else:
			
			wire = geompy.MakePolyline(sorted_vertexes, True)
			
		
		#-
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(wire, "FoilFromUnsortedVertexes", father)
			
		
		return wire
		
		#-
		
	

mffuv = MakeFoilFromUnsortedVertexes

def MakeEdgeOffset( dist, edge = None, pos = [0, 1], face = None, plane = None, np = 20, curv = True, close = False, rebuild = True, tol = 1e-7, rev = False, single = True, add = True, infa = False, dim = 1 ):
	"""
	
	
Description:
	Creates an offset of an edge.
	

Arguments:
	# dist 
		Description:       The offset distance. Must be an list to create a variable offset. 
		Type:              Float or  List of  Floats 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# edge 
		Description:       The input edge. 
		Type:              Edge 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# pos 
		Description:       The positions on the source edge (0 &lt; pos &lt; 1). Only necessary if the dist  argument is an list. 
		Type:              List of  Floats 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     [0,1]  

	# face 
		Description:       See here. 
		Type:              Face 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# plane 
		Description:       See here. If the input edge is straight, the default plane is the OXY plane. 
		Type:              Face 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# np 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     50  

	# curv 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# rebuild 
		Description:       In case dim = 2, defines if the input edge has to be rebuilt in the same way than the offset edge. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# close 
		Description:       If equals True, the offset edge is linked to the source edge by two additional edges. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# rev 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

Returned Values:
	"dim" value:    0 
	"single" value: False 
	Type:           Vertex 
	Number:         n 
	Name:           "EdgeOffset (Vertex)"  

	"dim" value:    0 
	"single" value: True 
	Type:           Compound of Vertexes 
	Number:         1 
	Name:           "EdgeOffset (Vertexes)"  

	"dim" value:    1 
	"single" value: False 
	Type:           Edge 
	Number:         3 
	Name:           "ClosedEdgeOffset (Edge)"  

	"dim" value:    1 
	"single" value: True 
	Type:           Compound of Edges 
	Number:         1 
	Name:           "EdgeOffset" or "ClosedEdgeOffset"  

	"dim" value:    2 
	"single" value: - 
	Type:           Face 
	Number:         1 
	Name:           "EdgeOffset (Face)"  

Conditions of use:
	The input edge has to be open.
	
	In addition, if the input edge is straight, it is also necessary to set the face or the plane argument so as the function knows the offset direction 

"""
	
	if dim not in [0, 1, 2]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	edge = GetGUISelection(edge)
	
	[edge, face, plane] = GetObject([edge, face, plane])
	
	#-
	
	# Make this function recursive
	
	if isinstance(edge, list):
		
		return_list = []
		
		for sub_object in edge:
			
			return_list.append(MakeEdgeOffset(dist, sub_object, pos, face, plane, np, curv, close, rebuild, tol, rev, single, add, infa, dim))
			
		
		return return_list
		
		#-
	
	# Check the input shape existence
	
	if "error" in [edge, face, plane] or None in [edge]: return
	
	#-
	
	# Check the input shape types
	
	if geompy.NumberOfEdges(edge) != 1:
		
		print "[X] The second argument (edge) should be a single edge."; return
		
	
	if face != None and geompy.NumberOfFaces(face) != 1:
		
		print "[X] The fourth argument (face) should be a single face."; return
		
	
	if plane != None and geompy.NumberOfFaces(plane) != 1:
		
		print "[X] The fifth argument (plane) should be a single face."; return
		
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = edge
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the sub-shapes
		
		edge = GetSubShapes(edge)
		
		#-
		
		if face == None:# If no face is given by the user...
			
			if plane == None:# And if no plane is given by the user...
				
				# Check if the edge is closed
				
				boundary_vertexes = GetBoundaryVertexes(edge[-1], add = False, single = False)
				
				edge_is_closed = False
				if boundary_vertexes == None:
					
					edge_is_closed = True
					
				
				#-
				
				if edge_is_closed == True:# If it is closed...
					
					# Get the edge plane
					
					plane = geompy.MakeFace(edge[-1], True)
					
					#-
					
				
				else:
					
					# Close the input edge
					
					closing_edge = geompy.MakeEdge(edge[0][0], edge[0][1])
					
					closed_contour = geompy.MakeWire([edge[-1], closing_edge])
					
					#-
					
					if abs(geompy.BasicProperties(closing_edge)[0] - geompy.BasicProperties(edge[-1])[0]) < tol:# If the input wire is straight...
						
						# Use the OXY plane
						
						plane = geompy.MakeFaceHW(10, 10, 1)
						
						#-
					
					else:
						
						# Get the edge plane
						
						plane = geompy.MakeFace(closed_contour, True)
						
						#-
						
					
				
			
			# Get the plane normal
			
			normal = geompy.GetNormal(plane)
			
			#-
			
			# Extrude the edge perpendicular to its plane (to get its normal further)
			
			face = geompy.MakePrismVecH(edge[-1], normal, 0.1)
			
			#-
			
		
		offset_vertexes = []
		
		# Get the list of positions on the edge where to compute the offset
		
		if curv == True:
			
			parameter_list = DiscretizeEdgeByCurvature(edge[-1], np, dim = -1)
			
		
		else:
			
			parameter_list = [n / float(np) for n in range(np + 1)]
			
		
		#-
		
		# Create the offset vertexes
		
		for parameter in parameter_list:
			
			vertex = geompy.MakeVertexOnCurve(edge[-1], parameter)
			
			normal = geompy.GetNormal(face, vertex)
			
			if dist == None:
				
				edge_length = geompy.BasicProperties(edge[-1])[0]
				
				dist = edge_length / 100
				
				print "[i] No offset distance given > default one:", dist
				
			
			if isinstance(dist, list):
				
				#### Here the numpy function interp() was replaced by code doing the same thing.
				
				#offsetDistance = numpy.interp(parameter, pos, dist)
				
				for i in range(len(pos) - 1):
					
					if parameter >= pos[i] and parameter < pos[i + 1]:
						
						slope = (dist[i + 1] - dist[i]) / (pos[i + 1] - pos[i])
						
						offset_distance = dist[i] + (parameter - pos[i]) * slope
						
					
				if parameter == pos[-1]:
					
					offset_distance = dist[-1]
					
				
				#### -
				
			
			else:
				
				offset_distance = dist
				
			
			if rev == True:
				
				offset_distance *= -1.0
				
			
			offset_vertex = geompy.MakeTranslationVectorDistance(vertex, normal, offset_distance)
			
			offset_vertexes.append(offset_vertex)
		
		#-
		
		if dim == 0:# If the output dimension is 0...
			
			to_return = offset_vertexes
			to_return_name = "EdgeOffset (Vertex)"
			
			if single == True:
				
				compound = geompy.MakeCompound(offset_vertexes)
				
				to_return = compound
				to_return_name = "EdgeOffset (Vertexes)"
				
			
		
		else:
			
			# Create the offset spline
			
			offset_spline = geompy.MakeInterpol(offset_vertexes)
			
			#-
			
			to_return = offset_spline
			to_return_name = "EdgeOffset"
			
			if dim == 1 and close == True:
				
				# Create the intermediate edges
				
				offset_vertexes = geompy.SubShapeAll(offset_spline, geompy.ShapeType["VERTEX"])
				
				offset_edges = [offset_spline]
				
				intermediate_edge = geompy.MakeEdge(geompy.MakeVertexOnCurve(edge[-1], 0), offset_vertexes[0])
				
				offset_edges.append(intermediate_edge)
				
				intermediate_edge = geompy.MakeEdge(geompy.MakeVertexOnCurve(edge[-1], 1), offset_vertexes[1])
				
				offset_edges.append(intermediate_edge)
				
				#-
				
				to_return = offset_edges
				to_return_name = "ClosedEdgeOffset (Edge)"
				
				if single == True:
					
					compound = geompy.MakeCompound(offset_edges)
					
					to_return = compound
					to_return_name = "ClosedEdgeOffset"
					
				
			
			if dim == 2:
			
				# Rebuild edges if necessary
				
				if rebuild == True:
					
					parameter_list = DiscretizeEdgeByCurvature(edge[-1], np, dim = -1)
					
					edge[-1] = RebuildSpline(parameter_list, edge[-1], add = False)
					offset_spline = RebuildSpline(parameter_list, offset_spline, add = False)
					
				
				#-
				
				# Link the edge to the offset
				
				##########################################
				linking_face = geompy.MakeQuad2Edges(edge[-1], offset_spline) # This shown better meshing quality
				#tmp_compound = geompy.MakeCompound([edge, offset])
				#linking_face = geompy.MakeFilling(tmp_compound, theMethod = GEOM.FOM_AutoCorrect)
				##########################################
				
				#-
				
				to_return = linking_face
				to_return_name = "EdgeOffset (Face)"
				
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, father, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
	

meo = MakeEdgeOffset

def MakePlanarWireOffset( dist, wire = None, plane = None, np = 50, curv = True, simple = False, angle = 15, rebuild = True, tol = 1e-7, rev = False, single = True, add = True, infa = False, dim = 1 ):
	"""
	
	
Description:
	Creates an offset of a planar wire.
	

Arguments:
	# dist 
		Description:       The offset distance. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# wire 
		Description:       The input wire. 
		Type:              Wire 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# plane 
		Description:       See here. If the input wire is straight, the default plane is the OXY plane. 
		Type:              Face 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# np 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     50  

	# curv 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# angle 
		Description:       The angle in degrees above which an arc is added between two offset edges. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     15  

	# rebuild 
		Description:       In case dim = 2, defines if the input edge has to be rebuilt in the same way than the offset edge. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# rev 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

Returned Values:
	"dim" value:    1 
	"single" value: False 
	Type:           Edge 
	Number:         n 
	Name:           "WireOffset (Edge)"  

	"dim" value:    1 
	"single" value: True 
	Type:           Wire or Compound of Edges 
	Number:         1 
	Name:           "WireOffset"  

	"dim" value:    2 
	"single" value: False 
	Type:           Face 
	Number:         n 
	Name:           "WireOffset (Face)"  

	"dim" value:    2 
	"single" value: True 
	Type:           Shell or Compound of Faces 
	Number:         1 
	Name:           "WireOffset (Faces)"  

Conditions of use:
	-
	

"""
	
	if dim not in [1, 2]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	input_shape = wire
	
	# Get the input shape(s)
	
	input_shape = GetGUISelection(input_shape)
	
	[input_shape, plane] = GetObject([input_shape, plane])
	
	#-
	
	# Make this function recursive
	
	if isinstance(input_shape, list):
		
		return_list = []
		
		for sub_object in input_shape:
			
			return_list.append(MakePlanarWireOffset(dist, sub_object, plane, np, curv, simple, angle, rebuild, tol, rev, single, add, infa, dim))
			
		
		return return_list
		
		#-
	
	# Check the input shape existence
	
	if "error" in [input_shape, plane] or None in [input_shape]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True:
		
		father = input_shape
		
	
	#-
	
	wire = input_shape
	
	if False: pass
	
	else:# All checks done
		
		if rev == True: dist *= -1.0
		
		small_value = 1e-3
		
		# Check if the group is "wire-shaped"
		
		wire_edge_list = GetSubShapes(wire)[1]
		
		try:
			
			wire = geompy.MakeWire(wire_edge_list)
			
		except:
			
			print "[X] The input shape should be \"wire-shaped\"."; return
			
		
		#-
		
		# Check if the wire is closed
		
		boundary_vertexes = GetBoundaryVertexes(wire, add = False, single = False)
		
		wire_is_closed = False
		if boundary_vertexes == None:
			
			wire_is_closed = True
			
		
		#-
		
		# Reorder wire edges
		
		edges = GetReorderedEdges(wire, add = False)
		
		nb_edges = len(edges)
		
		#-
		
		# Get the input wire length
		
		wire_length = geompy.BasicProperties(wire)[0]
		
		#-
		
		if plane == None:# If no plane is given by the user...
			
			# Close the input edge
			
			wire_is_straigth = False
			if not wire_is_closed:
				
				closing_edge = geompy.MakeEdge(boundary_vertexes[0], boundary_vertexes[1])
				closing_edge_length = geompy.BasicProperties(closing_edge)[0]
				
				closed_contour = geompy.MakeWire([wire, closing_edge])
				
				# Check if the wire is straight
				
				if abs(closing_edge_length - wire_length) < tol:
					
					wire_is_straigth = True
					
				
			
			else:
				
				closed_contour = wire
				
			
			#-
			
			if wire_is_straigth:
				
				# Use the OXY plane
				
				plane = geompy.MakeFaceHW(10, 10, 1)
				
				#-
			
			else:
				
				# Get the wire plane
				
				plane = geompy.MakeFace(closed_contour, True)
				
				if geompy.NumberOfFaces(plane) > 1:
					
					plane = geompy.SubShapeAll(plane, geompy.ShapeType["FACE"])[0]
					
				
				#-
				
			
		
		# Get the plane normal
		
		normal = geompy.GetNormal(plane)
		
		#-
		
		# Check if the wire is planar
		
		some_vertex_from_wire = GetSubShapes(wire)[0][0]
		
		plane = geompy.MakePlane(some_vertex_from_wire, normal, wire_length * 1e3)
		
		common = geompy.MakeCommon(wire, plane)
		
		if GeometricalEquality([wire, common], tol = 1) == False:
			
			print "[X] The input wire should be planar."; return
			
		
		#-
		
		# Create offsets
		
		nb_loops = nb_edges
		
		if wire_is_closed:
			
			nb_loops += 1
			edges.append(edges[0])
			
		
		offsets = []
		contact_vertexes = []
		edge_turn_angles = []
		for i in range(nb_loops):
			
			edge = edges[i]
			
			offset = None
			
			try:
				offset = MakeEdgeOffset(dist, edge, np = np, plane = plane, curv = curv, add = False)
			except:
				dist = -dist
				offset = MakeEdgeOffset(dist, edge, np = np, plane = plane, curv = curv, add = False)
			
			if i > 0:
				
				# Get the previous edge and offset
				
				previous_edge = edges[i - 1]
				previous_offset = offsets[i - 1]
				
				current_edges = [previous_edge, edge]
				current_offsets = [previous_offset, offset]
				
				#-
				
				# Get contact vertex
				
				contact_vertex = geompy.MakeVertexOnLinesIntersection(previous_edge, edge)
				contact_vertexes.append(contact_vertex)
				
				#-
				
				# Get edge orientations
				
				edge_orientations = []
				for j in range(2):
					
					each_edge = current_edges[j]
					
					vertex = geompy.MakeVertexOnCurve(each_edge, 0)
					
					distance_from_contact = geompy.MinDistance(vertex, contact_vertex)
					
					if distance_from_contact <= tol:
						edge_orientations.append("out")
					else:
						edge_orientations.append("in")
					
				
				#-
				
				# Get edge directions close to contact vertex
				
				edge_directions = []
				for j in range(2):
					
					each_edge = current_edges[j]
					
					if edge_orientations[j] == "in":
						parameter_1 = 1.0
						parameter_2 = 1.0 - small_value
					else:
						parameter_1 = 0.0
						parameter_2 = 0.0 + small_value
					
					v1 = geompy.MakeVertexOnCurve(each_edge, parameter_1)
					v2 = geompy.MakeVertexOnCurve(each_edge, parameter_2)
					
					edge_direction = geompy.MakeVector(v1, v2)
					edge_direction = GetNormalizedVector(edge_direction, add = False)
					edge_directions.append(edge_direction)
					
				
				#-
				
				# Get the turn angle difference between edges
				
				edge_turn_angle = GetTurnAngle(edge_directions[0], edge_directions[1], normal, unit = "deg")
				edge_turn_angles.append(edge_turn_angle)
				
				#-
				
				# Get the offset edge directions
				
				offset_directions = []
				for j in range(2):
					
					each_edge = current_edges[j]
					each_offset = current_offsets[j]
					
					if edge_orientations[j] == "in":
						parameter = 1.0
					else:
						parameter = 0.0
					
					v1 = geompy.MakeVertexOnCurve(each_edge, parameter)
					v2 = geompy.MakeVertexOnCurve(each_offset, parameter)
					
					offset_direction = geompy.MakeVector(v1, v2)
					offset_direction = GetNormalizedVector(offset_direction, add = False)
					offset_directions.append(offset_direction)
					
				
				#-
				
				# Get the turn angle difference between edges
				
				offset_turn_angle = GetTurnAngle(offset_directions[0], offset_directions[1], normal, unit = "deg")
				
				#-
				
				# Reverse the offset if necessary
				
				turn_angle_difference = abs(offset_turn_angle - edge_turn_angle)
				
				if abs(180.0 - turn_angle_difference) > 10.0:
					
					offset = MakeEdgeOffset( -dist, edge, np = np, plane = plane, curv = curv, add = False)
					
				
				#-
				
			
			offsets.append(offset)
			
		#-
		
		tri_edge_faces = []
		linking_arcs = []
		
		if simple == False:
			
			# Link offsets
			
			for i in range(nb_loops):
				
				if i > 0:
					
					offset = offsets[i]
					previous_offset = offsets[i - 1]
					
					current_offsets = [previous_offset, offset]
					
					contact_vertex = contact_vertexes[i - 1]
					
					edge_turn_angle = edge_turn_angles[i - 1]
					
					# Detect intersection
					
					offsets_are_intersected = False
					
					intersection = geompy.MakeSection(previous_offset, offset)
					
					if geompy.NumberOfSubShapes(intersection, geompy.ShapeType["VERTEX"]) == 1:
						
						offsets_are_intersected = True
						
					
					#-
					
					if offsets_are_intersected:
						
						# Trim the offsets
						
						for j in range(2):
							
							each_edge = current_edges[j]
							each_offset = current_offsets[j]
							
							# Partition the offset
							
							partitioned_offset = geompy.MakePartition([each_offset], [intersection])
							
							#-
							
							# Keep the suitable edge
							
							partitioned_offset_edges = geompy.SubShapeAll(partitioned_offset, geompy.ShapeType["EDGE"])
							
							max_distance = 0
							for partitioned_offset_edge in partitioned_offset_edges:
								
								distance = geompy.MinDistance(contact_vertex, partitioned_offset_edge)
								
								if distance > max_distance:
									
									new_offset = partitioned_offset_edge
									max_distance = distance
									
								
							
							#-
							
							# Update the offset list
							
							offsets[i - 1 + j] = new_offset
							
							#-
							
						
						#-
						
					
					else:
						
						if abs(180.0 - edge_turn_angle) <= angle:# For small angles...
							
							# Extend the offsets
							
							extended_offsets = ExtendSplinesToIntersection(current_offsets, np, tol, add = False)
							
							#-
							
							# Update the offset list
							
							for j in range(2):
								
								offsets[i - 1 + j] = extended_offsets[j]
								
							
							#-
							
						
						else:# For big angles...
							
							# Get the offset boundary end
							
							boundary_vertexes = []
							for j in range(2):
								
								each_offset = current_offsets[j]
								
								boundary_vertex = geompy.GetShapesNearPoint(each_offset, contact_vertex, geompy.ShapeType["VERTEX"])
								boundary_vertex = geompy.SubShapeAll(boundary_vertex, geompy.ShapeType["VERTEX"])[0]
								
								boundary_vertexes.append(boundary_vertex)
								
							
							#-
							
							# Create the circle arc linking offsets
							
							linking_arc = geompy.MakeArcCenter(contact_vertex, boundary_vertexes[0], boundary_vertexes[1])
							linking_arcs.append(linking_arc)
							
							#-
							
							# Create the tri - angle face
							
							edge_1 = geompy.MakeEdge(contact_vertex, boundary_vertexes[0])
							edge_2 = geompy.MakeEdge(contact_vertex, boundary_vertexes[1])
							
							tri_angle_face = geompy.MakeFaceWires([edge_1, edge_2, linking_arc], isPlanarWanted = True)
							tri_edge_faces.append(tri_angle_face)
							
							#-
							
						
					
					if i == 1 and wire_is_closed:
						
						offsets[-1] = offsets[0]
						
						
					
				
			
			#-
			
		
		if wire_is_closed:
			
			edges[0] = edges[-1]
			offsets[0] = offsets[-1]
			
			del edges[-1]
			del offsets[-1]
			
		
		if dim == 1:
			
			to_return = offsets + linking_arcs
			to_return_name = "WireOffset (Edge)"
			
			if single == True:
				
				try:
					offset_wire = geompy.MakeWire(offsets + linking_arcs)
				except:
					offset_wire = geompy.MakeCompound(offsets + linking_arcs)
				
				to_return = offset_wire
				to_return_name = "WireOffset"
				
			
		
		else:
			
			# Rebuild edges if necessary
			
			if rebuild == True:
				
				for i in range(nb_edges):
					
					edge = edges[i]
					offset = offsets[i]
					
					parameter_list = DiscretizeEdgeByCurvature(edge, np, dim = -1)
					
					edge = RebuildSpline(parameter_list, edge, add = False)
					offset = RebuildSpline(parameter_list, offset, add = False)
					
					edges[i] = edge
					offsets[i] = offset
					
				
			
			#-
			
			# Link edges to offsets
			
			linking_faces = []
			for i in range(nb_edges):
				
				edge = edges[i]
				offset = offsets[i]
				
				##########################################
				linking_face = geompy.MakeQuad2Edges(edge, offset) # This shown better meshing quality
				#tmp_compound = geompy.MakeCompound([edge, offset])
				#linking_face = geompy.MakeFilling(tmp_compound, theMethod = GEOM.FOM_AutoCorrect)
				##########################################
				linking_faces.append(linking_face)
				
			
			#-
			
			to_return = linking_faces + tri_edge_faces
			to_return_name = "WireOffset (Face)"
			
			if single == True:
				
				try:
					shell = geompy.MakeShell(linking_faces + tri_edge_faces)
				except:
					shell = geompy.MakeCompound(linking_faces + tri_edge_faces)
				
				to_return = shell
				to_return_name = "WireOffset (Faces)"
				
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, father, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
	

mpwo = MakePlanarWireOffset

def ExtendViscousLayer( dist, wire = None, face = None, plane = None, scale = 1, ratio = 1, style = "smooth", coef = 0.5, tol = 1e-7, rev = False, add = True, infa = False, dim = 1 ):
	"""
	
	
Description:
	Extends a 2D trailing edge viscous layer.
	

Arguments:
	# dist 
		Description:       The length of the extension. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# wire 
		Description:       The input wire. 
		Type:              Wire 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# face 
		Description:       See here. 
		Type:              Face 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# plane 
		Description:       See here. If the input edge is straight, the default plane is the OXY plane. 
		Type:              Face 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# scale 
		Description:       The scale coefficient applied on the source middle edge before being "projected" on the end wire. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

	# ratio 
		Description:       The ratio between the ending wire and the input wire lengthes. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

	# style 
		Description:       See here. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "smooth"  

	# coef 
		Description:       A coefficient influencing the curvature of the extension edges (0 &lt; coef &lt; 1). The greater it is, the greater is the curvature. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     0.5  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# rev 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

Returned Values:
	"dim" value:    1 
	"single" value: - 
	Type:           Compound of Edges 
	Number:         1 
	Name:           "ViscousLayerExtension"  

	"dim" value:    2 
	"single" value: - 
	Type:           Shell or Compound of Faces 
	Number:         1 
	Name:           "ViscousLayerExtension (Faces)"  

Conditions of use:
	The input wire has to contain two or three connected edges.
	
	In addition, if the input wire is straight, it is also necessary to set the face or the plane argument so as to give the function the extension direction 

"""
	
	if dim not in [1, 2]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	wire = GetGUISelection(wire)
	
	[wire, face, plane] = GetObject([wire, face, plane])
	
	#-
	
	# Make this function recursive
	
	if isinstance(wire, list):
		
		return_list = []
		
		for sub_object in wire:
			
			return_list.append(ExtendViscousLayer(dist, sub_object, face, plane, scale, ratio, style, coef, tol, rev, add, infa, dim))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [wire, face, plane] or None in [wire]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = wire
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		dist = float(dist)
		
		wire_edges = GetSubShapes(wire)[1]
		
		try:
			
			wire = geompy.MakeWire(wire_edges)
			
		
		except:
			
			print "[X] The input shape should be \"wire-shaped\"."; return
			
		
		# Get the sub-shapes
		
		wire = GetSubShapes(wire)
		
		#-
		
		# Sort vertexes
		
		extremum_vertexes = []
		inside_vertexes = []
		
		for wire_vertex in wire[0]:
			
			nb_contacts = 0
			
			for wire_edge in wire[1]:
				
				min_distance = geompy.MinDistance(wire_edge, wire_vertex)
				
				if min_distance == 0:
					
					nb_contacts += 1
					
				
			
			if nb_contacts == 2:
				
				inside_vertexes.append(wire_vertex)
				
			
			else:
				
				extremum_vertexes.append(wire_vertex)
				
			
		
		#-
		
		# Get number of edges in the wire
		
		edge_number = len(wire[1])
		
		#-
		
		# Get the wire length
		
		wire_length = geompy.BasicProperties(wire[-1])[0]
		
		#-
		
		if edge_number == 3: # If the foil trailing edge is thicker than zero...
			
			# Get middle edge size
			
			middle_edge_length = geompy.MinDistance(inside_vertexes[0], inside_vertexes[1])
			
			#-
			
			# Get virtual wire size
			
			wire_length -= middle_edge_length
			
			middle_edge_length *= scale
			
			wire_length += middle_edge_length
			
			#-
			
		
		# Create the closing edge
		
		closing_edge = geompy.MakeEdge(extremum_vertexes[0], extremum_vertexes[1])
		
		#-
		
		# Get the extension direction
		
		if face == None:# If no face is given by the user...
			
			# Close the wire
			
			closed_contour = geompy.MakeWire([wire[-1], closing_edge])
			
			#-
			
			if plane == None:# And if no plane is given by the user...
				
				if abs(geompy.BasicProperties(closing_edge)[0] - geompy.BasicProperties(wire[-1])[0]) < tol:# If the input wire is straight...
					
					# Use the OXY plane
					
					plane = geompy.MakeFaceHW(10, 10, 1)
					
					#-
				
				else:
					
					# Get the wire plane
					
					plane = geompy.MakeFace(closed_contour, True)
					
					#-
					
				
			
			# Get the plane normal
			
			normal = geompy.GetNormal(plane)
			
			#-
			
			# Extrude the closing edge
			
			face = geompy.MakePrismVecH(closing_edge, normal, 0.1)
			
			#-
			
		
		extension_direction = geompy.GetNormal(face)
		
		#-
		
		# Create the end edge
		
		if dist == None:
			
			wire_length = geompy.BasicProperties(wire[-1])[0]
			
			dist = wire_length * 3
			
			print "[i] No offset distance given > default one:", dist
			
		
		if rev == True:
			
			dist *= -1.0
			
		
		end_edge = geompy.MakeTranslationVectorDistance(closing_edge, extension_direction, dist)
		
		#-
		
		if ratio != 1:
			
			# Get the end edge middle vertex
			
			end_edge_middle_vertex = geompy.MakeVertexOnCurve(end_edge, 0.5)
			
			#-
			
			# Scale the end edge
			
			end_edge_length = geompy.BasicProperties(end_edge)[0]
			
			end_edge_length *= ratio
			
			scaled_end_edge_first_vertex = geompy.MakeTranslationVectorDistance(end_edge_middle_vertex, end_edge, -end_edge_length / 2)
			scaled_end_edge_last_vertex = geompy.MakeTranslationVectorDistance(end_edge_middle_vertex, end_edge, end_edge_length / 2)
			
			end_edge = geompy.MakeEdge(scaled_end_edge_first_vertex, scaled_end_edge_last_vertex)
			
			#-
			
		
		# Create the inside extension edges
		
		inside_extension_edges = []
		
		inside_end_edge_vertexes = []
		
		for i in range(edge_number - 1):
			
			extremum_edge_length = geompy.MinDistance(inside_vertexes[i], extremum_vertexes[i])
			
			end_ratio = extremum_edge_length / wire_length
			
			if i == 1:
				
				end_ratio = 1.0 - end_ratio
				
			
			inside_end_edge_vertex = geompy.MakeVertexOnCurve(end_edge, end_ratio)
			
			inside_end_edge_vertexes.append(inside_end_edge_vertex)
			
			inside_extension_edge = geompy.MakeEdge(inside_vertexes[i], inside_end_edge_vertex)
			
			if style == "smooth":
				
				inside_extension_edge_middle_vertex = geompy.MakeVertexOnCurve(inside_extension_edge, 0.5)
				
				translated_inside_extension_edge_middle_vertex = geompy.MakeTranslationVectorDistance(inside_extension_edge_middle_vertex, extension_direction, dist / 2 * coef)
				
				inside_extension_edge = geompy.MakeInterpol([inside_vertexes[i], translated_inside_extension_edge_middle_vertex, inside_end_edge_vertex])
				
			
			inside_extension_edges.append(inside_extension_edge)
			
		
		#-
		
		# Create extremum extension edges
		
		extremum_extension_edges = []
		
		end_edge_vertexes = geompy.SubShapeAll(end_edge, geompy.ShapeType["VERTEX"])
		
		for i in range(2):
			
			extremum_extension_edge = geompy.MakeEdge(end_edge_vertexes[i], extremum_vertexes[i])
			
			if style == "smooth":
				
				extremum_extension_edge_middle_vertex = geompy.MakeVertexOnCurve(extremum_extension_edge, 0.5)
				
				TranslatedExtremumExtensionEdgeMiddleVertex = geompy.MakeTranslationVectorDistance(extremum_extension_edge_middle_vertex, extension_direction, dist / 2 * coef)
				
				#extremum_extension_edge = geompy.MakeInterpol([end_edge_vertexes[i], TranslatedExtremumExtensionEdgeMiddleVertex, extremum_vertexes[i]])
				extremum_extension_edge = geompy.MakeInterpol([extremum_vertexes[i], TranslatedExtremumExtensionEdgeMiddleVertex, end_edge_vertexes[i]])
				
			
			extremum_extension_edges.append(extremum_extension_edge)
		
		#-
		
		extension_edges = inside_extension_edges + extremum_extension_edges
		
		# Partition end edge
		
		end_edge_partition = geompy.MakePartition([end_edge], inside_end_edge_vertexes)
		
		end_edges = geompy.SubShapeAll(end_edge_partition, geompy.ShapeType["EDGE"])
		
		#-
		
		if dim == 1:
			
			extension_edges = geompy.MakeCompound(extension_edges + end_edges)
			
			to_return = extension_edges
			to_return_name = "ViscousLayerExtension"
			
		
		else:
			
			inside_extension_edge_compound = geompy.MakeCompound(inside_extension_edges)
			
			faces = []
			
			for extremum_extension_edge in extremum_extension_edges:
				
				some_vertex = geompy.MakeVertexOnCurve(extremum_extension_edge, 0)
				
				inside_extension_edge = geompy.GetShapesNearPoint(inside_extension_edge_compound, some_vertex, geompy.ShapeType["EDGE"])
				
				face = geompy.MakeQuad2Edges(inside_extension_edge, extremum_extension_edge)
				faces.append(face)
				
				
			
			if len(inside_extension_edges) == 2:
				
				face = geompy.MakeQuad2Edges(inside_extension_edges[0], inside_extension_edges[1])
				faces.append(face)
				
			
			# Create the output shell
			
			shell = geompy.MakeShell(faces)
			
			#-
			
			to_return = shell
			to_return_name = "ViscousLayerExtension (Faces)"
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(to_return, to_return_name, father)
			
		
		return to_return
		
		#-
		
	

evl = ExtendViscousLayer

def CloseViscousLayer( wire = None, dist = "auto", face = None, plane = None, style = "smooth", tol = 1e-7, rev = False, add = True, infa = False, dim = 1 ):
	"""
	
	
Description:
	Closes a 2D viscous layer.
	

Arguments:
	# wire 
		Description:       The input wire. 
		Type:              Wire 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# dist 
		Description:       The length of the closure. If equals "auto", the length is automatically calculated by the function. 
		Type:              Float or String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "auto"  

	# face 
		Description:       See here. 
		Type:              Face 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# plane 
		Description:       See here. If the input edge is straight, the default plane is the OXY plane. 
		Type:              Face 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# style 
		Description:       See here. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "smooth"  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# rev 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1  

Returned Values:
	"dim" value:    1 
	"single" value: - 
	Type:           Compound of Edges 
	Number:         1 
	Name:           "ViscousLayerClosing"  

	"dim" value:    2 
	"single" value: - 
	Type:           Shell or Compound of Faces 
	Number:         1 
	Name:           "ViscousLayerClosing (Faces)"  

Conditions of use:
	The input wire has to contain two or three connected edges.
	
	In this case, the smooth style can only be used if the wire is straight. Finally, if the input wire is straight, it is also necessary to set the face or the plane argument so as the function knows the closing direction. 

"""
	
	if dim not in [1, 2]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	wire = GetGUISelection(wire)
	
	[wire, face, plane] = GetObject([wire, face, plane])
	
	#-
	
	# Make this function recursive
	
	if isinstance(wire, list):
		
		return_list = []
		
		for sub_object in wire:
			
			return_list.append(CloseViscousLayer(sub_object, dist, face, plane, style, tol, rev, add, infa, dim))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [wire, face, plane] or None in [wire]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = wire
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		if not isinstance(dist, str):
			
			dist = float(dist)
			
		
		wire_edges = GetSubShapes(wire)[1]
		
		try:
			
			wire = geompy.MakeWire(wire_edges)
			
		
		except:
			
			print "[X] The input shape should be \"wire-shaped\"."; return
			
		
		# Get the sub-shapes
		
		wire = GetSubShapes(wire)
		
		#-
		
		# Sort the wire vertexes
		
		wire_vertexes = geompy.SubShapeAll(wire[-1], geompy.ShapeType["VERTEX"])
		
		inside_vertexes = []
		outside_vertexes = []
		
		for wire_vertex in wire_vertexes:
			
			nb_contacts = 0
			
			for edge in wire[1]:
				
				min_distance = geompy.MinDistance(edge, wire_vertex)
				
				if min_distance == 0:
					
					nb_contacts += 1
					
				
			
			if nb_contacts == 2:
				
				inside_vertexes.append(wire_vertex)
				
			
			else:
				
				outside_vertexes.append(wire_vertex)
				
			
		
		#-
		
		# Get the closing direction
		
		if face == None:# If no face is given by the user...
			
			# Close the wire
			
			closing_edge = geompy.MakeEdge(outside_vertexes[0], outside_vertexes[1])
			
			closed_contour = geompy.MakeWire([wire[-1], closing_edge])
			
			#-
			
			if plane == None:# And if no plane is given by the user...
				
				if abs(geompy.BasicProperties(closing_edge)[0] - geompy.BasicProperties(wire[-1])[0]) < tol:# If the input wire is straight...
					
					# Use the OXY plane
					
					plane = geompy.MakeFaceHW(10, 10, 1)
					
					#-
				
				else:
					
					# Get the wire plane
					
					plane = geompy.MakeFace(closed_contour, True)
					
					#-
					
				
			
			# Get the plane normal
			
			normal = geompy.GetNormal(plane)
			
			#-
			
			# Extrude the closing edge
			
			face = geompy.MakePrismVecH(closing_edge, normal, 0.1)
			
			#-
			
		
		normal_vector = geompy.GetNormal(face)
		
		#-
		
		# Create the inside vertex compound
		
		inside_vertex_compound = geompy.MakeCompound(inside_vertexes)
		
		#-
		
		# Get the external edges
		
		external_edges = []
		
		for edge in wire[1]:
			
			nb_contacts = 0
			
			for inside_vertex in inside_vertexes:
				
				min_distance = geompy.MinDistance(inside_vertex, edge)
				
				if min_distance == 0:
					
					nb_contacts += 1
					
				
			
			if nb_contacts == 1:
				
				external_edges.append(edge)
				
			
		
		#-
		
		# Calculate the closing thickness
		
		if dist == "auto":
			
			total_external_edge_length = 0
			
			for external_edge in external_edges:
				
				total_external_edge_length += geompy.BasicProperties(external_edge)[0]
				
			
			dist = total_external_edge_length / 2
			
		
		if rev == True:
			
			dist *= -1.0
			
		
		#-
		
		output_edges = []
		
		# Close the external edges
		
		translated_inside_vertexes = []
		
		for external_edge in external_edges:# For each external edge...
			
			external_edge_vertexes = geompy.SubShapeAll(external_edge, geompy.ShapeType["VERTEX"])
			
			# Sort the vertexes
			
			external_edge_inside_vertex = None
			external_edge_outide_vertex = None
			
			for external_edge_vertex in external_edge_vertexes:
				
				min_distance = geompy.MinDistance(external_edge_vertex, inside_vertex_compound)
				
				if min_distance == 0:
					
					external_edge_inside_vertex = external_edge_vertex
					
				
				else:
					
					external_edge_outide_vertex = external_edge_vertex
					
				
			
			#-
			
			# Translate the inside vertex
			
			translated_inside_vertex = geompy.MakeTranslationVectorDistance(external_edge_inside_vertex, normal_vector, dist)
			
			translated_inside_vertexes.append(translated_inside_vertex)
			
			#-
			
			# Create the closing edges
			
			if style == "straight":
				
				outside_closing_edge = geompy.MakeEdge(external_edge_outide_vertex, translated_inside_vertex)
				
			
			elif style == "smooth":
				
				outside_closing_edge = geompy.MakeArcOfEllipse(external_edge_inside_vertex, external_edge_outide_vertex, translated_inside_vertex)
				
			
			inside_closing_edge = geompy.MakeEdge(external_edge_inside_vertex, translated_inside_vertex)
			
			#-
			
			output_edges.append(outside_closing_edge)
			output_edges.append(inside_closing_edge)
			
		
		if len(wire[1]) == 3:# If there are three edges in the input wire...
			
			# Close the closing
			
			closing_closing_edge = geompy.MakeEdge(translated_inside_vertexes[0], translated_inside_vertexes[1])
			
			output_edges.append(closing_closing_edge)
			
			#-
			
		
		if len(wire[1]) == 2:# If there are two edges in the input wire...
			
			# Create the output edge compound
			
			output_edge_compound = geompy.MakeCompound(output_edges)
			
			#-
			
			# Glue the edges
			
			glued_output_edge_compound = geompy.MakeGlueEdges(output_edge_compound, tol)
			
			#-
			
			# Explode the glued compound
			
			output_edges = geompy.SubShapeAll(glued_output_edge_compound, geompy.ShapeType["EDGE"])
			
			#-
			
		
		if dim == 1:
			
			# Put the output edges into a compound
			
			output_edges = geompy.MakeCompound(output_edges)
			
			#-
			
			to_return = output_edges
			to_return_name = "ViscousLayerClosing"
			
		
		else:
			
			face = geompy.MakeFaceWires(external_edges[0:1] + output_edges[0:2], isPlanarWanted = True)
			
			faces = [face]
			if len(wire[1]) == 3:# If there are three edges in the input wire...
				
				face = geompy.MakeFaceWires(external_edges[1:2] + output_edges[2:4], isPlanarWanted = True)
				faces.append(face)
				
				face = geompy.MakeQuad2Edges(output_edges[1], output_edges[3])
				faces.append(face)
				
			
			if len(wire[1]) == 2:# If there are two edges in the input wire...
				
				face = geompy.MakeFaceWires(external_edges[1:2] + output_edges[1:3], isPlanarWanted = True)
				faces.append(face)
				
			
			# Put the output faces into a shell
			
			shell = geompy.MakeShell(faces)
			
			#-
			
			to_return = shell
			to_return_name = "ViscousLayerClosing (Faces)"
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(to_return, to_return_name, father)
			
		
		return to_return
		
		#-
		
	

cvl = CloseViscousLayer

def PropagateViscousLayerIntersection( compound = None, dir = "auto", tol = 1e-7, add = True, infa = False ):
	"""
	
	
Description:
	Propagates the intersection into two intersecting viscous layers.
	

Arguments:
	# compound 
		Description:       The source compound of edges. 
		Type:              Compound of Edges 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# dir 
		Description:       Equals "x", "y" or "z" to impose the approximate direction of the propagation, "auto" to let the function decide by itself. (Used to sort intersection vertexes.) 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "auto"  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Compound of Edges 
	Number:         1 
	Name:           "IntersectionPropagation"  

Conditions of use:
	The source compound has to be planar and must contain only "parallel" edges (in the "blocking" sense).
	

"""
	
	# Get the input shape(s)
	
	compound = GetGUISelection(compound)
	
	compound = GetObject(compound)
	
	#-
	
	# Make this function recursive
	
	if isinstance(compound, list):
		
		return_list = []
		
		for sub_object in compound:
			
			return_list.append(PropagateViscousLayerIntersection(sub_object, dir, tol, add, infa))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [compound] or None in [compound]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = compound
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the sub-shapes
		
		compound = GetSubShapes(compound)
		
		#-
		
		# Get the intersection vertexes
		
		partition = geompy.MakePartition([compound[-1]], Limit = geompy.ShapeType["VERTEX"])
		
		partition_vertexes = geompy.SubShapeAll(partition, geompy.ShapeType["VERTEX"])
		
		intersection_vertexes = []
		
		for partition_vertex in partition_vertexes:
			
			is_intersection_vertex = True
			
			for compound_vertex in compound[0]:
				
				distance = geompy.MinDistance(partition_vertex, compound_vertex)
				
				if distance == 0:
					
					is_intersection_vertex = False
					
				
			
			if is_intersection_vertex == True: 
				
				intersection_vertexes.append(partition_vertex)
				
			
		
		#-
		
		# Get the compound plane
		
		quadrangle_face = geompy.MakeQuad2Edges(compound[1][0], compound[1][1])
		
		#-
		
		# Get the compound plane normal
		
		compound_plane_normal = geompy.GetNormal(quadrangle_face)
		
		#-
		
		# Extrude compound edges
		
		compound_edge_extensions = []
		
		for compound_edge in compound[1]:
			
			compound_edge_extension = geompy.MakePrismVecH(compound_edge, compound_plane_normal, 0.1)
			
			compound_edge_extensions.append(compound_edge_extension)
			
		
		#-
		
		# Get the dimension used to sort the intermediate vertexes
		
		if dir == "x":
			
			sorting_dimension = 0
			
		
		elif dir == "y":
			
			sorting_dimension = 1
			
		
		elif dir == "z":
			
			sorting_dimension = 2
			
		
		#-
		
		# Create intermediate edges
		
		intermediate_edges = []
		
		for intersection_vertex in intersection_vertexes:# For each intersection vertex...
			
			# Project intersection vertex on extruded edges
			
			projected_vertexes = []
			
			for compound_edge_extension in compound_edge_extensions:
				
				projected_vertex = geompy.MakeProjection(intersection_vertex, compound_edge_extension)
				
				projected_vertexes.append(projected_vertex)
				
			
			#-
			
			# Get the number of projected vertexes
			
			nb_projected_vertexes = len(projected_vertexes)
			
			#-
			
			# Get the sorting dimension if "auto" enabled
			
			if dir == "auto":
				
				projected_vertex_compound = geompy.MakeCompound(projected_vertexes)
				
				bounding_box = geompy.BoundingBox(projected_vertex_compound)
				
				dx = abs(bounding_box[1] - bounding_box[0])
				dy = abs(bounding_box[2] - bounding_box[1])
				dz = abs(bounding_box[3] - bounding_box[2])
				
				if max(dx, dy, dz) == dx:
					
					sorting_dimension = 0
					
				
				elif max(dx, dy, dz) == dy:
					
					sorting_dimension = 1
					
				
				elif max(dx, dy, dz) == dz:
					
					sorting_dimension = 2
					
				
			
			#-
			
			# Reorder projected vertexes
			
			reorder_projected_vertexes = []
			
			resting_vertexes = projected_vertexes[:]
			
			next_vertex_index = 0
			
			for i in range(nb_projected_vertexes):# Each time they are projected vertex left...
				
				vertex_index = 0
				
				min_position = 1e99
				
				for resting_vertex in resting_vertexes:
					
					resting_vertex_position = geompy.PointCoordinates(resting_vertex)[sorting_dimension]
					
					if resting_vertex_position < min_position:
						
						next_vertex_index = vertex_index
						
						min_position = resting_vertex_position
						
					
					vertex_index += 1
					
				
				next_vertex = resting_vertexes[next_vertex_index]
				
				reorder_projected_vertexes.append(next_vertex)
				
				del resting_vertexes[next_vertex_index]
				
			
			#-
			
			# Create intermediate edges
			
			for reordered_vertex_index in range(nb_projected_vertexes - 1):
				
				first_intermediate_edge_vertex = reorder_projected_vertexes[reordered_vertex_index]
				second_intermediate_edge_vertex = reorder_projected_vertexes[reordered_vertex_index + 1]
				
				distance = geompy.MinDistance(first_intermediate_edge_vertex, second_intermediate_edge_vertex)
				
				if distance > tol:
					
					intermediate_edge = geompy.MakeEdge(first_intermediate_edge_vertex, second_intermediate_edge_vertex)
					
					intermediate_edges.append(intermediate_edge)
					
				
			
			#-
			
		
		#-
		
		# Partition the whole geometry
		
		edges = compound[1] + intermediate_edges
		
		partition = geompy.MakePartition(edges)
		
		#-
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(partition, "PropagatedIntersection", father)
			
		
		return partition
		
		#-
		
	

pvli = PropagateViscousLayerIntersection

def MakeTipViscousLayer( dist, offset, foil = None, style = "smooth", np = 60, curv = True, tol = 1e-4, by_param = False, rev = False, add = True, infa = False, dim = 3 ):
	"""
	
	
Description:
	Creates a tip viscous layer volume following a foil edge.
	

Arguments:
	# dist 
		Description:       The offset distance normal to the wing tip. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# offset 
		Description:       The edge describing the offset of the viscous layer in the wing tip plane. 
		Type:              Edge 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     -  

	# foil 
		Description:       The edge touching the wing tip. 
		Type:              Edge 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# style 
		Description:       See here. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "smooth"  

	# np 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     40  

	# curv 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-4  

	# by_param 
		Description:       Defines if the function has to create two points at the same position  on the foil edge and on the offset edge respectively by using a same distance from  the edge start (True) or the same parameter on the edge (False).  In some cases, switch this parameter can give better results. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# rev 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     3  

Returned Values:
	"dim" value:    1 
	"single" value: - 
	Type:           Compound of Edge 
	Number:         2 
	Name:           "TipViscousLayer (Edges)"  

	"dim" value:    2 
	"single" value: - 
	Type:           Compound of Faces 
	Number:         1 
	Name:           "TipViscousLayer (Faces)"  

	"dim" value:    3 
	"single" value: - 
	Type:           Solid 
	Number:         1 
	Name:           "TipViscousLayer"  

Conditions of use:
	The input edges have to be open.
	

"""
	
	if dim == 0: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	foil = GetGUISelection(foil, uniq = True)
	
	[foil, offset] = GetObject([foil, offset])
	
	#-
	
	# Check the input shape existence
	
	if "error" in [foil, offset] or None in [foil, offset]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = foil
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the sub-shapes
		
		[foil, offset] = GetSubShapes([foil, offset])
		
		#-
		
		# Get the edge lengths
		
		foil_length = geompy.BasicProperties(foil[-1])[0]
		offset_length = geompy.BasicProperties(offset[-1])[0]
		
		#-
		
		# Get the offset edge sense
		
		linking_edge_1 = geompy.MakeEdge(foil[0][0], offset[0][0])
		linking_edge_2 = geompy.MakeEdge(foil[0][0], offset[0][1])
		
		linking_edge_1_length = geompy.BasicProperties(linking_edge_1)[0]
		linking_edge_2_length = geompy.BasicProperties(linking_edge_2)[0]
		
		reverse_length = False
		
		if linking_edge_1_length > linking_edge_2_length:
			
			reverse_length = True
			
		
		#-
		
		# Get the foil normal vector
		
		face = geompy.MakeQuad2Edges(foil[-1], offset[-1])
		
		normal_vector = geompy.GetNormal(face)
		
		#-
		
		filling_edges_3d = []
		filling_edges_2d = []
		boundary_faces = []
		
		if rev == True:
			
			dist *= -1.0
			
		
		if curv == True:
			
			parameter_list = DiscretizeEdgeByCurvature(foil[-1], np, dim = -1)
			
		
		else:
			
			parameter_list = [n / float(np) for n in range(np + 1)]
			
		
		#-
		
		# Create the offset vertexes
		
		for parameter in parameter_list:# For each position on the foil edge...
		#for parameter in [1 - n / float(np - 1) for n in range(np)]:# For each position on the foil edge...
			
			# Create the vertexes
			
			if by_param == True:
				
				foil_vertex = geompy.MakeVertexOnCurve(foil[-1], parameter)
				
			
			else:
				
				foil_vertex = geompy.MakeVertexOnCurveByLength(foil[-1], parameter * foil_length, foil[0][0])
				
			
			if reverse_length == True:
				
				parameter = 1.0 - parameter
				
			
			if by_param == True:
				
				offset_vertex = geompy.MakeVertexOnCurve(offset[-1], parameter)
				
			
			else:
				
				offset_vertex = geompy.MakeVertexOnCurveByLength(offset[-1], parameter * offset_length, offset[0][0])
				
			
			translated_vertex = geompy.MakeTranslationVectorDistance(foil_vertex, normal_vector, dist)
			
			#-
			
			# Create the 2D filling edge
			
			filling_edge_2d = geompy.MakeEdge(foil_vertex, offset_vertex)
			
			filling_edges_2d.append(filling_edge_2d)
			
			#-
			
			# Create the 3D filling edge
			
			if style == "smooth":
				
				filling_edge_3d = geompy.MakeArcOfEllipse(foil_vertex, offset_vertex, translated_vertex)
				
				filling_edges_3d.append(filling_edge_3d)
				
			
			else:
				
				filling_edge_3d = geompy.MakeEdge(offset_vertex, translated_vertex)
				
				filling_edges_3d.append(filling_edge_3d)
				
			
			#-
			
			if dim >= 2:
				
				if parameter == 0 or parameter == 1:# If it is the first or the last position...
					
					# Create the boundary face
					
					third_edge = geompy.MakeEdge(foil_vertex, translated_vertex)
					
					boundary_faces.append(geompy.MakeFaceWires([filling_edge_3d, filling_edge_2d, third_edge], True))
					
					#-
				
			
		
		# Put the filling edges into compounds
		
		filling_edge_compound_2d = geompy.MakeCompound(filling_edges_2d)
		
		filling_edge_compound_3d = geompy.MakeCompound(filling_edges_3d)
		
		#-
		
		# Add and return the resulting shape(s)
		
		if dim == 1:
			
			if add == True:
				
				AddToStudy(filling_edge_compound_2d, "TipViscousLayer (Edges)", father)
				AddToStudy(filling_edge_compound_3d, "TipViscousLayer (Edges)", father)
				
			
			return [filling_edge_compound_2d, filling_edge_compound_3d]
			
		
		#-
		
		else:
			
			# Create the fillings
			
			filling_2d = geompy.MakeFilling(filling_edge_compound_2d, theMinDeg = 15, theMaxDeg = 20, theTol2D = 1e-5, theTol3D = 1e-5, theMethod = GEOM.FOM_AutoCorrect)
			
			filling_3d = geompy.MakeFilling(filling_edge_compound_3d, theMinDeg = 15, theMaxDeg = 20, theTol2D = 1e-5, theTol3D = 1e-5, theMethod = GEOM.FOM_AutoCorrect)
			
			#-
			
			# Extrude the foil edge
			
			foil_extension = geompy.MakePrismVecH(foil[-1], normal_vector, dist)
			
			#-
			
			# Create the compound from faces
			
			face_compound = geompy.MakeCompound([filling_2d, filling_3d, foil_extension, boundary_faces[0], boundary_faces[1]])
			
			#-
			
			# Add and return the resulting shape(s)
			
			if dim == 2:
				
				if add == True:
					
					AddToStudy(face_compound, "TipViscousLayer (Faces)", father)
					
				
				return face_compound
				
			
			#-
			
			else:
				
				# Glue the edges
				
				gluing_tolerance = tol
				
				while True:
					
					free_boundaries = geompy.GetFreeBoundary(face_compound)[1]
					
					if len(free_boundaries) == 0:
						
						break
						
					
					face_compound = geompy.MakeGlueEdges(face_compound, gluing_tolerance)
					
					gluing_tolerance *= 2
					
				
				#-
				
				# Create the shell form the compound
				
				shell = geompy.MakeShell([face_compound])
				
				#-
				
				# Create the solid from the shell
				
				solid = geompy.MakeSolid([shell])
				
				#-
				
				# Add and return the resulting shape(s)
				
				if add == True:
					
					AddToStudy(solid, "TipViscousLayer", father)
					
				
				return solid
				
				#-
			
		
	

mtvl = MakeTipViscousLayer

def ExtendTipViscousLayer( shell_and_compound = [None], np = 40, tol = 1e-7, add = True, infa = False, dim = 3 ):
	"""
	
	
Description:
	Extends a tip viscous layer.
	

Arguments:
	# shell_and_compound 
		Description:       the input shell to extend and its guiding edge compound. 
		Type:              List of  1 Shell +  1 Compound of Edges 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# np 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     40  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     3  

Returned Values:
	"dim" value:    1 
	"single" value: - 
	Type:           Compound of Edges 
	Number:         5 or 8 
	Name:           "TipViscousLayerExtension (Edges)"  

	"dim" value:    2 
	"single" value: - 
	Type:           Compound of Faces 
	Number:         2 or 3 
	Name:           "TipViscousLayerExtension (Faces)"  

	"dim" value:    3 
	"single" value: - 
	Type:           Compound of Solids 
	Number:         1 
	Name:           "TipViscousLayerExtension"  

Conditions of use:
	The input shell has to contain 2 faces having the shape of triangles or ellipse quarters and an optional middle face being a quadrangle. The edge compound has to have all the characteristics of a compound build with the ExtendViscousLayer function. 
	

"""
	
	if isinstance(shell_and_compound, list) == False: print "[X] The first argument (shell_and_compound) should be an array."; return
	if isinstance(np, str): print "[X] The second argument (np) should be an integer ."; return
	
	if dim == 0: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	shell_and_compound = GetGUISelection(shell_and_compound)
	
	shell_and_compound = GetObject(shell_and_compound)
	
	#-
	
	# Check the input shape existence
	
	if "error" in shell_and_compound or None in shell_and_compound: return
	
	#-
	
	# Check the number of selected objects
	
	if len(shell_and_compound) != 2:
		
		print "[X] Two objects should be selected."
		
		return
		
	
	#-
	
	# Distinguish input shapes
	
	shell = None
	compound = None
	
	for object in shell_and_compound:
		
		nb_faces = geompy.NumberOfFaces(object)
		
		if nb_faces > 0:
			
			shell = object
		
		else:
			
			compound = object
			
		
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = compound
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Check if the input shape is "shell-shaped"
		
		shell_faces = GetSubShapes(shell)[2]
		
		try:
			
			shell = geompy.MakeShell(shell_faces)
			
		except:
			
			print "[X] The input 2D shape should be \"shell-shaped\"."; return
			
		
		#-
		
		# Keep edges touching the input shell
		
		compound_edges = GetSubShapes(compound)[1]
		
		edges_to_keep = []
		for edge in compound_edges:
			
			edge_vertexes = GetSubShapes(edge)[0]
			
			distance_1 = geompy.MinDistance(edge_vertexes[0], shell)
			distance_2 = geompy.MinDistance(edge_vertexes[1], shell)
			
			distances = [distance_1, distance_2]
			
			if min(distances) <= tol and max(distances) > tol:
				
				edges_to_keep.append(edge)
				
			
		
		compound = geompy.MakeCompound(edges_to_keep)
		
		#-
		
		# Get the sub - geometries
		
		[shell, compound] = GetSubShapes([shell, compound])
		
		#-
		
		# Get the normal direction
		
		compound_vertex_compound = geompy.MakeCompound(compound[0])
		shell_vertex_compound = geompy.MakeCompound(shell[0])
		
		top_vertex_compound = geompy.MakeCut(shell_vertex_compound, compound_vertex_compound)
		
		top_vertex = None
		for vertex in shell[0]:
			
			distance = geompy.MinDistance(vertex, compound[-1])
			
			if distance > tol:
				
				top_vertex = vertex
				break
				
			
		
		bottom_vertex = geompy.GetShapesNearPoint(compound[-1], top_vertex, geompy.ShapeType["VERTEX"])
		
		normal = geompy.MakeVector(bottom_vertex, top_vertex)
		
		#-
		
		# Get root normal thickness
		
		root_normal_thickness = geompy.BasicProperties(normal)[0]
		
		#-
		
		# Distinguish inside and outside edges
		
		inside_edges = []
		outside_edges = []
		
		for edge in compound[1]:
			
			edge_vertexes = geompy.SubShapeAll(edge, geompy.ShapeType["VERTEX"])
			
			for edge_vertex in edge_vertexes:
				
				min_distance = geompy.MinDistance(edge_vertex, shell[-1])
				
				if min_distance <= tol:
					
					nb_contacts = 0
					
					for face in shell[2]:
						
						min_distance = geompy.MinDistance(edge_vertex, face)
						
						if min_distance <= tol:
							
							nb_contacts += 1
							
						
					
					if nb_contacts == 1:
						
						outside_edges.append(edge)
						
					
					else:
						
						inside_edges.append(edge)
						
					
					break
					
				
			
		
		#-
		
		# Get local thickness
		
		inside_edge_compound = geompy.MakeCompound(inside_edges)
		
		local_thickness_lists = []
		for outside_edge in outside_edges:
			
			some_outside_edge_vertex = GetSubShapes(outside_edge)[0][0]
			
			inside_edge = geompy.GetShapesNearPoint(inside_edge_compound, some_outside_edge_vertex, geompy.ShapeType["EDGE"])
			
			edge_1 = inside_edge
			edge_2 = outside_edge
			
			length_1 = geompy.BasicProperties(edge_1)[0]
			length_2 = geompy.BasicProperties(edge_2)[0]
			
			[x, y, z] = geompy.ClosestPoints(edge_1, shell[-1])[1][0:3]
			first_vertex_1 = geompy.MakeVertex(x, y, z)
			
			[x, y, z] = geompy.ClosestPoints(edge_2, shell[-1])[1][0:3]
			first_vertex_2 = geompy.MakeVertex(x, y, z)
			
			local_thicknesses = []
			for parameter in [n / float(np - 1) for n in range(np)]:
				
				vertex_1 = geompy.MakeVertexOnCurveByLength(edge_1, parameter * length_1, first_vertex_1)
				vertex_2 = geompy.MakeVertexOnCurveByLength(edge_2, parameter * length_2, first_vertex_2)
				
				local_thickness = geompy.MinDistance(vertex_1, vertex_2)
				local_thicknesses.append(local_thickness)
				
			
			local_thickness_lists.append(local_thicknesses)
			
		
		nb_local_thicknesses = len(local_thickness_lists[0])
		
		final_local_thicknesses = []
		for i in range(nb_local_thicknesses):
			
			final_local_thickness = (local_thickness_lists[0][i] + local_thickness_lists[1][i]) / 2.0
			final_local_thicknesses.append(final_local_thickness)
			
		
		normal_thickness_scale = root_normal_thickness / final_local_thicknesses[0]
		
		for i in range(nb_local_thicknesses):
			
			final_local_thicknesses[i] = final_local_thicknesses[i] * normal_thickness_scale
			
		
		#-
		
		# Create the missing outside edges
		
		missing_outside_edges = []
		
		for inside_edge in inside_edges:
			
			edge_1 = inside_edge
			
			length_1 = geompy.BasicProperties(edge_1)[0]
			
			[x, y, z] = geompy.ClosestPoints(edge_1, shell[-1])[1][0:3]
			first_vertex_1 = geompy.MakeVertex(x, y, z)
			
			outside_missing_edge_vertexes = []
			i = 0
			for parameter in [n / float(np - 1) for n in range(np)]:
				
				vertex_1 = geompy.MakeVertexOnCurveByLength(edge_1, parameter * length_1, first_vertex_1)
				
				vertex_2 = geompy.MakeTranslationVectorDistance(vertex_1, normal, final_local_thicknesses[i])
				outside_missing_edge_vertexes.append(vertex_2)
				
				i += 1
				
			
			missing_outside_edge = geompy.MakeInterpol(outside_missing_edge_vertexes)
			missing_outside_edges.append(missing_outside_edge)
			
			
		
		# Add the missing outside edges to the edge list
		
		path_edges = compound[1] + missing_outside_edges
		
		#-
		
		# Create the fillings
		
		shell_edges = geompy.SubShapeAll(shell[-1], geompy.ShapeType["EDGE"])
		
		fillings = []
		filling_edge_compounds = []
		
		i = 0
		for shell_edge in shell_edges:# For each edge of the face compound...
			
			# Get the edge style
			
			shell_edge_length = geompy.BasicProperties(shell_edge)[0]
			
			shell_edge_vertexes = geompy.SubShapeAll(shell_edge, geompy.ShapeType["VERTEX"])
			
			rebuilt_straight_edge = geompy.MakeEdge(shell_edge_vertexes[0], shell_edge_vertexes[1])
			
			rebuilt_straight_edge_length = geompy.BasicProperties(rebuilt_straight_edge)[0]
			
			if abs(shell_edge_length - rebuilt_straight_edge_length) <= tol:
				
				style = "straight"
				
			
			else:
				
				style = "smooth"
				
			
			#-
			
			# Get the path edges
			
			edge_path_edges = []
			
			for path_edge in path_edges:
				
				min_distance = geompy.MinDistance(path_edge, shell_edge)
				
				if min_distance <= tol:
					
					edge_path_edges.append(path_edge)
					
				
			
			#-
			
			# Get the center edge
			
			if style == "smooth":
				
				# Get the adjacent edges
				
				shell_edge_adjacent_edges = []
				
				other_face_compound_edges = list(shell_edges)
				
				del other_face_compound_edges[i]
				
				for other_face_compound_edge in other_face_compound_edges:
					
					min_distance = geompy.MinDistance(other_face_compound_edge, shell_edge)
					
					if min_distance <= tol:
						
						shell_edge_adjacent_edges.append(other_face_compound_edge)
						
					
				
				#-
				
				# Put them in a compound
				
				shell_edge_adjacent_edge_compound = geompy.MakeCompound(shell_edge_adjacent_edges)
				
				#-
				
				# Get the center edge
				
				center_edge = None
				
				for inside_edge in inside_edges:
					
					min_distance = geompy.MinDistance(inside_edge, shell_edge_adjacent_edge_compound)
					
					if min_distance <= tol:
						
						center_edge = inside_edge
						
						break
						
					
				
				#-
				
			
			#-
			
			# Get the edge lengths
			
			length_1 = geompy.BasicProperties(edge_path_edges[0])[0]
			length_2 = geompy.BasicProperties(edge_path_edges[1])[0]
			
			#-
			
			# Get the edge vertexes
			
			edge_path_edge_1_vertexes = geompy.SubShapeAll(edge_path_edges[0], geompy.ShapeType["VERTEX"])
			first_vertex_1 = edge_path_edge_1_vertexes[0]
			last_vertex_1 = edge_path_edge_1_vertexes[1]
			
			edge_path_edge_2_vertexes = geompy.SubShapeAll(edge_path_edges[1], geompy.ShapeType["VERTEX"])
			first_vertex_2 = edge_path_edge_2_vertexes[0]
			last_vertex_2 = edge_path_edge_2_vertexes[1]
			
			# Get the offset edge sense
			
			linking_edge_1 = geompy.MakeEdge(first_vertex_1, first_vertex_2)
			linking_edge_2 = geompy.MakeEdge(first_vertex_1, last_vertex_2)
			
			linking_edge_1_length = geompy.BasicProperties(linking_edge_1)[0]
			linking_edge_2_length = geompy.BasicProperties(linking_edge_2)[0]
			
			reverse_length = False
			
			if linking_edge_1_length > linking_edge_2_length:
				
				reverse_length = True
				
			
			#-
			
			# Create the filling edges
			
			filling_edges = []
			
			#for parameter in [1 - n / float(np - 1) for n in range(np)]:
			for parameter in [n / float(np - 1) for n in range(np)]:
				
				# Create the vertexes
				
				vertex_1 = geompy.MakeVertexOnCurveByLength(edge_path_edges[0], parameter * length_1, first_vertex_1)
				
				if reverse_length == True:
					
					parameter = 1.0 - parameter
					
				
				vertex_2 = geompy.MakeVertexOnCurveByLength(edge_path_edges[1], parameter * length_2, first_vertex_2)
				
				if style == "smooth":
					
					length_0 = geompy.BasicProperties(center_edge)[0]
					first_vertex_0 = geompy.SubShapeAll(center_edge, geompy.ShapeType["VERTEX"])[0]
					vertex_0 = geompy.MakeVertexOnCurveByLength(center_edge, parameter * length_0, first_vertex_0)
					
				
				#-
				
				# Create the filling edge
				
				if style == "straight":
					
					filling_edge = geompy.MakeEdge(vertex_1, vertex_2)
					
				
				elif style == "smooth":
					
					filling_edge = geompy.MakeArcOfEllipse(vertex_0, vertex_1, vertex_2)
					
				
				#-
				
				# Create the filling edge compound
				
				filling_edges.append(filling_edge)
				
				#-
				
			
			# Create the filling edge compound
			
			filling_edge_compound = geompy.MakeCompound(filling_edges)
			
			filling_edge_compounds.append(filling_edge_compound)
			
			#-
			
			# Create the filling
			
			fillings.append(geompy.MakeFilling(filling_edge_compound, theMinDeg = 15, theMaxDeg = 20, theTol2D = 1e-5, theTol3D = 1e-5, theMethod = GEOM.FOM_AutoCorrect))
			
			#-
			
		
		#-
		
		# Add and return the resulting shape(s)
		
		if dim == 1:
			
			if add == True:
				
				AddToStudy(filling_edge_compounds, "TipViscousLayerExtension (Edges)", father)
				
			
			return filling_edge_compounds
			
		
		#-
		
		else:
			
			# Create the filling shells
			
			filling_shells = []
			
			for face in shell[2]:# For each face of the input compound...
				
				# Get the fillings
				
				face_fillings = []
				
				for filling in fillings:
					
					filling_vertexes = geompy.SubShapeAll(filling, geompy.ShapeType["VERTEX"])
					
					nb_contacts = 0
					
					for filling_vertex in filling_vertexes:
						
						min_distance = geompy.MinDistance(filling_vertex, face)
						
						if min_distance <= tol:
							
							nb_contacts += 1
							
						
					
					if nb_contacts == 2:
						
						face_fillings.append(filling)
						
					
				
				#-
				
				# Create the filling shell
				
				filling_shells.append(geompy.MakeShell(face_fillings + [face]))
				
				#-
				
			
			#-
			
			# Add and return the resulting shape(s)
			
			if dim == 2:
				
				if add == True:
					
					AddToStudy(filling_shells, "TipViscousLayerExtension (Faces)", father)
					
				
				return filling_shells
				
			
			#-
			
			else:
				
				# Create the solids
				
				solids = []
				
				for filling_shell in filling_shells:
				
					# Glue the edges
					
					gluing_tolerance = tol * 1e2
					
					while True:
						
						free_boundaries = geompy.GetFreeBoundary(filling_shell)[1]
						
						if len(free_boundaries) == 1:
							
							free_boundary = free_boundaries[0]
							
							free_boundary_length = geompy.BasicProperties(free_boundary)[0]
							
							free_boundary_nodes = GetSubShapes(free_boundary)[0]
							
							plane = geompy.MakePlaneThreePnt(free_boundary_nodes[0], free_boundary_nodes[1], free_boundary_nodes[2], free_boundary_length * 1e3)
							
							common = geompy.MakeCommon(free_boundary, plane)
							
							if GeometricalEquality([free_boundary, common], tol = 1) == True:
								
								break
								
							
						
						try:
							
							filling_shell = geompy.MakeGlueEdges(filling_shell, gluing_tolerance)
							
						except:
							
							try:
								
								tmp_shape = geompy.MakeSewing(filling_shell, gluing_tolerance)
								
								if tmp_shape != None:
									
									filling_shell = tmp_shape
									
								
							except:
								
								AddToStudy(filling_shell, "ProblematicShape")
								
								print "[X] Some internal shape could not be glued."; return
								
							
						
						gluing_tolerance *= 2
						
					
					#-
					
					# Get the missing face wire
					
					filling_shell_hole_wire = geompy.GetFreeBoundary(filling_shell)[1][0]
					
					#-
					
					# Create the missing face
					
					try:
						
						filling_shell_missing_face = geompy.MakeFace(filling_shell_hole_wire, True)
						
					except:
						
						print "[X] One internal shell could not be closed."
						
						if add == True:
							
							AddToStudy(filling_shell, "ProblematicShape")
							
						
						return filling_shell
						
					
					#-
					
					# Create the final shell
					
					filling_shell = geompy.MakeShell([filling_shell, filling_shell_missing_face])
					
					#-
					
					# Create the solid
					
					solids.append(geompy.MakeSolid([filling_shell]))
					
					#-
					
				
				#-
				
				# Put the solids into a compound
				
				solids = geompy.MakeCompound(solids)
				
				#-
				
				# Glue faces into the compound
				
				try:
					
					solids = geompy.MakeGlueFaces(solids, tol * 1e2)
					
				except:
					
					print "[*] The glue operation failed on the final shape."
					
				
				#-
				
				# Add and return the resulting shape(s)
				
				if add == True:
					
					AddToStudy(solids, "TipViscousLayerExtension", father)
					
				
				return solids
				
				#-
				
			
		
	

etvl = ExtendTipViscousLayer

def CloseTipViscousLayer( shell_and_compound = [None], np = 20, tol = 1e-7, add = True, infa = False, dim = 3 ):
	"""
	
	
Description:
	Close a tip viscous layer.
	

Arguments:
	# shell_and_compound 
		Description:       the shell to close and its guiding edge compound. 
		Type:              List of  1 Shell +  1 Compound of Edges 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# np 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     20  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     3  

Returned Values:
	"dim" value:    1 
	"single" value: - 
	Type:           Compound of Edges 
	Number:         4 or 6 
	Name:           "TipViscousLayerClosing (Edges)"  

	"dim" value:    2 
	"single" value: - 
	Type:           Compound of Faces 
	Number:         2 or 3 
	Name:           "TipViscousLayerClosing (Faces)"  

	"dim" value:    3 
	"single" value: - 
	Type:           Compound of Solids 
	Number:         1 
	Name:           "TipViscousLayerClosing"  

Conditions of use:
	The input shell has to contain 2 faces having the shape of triangles or ellipse quarters and an optional middle face being a quadrangle. The edge compound has to have all the characteristics of a compound build with the CloseViscousLayer function. 
	

"""
	
	if isinstance(np, str): print "[X] The first argument (np) should be an integer ."; return
	if isinstance(shell_and_compound, list) == False: print "[X] The second argument (shell_and_compound) should be an array."; return
	
	if dim == 0: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	shell_and_compound = GetGUISelection(shell_and_compound)
	
	shell_and_compound = GetObject(shell_and_compound)
	
	#-
	
	# Check the input shape existence
	
	if "error" in shell_and_compound or None in shell_and_compound: return
	
	#-
	
	# Check the number of selected objects
	
	if len(shell_and_compound) != 2:
		
		print "[X] Two objects should be selected."
		
		return
		
	
	#-
	
	# Distinguish input shapes
	
	shell = None
	compound = None
	
	for object in shell_and_compound:
		
		nb_faces = int(geompy.WhatIs(object).split("\n")[3].split(": ")[1])
		
		if nb_faces > 0:
			
			shell = object
		
		else:
			
			compound = object
			
		
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = compound
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Check if the input shape is "shell-shaped"
		
		shell_faces = GetSubShapes(shell)[2]
		
		try:
			
			shell = geompy.MakeShell(shell_faces)
			
		except:
			
			print "[X] The input 2D shape should be \"shell-shaped\"."; return
			
		
		#-
		
		# Keep edges touching the input shell
		
		compound_edges = GetSubShapes(compound)[1]
		
		edges_to_keep = []
		for edge in compound_edges:
			
			edge_vertexes = GetSubShapes(edge)[0]
			
			distance_1 = geompy.MinDistance(edge_vertexes[0], shell)
			distance_2 = geompy.MinDistance(edge_vertexes[1], shell)
			
			distances = [distance_1, distance_2]
			
			if max(distances) > tol:
				
				edges_to_keep.append(edge)
				
			
		
		compound = geompy.MakeCompound(edges_to_keep)
		
		#-
		
		shapes_to_return = []
		
		# Get the sub-shapes
		
		[shell, compound] = GetSubShapes([shell, compound])
		
		#-
		
		# Get the start edges
		
		start_edges = []
		
		for shell_edge in shell[1]:# For each edge in the face compound...
			
			shell_edge_vertexes = geompy.SubShapeAll(shell_edge, geompy.ShapeType["VERTEX"])
			
			# Get the number of adjacent face
			
			nb_adjacent_faces = 0
			
			for face in shell[2]:
				
				nb_contacts = 0
				
				for shell_edge_vertex in shell_edge_vertexes:
					
					min_distance = geompy.MinDistance(shell_edge_vertex, face)
					
					if min_distance <= tol:
						
						nb_contacts += 1
						
					
				
				if nb_contacts == 2:
					
					nb_adjacent_faces += 1
					
				
				
			
			#-
			
			# Get the number of contact with the edge compound
			
			nb_contacts = 0
			
			for shell_edge_vertex in shell_edge_vertexes:
				
				min_distance = geompy.MinDistance(shell_edge_vertex, compound[-1])
				
				if min_distance <= tol:
					
					nb_contacts += 1
					
				
			
			#-
			
			# Add the edge to the start edge list
			
			if nb_adjacent_faces == 1 and nb_contacts == 1:
				
				start_edges.append(shell_edge)
				
			
			#-
			
		
		#-
		
		# Make the outside solids
		
		solids = []
		
		for start_edge in start_edges:# For each start edge...
			
			start_edge_vertexes = geompy.SubShapeAll(start_edge, geompy.ShapeType["VERTEX"])
			
			# Get the adjacent face
			
			adjacent_face = None
			
			for face in shell[2]:
				
				nb_contacts = 0
				
				for start_edge_vertex in start_edge_vertexes:
					
					min_distance = geompy.MinDistance(start_edge_vertex, face)
					
					if min_distance <= tol:
						
						nb_contacts += 1
						
					
				
				if nb_contacts == 2:
					
					adjacent_face = face
					
					break
					
				
			
			#-
			
			# Get the center vertex
			
			center_vertex = None
			
			adjacent_face_vertexes = geompy.SubShapeAll(adjacent_face, geompy.ShapeType["VERTEX"])
			
			for adjacent_face_vertex in adjacent_face_vertexes:
				
				min_distance = geompy.MinDistance(adjacent_face_vertex, start_edge)
				
				if min_distance > tol:
					
					center_vertex = adjacent_face_vertex
					
					break
					
				
			
			#-
			
			# Get the start vertex
			
			start_vertex = None
			
			for adjacent_face_vertex in adjacent_face_vertexes:
				
				min_distance = geompy.MinDistance(adjacent_face_vertex, compound[-1])
				
				if min_distance > tol:
					
					start_vertex = adjacent_face_vertex
					
					break
					
				
			
			
			#-
			
			# Get the center edge
			
			center_edge = geompy.MakeEdge(center_vertex, start_vertex)
			
			#-
			
			# Get the path edge
			
			path_edge = None
			
			for edge in compound[1]:
				
				min_distance = geompy.MinDistance(edge, start_edge)
				
				if min_distance <= tol:
					
					path_edge = edge
					
					break
					
				
			
			#-
			
			# Get the edge style
			
			start_edge_length = geompy.BasicProperties(start_edge)[0]
			
			rebuilt_straight_start_edge = geompy.MakeEdge(start_edge_vertexes[0], start_edge_vertexes[1])
			
			rebuilt_straight_start_edge_length = geompy.BasicProperties(rebuilt_straight_start_edge)[0]
			
			if abs(start_edge_length - rebuilt_straight_start_edge_length) <= tol:
				
				style = "straight"
				
			
			else:
				
				style = "smooth"
				
			
			#-
			
			# Create the filling edges
			
			start_face = None
			end_face = None
			
			filling_edges_2d = []
			filling_edges_3d = []
			
			for parameter in [n / float(np - 1) for n in range(np)]:
				
				# Create the vertexes
				
				length = geompy.BasicProperties(path_edge)[0]
				
				vertex = geompy.MakeVertexOnCurveByLength(path_edge, parameter * length)
				
				#-
				
				# Create the filling edge
				
				if style == "straight":
					
					filling_edge_3d = geompy.MakeEdge(start_vertex, vertex)
					
				
				elif style == "smooth":
					
					filling_edge_3d = geompy.MakeArcOfEllipse(center_vertex, start_vertex, vertex)
					
				
				filling_edge_2d = geompy.MakeEdge(center_vertex, vertex)
				
				filling_edges_3d.append(filling_edge_3d)
				filling_edges_2d.append(filling_edge_2d)
				
				#-
				
				if parameter == 0:
					
					# Create the start face
					
					start_face_wire = geompy.MakeWire([center_edge, filling_edge_2d, filling_edge_3d])
					
					start_face = geompy.MakeFace(start_face_wire, True)
					
					#-
				
				if parameter == 1:
					
					# Create the end face
					
					end_face_wire = geompy.MakeWire([center_edge, filling_edge_2d, filling_edge_3d])
					
					end_face = geompy.MakeFace(end_face_wire, True)
					
					#-
					
				
			
			# Create the filling edge compounds
			
			filling_edge_compound_2d = geompy.MakeCompound(filling_edges_2d)
			filling_edge_compound_3d = geompy.MakeCompound(filling_edges_3d)
			
			#-
			
			if dim == 1:
				
				shapes_to_return.append(filling_edge_compound_2d)
				shapes_to_return.append(filling_edge_compound_3d)
				
			
			else:
				
				# Create the fillings
				
				filling_2d = geompy.MakeFilling(filling_edge_compound_2d, theMaxDeg = 20, theNbIter = 1, theTol2D = 1e-5, theTol3D = 1e-5, theMethod = GEOM.FOM_AutoCorrect)
				filling_3d = geompy.MakeFilling(filling_edge_compound_3d, theMaxDeg = 20, theNbIter = 1, theTol2D = 1e-5, theTol3D = 1e-5, theMethod = GEOM.FOM_AutoCorrect)
				
				#-
				
				# Remove the extra edges
				
				filling_2d = RemoveFaceExtraEdges(filling_2d, add = False)
				filling_3d = RemoveFaceExtraEdges(filling_3d, add = False)
				
				#-
				
				# Create the filling compound
				
				filling_shell = geompy.MakeShell([start_face, end_face, filling_2d, filling_3d])
				
				#-
				
				if dim == 2:
					
					shapes_to_return.append(filling_shell)
					
				
				else:
					
					# Sew the shell
					
					sewing_tolerance = tol
					
					while True:
						
						free_boundaries = geompy.GetFreeBoundary(filling_shell)[1]
						
						if len(free_boundaries) == 0:
							
							break
							
						
						filling_shell = geompy.MakeSewing(filling_shell, sewing_tolerance)
						
						sewing_tolerance *= 2
						
					
					#-
					
					# Create the solid
					
					solids.append(geompy.MakeSolid([filling_shell]))
					
					#-
					
				
			
		
		#-
		
		# Get the inside face
		
		inside_faces = []
		
		for face in shell[2]:
			
			nb_adjacent_start_edges = 0
			
			for start_edge in start_edges:
				
				start_edge_vertexes = geompy.SubShapeAll(start_edge, geompy.ShapeType["VERTEX"])
				
				nb_contacts = 0
				
				for start_edge_vertex in start_edge_vertexes:
					
					min_distance = geompy.MinDistance(start_edge_vertex, face)
					
					if min_distance <= tol:
						
						nb_contacts += 1
						
					
				
				if nb_contacts >= 2:
					
					nb_adjacent_start_edges += 1
					
				
			
			if nb_adjacent_start_edges == 0:
				
				inside_faces.append(face)
				
			
		
		#-
		
		# Create the inside solid
		
		for inside_face in inside_faces:# For inside face...
			
			inside_face_edges = geompy.SubShapeAll(inside_face, geompy.ShapeType["EDGE"])
			
			path_edges = []
			center_edge = None
			
			for inside_face_edge in inside_face_edges:
				
				# Get the center edge
				
				nb_contacts = 0
				
				inside_face_edge_vertexes = geompy.SubShapeAll(inside_face_edge, geompy.ShapeType["VERTEX"])
				
				for inside_face_edge_vertex in inside_face_edge_vertexes:
					
					min_distance = geompy.MinDistance(inside_face_edge_vertex, compound[-1])
					
					if min_distance <= tol:
						
						nb_contacts += 1
						
					
				
				if nb_contacts == 2:
					
					center_edge = inside_face_edge
					
				
				#-
				
				# Get the first path edge
				
				min_distance = geompy.MinDistance(inside_face_edge, compound[-1])
				
				if min_distance > tol:
					
					path_edges.append(inside_face_edge)
					
				
				#-
				
			
			# Get the second path edge
			
			for edge in compound[1]:
				
				min_distance = geompy.MinDistance(shell[-1], edge)
				
				if min_distance > tol:
					
					path_edges.append(edge)
					
				
			
			#-
			
			# Create filling edges
			
			filling_edges_2d = []
			filling_edges_3d = []
			
			# Get the start vertexes
			
			length_0 = geompy.BasicProperties(center_edge)[0]
			length_1 = geompy.BasicProperties(path_edges[0])[0]
			length_2 = geompy.BasicProperties(path_edges[1])[0]
			
			first_vertex_0 = geompy.SubShapeAll(center_edge, geompy.ShapeType["VERTEX"])[0]
			first_vertex_1 = geompy.SubShapeAll(path_edges[0], geompy.ShapeType["VERTEX"])[0]
			last_vertex_1 = geompy.SubShapeAll(path_edges[0], geompy.ShapeType["VERTEX"])[1]
			
			first_vertex_1_adjacent_edge = None
			
			for edge in compound[1]:
				
				min_distance = geompy.MinDistance(edge, first_vertex_0)
				
				if min_distance <= tol:
					
					first_vertex_1_adjacent_edge = edge
					
					break
					
				
			
			path_edge_vertexes = geompy.SubShapeAll(path_edges[1], geompy.ShapeType["VERTEX"])
			
			first_vertex_2 = None
			last_vertex_2 = None
			
			for path_edge_vertex in path_edge_vertexes:
				
				min_distance = geompy.MinDistance(path_edge_vertex, first_vertex_1_adjacent_edge)
				
				if min_distance <= tol:
					
					first_vertex_2 = path_edge_vertex
					
				
				else:
					
					last_vertex_2 = path_edge_vertex
					
				
			
			#-
			
			# Create the start face and end face edges
			
			center_edge_vertexes = geompy.SubShapeAll(center_edge, geompy.ShapeType["VERTEX"])
			
			start_face_edge_1 = geompy.MakeEdge(first_vertex_0, first_vertex_1)
			start_face_edge_2 = geompy.MakeEdge(first_vertex_0, first_vertex_2)
			
			end_face_edge_1 = geompy.MakeEdge(center_edge_vertexes[1], last_vertex_1)
			end_face_edge_2 = geompy.MakeEdge(center_edge_vertexes[1], last_vertex_2)
			
			#-
			
			for parameter in [n / float(np - 1) for n in range(np)]:
				
				# Create the vertexes
				
				vertex_0 = geompy.MakeVertexOnCurveByLength(center_edge, parameter * length_0, first_vertex_0)
				vertex_1 = geompy.MakeVertexOnCurveByLength(path_edges[0], parameter * length_1, first_vertex_1)
				vertex_2 = geompy.MakeVertexOnCurveByLength(path_edges[1], parameter * length_2, first_vertex_2)
				
				#-
				
				# Create the filling edges 3D
				
				if style == "straight":
					
					filling_edge_3d = geompy.MakeEdge(vertex_1, vertex_2)
					
				
				elif style == "smooth":
					
					filling_edge_3d = geompy.MakeArcOfEllipse(vertex_0, vertex_1, vertex_2)
					
				
				filling_edges_3d.append(filling_edge_3d)
				
				#-
				
				# Create the filling edges 2D
				
				filling_edge_2d = geompy.MakeEdge(vertex_0, vertex_2)
				
				filling_edges_2d.append(filling_edge_2d)
				
				#-
				
				if parameter == 0:
					
					# Create the start face
					
					start_face_wire = geompy.MakeWire([start_face_edge_1, start_face_edge_2, filling_edge_3d])
					
					start_face = geompy.MakeFace(start_face_wire, True)
					
					#-
				
				if parameter == 1:
					
					# Create the end face
					
					end_face_wire = geompy.MakeWire([end_face_edge_1, end_face_edge_2, filling_edge_3d])
					
					end_face = geompy.MakeFace(end_face_wire, True)
					
					#-
					
				
			
			#-
			
			# Create the filling edge compounds
			
			filling_edge_compound_2d = geompy.MakeCompound(filling_edges_2d)
			filling_edge_compound_3d = geompy.MakeCompound(filling_edges_3d)
			
			#-
			
			if dim == 1:
				
				shapes_to_return.append(filling_edge_compound_2d)
				shapes_to_return.append(filling_edge_compound_3d)
				
			
			else:
				
				# Create the fillings
				
				filling_2d = geompy.MakeFilling(filling_edge_compound_2d, theMaxDeg = 20, theNbIter = 1, theTol2D = 1e-5, theTol3D = 1e-5, theMethod = GEOM.FOM_AutoCorrect)
				filling_3d = geompy.MakeFilling(filling_edge_compound_3d, theMaxDeg = 20, theNbIter = 1, theTol2D = 1e-5, theTol3D = 1e-5, theMethod = GEOM.FOM_AutoCorrect)
				
				#-
				
				# Create the filling compound
				
				filling_shell = geompy.MakeShell([inside_face, start_face, end_face, filling_2d, filling_3d])
				
				#-
				
				if dim == 2:
					
					shapes_to_return.append(filling_shell)
					
				
				else:
					
					# Sew the shell
					
					sewing_tolerance = tol * 1e2
					
					while True:
						
						free_boundaries = geompy.GetFreeBoundary(filling_shell)[1]
						
						if len(free_boundaries) == 0:
							
							break
							
						
						filling_shell = geompy.MakeSewing(filling_shell, sewing_tolerance)
						
						sewing_tolerance *= 2
						
					
					#-
					
					# Create the solid
					
					solids.append(geompy.MakeSolid([filling_shell]))
					
					#-
					
				
			
		
		#-
		
		if dim == 1:
			
			if add == True:
				
				AddToStudy(shapes_to_return, "TipViscousLayerClosing (Edges)", father)
				
			
			return shapes_to_return
			
		
		elif dim == 2:
			
			if add == True:
				
				AddToStudy(shapes_to_return, "TipViscousLayerClosing (Faces)", father)
				
			
			return shapes_to_return
			
		
		else:
			
			# Put the solids into a compound
			
			solids = geompy.MakeCompound(solids)
			
			#-
			
			# Glue faces into the compound
			
			try:
				
				solids = geompy.MakeGlueFaces(solids, tol * 1e2)
				
			except:
				
				print "[*] The glue operation failed on the final shape."
				
			
			#-
			
			# Add and return the resulting shape(s)
			
			if add == True:
				
				AddToStudy(solids, "TipViscousLayerClosing", father)
				
			
			return solids
			
			#-
			
		
	

ctvl = CloseTipViscousLayer

def MakeLinkingSolids( face_and_edge_compounds = [None], tol = 1e-7, add = True, dim = 3 ):
	"""
	
	
Description:
	Creates solids linking two sets of faces.
	

Arguments:
	# face_and_edge_compounds 
		Description:       The faces compounds to link + the linking edge compound. 
		Type:              List of  2 Compounds of Faces +  1 Compound of Edges  
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     3  

Returned Values:
	"dim" value:    2 
	"single" value: - 
	Type:           Compound of Faces 
	Number:         n 
	Name:           "LinkingSolids (Faces)"  

	"dim" value:    3 
	"single" value: - 
	Type:           Compound of Solids 
	Number:         1 
	Name:           "LinkingSolids"  

Conditions of use:
	All vertexes of one face compound have to be linked with another vertex from the second face compound.
	

"""
	
	if isinstance(face_and_edge_compounds, list) == False: print "[X] The first argument (face_and_edge_compounds) should be an array."; return
	
	if dim < 2: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	face_and_edge_compounds = GetGUISelection(face_and_edge_compounds)
	
	face_and_edge_compounds = GetObject(face_and_edge_compounds)
	
	#-
	
	# Check the input shape existence
	
	if "error" in face_and_edge_compounds or None in face_and_edge_compounds: return
	
	#-
	
	# Check the number of selected objects
	
	if len(face_and_edge_compounds) != 3:
		
		print "[X] Three objects should be selected."
		
		return
		
	
	#-
	
	# Distinguish input shapes
	
	face_compounds = []
	edge_compound = None
	
	for object in face_and_edge_compounds:
		
		nb_faces = int(geompy.WhatIs(object).split("\n")[3].split(": ")[1])
		
		if nb_faces > 0:
			
			face_compounds.append(object)
		
		else:
			
			edge_compound = object
			
		
	
	#-
	
	if False: pass
	
	else:# All checks done
	
		shapes_to_return = []
		
		# Get the sub-shapes
		
		#[face_compound1, face_compound2, edge_compound] = GetSubShapes(face_compounds + [edge_compound])
		[face_compound2, face_compound1, edge_compound] = GetSubShapes(face_compounds + [edge_compound])
		
		#-
		
		# Create the solids
		
		solids = []
		
		for face_1 in face_compound1[2]:# For each face of the face compound 1...
			
			# Get the linking edges
			
			face_1_linking_edges = []
			
			for edge in edge_compound[1]:
				
				min_distance = geompy.MinDistance(edge, face_1)
				
				if min_distance <= tol:
					
					face_1_linking_edges.append(edge)
					
				
			
			#-
			
			# Get the target face
			
			face_1_target_face = None
			
			nb_face_1_linking_edges = len(face_1_linking_edges)
			
			for face_2 in face_compound2[2]:
				
				nb_contact = 0
				
				for face_1_linking_edge in face_1_linking_edges:
					
					min_distance = geompy.MinDistance(face_1_linking_edge, face_2)
					
					if min_distance <= tol:
						
						nb_contact += 1
						
					
				
				if nb_contact == nb_face_1_linking_edges:
					
					face_1_target_face = face_2
					
					break
					
				
			
			#-
			
			# Create the linking fillings
			
			face_1_linking_fillings = []
			
			face_1_edges = geompy.SubShapeAll(face_1, geompy.ShapeType["EDGE"])
			face_1_target_face_edges = geompy.SubShapeAll(face_1_target_face, geompy.ShapeType["EDGE"])
			
			for face_1_edge in face_1_edges:# For each edge of the face 1...
				
				# Get the linking edges
				
				face_1_edge_linking_edges = []
				
				for face_1_linking_edge in face_1_linking_edges:
					
					min_distance = geompy.MinDistance(face_1_linking_edge, face_1_edge)
					
					if min_distance <= tol:
						
						face_1_edge_linking_edges.append(face_1_linking_edge)
						
					
				
				#-
				
				# Get the target edge
				
				face_1_edge_target_edge = None
				
				for face_1_target_face_edge in face_1_target_face_edges:
					
					nb_contact = 0
					
					for face_1_edge_linking_edge in face_1_edge_linking_edges:
						
						min_distance = geompy.MinDistance(face_1_edge_linking_edge, face_1_target_face_edge)
						
						if min_distance <= tol:
							
							nb_contact += 1
							
						
					
					if nb_contact == 2:
						
						face_1_edge_target_edge = face_1_target_face_edge
						
					
				
				#-
				
				# Create the filling edge compound
				
				filling_edge_compound = geompy.MakeCompound([face_1_edge, face_1_edge_target_edge])
				
				#-
				
				# Create the filling
				
				face_1_linking_filling = geompy.MakeFilling(filling_edge_compound, theMethod = GEOM.FOM_AutoCorrect)
				
				face_1_linking_fillings.append(face_1_linking_filling)
				
				#-
				
			
			#-
			
			# Create the compound
			
			face_1_shell = geompy.MakeShell([face_1, face_1_target_face] + face_1_linking_fillings)
			
			#-
			
			if dim == 2:
				
				shapes_to_return.append(face_1_shell)
				
			
			else:
				
				# Sew the shell
				
				sewing_tolerance = tol
				
				while True:
					
					free_boundaries = geompy.GetFreeBoundary(face_1_shell)[1]
					
					if len(free_boundaries) == 0:
						
						break
						
					
					face_1_shell = geompy.MakeGlueEdges(face_1_shell, sewing_tolerance)
					
					sewing_tolerance *= 2
					
				
				#-
				
				# Create the solid
				
				face_1_shell = geompy.MakeShell([face_1_shell])
				
				face_1_solid = geompy.MakeSolid([face_1_shell])
				
				solids.append(face_1_solid)
				
				#-
				
			
		
		#-
		
		if dim == 2:
			
			if add == True:
				
				AddToStudy(shapes_to_return, "LinkingSolids (Faces)")
				
			
			return shapes_to_return
			
		
		else:
			
			# Put the solids into a compound
			
			solids = geompy.MakeCompound(solids)
			
			#-
			
			# Glue faces
			
			try:
				
				solids = geompy.MakeGlueFaces(solids, tol)
				
			except:
				
				print "[*] The glue operation failed on the final shape."
				
			
			#-
			
			# Add and return the resulting shape(s)
			
			if add == True:
				
				AddToStudy(solids, "LinkingSolids")
				
			
			return solids
			
			#-
			
		
	

mls = MakeLinkingSolids

def CopyGeometricalGroups( shape1, shape2, only = [None], ignore = [None], type = None, tol = 1e-7, add = True ):
	"""
	
	
Description:
	Copies groups from a geometrical object to another according to the shape of group elements.
	

Arguments:
	# shape1 
		Description:       the source geometrical object. 
		Type:              Any geometrical object 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     -  

	# shape2 
		Description:       The target geometrical object. 
		Type:              Any geometrical object 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     -  

	# only 
		Description:       The list of names of groups to copy, excluding the others. 
		Type:              List of Strings 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     [None]  

	# ignore 
		Description:       The list of names of groups to ignore. 
		Type:              List of Strings 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     [None]  

	# type 
		Description:       The type of groups to copy. Can equal "vertex", "edge", "face" or "solid". 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     None  

	# tol 
		Description:       See here. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1e-7  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Group 
	Number:         n 
	Name:           The name of the source group  

Conditions of use:
	The groups inside the source shape must have each one a different name.
	

"""
	
	if add == True:
		
		gg = salome.ImportComponentGUI("GEOM")
		
	
	# Get the input shape(s)
	
	[shape1, shape2] = GetObject([shape1, shape2])
	
	#-
	
	# Check the input shape existence
	
	if "error" in [shape1, shape2] or None in [shape1, shape2]: return
	
	#-
	
	else:# All checks done
		
		# Get the list of the IDs of all the shapes visible in the study tree
		
		visible_ids = ListComponentShapes("GEOM", output = "ID")
		
		#-
		
		# Get the shape 1 groups
		
		groups_1 = geompy.GetGroups(shape1)
		
		visible_groups_1 = []
		
		for group_1 in groups_1:
			
			group_1_id = salome.ObjectToID(group_1)
			
			if group_1_id in visible_ids:
				
				visible_groups_1.append(group_1)
				
			
		
		#-
		
		# Sort the shape 1 groups
		
		sorted_shape_groups_1 = []
		
		if only != [None]:
			
			for visible_group_1 in visible_groups_1:
				
				visible_groups_name1 = visible_group_1.GetName()
				
				if visible_groups_name1 in only:
					
					sorted_shape_groups_1.append(visible_group_1)
					
				
			
			visible_groups_1 = sorted_shape_groups_1
			
		
		sorted_shape_groups_1 = []
		
		if ignore != [None]:
			
			for visible_group_1 in visible_groups_1:
				
				visible_groups_name1 = visible_group_1.GetName()
				
				if visible_groups_name1 not in ignore:
					
					sorted_shape_groups_1.append(visible_group_1)
					
				
			
			visible_groups_1 = sorted_shape_groups_1
			
			
		
		sorted_shape_groups_1 = []
		
		if type != None:
			
			for visible_group_1 in visible_groups_1:
				
				visible_group_type1 = str(visible_group_1.GetMaxShapeType())
				
				if visible_group_type1 == type.upper():
					
					sorted_shape_groups_1.append(visible_group_1)
					
				
			
			visible_groups_1 = sorted_shape_groups_1
			
		
		#-
		
		# Get the shape 2 groups
		
		groups_2 = geompy.GetGroups(shape2)
		
		visible_groups_2 = []
		
		for group_2 in groups_2:
			
			group_2_id = salome.ObjectToID(group_2)
			
			if group_2_id in visible_ids:
				
				visible_groups_2.append(group_2)
				
			
		
		#-
		
		# Get the shape 2 group names
		
		visible_group_names_2 = [visible_group_2.GetName() for visible_group_2 in visible_groups_2]
		
		#-
		
		new_groups_2 = []
		
		for visible_group_1 in visible_groups_1:# For each of these groups...
			
			# Get the group name
			
			visible_group_1_name = visible_group_1.GetName()
			
			#-
			
			# Get the group type
			
			visible_group_1_type = str(visible_group_1.GetMaxShapeType())
			
			#-
			
			if visible_group_1_name in visible_group_names_2:# If the group already exists in the shape 2...
				
				# Delete this group
				
				i = 0
				
				for visible_group_name_2 in visible_group_names_2:
					
					if visible_group_1_name == visible_group_name_2:
						
						try:
							
							salome.geom.geomtools.GeomStudyTools().deleteShape(salome.ObjectToID(visible_groups_2[i]))
							
						
						except:
							
							pass
							
						
						break
						
					
					i += 1
					
				
			
			# Create the shape 2 group
			
			new_group_2 = geompy.CreateGroup(shape2, geompy.ShapeType[visible_group_1_type])
			
			#if strict == False:
				
			try: 
				
				new_group_2 = geompy.GetInPlace(shape2, visible_group_1)
				
			
			except:
				
				new_group_2 = None
				
				
			
			#else:
				
				#try:
					
					#shape2MatchedSubShapes = geompy.GetSharedShapes(shape2, visible_group_1, geompy.ShapeType[visible_group_1_type])
					
					#for shape2_matched_sub_shape in shape2_matched_sub_shapes:
						
						#shape2MatchedSubShapeID = geompy.GetSubShapeID(shape2, shape2_matched_sub_shape)
						
						#geompy.AddObject(new_group_2, shape2_matched_sub_shape_id)
						
					
				
				#except:
					
					#new_group_2 = None
					
				
			
			#-
			
			# Add the group to the list
			
			new_groups_2.append(new_group_2)
			
			#-
			
			# Add the group to the study
			
			if new_group_2 != None:
				
				if add == True:
					
					try:
						
						id = geompy.addToStudyInFather(shape2, new_group_2, visible_group_1_name)
						
						gg.createAndDisplayGO(id)
						
						if salome.sg.hasDesktop():
							
							salome.sg.updateObjBrowser(1)
							
						
					
					except:
						
						pass
						
						
					
				
			
			#-
			
		
		#-
		
		# Return the resulting shape(s)
		
		return new_groups_2
		
		#-
		
		salome.sg.updateObjBrowser(1)
		
	

cgg = CopyGeometricalGroups

def ExportGeometricalGroups( shape = None, file = "cfdmsh_grps", only = [None], ignore = [None], type = None ):
	"""
	
	
Description:
	Exports into a file the geometrical groups of a geometrical object in the form of sets of subshape IDs.
	

Arguments:
	# shape 
		Description:       The source geometrical object. 
		Type:              Any geometrical object 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# file 
		Description:       The name of the file to write. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "cfdmsh_grps"  

	# only 
		Description:       The list of names of groups to export, excluding the others. 
		Type:              List of Strings 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     [None]  

	# ignore 
		Description:       The list of names of groups to ignore. 
		Type:              List of Strings 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     [None]  

	# type 
		Description:       Type of groups to export. Can equal "vertex", "edge", "face" or "solid". 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     None  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	-
	

"""
	
	# Get the input shape(s)
	
	shape = GetGUISelection(shape, uniq = True)
	
	shape = GetObject(shape)
	
	#-
	
	# Check the input shape existence
	
	if "error" in [shape] or None in [shape]: return
	
	#-
	
	else:# All checks done
		
		# Get the list of the IDs of all the shapes visible in the study tree
		
		visible_ids = ListComponentShapes("GEOM", output = "ID")
		
		#-
		
		# Open the group file
		
		group_file = open(file, "w")
		
		#-
		
		# Get the groups
		
		shape_groups = geompy.GetGroups(shape)
		
		visible_shape_groups = []
		
		for shape_group in shape_groups:
			
			shape_group_id = salome.ObjectToID(shape_group)
			
			if shape_group_id in visible_ids:
				
				visible_shape_groups.append(shape_group)
				
			
		
		#shapeGroups = geompy.GetGroups(shape)
		
		#-
		
		# Sort the groups
		
		sorted_shape_groups = []
		
		if only != [None]:
			
			for visible_group in visible_shape_groups:
				
				visible_shape_groups_name = visible_group.GetName()
				
				if visible_shape_groups_name in only:
					
					sorted_shape_groups.append(visible_group)
					
				
			
			visible_shape_groups = sorted_shape_groups
			
		
		sorted_shape_groups = []
		
		if ignore != [None]:
			
			for visible_group in visible_shape_groups:
				
				visible_shape_groups_name = visible_group.GetName()
				
				if visible_shape_groups_name not in ignore:
					
					sorted_shape_groups.append(visible_group)
					
				
			
			visible_shape_groups = sorted_shape_groups
			
			
		
		sorted_shape_groups = []
		
		if type != None:
			
			for visible_group in visible_shape_groups:
				
				visible_group_type = str(visible_group.GetMaxShapeType())
				
				if visible_group_type == type.upper():
					
					sorted_shape_groups.append(visible_group)
					
				
			
			visible_shape_groups = sorted_shape_groups
			
		
		#-
		
		# Write the group file
		
		for visible_shape_group in visible_shape_groups:
			
			# Get the name of groups
			
			group_name = visible_shape_group.GetName()
			
			#-
			
			if group_name != "":
				
				# Write the name of groups
				
				group_file.write("%s\n"%(group_name))
				
				#-
				
				# Get the type of group
				
				nb_solids = geompy.NbShapes(visible_shape_group, geompy.ShapeType["SOLID"])
				nb_faces = geompy.NbShapes(visible_shape_group, geompy.ShapeType["FACE"])
				nb_edges = geompy.NbShapes(visible_shape_group, geompy.ShapeType["EDGE"])
				nb_vertexes = geompy.NbShapes(visible_shape_group, geompy.ShapeType["VERTEX"])
				
				if nb_solids > 0:
					
					group_type = geompy.ShapeType["SOLID"]
					
				
				elif nb_faces > 0:
					
					group_type = geompy.ShapeType["FACE"]
					
				
				elif nb_edges > 0:
					
					group_type = geompy.ShapeType["EDGE"]
					
				
				elif nb_vertexes > 0:
					
					group_type = geompy.ShapeType["VERTEX"]
					
				
				#-
				
				# Write the type of groups
				
				group_file.write("%s\n"%(group_type))
				
				#-
				
				# Get the IDs of groups
				
				group_sub_shapes = geompy.SubShapeAll(visible_shape_group, group_type)
				
				#-
				
				# Write the IDs of groups
				
				for sub_shape in group_sub_shapes:
					
					sub_shape_id = geompy.GetSubShapeID(shape, sub_shape)
					
					group_file.write("%s\t"%(sub_shape_id))
					
				
				#-
				
				group_file.write("\n")
			
		
		#-
		
		# Close the group file
		
		group_file.close()
		
		#-
		
	

egg = ExportGeometricalGroups

def ImportGeometricalGroups( shape = None, file = "cfdmsh_grps", only = [None], ignore = [None], type = None, add = True ):
	"""
	
	
Description:
	Imports from a file created with the ExportGeometricalGroups function into a geometrical object groups in the form of sets of subshape IDs.
	

Arguments:
	# shape 
		Description:       The target geometrical object. 
		Type:              Any geometrical object 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# file 
		Description:       The name of the file to read. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "cfdmsh_grps"  

	# only 
		Description:       The list of names of groups to export, excluding the others. 
		Type:              List of Strings 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     [None]  

	# ignore 
		Description:       The list of names of groups to ignore. 
		Type:              List of Strings 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     [None]  

	# type 
		Description:       Type of groups to export. Can equal "vertex", "edge", "face" or "solid". 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     None  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True   

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Group 
	Number:         n 
	Name:           The name of the group in the file  

Conditions of use:
	-
	

"""
	
	if add == True: gg = salome.ImportComponentGUI("GEOM")
	
	# Get the input shape(s)
	
	shape = GetGUISelection(shape, uniq = True)
	
	shape = GetObject(shape)
	
	#-
	
	# Check the input shape existence
	
	if "error" in [shape] or None in [shape]: return
	
	#-
	
	else:# All checks done
		
		
		# Get the list of the IDs of all the shapes visible in the study tree
		
		visible_ids = ListComponentShapes("GEOM", output = "ID")
		
		#-
		
		# Get the already existing groups
		
		#oldGroups = geompy.GetGroups(shape)
		
		old_groups = geompy.GetGroups(shape)
		
		visible_old_groups = []
		
		for old_group in old_groups:
			
			old_group_id = salome.ObjectToID(old_group)
			
			if old_group_id in visible_ids:
				
				visible_old_groups.append(old_group)
				
			
		
		#-
		
		# Get the already existing group names
		
		visible_old_group_names = [visible_old_group.GetName() for visible_old_group in visible_old_groups]
		
		#-
		
		# Open the group file
		
		group_file = open(file, "r")
		
		#-
		
		# Import the groups
		
		i = 0
		
		for line in group_file:
			
			line = line[:-1]# Delete ending "\n"
			
			# Get the group name
			
			if i == 0:
				
				group_name = line
				
			
			#-
			
			# Get the group type and create or get the group
			
			if i == 1:
				
				group_type = int(line)
				
				############
				
				############
				
				############
				
				pass_group = False
				
				if only != [None] and group_name not in only:
					
					pass_group = True
					
				
				if ignore != [None] and group_name in ignore:
					
					pass_group = True
					
				
				if type != None and group_type != geompy.ShapeType[type.upper()]:
					
					pass_group = True
					
				
				############
				
				############
				
				############
				
				if pass_group == False:
					
					if group_name in visible_old_group_names:# If the group already exists...
						
						# Get the already existing group
						
						j = 0
						
						for visible_old_group_name in visible_old_group_names:
							
							if group_name == visible_old_group_name:
								
								try:
									
									salome.geom.geomtools.GeomStudyTools().deleteShape(salome.ObjectToID(visible_old_groups[j]))
									
								
								except:
									
									pass
									
								
								break
								
							
							j += 1
							
						
						#-
						
					
					# Create the new group
					
					new_group = geompy.CreateGroup(shape, group_type)
					
					#-
					
				
			
			#-
			
			#-Get the IDs and add them to the new group
			
			if i == 2:
				
				if pass_group == False:
					
					shape_ids = line.split()
					
					for shape_id in shape_ids:
						
						geompy.AddObject(new_group, int(shape_id))
						
					
					if add == True:
						
						id = geompy.addToStudyInFather(shape, new_group, group_name)
						
						gg.createAndDisplayGO(id)
						
						if salome.sg.hasDesktop():
							
							salome.sg.updateObjBrowser(1)
							
						
					
				
			
			#-
			
			i += 1
			
			if i == 3:
				
				i = 0
				
			
		
		#-
		
		# Close the group file
		
		group_file.close()
		
		#-
		
	

igg = ImportGeometricalGroups

def PutAllSubShapesInAGroup( dim, shape = None, add = True, infa = True ):
	"""
	
	
Description:
	Create a geometrical group containing all sub-shapes of a given dimension.
	

Arguments:
	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# shape 
		Description:       The source shape. 
		Type:              Any geometrical object 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    0 
	"single" value: - 
	Type:           Group of Vertexes 
	Number:         1 
	Name:           "AllSubShapes (Vertexes)"  

	"dim" value:    1 
	"single" value: - 
	Type:           Group of Edges 
	Number:         1 
	Name:           "AllSubShapes (Edges)"  

	"dim" value:    2 
	"single" value: - 
	Type:           Group of Faces 
	Number:         1 
	Name:           "AllSubShapes (Faces)"  

	"dim" value:    3 
	"single" value: - 
	Type:           Group of Solids 
	Number:         1 
	Name:           "AllSubShapes (Solids)"  

Conditions of use:
	-
	

"""
	
	if dim not in [0, 1, 2, 3]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	# Get the input shape(s)
	
	shape = GetGUISelection(shape)
	
	shape = GetObject(shape)
	
	#-
	
	# Make this function recursive
	
	if isinstance(shape, list):
		
		return_list = []
		
		for sub_object in shape:
			
			return_list.append(PutAllSubShapesInAGroup(dim, sub_object, add, infa))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [shape] or None in [shape]: return
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = shape
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get the group type
		
		if dim == 0: group_type = geompy.ShapeType["VERTEX"]
		if dim == 1: group_type = geompy.ShapeType["EDGE"]
		if dim == 2: group_type = geompy.ShapeType["FACE"]
		if dim == 3: group_type = geompy.ShapeType["SOLID"]
		
		#-
		
		# Create the group
		
		group = geompy.CreateGroup(shape, group_type)
		
		#-
		
		# Get the sub - shape IDs
		
		sub_shape_ids = geompy.SubShapeAllIDs(shape, group_type)
		
		#-
		
		# Add the sub-shapes in the group
		
		for sub_shape_id in sub_shape_ids:
			
			geompy.AddObject(group, sub_shape_id)
			
		
		#-
		
		# Publish the group
		
		if add == True:
			
			if dim == 0: geompy.addToStudyInFather(father, group, "AllSubShapes (Vertexes)")
			if dim == 1: geompy.addToStudyInFather(father, group, "AllSubShapes (Edges)")
			if dim == 2: geompy.addToStudyInFather(father, group, "AllSubShapes (Faces)")
			if dim == 3: geompy.addToStudyInFather(father, group, "AllSubShapes (Solids)")
			
			# Update the study tree
			
			salome.sg.updateObjBrowser(1)
			
			#-
			
		
		return group
		
		#-
		
	

passiag = PutAllSubShapesInAGroup

def SetRandomColors( ):
	"""
	
	
Description:
	Applies random colors on selected shapes in the Geometry module's 3D windows.
	
	On mesh groups and sub-meshes, the coloration takes effect only if the input objects were not displayed yet. Else, the mesh has to be cleared and computed again. 

Arguments:
	# - 
		Description:       - 
		Type:              - 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	This functions works only when used from the GUI.
	

"""
	
	gg = salome.ImportComponentGUI("GEOM")
	
	# Get selected objects
	
	selected_object_ids = salome.sg.getAllSelected()
	
	nb_selected_objects = len(selected_object_ids)
	
	selected_objects = []
	
	for selected_object_id in selected_object_ids:
		
		selected_objects.append(salome.myStudy.FindObjectID(selected_object_id).GetObject())
		
	
	#-
	
	# Define colors
	
	colors = [\
	[255, 0, 0], \
	[0, 0, 255], \
	[0, 255, 0], \
	[0, 255, 255], \
	[255, 0, 128], \
	[255, 128, 0], \
	[255, 255, 0], \
	[235, 235, 235], \
	[20, 20, 20], \
	[255, 0, 255], \
	[255, 128, 128], \
	[128, 255, 128], \
	[0, 128, 255], \
	[255, 255, 128], \
	[255, 128, 255], \
	[128, 255, 255], \
	[128, 0, 255], \
	[0, 255, 128], \
	[128, 128, 255], \
	[128, 255, 0], \
	[128, 128, 128], \
	]
	
	nb_colors = len(colors)
	
	#-
	
	# Define random colors if necessary
	
	for i in range(nb_selected_objects - nb_colors):
		
		color = []
		
		for i in range(3):
			
			color.append(int(random.random() * 255))
			
		
		colors.append(color)
		
	
	#-
	
	colors.reverse()
	
	#random.shuffle(colors)
	
	# Set color of selected objects
	
	for i in range(nb_selected_objects):
		
		color = colors.pop()
		
		selected_object = selected_objects[i]
		
		if "<SMESH." in str(selected_object):
			
			try:
				
				selected_object.SetColor(SALOMEDS.Color(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0))
				
			
			except:
				
				pass
				
			
		
		if "<GEOM." in str(selected_object):
			
			gg.setColor(selected_object_ids[i], color[0], color[1], color[2])
			
		
	
	#-
	

src = SetRandomColors

def ExportCSVFile( compound = None, file = None, head = True ):
	"""
	
	
Description:
	Exports a 3D vertex compound into a CSV file.
	

Arguments:
	# compound 
		Description:       The vertex compound to export. 
		Type:              Compound of Vertexes 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# file 
		Description:       The name of the file to write. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     None  

	# head 
		Description:       Defines if the function has to write a header to the file. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	-
	

"""
	
	input_shape = compound
	
	# Get the input shape(s)
	
	input_shape = GetGUISelection(input_shape)
	
	input_shape = GetObject(input_shape)
	
	#-
	
	# Check the input shape existence
	
	if "error" in [input_shape] or None in [input_shape]: return
	
	#-
	
	compound = input_shape
	
	if False: pass
	
	else:# All checks done
		
		# Get vertexes
		
		vertexes = GetSubShapes(compound)[0]
		
		#-
		
		# Get the file name
		
		if file == None:
			
			file = compound.GetName()
			
		
		#-
		
		# Export them in the CSV file
		
		with open(file, "wb") as csvfile:
			
			writer = csv.writer(csvfile, quoting = csv.QUOTE_NONNUMERIC)
			
			if head == True:
				
				writer.writerow(["X","Y","Z"])
				
			
			for vertex in vertexes:
				
				writer.writerow(geompy.PointCoordinates(vertex))
				
			
		
		#-
		
	

ecf = ExportCSVFile

def ImportCSVFile( file, single = True, add = True ):
	"""
	
	
Description:
	Imports a CSV file describing a 3D set of vertexes.
	

Arguments:
	# file 
		Description:       The name of the file to read. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         yes 
		Default value:     -  

	# single 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True 

Returned Values:
	"dim" value:    - 
	"single" value: False 
	Type:           Vertex 
	Number:         n 
	Name:           "VertexFromCSVFile"  

	"dim" value:    - 
	"single" value: True 
	Type:           Compound of Vertexes 
	Number:         1 
	Name:           "VertexesFromCSVFile"  

Conditions of use:
	-
	

"""
	
	# Make this function recursive
	
	if isinstance(file, list):
		
		return_list = []
		
		for sub_object in file:
			
			return_list.append(ImportCSVFile(sub_object, single, add))
			
		
		return return_list
		
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Put the CSV file into a list of lines
		
		file_line_list = []
		
		with open(file, "r") as opened_file:
			
			for line in opened_file:
				
				if not line.isspace():
					
					file_line_list.append(line)
					
				
			
		
		#-
		
		# Get the separator
		
		separator_list = [",", ";", "\t", "|", "^"]
		
		right_separator = ""
		right_nb_columns = 0
		for separator in separator_list:
			
			separator_found = True
			
			nb_columns = 0
			
			this_was_first_line = True
			for line in file_line_list:
				
				split_line = line.split(separator)
				
				if not this_was_first_line:
					if len(split_line) != nb_columns or len(split_line) <= 1:
						separator_found = False
						break
				
				nb_columns = len(split_line)
				
				this_was_first_line = False
				
			
			if separator_found:
				
				right_separator = separator
				right_nb_columns = nb_columns
				
			
		
		if right_separator == "":
			
			print "[X] The CSV file separator could not be determined. Please, use one of these separator characters: , ; | ^ tab"
			return
			
		else:
			
			separator = right_separator
			nb_columns = right_nb_columns
			
		
		#-
		
		# Check the number of columns
		
		if nb_columns not in [2, 3]:
			print "[X] The CSV file should contain a number of columns between two and three."
			return
			
		
		#-
		
		# Import the vertexes from the CSV file
		
		vertex_list = []
		for line in file_line_list:
			
			split_line = line.split(separator)
			
			try:
				x = float(split_line[0])
			except:
				continue
			
			try:
				y = float(split_line[1])
			except:
				continue
			
			if nb_columns == 3:
				
				try:
					z = float(split_line[2])
				except:
					continue
				
			else:
				
				z = 0.0
				
			
			vertex = geompy.MakeVertex(x, y, z)
			vertex_list.append(vertex)
			
		
		#-
		
		to_return = vertex_list
		to_return_name = "VertexFromCSVFile"
		
		if single == True:
			
			compound = geompy.MakeCompound(vertex_list)
			
			to_return = compound
			to_return_name = "VertexesFromCSVFile"
			
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			slow_add = False
			if not isinstance(to_return, list) or single == True: slow_add = True
			
			AddToStudy(to_return, to_return_name, suffix = slow_add, refresh = slow_add)
			
			if slow_add == False:
				if salome.sg.hasDesktop():
					salome.sg.updateObjBrowser(1)
			
		
		return to_return
		
		#-
		
	

icf = ImportCSVFile

def MakeVirtualOffsetEdgeSubmeshes( thick_and_size, group_and_mesh = [None], np = 40, curv = True, rev = False, add = True, infa = False, dim = -1 ):
	"""
	
	
Description:
	Creates submeshes on an edge group so as to prepare it for automatic viscous layer meshing.
	

Arguments:
	# thick_and_size 
		Description:       The desired viscous layer thickness and the desired cell size along the edge. 
		Type:              List of 2 Floats 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# group_and_mesh 
		Description:       The input group and the mesh in which to create sub-meshes. 
		Type:              List of1 Group of Edges + 1 Mesh 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# np 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     40  

	# curv 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# rev 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# infa 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

	# dim 
		Description:       See here. 
		Type:              Integer 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -1  

Returned Values:
	"dim" value:    1 
	"single" value: - 
	Type:           Compound of Edges 
	Number:         1 
	Name:           "VirtualOffset"  

	"dim" value:    -1 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	-
	

"""
	
	if dim not in [-1, 0, 1]: print "[X] There is no shape to return corresponding to the given dimension."; return
	
	if not isinstance(thick_and_size, list):
		
		print "[X] The first argument (thick_and_size) should be an array."; return
		
	
	if not isinstance(group_and_mesh, list):
		
		print "[X] The second argument (group_and_mesh) should be an array."; return
		
	
	if len(thick_and_size) != 2:
		
		print "[X] The first argument (thick_and_size) should have exactly two elements."; return
		
	
	input_shapes = group_and_mesh
	
	# Get the input shape(s)
	
	input_shapes = GetGUISelection(input_shapes)
	
	input_shapes = GetObject(input_shapes, "GEOM", silent = True) + GetObject(input_shapes, "SMESH", silent = True)
	
	#-
	
	# Distinguish input shapes
	
	group = None
	mesh = None
	
	for object in input_shapes:
		
		if "GEOM_Object instance" in str(object): group = object
		if "SMESH_Mesh instance" in str(object) or "meshProxy instance" in str(object) or "Mesh object" in str(object): mesh = object
		
	
	if None in [group, mesh]:
		
		print "[X] The input objects are incorrect or the Mesh module was not yet loaded."; return
		
	
	
	#-
	
	# Set father object
	
	father = None
	
	if infa == True: father = group
	
	#-
	
	if False: pass
	
	else:# All checks done
		
		# Get input objects
		
		[dist, step] = thick_and_size
		
		try:
			mesh = smesh.Mesh(mesh)
		except:
			pass
		
		main_shape = group.GetMainShape()
		
		if main_shape == None:
			
			print "[X] The input group has no parent shape."; return
			
		
		group_name = group.GetName()
		
		group_vertexes = GetSubShapes(group)[0]
		
		#-
		
		# Check if the group is "wire-shaped"
		
		group_edge_list = GetSubShapes(group)[1]
		
		try:
			
			group_wire = geompy.MakeWire(group_edge_list)
			
		except:
			
			print "[X] The input group should be \"wire-shaped\"."; return
			
		
		#-
		
		# Make wire edge offsets
		
		if rev == True:
			
			dist *= -1
			
		
		offsets = MakePlanarWireOffset(dist, group_wire, np = np, curv = curv, simple = True, single = False, add = False)
		
		edges = GetReorderedEdges(group_wire, add = False)
		
		#-
		
		if dim == 1:
			
			compound = geompy.MakeCompound(offsets)
			
			to_return = compound
			to_return_name = "VirtualOffset"
			
		
		else:
			
			whole_vertex_list = list(group_vertexes)
			
			nb_edges = len(edges)
			for i in range(nb_edges):# For each edge of the input group...
				
				edge = edges[i]
				offset = offsets[i]
				
				offset_vertexes = GetSubShapes(offset)[0]
				whole_vertex_list += offset_vertexes
				
				# Get the number of steps
				
				edge_length = geompy.BasicProperties(edge)[0]
				offset_length = geompy.BasicProperties(offset)[0]
				
				nb_steps = math.ceil(offset_length / step)
				
				real_step = offset_length / nb_steps
				
				#-
				
				# Project offset vertexes on the edge
				
				distance = real_step
				projected_vertex_list = []
				vertex_on_offset_list = []
				while distance < offset_length - real_step / 2:
					
					vertex_on_offset = geompy.MakeVertexOnCurveByLength(offset, distance)
					vertex_on_offset_list.append(vertex_on_offset)
					
					##############################
					#projected_vertex = geompy.MakeProjection(vertex_on_offset, edge)# Not available on Salome 7.5.1
					[x,y,z] = geompy.ClosestPoints(vertex_on_offset, edge)[1][3:6]
					projected_vertex = geompy.MakeVertex(x, y, z)
					##############################
					projected_vertex_list.append(projected_vertex)
					
					distance += real_step
					
				
				#-
				
				whole_vertex_list += projected_vertex_list
				whole_vertex_list += vertex_on_offset_list
				
				# Split the edge with projected vertexes
				
				discretized_edge = geompy.MakePartition([edge], projected_vertex_list)
				
				#-
				
				# Reorder discretized edges
				
				reordered_edges = GetReorderedEdges(discretized_edge, add = False)
				nb_sub_edges = len(reordered_edges)
				
				#-
				
				if dim == -1:
					
					# Publish the edge in the study tree
					
					published_edge = geompy.GetInPlace(group, edge, theName = "SubEdge_" + str(i))
					
					#-
					
				
				if nb_sub_edges == 1:# If the edge was not discretized...
					
					if dim == -1:
						
						# Create a Nb. Segments sub-mesh
						
						algo = mesh.Segment(geom = published_edge)
						hypo = algo.NumberOfSegments(1)
						
						mesh.GetSubMesh(published_edge, "VirtualOffsetSubmesh_" + str(i) + " on " + group_name)
						
						#-
					
				
				else:# If the edge was discretized...
					
					# Get the suitable Fixed Points 1D hypothesis parameters
					
					parameter_list = []
					total_distance = 0
					for sub_edge in reordered_edges:
						sub_edge_length = geompy.BasicProperties(sub_edge)[0]
						parameter = (total_distance + sub_edge_length) / edge_length
						parameter_list.append(parameter)
						if len(parameter_list) == nb_sub_edges - 1:
							break
						total_distance += sub_edge_length
						
					
					#-
					
					if dim == -1:
						
						# Create temporary mesh and Fixed Points 1D sub-mesh
						
						tmp_mesh = smesh.Mesh(main_shape)
						
						algo = tmp_mesh.Segment(geom = published_edge)
						tmp_hypo = algo.FixedPoints1D(parameter_list, [1] * nb_sub_edges, [])
						sub_mesh = tmp_mesh.GetSubMesh(published_edge, "VirtualOffsetSubmesh_" + str(i) + " on " + group_name)
						
						tmp_mesh.Compute()
						
						#-
						
						# Check if the edge is reversed
						
						vertex_compound = MakeVertexesFromMeshGroup(sub_mesh, add = False)
						
						projected_vertex_compound = geompy.MakeCompound(projected_vertex_list)
						
						cut = geompy.MakeCut(vertex_compound, projected_vertex_compound)
						
						nb_resting_vertexes = geompy.NumberOfSubShapes(cut, geompy.ShapeType["VERTEX"])
						
						reversed_edges = []
						if nb_resting_vertexes > 2:
							
							reversed_edges = [published_edge]
							
						
						#-
						
						# Delete temporary geometrical shapes and mesh
						
						#http://www.salome-platform.org/forum/forum_10/366900504#419952388
						try:
							so = salome.ObjectToSObject(vertex_compound)
							sb = salome.myStudy.NewBuilder()
							sb.RemoveObjectWithChildren(so)
						except:
							pass
						
						try:
							so = salome.ObjectToSObject(tmp_mesh.GetMesh())
							sb = salome.myStudy.NewBuilder()
							sb.RemoveObjectWithChildren(so)
						except:
							pass
						
						try:
							so = salome.ObjectToSObject(tmp_hypo)
							sb = salome.myStudy.NewBuilder()
							sb.RemoveObjectWithChildren(so)
						except:
							pass
						
						#-
						
						# Create the final Fixed Points 1D sub-mesh
						
						algo = mesh.Segment(geom = published_edge)
						hypo = algo.FixedPoints1D(parameter_list, [1] * nb_sub_edges, reversed_edges)
						
						mesh.GetSubMesh(published_edge, "VirtualOffsetSubmesh_" + str(i) + " on " + group_name)
						
						#-
						
				
			
			if dim == 0:
				
				compound = geompy.MakeCompound(whole_vertex_list)
				
				to_return = compound
				to_return_name = "VirtualOffset (Vertexes)"
				
			
		
		if dim >= 0:
			
			if add == True:
				
				# Add and return the resulting shape(s)
				
				if add == True:
					
					AddToStudy(to_return, to_return_name, father)
					
				
				return to_return
				
				#-
				
			
		
		else:
			
			# Update the study tree
			
			if salome.sg.hasDesktop():
				
				salome.sg.updateObjBrowser(1)
				
			
			#-
			
		
	

mvoes = MakeVirtualOffsetEdgeSubmeshes

def MakeTriEdgeFaceSubmeshes( groups_and_mesh = None ):
	"""
	
	
Description:
	Creates quadrangle submeshes on tri-edge face groups (that can be create using the GetTriEdgeFaces function) and add base vertexes when possible.
	

Arguments:
	# groups_and_mesh 
		Description:       The input tri-edge face groups and the mesh in which to create sub-meshes. 
		Type:              List ofGroups of 1 Face + 1 Mesh 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	-
	

"""
	
	# Get the input shape(s)
	
	groups_and_mesh = GetGUISelection(groups_and_mesh)
	
	groups_and_mesh = GetObject(groups_and_mesh, "GEOM", silent = True) + GetObject(groups_and_mesh, "SMESH", silent = True)
	
	#-
	
	# Distinguish input shapes
	
	mesh = None
	groups = []
	
	for object in groups_and_mesh:
		
		if "SMESH_Mesh instance" in str(object) or "meshProxy instance" in str(object) or "Mesh object" in str(object): mesh = object
		if "GEOM_Object instance" in str(object): groups.append(object)
		
	
	if None in [mesh] or len(groups) == 0:
		
		print "[X] The input objects are incorrect or the Mesh module was not yet loaded."; return
		
	
	#-
	
	else:# All checks done
		
		try:
			mesh = smesh.Mesh(mesh)
		except:
			pass
		
		# Get the mesh main shape
		
		main_shape = mesh.GetShape()
		
		#-
		
		# For each input group...
		for group in groups:
			
			# Get group edge
			
			group_edges = geompy.SubShapeAll(group, geompy.ShapeType["EDGE"])
			
			#-
			
			# Keep only straight edges
			
			straight_edges = []
			
			for edge in group_edges:
				
				edge_length = geompy.BasicProperties(edge)[0]
				
				edge_vertexes = geompy.SubShapeAll(edge, geompy.ShapeType["VERTEX"])
				min_edge_length = geompy.MinDistance(edge_vertexes[0], edge_vertexes[1])
				
				if abs(edge_length - min_edge_length) < 1e-9:
					straight_edges.append(edge)
			
			#-
			
			# Get the group vertexes
			
			group_vertexes = geompy.SubShapeAll(group, geompy.ShapeType["VERTEX"])
			
			#-
			
			# Find the base vertex
			
			base_vertex = None
			
			for vertex in group_vertexes:
				
				nb_touching_edges = 0
				
				for edge in straight_edges:
					
					if geompy.MinDistance(edge, vertex) < 1e-9:
						
						nb_touching_edges += 1
				
				if nb_touching_edges == 2:
					
					base_vertex = vertex
					
					break
					
				
			
			#-
			
			# Get the base vertex ID
			
			base_vertex_id = geompy.GetSubShapeID(main_shape, base_vertex)
			
			#-
			
			# Create a sub-mesh on the group
			
			algo = mesh.Quadrangle(geom = group)
			hypo = algo.QuadrangleParameters()
			hypo.SetTriaVertex(base_vertex_id)
			submesh = mesh.GetSubMesh(group, group.GetName())
			
			#-
			
			# Update the study tree
			
			salome.sg.updateObjBrowser(1)
			
			#-
			
		
	

mtefs = MakeTriEdgeFaceSubmeshes

def ProjectEdgeSubmesh( submesh_and_edge = [None] ):
	"""
	
	
Description:
	Projects orthogonally an edge sub-mesh on another.
	

Arguments:
	# submesh_and_edge 
		Description:       The source submesh and the target sub-edge. 
		Type:              List of1 Edge + 1 Sub-mesh 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	The source sub-mesh has to be already computed.
	

"""
	
	if isinstance(submesh_and_edge, list) == False: print "[X] The first argument (submesh_and_edge) should be an array."; return
	
	# Get the input shape(s)
	
	submesh_and_edge = GetGUISelection(submesh_and_edge)
	
	submesh_and_edge = GetObject(submesh_and_edge, "GEOM", silent = True) + GetObject(submesh_and_edge, "SMESH", silent = True)
	
	#-
	
	# Distinguish input shapes
	
	submesh = None
	edge = None
	
	for object in submesh_and_edge:
		
		if "SMESH_subMesh instance" in str(object): submesh = object
		if "GEOM_Object" in str(object): edge = object
		
	
	if None in [submesh, edge]:
		
		print "[X] The input objects are incorrect or the Mesh module was not yet loaded."
		
		return
		
	
	#-
	
	else:# All checks done
		
		# Create vertexes from the sub-mesh
		
		vertexes_from_submesh_compound = MakeVertexesFromMeshGroup(submesh, add = False)
		vertexes_from_submesh = geompy.SubShapeAll(vertexes_from_submesh_compound, geompy.ShapeType["VERTEX"])
		
		#-
		
		# Project vertexes on the edge
		
		projected_vertex_list = []
		for vertex_from_submesh in vertexes_from_submesh:
			[x, y, z] = geompy.ClosestPoints(vertex_from_submesh, edge)[1][3:6]
			projected_vertex_list.append(geompy.MakeVertex(x, y, z))
		
		#-
		
		# Split the edge with projected vertexes
		
		discretized_edge = geompy.MakePartition([edge], projected_vertex_list)
		
		#-

		# Get vertex parameters on the input edge
		
		edge_length = geompy.BasicProperties(edge)[0]
		
		reordered_edges = GetReorderedEdges(discretized_edge, add = False)
		nb_sub_edges = len(reordered_edges)

		parameter_list = []
		total_distance = 0
		for sub_edge in reordered_edges:
			sub_edge_length = geompy.BasicProperties(sub_edge)[0]
			parameter = (total_distance + sub_edge_length) / edge_length
			parameter_list.append(parameter)
			if len(parameter_list) == nb_sub_edges - 1:
				break
			total_distance += sub_edge_length
		
		#-
		
		# Get the mesh
		
		mesh = smesh.Mesh(submesh.GetMesh())
		
		#-
		
		# Create a sub-mesh on the edge
		
		algo = mesh.Segment(geom = edge)
		fixed_points_hypo = algo.FixedPoints1D(parameter_list, [1] * nb_sub_edges, [])
		mesh.GetSubMesh(edge, edge.GetName())
		smesh.SetName(fixed_points_hypo, edge.GetName())
		
		#-
		
		# Update the study tree
		
		if salome.sg.hasDesktop():
			
			salome.sg.updateObjBrowser(1)
			
		
		#-
		
	

pes = ProjectEdgeSubmesh

def MakeNetgenRefinement( size, hypo_and_area = [None], ratio = 0.7, test = False ):
	"""
	
	
Description:
	Create an arbitrary 3D refinement area in a Netgen hypothesis.
	

Arguments:
	# size 
		Description:       The desired cell size in the refinement area. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# hypo_and_area 
		Description:       The volume defining the refinement area and the Netgen hypothesis. 
		Type:              List of 1 Mesh hypothesis + 1 Solid 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# ratio 
		Description:       Defines the distance between edges describing the refinement area.  If equals one, this distance equals the desired cell size. If lower than one,  this distance is increased. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     0.7  

	# test 
		Description:       If equals True, the edges are not created, but the number of necessary edge is displayed  in the Python console. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Compound 
	Number:         1 
	Name:           "RefinementEdges"  

Conditions of use:
	-
	

"""
	
	if isinstance(size, str): print "[X] The first argument (size) should be a float number."; return
	if isinstance(hypo_and_area, list) == False: print "[X] The second argument (hypo_and_area) should be an array."; return
	
	# Get the input shape(s)
	
	hypo_and_area = GetGUISelection(hypo_and_area)
	
	hypo_and_area = GetObject(hypo_and_area, "GEOM", silent = True) + GetObject(hypo_and_area, "NETGENPlugin", silent = True)
	
	#-
	
	# Distinguish input shapes
	
	hypo = None
	area = None
	
	for object in hypo_and_area:
		
		if str(object)[1:45] == "NETGENPlugin._objref_NETGENPlugin_Hypothesis": hypo = object
		if str(object)[1:25] == "GEOM._objref_GEOM_Object": area = object
		
	
	if None in [hypo, area]:
		
		print "[X] The input objects are incorrect or the Mesh module was not yet loaded."
		
		return
		
	
	hypothesis_type = hypo.GetName()
	
	if str(hypothesis_type) != "NETGEN_Parameters_2D" and str(hypothesis_type) != "NETGEN_Parameters":
		
		print "[X] The selected hypothesis is not a Netgen 1D - 2D or Netgen 1D - 2D - 3D hypothesis."
		
		return
		
	
	#-
	
	else:# All checks done
		
		# Get the area bounding box
		
		[x_min, x_max, y_min, y_max, z_min, z_max] = geompy.BoundingBox(area)
		
		x_margin = (x_max - x_min) / 10000
		
		x_min += x_margin
		x_max -= x_margin
		
		#-
		
		# Create edges
		
		void_compound = geompy.MakeCompound([])
		
		nb_edges_x = int((x_max - x_min) / size * ratio)
		nb_edges_y = int((y_max - y_min) / size * ratio)
		
		x_step = (x_max - x_min) / (float(nb_edges_x) - 1)
		y_step = (y_max - y_min) / (float(nb_edges_y) - 1)
		
		nb_edges = nb_edges_x * nb_edges_y
		
		print "[i]", nb_edges, " edges to create."
		
		if test == False:
			
			AddToStudy(void_compound, "RefinementEdges")
			
			edges = []
			
			x = x_min
			n = 1
			
			for i in range(nb_edges_x):
				y = y_min
				for j in range (nb_edges_y):
					
					start_vertex = geompy.MakeVertex(x, y, z_min)
					end_vertex = geompy.MakeVertex(x, y, z_max)
					
					edge = geompy.MakeEdge(start_vertex, end_vertex)
					
					edges.append(edge)
					
					n += 1
					
					y += y_step
				x += x_step
			
			edge_compound = geompy.MakeCompound(edges)
			
			common = geompy.MakeCommon(area, edge_compound)
			
			edges = geompy.SubShapeAll(common, geompy.ShapeType["EDGE"])
			
			n = 1
			
			for edge in edges:
				
				geompy.addToStudyInFather(void_compound, edge, "edge_" + str(n))
				
				hypo.SetLocalSizeOnShape(edge, size)
				
				n += 1
				
			
		
		#-
		
		if salome.sg.hasDesktop():
			
			salome.sg.updateObjBrowser(1)
			
		
		return void_compound
		
	

mnr = MakeNetgenRefinement

def SetNetgenRefinement( size, hypo_and_compound = [None], clear = False ):
	"""
	
	
Description:
	Applies a new cell size on a Netgen refinement created thanks to the MakeNetgenRefinement function.
	

Arguments:
	# size 
		Description:       The desired cell size in the refinement area. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# hypo_and_compound 
		Description:       The refinement compound containing refinement edges (eg. "RefinementEdges_1") and the Netgen hypothesis. 
		Type:              List of 1 Mesh hypothesis + 1 Compound 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	The new cell size should not be lower than the one used to create the Netgen refinement.
	

"""
	
	if isinstance(size, str): print "[X] The first argument (size) should be a float number."; return
	if isinstance(hypo_and_compound, list) == False: print "[X] The second argument (hypo_and_compound) should be an array."; return
	
	# Get the input shape(s)
	
	hypo_and_compound = GetGUISelection(hypo_and_compound)
	
	hypo_and_compound = GetObject(hypo_and_compound, "GEOM", silent = True) + GetObject(hypo_and_compound, "NETGENPlugin", silent = True)
	
	#-
	
	# Distinguish input shapes
	
	hypo = None
	refinement_edge_compound = None
	
	for object in hypo_and_compound:
		
		if str(object)[1:45] == "NETGENPlugin._objref_NETGENPlugin_Hypothesis": hypo = object
		if str(object)[1:25] == "GEOM._objref_GEOM_Object": refinement_edge_compound = object
		
	
	if None in [hypo, refinement_edge_compound]:
		
		print "[X] The input objects are incorrect or the Mesh module was not yet loaded."
		
		return
		
	
	hypothesis_type = hypo.GetName()
	
	if str(hypothesis_type) != "NETGEN_Parameters_2D" and str(hypothesis_type) != "NETGEN_Parameters":
		
		print "[X] The selected hypothesis is not a Netgen 1D - 2D or Netgen 1D - 2D - 3D hypothesis."
		
		return
		
	
	#-
	
	else:# All checks done
		
		# Get the refinement edge compound ID
		
		refinement_edge_compound_id = refinement_edge_compound.GetStudyEntry()
		
		split_refinement_edge_compound_id = refinement_edge_compound_id.split(":")
		
		#-
		
		# Get the study object IDs
		
		study_object_ids = ListComponentShapes("GEOM", output = "ID")
		
		#-
		
		# Get the refinement edges
		
		refinement_edges = []
		
		for study_object_id in study_object_ids:
			
			split_study_object_id = study_object_id.split(":")
			
			if len(split_study_object_id) >= 4:
				
				if split_study_object_id[3] == split_refinement_edge_compound_id[3] and len(split_study_object_id) > 4:
					
					refinement_edge = salome.myStudy.FindObjectID(study_object_id).GetObject()
					
					refinement_edges.append(refinement_edge)
					
					
			
		
		#-
		
		# Clear the netgen hypo
		
		if clear == True:
			
			try:
				
				local_sizes = hypo.GetLocalSizeEntries()
				for local_size in local_sizes: hypo.UnsetLocalSizeOnEntry(local_size)
				
			
			except: pass
			
		
		#-
		
		# Set the new refinement size
		
		for refinement_edge in refinement_edges:
			
			hypo.SetLocalSizeOnShape(refinement_edge, size)
			
		
		#-
		
	

snr = SetNetgenRefinement

def ClearNetgenRefinement( hypo = None ):
	"""
	
	
Description:
	Cancels all Netgen refinements.
	

Arguments:
	# hypo 
		Description:       The Netgen hypothesis to clean. 
		Type:              Mesh hypothesis 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	-
	

"""
	
	# Get the input shape(s)
	
	hypo = GetGUISelection(hypo)
	
	hypo = GetObject(hypo, "NETGENPlugin")
	
	#-
	
	# Make this function recursive
	
	if isinstance(hypo, list):
		
		for sub_object in hypo:
			
			ClearNetgenRefinement(sub_object)
			
		
		return
	
	#-
	
	# Check the input shape existence
	
	if "error" in [hypo] or None in [hypo]: return
	
	#-
	
	# Check the input shape characteritics
	
	if str(hypo)[1:45] != "NETGENPlugin._objref_NETGENPlugin_Hypothesis":
		
		print "[X] The input object is incorrect or the Mesh module was not yet loaded."
		
		return
		
	
	hypothesis_type = hypo.GetName()
	
	if str(hypothesis_type) != "NETGEN_Parameters_2D" and str(hypothesis_type) != "NETGEN_Parameters":
		
		print "[X] The selected hypothesis is not a Netgen 1D - 2D or Netgen 1D - 2D - 3D hypothesis."
		
		return
		
	
	#-
	
	else:# All checks done
		
		try:
			
			local_sizes = hypo.GetLocalSizeEntries()
			for local_size in local_sizes: hypo.UnsetLocalSizeOnEntry(local_size)
			
		
		except: pass
		
	

cnr = ClearNetgenRefinement

def ProjectMeshGroupOnFace( group_and_face = [None] ):
	"""
	
	
Description:
	Moves nodes of a Mesh Group by projecting them on a Face defined in the Geometry module.
	

Arguments:
	# group_and_face 
		Description:       The group to project and the target face. 
		Type:              List of 1 Mesh Group+ 1 Face 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	-
	

"""
	
	# Get the input shape(s)
	
	group_and_face = GetGUISelection(group_and_face)
	
	group_and_face = GetObject(group_and_face, "GEOM", silent = True) + GetObject(group_and_face, "SMESH", silent = True)
	
	#-
	
	# Distinguish input shapes
	
	group = None
	face = None
	
	for object in group_and_face:
		
		if "SMESH._objref_SMESH_Group" in str(object):
			
			group = object
			
		
		if "GEOM._objref_GEOM_Object" in str(object):
			
			nb_faces = int(geompy.WhatIs(object).split("\n")[3].split(": ")[1])
			
			if nb_faces == 1:
				
				face = object
				
			
		
	
	if None in [group, face]:
		
		print "[X] A node group and a face should be selected."
		
		return
		
	
	#-
	
	else:# All checks done
		
		# Get the group mesh
		
		group_mesh = group.GetMesh()
		
		group_mesh = smesh.Mesh(group_mesh)
		
		#-
		
		# Get the node Ids
		
		group_nodes_ids = group.GetNodeIDs()
		
		#-
		
		# Project the nodes
		
		for group_node_id in group_nodes_ids:
			
			[x, y, z] = group_mesh.GetNodeXYZ(group_node_id)
			
			vertex = geompy.MakeVertex(x, y, z)
			
			projected_vertex = geompy.MakeProjection(vertex, face)
			
			[new_x, new_y, new_z] = geompy.PointCoordinates(projected_vertex)
			
			group_mesh.MoveNode(group_node_id, new_x, new_y, new_z)
			
		
		#-
	

pmgof = ProjectMeshGroupOnFace

def MakeVertexesFromMeshGroup( group = None, add = True ):
	"""
	
	
Description:
	Creates a compound of vertexes from a mesh group.
	

Arguments:
	# group 
		Description:       The group from wich to create vertexes. 
		Type:              Mesh Group 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# add 
		Description:       See here. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Compound of Vertexes 
	Number:         1 
	Name:           "VertexesFromMeshGroup"  

Conditions of use:
	-
	

"""
	
	# Get the input shape(s)
	
	group = GetGUISelection(group)
	
	group = GetObject(group, "SMESH")
	
	#-
	
	# Make this function recursive
	
	if isinstance(group, list):
		
		return_list = []
		
		for sub_object in group:
			
			return_list.append(MakeVertexesFromMeshGroup(sub_object, add))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [group] or None in [group]: return
	
	#-
	
	else:
		
		# Get the group mesh
		
		group_mesh = group.GetMesh()
		
		#-
		
		# Get the node Ids
		
		try:
			group_nodes_ids = group.GetNodeIDs()
		except:
			group_nodes_ids = group.GetNodesId()
		
		#-
		
		# Create the vertexes
		
		vertexes = []
		
		for group_node_id in group_nodes_ids:
			
			[x, y, z] = group_mesh.GetNodeXYZ(group_node_id)
			
			vertex = geompy.MakeVertex(x, y, z)
			
			vertexes.append(vertex)
			
		
		#-
		
		# Put the vertexes in a compound
		
		vertex_compound = geompy.MakeCompound(vertexes)
		
		#-
		
		# Add and return the resulting shape(s)
		
		if add == True:
			
			AddToStudy(vertex_compound, "VertexesFromMeshGroup")
			
		
		return vertex_compound
		
		#-
		
	

mvfmg = MakeVertexesFromMeshGroup

def RotateFlapGenerateAndExportMeshInAmshFormat( angles, group_file = "cfdmsh_grps", mesh_file = "cfdmsh_msh", domain = "domain", fixed_edges = "fixed_edges", rotating_face = "rotating_face", rotating_edges = "rotating_edges", flap_axis = "flap_axis", keep_mesh = True, help = False ):
	"""
	
	
Description:
	Rotates a flap, generates a mesh and exports it into an .amsh file readable with Edge 5.0.0.
	

Arguments:
	# angles 
		Description:       The list of flap angles to compute 
		Type:              List of Floats 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# group_file 
		Description:       The name of the group file to import in the final partitions. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "cfdmsh_grps"  

	# mesh_file 
		Description:       The name of the mesh file to import in the meshes. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "cfdmsh_msh"  

	# domain 
		Description:       The face describing the domain before cutting the flap face. 
		Type:              Face 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     "domain"  

	# fixed_edges 
		Description:       The compound of edges which won't move with the flap. 
		Type:              Compound of Edges 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     "fixed_edges"  

	# rotating_face 
		Description:       The face describing the flap. 
		Type:              Face 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     "rotating_face"  

	# rotating_edges 
		Description:       The compound of edges which move with the flap. 
		Type:              Compound of Edges 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     "rotating_edges"  

	# flap_axis 
		Description:       The axis of the flap rotation. 
		Type:              Edge 
		GUI selection:     - 
		Selection by name: yes 
		Recursive:         - 
		Default value:     "flap_axis"  

	# keep_mesh 
		Description:       If equals True, meshes are not cleared after each mesh export. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     True  

	# help 
		Description:       This argument is passed to the ExportAmshFile function. 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -   

Conditions of use:
	To use this function, the group file and mesh file have to be previously generated manually and the hypotheses to be used in the mesh have to be present in the study.
	

"""
	
	pi = 3.141592654
	
	# Get the input shape(s)
	
	[domain, fixed_edges, rotating_face, rotating_edges, flap_axis] = GetObject([domain, fixed_edges, rotating_face, rotating_edges, flap_axis], "GEOM")
	
	#-
	
	# Check the input shape existence
	
	if "error" in [domain, fixed_edges, rotating_face, rotating_edges, flap_axis]:
		
		return
		
	
	#-
	
	else:
		
		for angle in angles:# For each rotation angle...
			
			# Convert angle from degrees to radians
			
			angle_in_radians = angle * pi / 180
			
			#-
			
			# Rotate the flap
			
			rotated_flap_face = geompy.MakeRotation(rotating_face, flap_axis, angle_in_radians)
			
			rotated_flap_edges = geompy.MakeRotation(rotating_edges, flap_axis, angle_in_radians)
			
			#-
			
			# Cut and partition the domain
			
			cut_domain = geompy.MakeCut(domain, rotated_flap_face)
			
			partition = geompy.MakePartition([cut_domain], [rotated_flap_edges, fixed_edges], Limit = geompy.ShapeType["FACE"])
			
			#-
			
			# Import the geometrical groups
			
			partition_name = "Partition_" + str(angle) + "deg"
			
			geompy.addToStudy(partition, partition_name)
			
			ImportGeometricalGroups(partition_name, group_file)
			
			#-
			
			# Create the mesh
			
			mesh_name = "Mesh_" + str(angle) + "deg"
			
			mesh = smesh.Mesh(partition, mesh_name)
			
			#-
			
			# Import the mesh configuration
			
			ImportMeshConfiguration(mesh, mesh_file)
			
			#-
			
			# Compute the mesh
			
			mesh.Compute()
			
			#-
			
			# Export the mesh
			
			ExportAmshFile(mesh, mesh_name, help = help)
			
			#-
			
			if keep_mesh == False:
				
				mesh.Clear()
				
			
		
	

rfgaemiaf = RotateFlapGenerateAndExportMeshInAmshFormat

def ViscousLayerScaleFactor( total_thick, wall_thick, ratio = 1.2 ):
	"""
	
	
Description:
	Calculates the parameters to use in a "Nb. Segment" hypothesis from common viscous layers parameters (total thickness, wall thickness and a ratio).
	

Arguments:
	# total_thick 
		Description:       The viscous layer total thickness. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# wall_thick 
		Description:       The desired thickness of the layer touching the wall. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     -  

	# ratio 
		Description:       The desired ratio between each layer n and n+1. 
		Type:              Float 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     1.2  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           Float 
	Number:         2 
	Name:           - 

Conditions of use:
	-
	

"""
	
	# Compute the thicknesses of an infinite number of layers
	
	layer_thicknesses = [wall_thick]
	
	for i in range(1000):
		
		layer_thicknesses.append(layer_thicknesses[i] * ratio)
		
	
	#-
	
	# Compute the total thicknesses for an infinite number of layers
	
	total_thicknesses = [wall_thick]
	
	for i in range(len(layer_thicknesses) - 1):
		
		total_thicknesses.append(total_thicknesses[i] + layer_thicknesses[i + 1])
		
	
	#-
	
	# Get the number of layers
	
	for i in range(len(total_thicknesses)):
		
		if total_thicknesses[i] > total_thick:
			
			nb_layers = i + 1
			
			break
			
		
	
	#-
	
	# compute the scale betwenn first and last layer
	
	scale = layer_thicknesses[nb_layers - 1] / wall_thick
	
	#-
	
	# Print the number of layers and scale
	
	print "Number of Segments = \t%i"%(nb_layers)
	
	print "Scale Factor = \t%.5f"%(scale)
	
	#-
	
	return [nb_layers, scale]
	

vlsf = ViscousLayerScaleFactor

def ExportMeshConfiguration( mesh = None, file = "cfdmsh_msh" ):
	"""
	
	
Description:
	Exports into a file the name of the algorithms, hypotheses and groups associated to a mesh and its sub-meshes.
	

Arguments:
	# mesh 
		Description:       The source mesh. 
		Type:              Mesh 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# file 
		Description:       The name of the file to write. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "cfdmsh_msh"  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	All the hypotheses and algorithms used by the mesh and its sub-meshes must have a different name. Also, the names of all mesh groups have to be the same as the names of their associated geometrical groups.
	

"""
	
	# Get the input shape(s)
	
	mesh = GetGUISelection(mesh, uniq = True)
	
	mesh = GetObject(mesh, "SMESH")
	
	#-
	
	# Check the input shape existence
	
	if "error" in [mesh] or None in [mesh]: return
	
	#-
	
	else:# All checks done
		
		if "SMESH_Mesh instance" in str(mesh) or "meshProxy instance" in str(mesh) or "Mesh object" in str(mesh):
			
			try:
				mesh = smesh.Mesh(mesh)
			except:
				pass
			
		
		else:
			
			print "[X] The input object is not a mesh or the Mesh module was not yet loaded."; return
			
		
		#-
		
		# Open the hypothesis file
		
		hypothesis_file = open(file, "w")
		
		#-
		
		# Get the mesh shape
		
		mesh_shape = mesh.GetShape()
		
		mesh_shape_name = mesh_shape.GetName()
		
		#-
		
		# Get the shape hypotheses
		
		shape_hypotheses = mesh.GetHypothesisList(mesh_shape)
		
		#-
		
		# Check if hypotheses are associated to the mesh shape
		
		nb_shape_hypotheses = len(shape_hypotheses)
		
		#-
		
		if nb_shape_hypotheses > 0:# If so...
			
			# Write the shape flag
			
			hypothesis_file.write("SHAPE:\n")
			
			#-
			
			for shape_hypothesis in shape_hypotheses:# For each shape hypothesis...
				
				# Get the hypothesis name
				
				shape_hypothesis_name = smeshBuilder.GetName(shape_hypothesis)
				
				#-
				
				# Write the hypothesis
				
				hypothesis_file.write("%s\n"%(shape_hypothesis_name))
				
				#-
				
			
		
		# Get the shape groups
		
		mesh_shape_groups = geompy.GetGroups(mesh_shape)
		
		#-
		
		for group in mesh_shape_groups:# For each group...
			
			# Get the group name
			
			group_name = group.GetName()
			
			#-
			
			# Get the hypothesis list
			
			group_hypotheses = mesh.GetHypothesisList(group)
			
			#-
			
			# Check if hypotheses are associated to the group
			
			nb_group_hypotheses = len(group_hypotheses)
			
			#-
			
			if nb_group_hypotheses > 0:# If so...
				
				# Write the group name
				
				hypothesis_file.write("SUBMESH:%s\n"%(group_name))
				
				#-
				
				for group_hypothesis in group_hypotheses:# For each hypothesis...
					
					# Get the hypothesis name
					
					group_hypothesis_name = smeshBuilder.GetName(group_hypothesis)
					
					#-
					
					# Write the hypothesis
					
					hypothesis_file.write("%s\n"%(group_hypothesis_name))
					
					#-
					
				
			
		
		# Get the mesh groups
		
		mesh_groups = mesh.GetGroups()
		
		#-
		
		# Check if there are mesh groups
		
		nb_mesh_groups = len(mesh_groups)
		
		#-
		
		if nb_mesh_groups > 0:# If so...
			
			# Write the group flag
			
			hypothesis_file.write("GROUPS:")
			
			#-
			
			for mesh_group in mesh_groups:# For each mesh group...
				
				# Get the mesh group name
				
				mesh_group_name = mesh_group.GetName()
				
				#-
				
				# Write the mesh group name
				
				hypothesis_file.write("%s\t"%(mesh_group_name))
				
				#-
				
			
		
		# Close hypothesis file
		
		hypothesis_file.close()
		
		#-
		
	

emc = ExportMeshConfiguration

def ImportMeshConfiguration( mesh = None, file = "cfdmsh_msh" ):
	"""
	
	
Description:
	Imports into a mesh algorithms, hypotheses and group names from a file created with the ExportMeshConfiguration function.
	

Arguments:
	# mesh 
		Description:       The target mesh. 
		Type:              Mesh 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         yes 
		Default value:     None  

	# file 
		Description:       Name of the file to read. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "cfdmsh_msh"  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	All the hypotheses and algorithms present in the file has to be also present in the study. Also, there must be, in the geometrical object associated to the target mesh, groups having the same name as the groups present in the file. 
	

"""
	
	# Get the input shape(s)
	
	mesh = GetGUISelection(mesh, uniq = True)
	
	mesh = GetObject(mesh, "SMESH")
	
	#-
	
	# Make this function recursive
	
	if isinstance(mesh, list):
		
		return_list = []
		
		for sub_object in mesh:
			
			return_list.append(ImportMeshConfiguration(sub_object, file))
			
		
		return return_list
		
	
	#-
	
	# Check the input shape existence
	
	if "error" in [mesh] or None in [mesh]: return
	
	#-
	
	else:# All checks done
		
		if "SMESH_Mesh instance" in str(mesh) or "meshProxy instance" in str(mesh) or "Mesh object" in str(mesh):
			
			try:
				mesh = smesh.Mesh(mesh)
			except:
				pass
			
		
		else:
			
			print "[X] The input object is not a mesh or the Mesh module was not yet loaded."; return
			
		
		# Get the mesh shape
		
		mesh_shape = mesh.GetShape()
		
		#-
		
		# Get the mesh groups
		
		shape_groups = geompy.GetGroups(mesh_shape)
		
		shape_group_names = [group.GetName() for group in shape_groups]
		
		nb_shape_groups = len(shape_groups)
		
		#-
		
		# Open the hypothesis file
		
		hypothesis_file = open(file, "r")
		
		#-
		
		# Read the file
		
		for line in hypothesis_file:# For each line in the hypothesis file...
			
			is_a_sub_mesh_line = (line.find("SUBMESH:") == 0)
			is_a_shape_line = (line.find("SHAPE:") == 0)
			is_a_group_line = (line.find("GROUPS:") == 0)
			
			geometry = None
			
			if is_a_shape_line == True:# If it is a "shape" line...
				
				group = None
				
			
			elif is_a_sub_mesh_line == True:# If it is a "submesh" line...
				
				# Get the group name
				
				group_name = line[8: - 1]
				
				#-
				
				# Get the group
				
				for i in range(nb_shape_groups):# For all groups in the shape...
					
					if group_name == shape_group_names[i]:# Compare their name with the one from the file...
						
						group = shape_groups[i]# If matched, extract the group in the shape group list
						
						break
						
					
				
				#-
				
				# Create a submesh associated to this group
				
				mesh.GetSubMesh(group, group_name)
				
				#
				
			
			elif is_a_group_line == True:
				
				# Get the group names
				
				group_names = line[7: - 1]
				
				group_names = group_names.split("\t")
				
				#-
				
				for group_name in group_names:# For each group name...
					
					# Get the shape group
					
					shape_group = None
					for i in range(nb_shape_groups):# For all groups in the shape...
						
						if group_name == shape_group_names[i]:# Compare their name with the one from the file...
							
							shape_group = shape_groups[i]# If matched, extract the group in the shape group list
							
							break
							
						
					
					#-
					
					# Create the mesh group
					
					mesh_group = mesh.GroupOnGeom(shape_group)
					
					#-
					
				
				#-
				
			
			else:# If it is a hypothesis line...
				
				# Get the hypothesis name
				
				hypothesis_name = line[:-1]
				
				#-
				
				# Get the hypothesis
				
				try:# Look in the hypotheses...
					
					hypothesis = salome.myStudy.FindObjectByPath("/Mesh/Hypotheses/%s"%(hypothesis_name)).GetObject()
					
				
				except AttributeError:# Else, in the algorithms...
					
					hypothesis = salome.myStudy.FindObjectByPath("/Mesh/Algorithms/%s"%(hypothesis_name)).GetObject()
					
				
				#-
				
				# Add the hypothesis to the mesh
				
				mesh.AddHypothesis(hypothesis, group)
				
				#-
				
			
		
		#-
		
		# Update the study tree
		
		salome.sg.updateObjBrowser(1)
		
		#-
		
		# Close hypothesis file
		
		hypothesis_file.close()
		
		#-
		
	

imc = ImportMeshConfiguration

def ExportHypotheses( hypo = [None], file = "cfdmsh_hps" ):
	"""
	
	
Description:
	Exports hypotheses into a text file mesh.
	

Arguments:
	# hypo 
		Description:       The list of hypotheses to export. 
		Type:              Mesh 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     [None]  

	# file 
		Description:       The name of the file to write. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "cfdmsh_hps"  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	-
	

"""
	
	# Get the input shape(s)
	
	hypo = GetGUISelection(hypo)
	
	hypo = GetObject(hypo, "SMESH")
	
	#-
	
	# Check the input shape existence
	
	if "error" in hypo or None in hypo: return
	
	#-
	
	else:# All checks done
		
		# Open the hypothesis file
		
		hypothesis_file = open(file, "w")
		
		#-
		
		for hypothesis in hypo:
			
			# Get the hypothesis name
			
			hypothesis_name = smeshBuilder.GetName(hypothesis)
			
			#-
			
			# Get the hypothesis type
			
			hypothesis_type = hypothesis.GetName()
			
			#-
			
			# Add the hypothesis to the hypothesis file
			
			hypothesis_file.write("TYPE:\n%s\n"%(hypothesis_type))
			hypothesis_file.write("NAME:\n%s\n"%(hypothesis_name))
			
			#-
			
			# Add the hypothesis parameters to the hypothesis file
			
			if hypothesis_type == "SegmentLengthAroundVertex":
				
				hypothesis_file.write("LENGTH:\n%s\n"%(hypothesis.GetLength()))
				
			
			if hypothesis_type == "LocalLength":
				
				hypothesis_file.write("LENGTH:\n%s\n"%(hypothesis.GetLength()))
				hypothesis_file.write("PRECISION:\n%s\n"%(hypothesis.GetPrecision()))
				
			
			if hypothesis_type == "MaxLength":
				
				hypothesis_file.write("LENGTH:\n%s\n"%(hypothesis.GetLength()))
				hypothesis_file.write("PRESSTIMATEDLENGTH:\n%s\n"%(hypothesis.GetPreestimatedLength()))
				hypothesis_file.write("USEPRESSTIMATEDLENGTH:\n%s\n"%(hypothesis.GetUsePreestimatedLength()))
				
			
			if hypothesis_type == "Arithmetic1D":
				
				hypothesis_file.write("STARTLENGTH:\n%s\n"%(hypothesis.GetLength(1)))
				hypothesis_file.write("ENDLENGTH:\n%s\n"%(hypothesis.GetLength(0)))
				
			
			if hypothesis_type == "GeometricProgression":
				
				hypothesis_file.write("STARTLENGTH:\n%s\n"%(hypothesis.GetStartLength()))
				hypothesis_file.write("COMMONRATIO:\n%s\n"%(hypothesis.GetCommonRatio()))
				
			
			if hypothesis_type == "FixedPoints1D":
				
				hypothesis_file.write("NBSEGMENTS:\n%s\n"%(hypothesis.GetNbSegments()))
				hypothesis_file.write("POINTS:\n%s\n"%(hypothesis.GetPoints()))
				
			
			if hypothesis_type == "StartEndLength":
				
				hypothesis_file.write("STARTLENGTH:\n%s\n"%(hypothesis.GetLength(1)))
				hypothesis_file.write("ENDLENGTH:\n%s\n"%(hypothesis.GetLength(0)))
				
			
			if hypothesis_type == "NumberOfSegments":
				
				hypothesis_file.write("NUMBEROFSEGMENTS:\n%s\n"%(hypothesis.GetNumberOfSegments()))
				hypothesis_file.write("DISTRTYPE:\n%s\n"%(hypothesis.GetDistrType()))
				try: hypothesis_file.write("SCALEFACTOR:\n%s\n"%(hypothesis.GetScaleFactor()))
				except: pass
				try: hypothesis_file.write("TABLEFUNCTION:\n%s\n"%(hypothesis.GetTableFunction()))
				except: pass
				try: hypothesis_file.write("EXPRESSIONFUNCTION:\n%s\n"%(hypothesis.GetExpressionFunction()))
				except: pass
				hypothesis_file.write("CONVERSIONMODE:\n%s\n"%(hypothesis.ConversionMode()))
				
			
			if hypothesis_type == "Deflection1D":
				
				hypothesis_file.write("DEFLECTION:\n%s\n"%(hypothesis.GetDeflection()))
				
			
			if hypothesis_type == "Adaptive1D":
				
				hypothesis_file.write("MINSIZE:\n%s\n"%(hypothesis.GetMinSize()))
				hypothesis_file.write("MAXSIZE:\n%s\n"%(hypothesis.GetMaxSize()))
				hypothesis_file.write("DEFLECTION:\n%s\n"%(hypothesis.GetDeflection()))
				
			
			if hypothesis_type == "AutomaticLength":
				
				hypothesis_file.write("FINENESS:\n%s\n"%(hypothesis.GetFineness()))
				
			
			if hypothesis_type == "LengthFromEdges":
				
				pass
				
			
			if hypothesis_type == "MaxElementArea":
				
				hypothesis_file.write("MAXELEMENTAREA:\n%s\n"%(hypothesis.GetMaxElementArea()))
				
			
			if hypothesis_type == "QuadrangleParams":
				
				hypothesis_file.write("QUADTYPE:\n%s\n"%(hypothesis.GetQuadType()))
				
			
			if hypothesis_type == "NumberOfLayers2D":
				
				hypothesis_file.write("NUMBEROFLAYERS:\n%s\n"%(hypothesis.GetNumberOfLayers()))
				
			
			if hypothesis_type == "NETGEN_Parameters_2D_ONLY" or hypothesis_type == "NETGEN_Parameters_3D":
				
				hypothesis_file.write("MAXSIZE:\n%s\n"%(hypothesis.GetMaxSize()))
				hypothesis_file.write("MINSIZE:\n%s\n"%(hypothesis.GetMinSize()))
				hypothesis_file.write("FINENESS:\n%s\n"%(hypothesis.GetFineness()))
				hypothesis_file.write("GROWTHRATE:\n%s\n"%(hypothesis.GetGrowthRate()))
				hypothesis_file.write("USESURFACECURVATURE:\n%s\n"%(hypothesis.GetUseSurfaceCurvature()))
				hypothesis_file.write("QUADALLOWED:\n%s\n"%(hypothesis.GetQuadAllowed()))
				hypothesis_file.write("OPTIMIZE:\n%s\n"%(hypothesis.GetOptimize()))
				
			
			if hypothesis_type == "NETGEN_Parameters_2D" or hypothesis_type == "NETGEN_Parameters":# 3D
				
				hypothesis_file.write("FINENESS:\n%s\n"%(hypothesis.GetFineness()))
				hypothesis_file.write("GROWTHRATE:\n%s\n"%(hypothesis.GetGrowthRate()))
				hypothesis_file.write("MAXSIZE:\n%s\n"%(hypothesis.GetMaxSize()))
				hypothesis_file.write("MINSIZE:\n%s\n"%(hypothesis.GetMinSize()))
				hypothesis_file.write("SECONDORDER:\n%s\n"%(hypothesis.GetSecondOrder()))
				hypothesis_file.write("NBSEGPEREDGE:\n%s\n"%(hypothesis.GetNbSegPerEdge()))
				hypothesis_file.write("NBSEGPERRADIUS:\n%s\n"%(hypothesis.GetNbSegPerRadius()))
				hypothesis_file.write("USESURFACECURVATURE:\n%s\n"%(hypothesis.GetUseSurfaceCurvature()))
				hypothesis_file.write("QUADALLOWED:\n%s\n"%(hypothesis.GetQuadAllowed()))
				hypothesis_file.write("OPTIMIZE:\n%s\n"%(hypothesis.GetOptimize()))
				hypothesis_file.write("FUSEEDGES:\n%s\n"%(hypothesis.GetFuseEdges()))
				
			
			if hypothesis_type == "NETGEN_SimpleParameters_2D" or hypothesis_type == "NETGEN_SimpleParameters_3D":
				
				hypothesis_file.write("NUMBEROFSEGMENTS:\n%s\n"%(hypothesis.GetNumberOfSegments()))
				hypothesis_file.write("LOCALLENGTH:\n%s\n"%(hypothesis.GetLocalLength()))
				hypothesis_file.write("MAXELEMENTAREA:\n%s\n"%(hypothesis.GetMaxElementArea()))
				hypothesis_file.write("ALLOWQUADRANGLES:\n%s\n"%(hypothesis.GetAllowQuadrangles()))
				
			
			if hypothesis_type == "MG - CADSurf Parameters":
				
				hypothesis_file.write("PHYSICALMESH:\n%s\n"%(hypothesis.GetPhysicalMesh()))
				hypothesis_file.write("GEOMETRICMESH:\n%s\n"%(hypothesis.GetGeometricMesh()))
				hypothesis_file.write("ANGLEMESH:\n%s\n"%(hypothesis.GetAngleMesh()))
				hypothesis_file.write("CHORDALERROR:\n%s\n"%(hypothesis.GetChordalError()))
				hypothesis_file.write("PHYSIZE:\n%s\n"%(hypothesis.GetPhySize()))
				hypothesis_file.write("ISPHYSIZEREL:\n%s\n"%(hypothesis.IsPhySizeRel()))
				hypothesis_file.write("MINSIZE:\n%s\n"%(hypothesis.GetMinSize()))
				hypothesis_file.write("ISMINSIZEREL:\n%s\n"%(hypothesis.IsMinSizeRel()))
				hypothesis_file.write("MAXSIZE:\n%s\n"%(hypothesis.GetMaxSize()))
				hypothesis_file.write("ISMAXSIZEREL:\n%s\n"%(hypothesis.IsMaxSizeRel()))
				hypothesis_file.write("QUADRATICMESH:\n%s\n"%(hypothesis.GetQuadraticMesh()))
				hypothesis_file.write("GRADATION:\n%s\n"%(hypothesis.GetGradation()))
				hypothesis_file.write("ANISOTROPIC:\n%s\n"%(hypothesis.GetAnisotropic()))
				hypothesis_file.write("ANISOTROPICRATIO:\n%s\n"%(hypothesis.GetAnisotropicRatio()))
				hypothesis_file.write("REMOVETINYEDGES:\n%s\n"%(hypothesis.GetRemoveTinyEdges()))
				hypothesis_file.write("TINYEDGELENGTH:\n%s\n"%(hypothesis.GetTinyEdgeLength()))
				hypothesis_file.write("BADELEMENTREMOVAL:\n%s\n"%(hypothesis.GetBadElementRemoval()))
				hypothesis_file.write("BADELEMENTASPECTRATIO:\n%s\n"%(hypothesis.GetBadElementAspectRatio()))
				hypothesis_file.write("OPTIMIZEMESH:\n%s\n"%(hypothesis.GetOptimizeMesh()))
				hypothesis_file.write("QUADALLOWED:\n%s\n"%(hypothesis.GetQuadAllowed()))
				hypothesis_file.write("OPTIONVALUES:\n%s\n"%(hypothesis.GetOptionValues()))
				hypothesis_file.write("PRECADOPTIONVALUES:\n%s\n"%(hypothesis.GetPreCADOptionValues()))
				hypothesis_file.write("TOPOLOGY:\n%s\n"%(hypothesis.GetTopology()))# int
				hypothesis_file.write("PRECADMERGEEDGES:\n%s\n"%(hypothesis.GetPreCADMergeEdges()))
				hypothesis_file.write("PRECADPROCESS3DTOPOLOGY:\n%s\n"%(hypothesis.GetPreCADProcess3DTopology()))
				hypothesis_file.write("PRECADDISCARDINPUT:\n%s\n"%(hypothesis.GetPreCADDiscardInput()))
				hypothesis_file.write("VERBOSITY:\n%s\n"%(hypothesis.GetVerbosity()))
				hypothesis_file.write("GMFFILE:\n%s\n"%(hypothesis.GetGMFFile()))
				
			
			if hypothesis_type == "ViscousLayers2D":
				
				hypothesis_file.write("NUMBERLAYERS:\n%s\n"%(hypothesis.GetNumberLayers()))
				hypothesis_file.write("STRETCHFACTOR:\n%s\n"%(hypothesis.GetStretchFactor()))
				hypothesis_file.write("TOTALTHICKNESS:\n%s\n"%(hypothesis.GetTotalThickness()))
				
			
			if hypothesis_type == "NumberOfLayers":# 3D
				
				hypothesis_file.write("NUMBEROFLAYERS:\n%s\n"%(hypothesis.GetNumberOfLayers()))
				
			
			if hypothesis_type == "MaxElementVolume":
				
				hypothesis_file.write("MAXELEMENTVOLUME:\n%s\n"%(hypothesis.GetMaxElementVolume()))
				
			
			if hypothesis_type == "NETGEN_SimpleParameters_3D":
				
				hypothesis_file.write("MAXELEMENTVOLUME:\n%s\n"%(hypothesis.GetMaxElementVolume()))
				
			
			if hypothesis_type == "MG - Tetra Parallel Parameters":
				
				hypothesis_file.write("MEDNAME:\n%s\n"%(hypothesis.GetMEDName()))
				hypothesis_file.write("NBPART:\n%s\n"%(hypothesis.GetNbPart()))
				hypothesis_file.write("KEEPFILES:\n%s\n"%(hypothesis.GetKeepFiles()))
				hypothesis_file.write("BACKGROUND:\n%s\n"%(hypothesis.GetBackground()))
				hypothesis_file.write("MERGESUBDOMAINS:\n%s\n"%(hypothesis.GetToMergeSubdomains()))
				hypothesis_file.write("TAGSUBDOMAINS:\n%s\n"%(hypothesis.GetToTagSubdomains()))
				hypothesis_file.write("OUTPUTINTERFACES:\n%s\n"%(hypothesis.GetToOutputInterfaces()))
				hypothesis_file.write("DISCARDSUBDOMAINS:\n%s\n"%(hypothesis.GetToDiscardSubdomains()))
				
			
			if hypothesis_type == "MG - Hexa Parameters":
				
				hypothesis_file.write("MINSIZE:\n%s\n"%(hypothesis.GetMinSize()))
				hypothesis_file.write("MAXSIZE:\n%s\n"%(hypothesis.GetMaxSize()))
				hypothesis_file.write("HEXESMINLEVEL:\n%s\n"%(hypothesis.GetHexesMinLevel()))
				hypothesis_file.write("HEXESMAXLEVEL:\n%s\n"%(hypothesis.GetHexesMaxLevel()))
				hypothesis_file.write("HEXOTICIGNORERIDGES:\n%s\n"%(hypothesis.GetHexoticIgnoreRidges()))
				hypothesis_file.write("HEXOTICINVALIDELEMENTS:\n%s\n"%(hypothesis.GetHexoticInvalidElements()))
				hypothesis_file.write("HEXOTICSHARPANGLETHRESHOLD:\n%s\n"%(hypothesis.GetHexoticSharpAngleThreshold()))
				hypothesis_file.write("HEXOTICNBPROC:\n%s\n"%(hypothesis.GetHexoticNbProc()))
				hypothesis_file.write("HEXOTICWORKINGDIRECTORY:\n%s\n"%(hypothesis.GetHexoticWorkingDirectory()))
				hypothesis_file.write("HEXOTICMAXMEMORY:\n%s\n"%(hypothesis.GetHexoticMaxMemory()))
				hypothesis_file.write("HEXOTICVERBOSITY:\n%s\n"%(hypothesis.GetHexoticVerbosity()))
				hypothesis_file.write("HEXOTICSDMODE:\n%s\n"%(hypothesis.GetHexoticSdMode()))
				hypothesis_file.write("TEXTOPTIONS:\n%s\n"%(hypothesis.GetTextOptions()))
				hypothesis_file.write("NBLAYERS:\n%s\n"%(hypothesis.GetNbLayers()))
				hypothesis_file.write("FIRSTLAYERSIZE:\n%s\n"%(hypothesis.GetFirstLayerSize()))
				hypothesis_file.write("DIRECTION:\n%s\n"%(hypothesis.GetDirection()))
				hypothesis_file.write("GROWTH:\n%s\n"%(hypothesis.GetGrowth()))
				
			
			if hypothesis_type == "MG - Tetra Parameters":
				
				hypothesis_file.write("TOMESHHOLES:\n%s\n"%(hypothesis.GetToMeshHoles()))
				hypothesis_file.write("TOMAKEGROUPSOFDOMAINS:\n%s\n"%(hypothesis.GetToMakeGroupsOfDomains()))
				hypothesis_file.write("OPTIMIZATIONLEVEL:\n%s\n"%(hypothesis.GetOptimizationLevel()))
				hypothesis_file.write("INITIALMEMORY:\n%s\n"%(hypothesis.GetInitialMemory()))
				hypothesis_file.write("MAXIMUMMEMORY:\n%s\n"%(hypothesis.GetMaximumMemory()))
				hypothesis_file.write("WORKINGDIRECTORY:\n%s\n"%(hypothesis.GetWorkingDirectory()))
				hypothesis_file.write("VERBOSELEVEL:\n%s\n"%(hypothesis.GetVerboseLevel()))
				hypothesis_file.write("STANDARDOUTPUTLOG:\n%s\n"%(hypothesis.GetStandardOutputLog()))
				hypothesis_file.write("REMOVELOGONSUCCESS:\n%s\n"%(hypothesis.GetRemoveLogOnSuccess()))
				hypothesis_file.write("KEEPFILES:\n%s\n"%(hypothesis.GetKeepFiles()))
				hypothesis_file.write("TOCREATENEWNODES:\n%s\n"%(hypothesis.GetToCreateNewNodes()))
				hypothesis_file.write("TOUSEBOUNDARYRECOVERYVERSION:\n%s\n"%(hypothesis.GetToUseBoundaryRecoveryVersion()))
				hypothesis_file.write("TOREMOVECENTRALPOINT:\n%s\n"%(hypothesis.GetToRemoveCentralPoint()))
				hypothesis_file.write("FEMCORRECTION:\n%s\n"%(hypothesis.GetFEMCorrection()))
				hypothesis_file.write("GRADATION:\n%s\n"%(hypothesis.GetGradation()))
				hypothesis_file.write("TEXTOPTION:\n%s\n"%(hypothesis.GetTextOption()))
				
			
			if hypothesis_type == "HYBRID_Parameters":
				
				hypothesis_file.write("BOUNDARYLAYERSGROWTH:\n%s\n"%(hypothesis.GetBoundaryLayersGrowth()))
				hypothesis_file.write("HEIGHTFIRSTLAYER:\n%s\n"%(hypothesis.GetHeightFirstLayer()))
				hypothesis_file.write("NBOFBOUNDARYLAYERS:\n%s\n"%(hypothesis.GetNbOfBoundaryLayers()))
				hypothesis_file.write("BOUNDARYLAYERSPROGRESSION:\n%s\n"%(hypothesis.GetBoundaryLayersProgression()))
				hypothesis_file.write("COLLISIONMODE:\n%s\n"%(hypothesis.GetCollisionMode()))
				hypothesis_file.write("ELEMENTGENERATION:\n%s\n"%(hypothesis.GetElementGeneration()))
				hypothesis_file.write("ADDMULTINORMALS:\n%s\n"%(hypothesis.GetAddMultinormals()))
				hypothesis_file.write("MULTINORMALSANGLE:\n%s\n"%(hypothesis.GetMultinormalsAngle()))
				hypothesis_file.write("SMOOTHNORMALS:\n%s\n"%(hypothesis.GetSmoothNormals()))
				hypothesis_file.write("WORKINGDIRECTORY:\n%s\n"%(hypothesis.GetWorkingDirectory()))
				hypothesis_file.write("VERBOSELEVEL:\n%s\n"%(hypothesis.GetVerboseLevel()))
				hypothesis_file.write("STANDARDOUTPUTLOG:\n%s\n"%(hypothesis.GetStandardOutputLog()))
				hypothesis_file.write("REMOVELOGONSUCCESS:\n%s\n"%(hypothesis.GetRemoveLogOnSuccess()))
				hypothesis_file.write("KEEPFILES:\n%s\n"%(hypothesis.GetKeepFiles()))
				hypothesis_file.write("TEXTOPTION:\n%s\n"%(hypothesis.GetTextOption()))
				
			
			if hypothesis_type == "ViscousLayers":# 3D
				
				hypothesis_file.write("NUMBERLAYERS:\n%s\n"%(hypothesis.GetNumberLayers()))
				hypothesis_file.write("STRETCHFACTOR:\n%s\n"%(hypothesis.GetStretchFactor()))
				hypothesis_file.write("TOTALTHICKNESS:\n%s\n"%(hypothesis.GetTotalThickness()))
				hypothesis_file.write("METHOD:\n%s\n"%(hypothesis.GetMethod()))
				
			
			#-
			
		
		# Close hypothesis file
		
		hypothesis_file.close()
		
		#-
		
	

eh = ExportHypotheses

def ImportHypotheses( file = "cfdmsh_hps" ):
	"""
	
	
Description:
	Imports a hypotheses file created with the ExportHypotheses function.
	

Arguments:
	# file 
		Description:       The name of the file to read. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     "cfdmsh_hps"  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	-
	

"""
	
	if False: pass
	
	else:# All checks done
		
		# Open the hypothesis file
		
		hypothesis_file = open(file, "r")
		
		#-
		
		# Read the file
		
		is_a_hypothesis_type_line = False
		is_a_hypothesis_name_line = False
		is_a_hypothesis_parameter_line = False
		
		min_size = 0.0# This is for MG - CADSurf
		max_size = 0.0#
		phy_size = 0.0#
		
		for line in hypothesis_file:# For each line in the hypothesis file...
			
			line = line[:-1]# Delete ending "\n"
			
			if is_a_hypothesis_type_line == True:# If it is a "type" line...
				
				if "NETGEN" in line:
					
					hypothesis = smesh.CreateHypothesis(line, "NETGENEngine")
					
				elif "MG - CADSurf" in line:
					
					hypothesis = smesh.CreateHypothesis(line, "BLSURFEngine")
					
				elif "MG - Tetra Parallel" in line:
					
					hypothesis = smesh.CreateHypothesis(line, "GHS3DPRLEngine")
					
				elif "MG - Hexa Parameters" in line:
					
					hypothesis = smesh.CreateHypothesis(line, "HexoticEngine")
					
				elif "MG - Tetra Parameters" in line:
					
					hypothesis = smesh.CreateHypothesis(line, "GHS3DEngine")
					
				elif "HYBRID" in line:
					
					hypothesis = smesh.CreateHypothesis(line, "HYBRIDEngine")
					
				else:
					
					hypothesis = smesh.CreateHypothesis(line)
					
				
			
			elif is_a_hypothesis_name_line == True:# If it is a "name" line...
				
				smesh.SetName(hypothesis, line)
				
			
			elif is_a_hypothesis_parameter_line == True:# If it is a parameter line...
				
				if parameter_type == "LENGTH:": hypothesis.SetLength(float(line))
				if parameter_type == "PRECISION:": hypothesis.SetPrecision(float(line))
				if parameter_type == "PRESSTIMATEDLENGTH:": hypothesis.SetPreestimatedLength(float(line))
				if parameter_type == "USEPRESSTIMATEDLENGTH:": hypothesis.SetUsePreestimatedLength(line == "True")
				if parameter_type == "STARTLENGTH:": hypothesis.SetStartLength(float(line))
				if parameter_type == "ENDLENGTH:": hypothesis.SetEndLength(float(line))
				if parameter_type == "COMMONRATIO:": hypothesis.SetCommonRatio(float(line))
				if parameter_type == "NBSEGMENTS:": hypothesis.SetNbSegments(ast.literal_eval(line))
				if parameter_type == "POINTS:": hypothesis.SetPoints(ast.literal_eval(line))
				if parameter_type == "NUMBEROFSEGMENTS:":
					
					try: hypothesis.SetNumberOfSegments(int(line))
					except: pass
					
				if parameter_type == "DISTRTYPE:": hypothesis.SetDistrType(int(line))
				if parameter_type == "SCALEFACTOR:": hypothesis.SetScaleFactor(float(line))
				if parameter_type == "TABLEFUNCTION:": hypothesis.SetTableFunction(ast.literal_eval(line))
				if parameter_type == "EXPRESSIONFUNCTION:": hypothesis.SetExpressionFunction(str(line))
				if parameter_type == "CONVERSIONMODE:": hypothesis.SetConversionMode(int(line))
				if parameter_type == "DEFLECTION:": hypothesis.SetDeflection(float(line))
				if parameter_type == "MINSIZE:": 
					
					min_size = float(line)
					hypothesis.SetMinSize(min_size)
					
				if parameter_type == "MAXSIZE:":
					
					max_size = float(line)
					hypothesis.SetMaxSize(max_size)
					
				if parameter_type == "FINENESS:":
					
					try: hypothesis.SetFineness(float(line))
					except: hypothesis.SetFineness(int(line))
					
				if parameter_type == "GROWTHRATE:": hypothesis.SetGrowthRate(float(line))
				if parameter_type == "NBSEGPEREDGE:": hypothesis.SetNbSegPerEdge(float(line))
				if parameter_type == "NBSEGPERRADIUS:": hypothesis.SetNbSegPerRadius(float(line))
				if parameter_type == "USESURFACECURVATURE:": hypothesis.SetUseSurfaceCurvature(line == "True")
				if parameter_type == "QUADALLOWED:": hypothesis.SetQuadAllowed(line == "True")
				if parameter_type == "ALLOWQUADRANGLES:": hypothesis.SetAllowQuadrangles(line == "True")
				if parameter_type == "OPTIMIZE:": hypothesis.SetOptimize(line == "True")
				if parameter_type == "FUSEEDGES:": hypothesis.SetFuseEdges(line == "True")
				if parameter_type == "SECONDORDER:": hypothesis.SetSecondOrder(line == "True")
				if parameter_type == "MAXELEMENTAREA:": hypothesis.SetMaxElementArea(float(line))
				if parameter_type == "MAXELEMENTVOLUME:": hypothesis.SetMaxElementVolume(float(line))
				if parameter_type == "LOCALLENGTH:":
					
					try:hypothesis.SetLocalLength(float(line))
					except:pass
					
				if parameter_type == "QUADTYPE:":
					
					if line == "QUAD_STANDARD":hypothesis.SetQuadType(StdMeshersBuilder.QUAD_STANDARD)
					if line == "QUAD_TRIANGLE_PREF":hypothesis.SetQuadType(StdMeshersBuilder.QUAD_TRIANGLE_PREF)
					if line == "QUAD_QUADRANGLE_PREF":hypothesis.SetQuadType(StdMeshersBuilder.QUAD_QUADRANGLE_PREF)
					if line == "QUAD_QUADRANGLE_PREF_REVERSED":hypothesis.SetQuadType(StdMeshersBuilder.QUAD_QUADRANGLE_PREF_REVERSED)
					if line == "QUAD_REDUCED":hypothesis.SetQuadType(StdMeshersBuilder.QUAD_REDUCED)
					
				if parameter_type == "NUMBEROFLAYERS:": hypothesis.SetNumberOfLayers(int(line))
				if parameter_type == "NUMBERLAYERS:": hypothesis.SetNumberLayers(int(line))
				if parameter_type == "STRETCHFACTOR:": hypothesis.SetStretchFactor(float(line))
				if parameter_type == "TOTALTHICKNESS:": hypothesis.SetTotalThickness(float(line))
				if parameter_type == "METHOD:":
					
					if line == "SURF_OFFSET_SMOOTH": hypothesis.SetMethod(StdMeshersBuilder.SURF_OFFSET_SMOOTH)
					if line == "NODE_OFFSET": hypothesis.SetMethod(StdMeshersBuilder.NODE_OFFSET)
					if line == "FACE_OFFSET": hypothesis.SetMethod(StdMeshersBuilder.FACE_OFFSET)
					
				if parameter_type == "MEDNAME:": hypothesis.SetMEDName(str(line))
				if parameter_type == "NBPART:": hypothesis.SetNbPart(int(line))
				if parameter_type == "KEEPFILES:": hypothesis.SetKeepFiles(line == "True")
				if parameter_type == "BACKGROUND:": hypothesis.SetBackground(line == "True")
				if parameter_type == "MERGESUBDOMAINS:": hypothesis.SetToMergeSubdomains(line == "True")
				if parameter_type == "TAGSUBDOMAINS:": hypothesis.SetToTagSubdomains(line == "True")
				if parameter_type == "OUTPUTINTERFACES:": hypothesis.SetToOutputInterfaces(line == "True")
				if parameter_type == "DISCARDSUBDOMAINS:": hypothesis.SetToDiscardSubdomains(line == "True")
				if parameter_type == "HEXESMINLEVEL:": hypothesis.SetHexesMinLevel(int(line))
				if parameter_type == "HEXESMAXLEVEL:": hypothesis.SetHexesMaxLevel(int(line))
				if parameter_type == "HEXOTICIGNORERIDGES:": hypothesis.SetHexoticIgnoreRidges(line == "True")
				if parameter_type == "HEXOTICINVALIDELEMENTS:": hypothesis.SetHexoticInvalidElements(line == "True")
				if parameter_type == "HEXOTICSHARPANGLETHRESHOLD:": hypothesis.SetHexoticSharpAngleThreshold(float(line))
				if parameter_type == "HEXOTICNBPROC:": hypothesis.SetHexoticNbProc(int(line))
				if parameter_type == "HEXOTICWORKINGDIRECTORY:": hypothesis.SetHexoticWorkingDirectory(str(line))
				if parameter_type == "HEXOTICMAXMEMORY:": hypothesis.SetHexoticMaxMemory(int(line))
				if parameter_type == "HEXOTICVERBOSITY:": hypothesis.SetHexoticVerbosity(int(line))
				if parameter_type == "HEXOTICSDMODE:": hypothesis.SetHexoticSdMode(int(line))
				if parameter_type == "NBLAYERS:": hypothesis.SetNbLayers(int(line))
				if parameter_type == "FIRSTLAYERSIZE:": hypothesis.SetFirstLayerSize(float(line))
				if parameter_type == "DIRECTION:": hypothesis.SetDirection(line == "True")
				if parameter_type == "GROWTH:": hypothesis.SetGrowth(float(line))
				if parameter_type == "MAXSIZE:": hypothesis.SetMaxSize(float(line))
				if parameter_type == "MINSIZE:": hypothesis.SetMinSize(float(line))
				if parameter_type == "KEEPFILES:": hypothesis.SetKeepFiles(line == "True")
				if parameter_type == "TEXTOPTIONS:": hypothesis.SetTextOptions(str(line))
				if parameter_type == "TOMESHHOLES:": hypothesis.SetToMeshHoles(line == "True")
				if parameter_type == "TOMAKEGROUPSOFDOMAINS:": hypothesis.SetToMakeGroupsOfDomains(line == "True")
				if parameter_type == "OPTIMIZATIONLEVEL:": hypothesis.SetOptimizationLevel(int(line))
				if parameter_type == "INITIALMEMORY:": hypothesis.SetInitialMemory(int(line))
				if parameter_type == "MAXIMUMMEMORY:": hypothesis.SetMaximumMemory(int(line))
				if parameter_type == "WORKINGDIRECTORY:": hypothesis.SetWorkingDirectory(str(line))
				if parameter_type == "VERBOSELEVEL:": hypothesis.SetVerboseLevel(int(line))
				if parameter_type == "STANDARDOUTPUTLOG:": hypothesis.SetStandardOutputLog(line == "True")
				if parameter_type == "REMOVELOGONSUCCESS:": hypothesis.SetRemoveLogOnSuccess(line == "True")
				if parameter_type == "TOCREATENEWNODES:": hypothesis.SetToCreateNewNodes(line == "True")
				if parameter_type == "TOUSEBOUNDARYRECOVERYVERSION:": hypothesis.SetToUseBoundaryRecoveryVersion(line == "True")
				if parameter_type == "TOREMOVECENTRALPOINT:": hypothesis.SetToRemoveCentralPoint(line == "True")
				if parameter_type == "FEMCORRECTION:": hypothesis.SetFEMCorrection(line == "True")
				if parameter_type == "GRADATION:": hypothesis.SetGradation(float(line))
				if parameter_type == "TEXTOPTION:": hypothesis.SetTextOption(str(line))
				if parameter_type == "BOUNDARYLAYERSGROWTH:": hypothesis.SetBoundaryLayersGrowth(int(line))
				if parameter_type == "HEIGHTFIRSTLAYER:": hypothesis.SetHeightFirstLayer(float(line))
				if parameter_type == "NBOFBOUNDARYLAYERS:": hypothesis.SetNbOfBoundaryLayers(int(line))
				if parameter_type == "BOUNDARYLAYERSPROGRESSION:": hypothesis.SetBoundaryLayersProgression(float(line))
				if parameter_type == "COLLISIONMODE:": hypothesis.SetCollisionMode(int(line))
				if parameter_type == "ELEMENTGENERATION:": hypothesis.SetElementGeneration(int(line))
				if parameter_type == "ADDMULTINORMALS:": hypothesis.SetAddMultinormals(line == "True")
				if parameter_type == "MULTINORMALSANGLE:": hypothesis.SetMultinormalsAngle(float(line))
				if parameter_type == "SMOOTHNORMALS:": hypothesis.SetSmoothNormals(line == "True")
				if parameter_type == "PHYSICALMESH:": hypothesis.SetPhysicalMesh(int(line))
				if parameter_type == "GEOMETRICMESH:": hypothesis.SetGeometricMesh(int(line))
				if parameter_type == "ANGLEMESH:": hypothesis.SetAngleMesh(float(line))
				if parameter_type == "CHORDALERROR:": hypothesis.SetChordalError(float(line))
				if parameter_type == "PHYSIZE:":
					
					phy_size = float(line)
					hypothesis.SetPhySize(phy_size)
					
				if parameter_type == "ISPHYSIZEREL:":
					
					if line == "True": hypothesis.SetPhySizeRel(phy_size)
					
				if parameter_type == "ISMINSIZEREL:":
					
					if line == "True": hypothesis.SetMinSizeRel(min_size)
					
				if parameter_type == "ISMAXSIZEREL:":
					
					if line == "True": hypothesis.SetMaxSizeRel(max_size)
					
				if parameter_type == "QUADRATICMESH:": hypothesis.SetQuadraticMesh(line == "True")
				if parameter_type == "ANISOTROPIC:": hypothesis.SetAnisotropic(line == "True")
				if parameter_type == "ANISOTROPICRATIO:": hypothesis.SetAnisotropicRatio(float(line))
				if parameter_type == "REMOVETINYEDGES:": hypothesis.SetRemoveTinyEdges(line == "True")
				if parameter_type == "TINYEDGELENGTH:": hypothesis.SetTinyEdgeLength(float(line))
				if parameter_type == "BADELEMENTREMOVAL:": hypothesis.SetBadElementRemoval(line == "True")
				if parameter_type == "BADELEMENTASPECTRATIO:": hypothesis.SetBadElementAspectRatio(float(line))
				if parameter_type == "OPTIMIZEMESH:": hypothesis.SetOptimizeMesh(line == "True")
				if parameter_type == "OPTIONVALUES:": hypothesis.SetOptionValues(ast.literal_eval(line))
				if parameter_type == "PRECADOPTIONVALUES:": hypothesis.SetPreCADOptionValues(ast.literal_eval(line))
				if parameter_type == "TOPOLOGY:": hypothesis.SetTopology(int(line))# int
				if parameter_type == "PRECADMERGEEDGES:": hypothesis.SetPreCADMergeEdges(line == "True")
				if parameter_type == "PRECADPROCESS3DTOPOLOGY:": hypothesis.SetPreCADProcess3DTopology(line == "True")
				if parameter_type == "PRECADDISCARDINPUT:": hypothesis.SetPreCADDiscardInput(line == "True")
				if parameter_type == "VERBOSITY:": hypothesis.SetVerbosity(int(line))
				if parameter_type == "GMFFILE:": hypothesis.SetGMFFile(str(line))
				
			
			is_a_hypothesis_type_line = False
			is_a_hypothesis_name_line = False
			is_a_hypothesis_parameter_line = False
			
			if line.find("TYPE:") == 0:
				
				is_a_hypothesis_type_line = True
				
			
			elif line.find("NAME:") == 0:
				
				is_a_hypothesis_name_line = True
				
			
			elif line in [\
				"LENGTH:", \
				"PRECISION:", \
				"PRESSTIMATEDLENGTH:", \
				"USEPRESSTIMATEDLENGTH:", \
				"STARTLENGTH:", \
				"ENDLENGTH:", \
				"COMMONRATIO:", \
				"NBSEGMENTS:", \
				"POINTS:", \
				"NUMBEROFSEGMENTS:", \
				"DISTRTYPE:", \
				"SCALEFACTOR:", \
				"TABLEFUNCTION:", \
				"EXPRESSIONFUNCTION:", \
				"CONVERSIONMODE:", \
				"DEFLECTION:", \
				"MINSIZE:", \
				"MAXSIZE:", \
				"FINENESS:", \
				"GROWTHRATE:", \
				"NBSEGPEREDGE:", \
				"NBSEGPERRADIUS:", \
				"USESURFACECURVATURE:", \
				"QUADALLOWED:", \
				"OPTIMIZE:", \
				"FUSEEDGES:", \
				"ALLOWQUADRANGLES:", \
				"SECONDORDER:", \
				"MAXELEMENTAREA:", \
				"MAXELEMENTVOLUME:", \
				"LOCALLENGTH:", \
				"QUADTYPE:", \
				"MAXELEMENTAREA:", \
				"NUMBEROFLAYERS:", \
				"NUMBERLAYERS:", \
				"STRETCHFACTOR:", \
				"TOTALTHICKNESS:", \
				"METHOD:", \
				"MEDNAME:", \
				"NBPART:", \
				"KEEPFILES:", \
				"BACKGROUND:", \
				"MERGESUBDOMAINS:", \
				"TAGSUBDOMAINS:", \
				"OUTPUTINTERFACES:", \
				"DISCARDSUBDOMAINS:", \
				"HEXESMINLEVEL:", \
				"HEXESMAXLEVEL:", \
				"HEXOTICIGNORERIDGES:", \
				"HEXOTICINVALIDELEMENTS:", \
				"HEXOTICMAXMEMORY:", \
				"HEXOTICNBPROC:", \
				"HEXOTICSDMODE:", \
				"NBLAYERS:", \
				"FIRSTLAYERSIZE:", \
				"DIRECTION:", \
				"GROWTH:", \
				"HEXOTICSHARPANGLETHRESHOLD:", \
				"HEXOTICVERBOSITY:", \
				"HEXOTICWORKINGDIRECTORY:", \
				"MAXSIZE:", \
				"MINSIZE:", \
				"TEXTOPTIONS:", \
				"TOMESHHOLES:", \
				"TOMAKEGROUPSOFDOMAINS:", \
				"OPTIMIZATIONLEVEL:", \
				"INITIALMEMORY:", \
				"MAXIMUMMEMORY:", \
				"WORKINGDIRECTORY:", \
				"VERBOSELEVEL:", \
				"STANDARDOUTPUTLOG:", \
				"REMOVELOGONSUCCESS:", \
				"TOCREATENEWNODES:", \
				"TOUSEBOUNDARYRECOVERYVERSION:", \
				"TOREMOVECENTRALPOINT:", \
				"FEMCORRECTION:", \
				"GRADATION:", \
				"TEXTOPTION:", \
				"BOUNDARYLAYERSGROWTH:", \
				"HEIGHTFIRSTLAYER:", \
				"NBOFBOUNDARYLAYERS:", \
				"BOUNDARYLAYERSPROGRESSION:", \
				"COLLISIONMODE:", \
				"ELEMENTGENERATION:", \
				"ADDMULTINORMALS:", \
				"MULTINORMALSANGLE:", \
				"SMOOTHNORMALS:", \
				"PHYSICALMESH:", \
				"GEOMETRICMESH:", \
				"ANGLEMESH:", \
				"CHORDALERROR:", \
				"PHYSIZE:", \
				"ISPHYSIZEREL:", \
				"ISMINSIZEREL:", \
				"ISMAXSIZEREL:", \
				"QUADRATICMESH:", \
				"ANISOTROPIC:", \
				"ANISOTROPICRATIO:", \
				"REMOVETINYEDGES:", \
				"TINYEDGELENGTH:", \
				"BADELEMENTREMOVAL:", \
				"BADELEMENTASPECTRATIO:", \
				"OPTIMIZEMESH:", \
				"OPTIONVALUES:", \
				"PRECADOPTIONVALUES:", \
				"TOPOLOGY:", \
				"PRECADMERGEEDGES:", \
				"PRECADPROCESS3DTOPOLOGY:", \
				"PRECADDISCARDINPUT:", \
				"VERBOSITY:", \
				"GMFFILE:" \
				]:
				
				is_a_hypothesis_parameter_line = True
				
				parameter_type = line
				
			
		
		#-
		
		# Update the study tree
		
		salome.sg.updateObjBrowser(1)
		
		#-
		
		# Close hypothesis file
		
		hypothesis_file.close()
		
		#-
		
	

ih = ImportHypotheses

def ExportAmshFile( mesh = None, file = None, only = [None], ignore = [None], help = False ):
	"""
	
	
Description:
	Exports a mesh into an .amsh file readable by the CFD solver Edge 5.0.0.
	

Arguments:
	# mesh 
		Description:       The mesh to export. 
		Type:              Mesh 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# file 
		Description:       The name without extension of the amsh file to write. If equals None, the name of the mesh in the study tree is taken. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     None  

	# only 
		Description:       The list of names of groups to export, excluding the others. 
		Type:              List of Strings 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     [None]  

	# ignore 
		Description:       The list of names of groups to ignore. 
		Type:              List of Strings 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     [None]  

	# help 
		Description:       Activates the generation of a help file giving relation between Edge and Salome node IDs (slows down the mesh export). 
		Type:              Boolean 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     False  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	The mesh has to be computed and to contain groups describing the desired boundary conditions (inlet, outlet, wall, farfield, etc.).
	
	Warning: In the case the mesh is the result of a mesh fusion, the nodes and then the elements of the meshes to fuse have to be reordered before the fusion, else Edge can detect a Max dev. of accum. surface vector superior to its allowed tolerance during the preprocessor command execution.  

"""
	
	# Get the input shape(s)
	
	mesh = GetGUISelection(mesh, uniq = True)
	
	mesh = GetObject(mesh, "SMESH")
	
	#-
	
	# Check the input shape existence
	
	if "error" in [mesh] or None in [mesh]: return
	
	#-
	
	else:# All checks done
		
		def WriteInColumns(file, table, nb_columns, nb_identation_spaces, nb_spaces = 6):
			
			n = 0
			
			for element in table:
				
				if n%nb_columns == 0:
					
					for s in range(nb_identation_spaces):
						
						file.write(" ")
						
					
				
				else:
					
					for s in range(nb_spaces):
						
						file.write(" ")
						
					
				
				if type(element) == type("string"):
					
					file.write("%s"%(element))
					
				
				elif type(element) == type(1.0):
					
					file.write("%.16f"%(element))
					
				
				elif type(element) == type(1):
					
					file.write("%i"%(element))
					
				
				if (n + 1)%nb_columns == 0 or n == len(table) - 1:
					
					file.write("\n")
					
				
				n += 1
			
		
		def powerOfTen(figure):
			
			figure *= 1.0
			
			n = 0
			
			if figure != 0:
				
				if abs(figure) < 1:
					
					while abs(figure) < 1:
						
						figure *= 10
						
						n -= 1
						
					
				
				if abs(figure) >= 10:
					
					while abs(figure) >= 10:
						
						figure /= 10
						
						n += 1
						
					
				
			
			return figure, n
			
		
		if "SMESH_Mesh instance" in str(mesh) or "meshProxy instance" in str(mesh) or "Mesh object" in str(mesh):
			
			try:
				mesh = smesh.Mesh(mesh)
			except:
				pass
			
		
		else:
			
			print "[X] The input object is not a mesh or the Mesh module was not yet loaded."; return
			
		
		# Get the mesh name
		
		mesh_name = mesh.GetName()
		
		#-
		
		# Renumber elements and nodes
		
		mesh.RenumberNodes()
		mesh.RenumberElements()
		
		#-
		
		# Get nodes number and IDs
		
		nb_nodes_in_mesh = mesh.NbNodes()
		
		node_ids_in_mesh = mesh.GetNodesId()
		
		#-
		
		# Get edges IDs
		
		edge_ids_in_mesh = mesh.GetElementsByType(SMESH.EDGE)
		
		nb_edges_in_mesh = mesh.NbEdges()
		
		#-
		
		# Get faces IDs
		
		face_ids_in_mesh = mesh.GetElementsByType(SMESH.FACE)
		
		nb_faces_in_mesh = mesh.NbFaces()
		nb_triangles_in_mesh = mesh.NbTriangles()
		nb_quadrangles_in_mesh = mesh.NbQuadrangles()
		
		#-
		
		# Get volumes IDs
		
		nb_volumes_in_mesh = mesh.NbVolumes()
		
		nb_tetrahedrons_in_mesh = mesh.NbTetras()
		nb_pyramids_in_mesh = mesh.NbPyramids()
		nb_prisms_in_mesh = mesh.NbPrisms()
		nb_hexahedrons_in_mesh = mesh.NbHexas()
		
		volume_ids_in_mesh = mesh.GetElementsByType(SMESH.VOLUME)
		
		#-
		
		# Get mesh dimension
		
		if nb_volumes_in_mesh != 0:
			
			mesh_dimension = 3
			
			nb_elements_in_domain = nb_volumes_in_mesh
		
		else:
			
			mesh_dimension = 2
			
			nb_elements_in_domain = nb_faces_in_mesh
			
		
		#-
		
		# Get groups
		
		group_names = mesh.GetGroupNames()
		
		groups = mesh.GetGroups()
		
		#-
		
		# Sort groups
		
		sorted_groups = []
		
		if only != [None]:
			
			for group in groups:
				
				group_name = group.GetName()
				
				if group_name in only:
					
					sorted_groups.append(group)
					
				
			
			groups = sorted_groups
			
		
		sorted_groups = []
		
		if ignore != [None]:
			
			for group in groups:
				
				group_name = group.GetName()
				
				if group_name not in ignore:
					
					sorted_groups.append(group)
					
				
			
			groups = sorted_groups
			
		
		# Get the number of groups
		
		nb_groups = len(groups)
		
		# Get group types
		
		group_types = []
		
		for group in groups:
			
			group_type = str(group.GetType())
			
			group_types.append(group_type)
			
		
		#-
		
		# Open the amsh file
		
		date = time.asctime(time.localtime())
		
		if file == None:
			
			file = mesh_name
			
		
		amsh_file = open("%s.amsh"%(file), "w")
		
		amsh_file.write("unstr_grid_data N 0 0 2\n")
		amsh_file.write(" title L 1 1 0\n")
		amsh_file.write(" '%s exported from Salome on %s'\n"%(mesh_name, date))
		
		#-
		
		# Open the help file
		
		if help == True:
			
			mesh_file = open("%s.help"%(file), "w")
			
			mesh_file.write("%s\n"%(date))
			mesh_file.write("'%s'	'%s'\n"%(mesh_name, file))
			mesh_file.write("NODES	EDGES	TRIA	QUAD	TETRA	PYRA	PRISM	HEXA\n")
			mesh_file.write("%i	%i	%i	%i	%i	%i	%i	%i\n"%(nb_nodes_in_mesh, nb_edges_in_mesh, nb_triangles_in_mesh, nb_quadrangles_in_mesh, nb_tetrahedrons_in_mesh, nb_pyramids_in_mesh, nb_prisms_in_mesh, nb_hexahedrons_in_mesh))
			
			for n in range(nb_groups):
				
				mesh_file.write("'%s'	"%(mesh.GetGroupNames()[n]))
				
			
			mesh_file.write("\n")
			
			mesh_file.write("NODES\nID	X	Y	Z\n")
			
		
		#-
		
		# Get the region ffa dimension
		
		region_ffa_dimension = 2 + nb_groups
		
		if mesh_dimension == 2:
			
			if nb_triangles_in_mesh > 0:
				
				region_ffa_dimension += 1
				
			
			if nb_quadrangles_in_mesh > 0:
				
				region_ffa_dimension += 1
				
			
		
		elif mesh_dimension == 3:
			
			if nb_tetrahedrons_in_mesh > 0:
				
				region_ffa_dimension += 1
				
			
			if nb_pyramids_in_mesh > 0:
				
				region_ffa_dimension += 1
				
			
			if nb_prisms_in_mesh > 0:
				
				region_ffa_dimension += 1
				
			
			if nb_hexahedrons_in_mesh > 0:
				
				region_ffa_dimension += 1
				
			
		
		amsh_file.write(" region N 0 0 %i\n"%(region_ffa_dimension))
		amsh_file.write(" region_name L 1 1 0\n")
		amsh_file.write(" 'volume_elements'\n")
		amsh_file.write(" coordinates DF %i %i 0\n"%(mesh_dimension, nb_nodes_in_mesh))
		
		#-
		
		print "[i] Writing node coordinates... (%s nodes)"%(nb_nodes_in_mesh)
		
		# Get the node coordinates
		
		node_coordinates = []
		
		for n in range(mesh_dimension):
			
			node_coordinates.append([])
			
		
		#-
		
		# Write the node coordinates
		
		for node_id in node_ids_in_mesh:
			
			if help == True:
				
				mesh_file.write("%i	%f	%f	%f\n"%(node_id, mesh.GetNodeXYZ(node_id)[0], mesh.GetNodeXYZ(node_id)[1], mesh.GetNodeXYZ(node_id)[2]))
				
			
			for n in range(mesh_dimension):
				
				node_coordinate = mesh.GetNodeXYZ(node_id)[n]
				
				[node_float_coordinate, node_coordinate_power_of_ten] = powerOfTen(node_coordinate)
				
				node_coordinate = "%.16fE%i"%(node_float_coordinate, node_coordinate_power_of_ten)
				
				node_coordinates[n].append(node_coordinate)
				
			
		
		figures = []
		
		for n in range(mesh_dimension):
			
			figures += node_coordinates[n]
			
		
		WriteInColumns(amsh_file, figures, mesh_dimension, 18)
		
		#-
		
		# Get the group element definition
		
		print "[i] Writing definition of group elements... (%s groups)"%(nb_groups)
		
		if help == True:
			
			mesh_file.write("GROUPS\n")
			
		
		for group in groups:# For each group of the mesh
			
			group_name = group.GetName()
			
			element_ids_in_group = group.GetListOfID()
			
			triangle_ids_in_group = []
			quadrangle_ids_in_group = []
			edges_ids_in_group = []
			
			for element_id_in_group in element_ids_in_group:
				
				nb_nodes_in_element = mesh.GetElemNbNodes(element_id_in_group)
				
				if mesh_dimension == 3:
					
					if nb_nodes_in_element == 3:
						
						triangle_ids_in_group.append(element_id_in_group)
						
					
					if nb_nodes_in_element == 4:
						
						quadrangle_ids_in_group.append(element_id_in_group)
						
					
				
				elif mesh_dimension == 2:
					
					edges_ids_in_group.append(element_id_in_group)
					
				
			
			nb_types_in_group = 0
			
			types_in_groups = 0 #-1 = edges ; + 1 = triangles ; + 2 = quadrangles
			
			nb_triangles_in_group = len(triangle_ids_in_group)
			nb_quadrangles_in_group = len(quadrangle_ids_in_group)
			nb_edges_in_group = len(edges_ids_in_group)
			
			if nb_triangles_in_group > 0:
				
				types_in_groups += 1
				
				nb_types_in_group += 1
				
			
			if nb_quadrangles_in_group > 0:
				
				types_in_groups += 2
				
				nb_types_in_group += 1
				
			
			if nb_edges_in_group > 0:
				
				types_in_groups -= 1
				
				nb_types_in_group += 1
				
			
			amsh_file.write(" boundary N 0 0 %i\n"%(nb_types_in_group + 1))
			amsh_file.write(" boundary_name L 1 1 0\n")
			amsh_file.write(" '%s'\n"%(group_name))
			
			if help == True:
				
				mesh_file.write("'%s'\n"%(group_name))
				
			
			for n in range(nb_types_in_group):
				
				amsh_file.write(" belem_group N 0 0 2\n")
				amsh_file.write(" bound_elem_type L 1 1 0\n")
				
				if types_in_groups == -1: # edges
					
					if help == True:
						
						mesh_file.write("EDGES\n")
						
					element_ids_in_group = edges_ids_in_group
					nb_elements_in_group = nb_edges_in_group
					
					nb_nodes_in_elements = 2
					
					elements_type = "bar2"
					
				
				elif types_in_groups == 2: # quadrangles
					
					if help == True:
						
						mesh_file.write("QUAD\n")
						
					
					element_ids_in_group = quadrangle_ids_in_group
					nb_elements_in_group = nb_quadrangles_in_group
					
					nb_nodes_in_elements = 4
					
					elements_type = "quad4"
					
				
				elif types_in_groups == 1 or types_in_groups == 3: # triangles
					
					if help == True:
						
						mesh_file.write("TRIA\n")
						
					
					element_ids_in_group = triangle_ids_in_group
					nb_elements_in_group = nb_triangles_in_group
					
					nb_nodes_in_elements = 3
					
					types_in_groups -= 1
					
					elements_type = "tria3"
					
				
				if help == True:
					
					mesh_file.write("N	ID	NODE1	NODE2	...\n")
					
					N = 1
					
				
				amsh_file.write(" '%s'\n"%(elements_type))
				amsh_file.write(" bound_elem_nodes IF %i %i 0\n"%(nb_nodes_in_elements, nb_elements_in_group))
				
				node_ids = []
				
				for n in range(nb_nodes_in_elements):
					
					node_ids.append([])
					
				
				for element_id in element_ids_in_group:
					
					if help == True:
						
						mesh_file.write("%i	%i	"%(N, element_id))
						
						N += 1
						
					
					for n in range(nb_nodes_in_elements):
						
						if help == True:
							
							mesh_file.write("%i	"%(mesh.GetElemNodes(element_id)[n]))
							
						
						node_ids[n].append(mesh.GetElemNodes(element_id)[n])
						
					
					if help == True:
						
						mesh_file.write("\n")
						
					
				
				figures = []
				
				for n in range(nb_nodes_in_elements):
					
					figures += node_ids[n]
					
				
				WriteInColumns(amsh_file, figures, nb_nodes_in_elements, 30)
			
		
		#-
		
		# Write the domain element definitions
		
		print "[i] Writing definition of domain elements... (%s elements)"%(nb_elements_in_domain)
		
		if help == True:
			
			mesh_file.write("DOMAIN CELLS\n")
			
		
		triangle_ids_in_domain = []
		quadrangle_ids_in_domain = []
		tetrahedron_ids_in_domain = []
		pyramid_ids_in_domain = []
		prism_ids_in_domain = []
		hexahedron_ids_in_domain = []
		
		if mesh_dimension == 2:
			
			element_ids_in_domain = face_ids_in_mesh
			
		
		elif mesh_dimension == 3:
			
			element_ids_in_domain = volume_ids_in_mesh
			
		
		for element_id_in_domain in element_ids_in_domain:
			
			nb_nodes_in_element = mesh.GetElemNbNodes(element_id_in_domain)
			
			if mesh_dimension == 2:
				
				if nb_nodes_in_element == 3:
					
					triangle_ids_in_domain.append(element_id_in_domain)
					
				
				if nb_nodes_in_element == 4:
					
					quadrangle_ids_in_domain.append(element_id_in_domain)
					
				
			
			elif mesh_dimension == 3:
				
				if nb_nodes_in_element == 4:
					
					tetrahedron_ids_in_domain.append(element_id_in_domain)
					
				
				if nb_nodes_in_element == 5:
					
					pyramid_ids_in_domain.append(element_id_in_domain)
					
				
				if nb_nodes_in_element == 6:
					
					prism_ids_in_domain.append(element_id_in_domain)
					
				
				if nb_nodes_in_element == 8:
					
					hexahedron_ids_in_domain.append(element_id_in_domain)
					
				
			
		
		nb_types_in_domain = 0
		types_in_domain = 0 #-2 = quadrangles ; - 1 = triangles ; + 1 = tetrahedrons ; + 2 = pyramids ; + 4 = prisms ; + 8 = hexahedrons
		
		nb_triangles_in_domain = len(triangle_ids_in_domain)
		nb_quandrangles_in_domain = len(quadrangle_ids_in_domain)
		nb_tetrahedrons_in_domain = len(tetrahedron_ids_in_domain)
		nb_pyramids_in_domain = len(pyramid_ids_in_domain)
		nb_prisms_in_domain = len(prism_ids_in_domain)
		nb_hexahedrons_in_domain = len(hexahedron_ids_in_domain)
		
		if nb_triangles_in_domain > 0:
			
			types_in_domain -= 1
			
			nb_types_in_domain += 1
			
		
		if nb_quandrangles_in_domain > 0:
			
			types_in_domain -= 2
			
			nb_types_in_domain += 1
			
		
		if nb_tetrahedrons_in_domain > 0:
			
			types_in_domain += 1
			
			nb_types_in_domain += 1
			
		
		if nb_pyramids_in_domain > 0:
			
			types_in_domain += 2
			
			nb_types_in_domain += 1
			
		
		if nb_prisms_in_domain > 0:
			
			types_in_domain += 4
			
			nb_types_in_domain += 1
			
		
		if nb_hexahedrons_in_domain > 0:
			
			types_in_domain += 8
			
			nb_types_in_domain += 1
			
		
		types_for_quadrangles = [ - 3, - 2]
		types_for_triangles = [ - 3, - 1]
		types_for_tetrahedrons = [1, 3, 5, 7, 9, 11, 13, 15]
		types_for_pyramids = [2, 3, 6, 7, 10, 11, 14, 15]
		types_for_prisms = [4, 5, 6, 7, 12, 13, 14, 15]
		types_for_hexahedrons = [8, 9, 10, 11, 12, 13, 14, 15]
		
		for n in range(nb_types_in_domain):
			
			amsh_file.write(" element_group N 0 0 2\n")
			amsh_file.write(" element_type L 1 1 0\n")
			
			if types_in_domain in types_for_quadrangles:
				
				if help == True:
					
					mesh_file.write("QUAD\n")
					
				
				element_ids_in_domain = quadrangle_ids_in_domain
				nb_elements_in_domain = nb_quandrangles_in_domain
				
				nb_nodes_in_elements = 4
				
				types_in_domain += 2
				
				elements_type = "quad4"
				
			
			elif types_in_domain in types_for_triangles:
				
				if help == True:
					
					mesh_file.write("TRIA\n")
					
				
				element_ids_in_domain = triangle_ids_in_domain
				nb_elements_in_domain = nb_triangles_in_domain
				
				nb_nodes_in_elements = 3
				
				types_in_domain += 1
				
				elements_type = "tria3"
				
			
			elif types_in_domain in types_for_hexahedrons:
				
				if help == True:
					
					mesh_file.write("HEXA\n")
					
				
				element_ids_in_domain = hexahedron_ids_in_domain
				nb_elements_in_domain = nb_hexahedrons_in_domain
				
				nb_nodes_in_elements = 8
				
				types_in_domain -= 8
				
				elements_type = "hexa8"
				
			
			elif types_in_domain in types_for_prisms:
				
				if help == True:
					
					mesh_file.write("PRISM\n")
					
				
				element_ids_in_domain = prism_ids_in_domain
				nb_elements_in_domain = nb_prisms_in_domain
				
				nb_nodes_in_elements = 6
				
				types_in_domain -= 4
				
				elements_type = "penta6"
				
			
			elif types_in_domain in types_for_pyramids:
				
				if help == True:
					
					mesh_file.write("PENTA\n")
					
				
				element_ids_in_domain = pyramid_ids_in_domain
				
				nb_elements_in_domain = nb_pyramids_in_domain
				
				nb_nodes_in_elements = 5
				
				types_in_domain -= 2
				
				elements_type = "penta5"
				
			
			elif types_in_domain in types_for_tetrahedrons:
				
				if help == True:
					
					mesh_file.write("TETRA\n")
					
				
				element_ids_in_domain = tetrahedron_ids_in_domain
				nb_elements_in_domain = nb_tetrahedrons_in_domain
				
				nb_nodes_in_elements = 4
				
				types_in_domain -= 1
				
				elements_type = "tetra4"
				
			
			if help == True:
				
				mesh_file.write("N	ID	NODE1	NODE2	...\n")
				
				N = 1
				
			
			amsh_file.write(" '%s'\n"%(elements_type))
			amsh_file.write(" element_nodes IF %i %i 0\n"%(nb_nodes_in_elements, nb_elements_in_domain))
			
			node_ids = []
			
			for n in range(nb_nodes_in_elements):
				
				node_ids.append([])
				
			
			for element_id in element_ids_in_domain:
				
				if help == True:
					
					mesh_file.write("%i	%i	"%(N, element_id))
					
					N += 1
					
				
				for n in range(nb_nodes_in_elements):
					
					if help == True:
						
						mesh_file.write("%i	"%(mesh.GetElemNodes(element_id)[n]))
						
					
					node_ids[n].append(mesh.GetElemNodes(element_id)[n])
					
				
				if help == True:
					
					mesh_file.write("\n")
					
				
			
			figures = []
			
			for n in range(nb_nodes_in_elements):
				
				figures += node_ids[n]
				
			
			if mesh_dimension == 3:
				
				# reorder node IDs
				
				reordered_figures = []
				split_figures = []
				reordered_split_figures = []
				
				for n in range(nb_nodes_in_elements):
					
					split_figures.append([])
					
					reordered_split_figures.append([])
					
				
				f = 0
				n = 0
				
				for figure in figures:
					
					split_figures[n].append(figure)
					
					f += 1
					
					if f == nb_elements_in_domain:
						
						n += 1
						f = 0
						
					
				
				if elements_type == "hexa8" or elements_type == "penta6":
					
					for n in range(nb_nodes_in_elements / 2):
						
						reordered_split_figures[n] = split_figures[nb_nodes_in_elements / 2 + n]
						reordered_split_figures[nb_nodes_in_elements / 2 + n] = split_figures[n]
						
					
					for n in range(nb_nodes_in_elements):
						
						reordered_figures += reordered_split_figures[n]
						
					
					figures = reordered_figures
					
				
				elif elements_type == "tetra4" or elements_type == "penta5":
					
					for n in range(nb_nodes_in_elements - 1):
						
						reordered_figures += split_figures[nb_nodes_in_elements - 2 - n]
						
					
					figures = reordered_figures + split_figures[nb_nodes_in_elements - 1]
					
				
			
			WriteInColumns(amsh_file, figures, nb_nodes_in_elements, 24)
			
		
		#-
		
		# Close the files
		
		amsh_file.close()
		
		if help == True:
			
			mesh_file.close()
			
		
		#-
		
	

eaf = ExportAmshFile

def ExportSU2File( mesh = None, file = None, only = [None], ignore = [None]):
	"""
	
	
Description:
	Exports a mesh into an .su2 file readable by the CFD solver SU2 4.0.
	

Arguments:
	# mesh 
		Description:       The mesh to export. 
		Type:              Mesh 
		GUI selection:     yes 
		Selection by name: yes 
		Recursive:         - 
		Default value:     None  

	# file 
		Description:       The name without extension of the amsh file to write. If equals None, the name of the mesh in the study tree is taken. 
		Type:              String 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     None  

	# only 
		Description:       The list of names of groups to export, excluding the others. 
		Type:              List of Strings 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     [None]  

	# ignore 
		Description:       The list of names of groups to ignore. 
		Type:              List of Strings 
		GUI selection:     - 
		Selection by name: - 
		Recursive:         - 
		Default value:     [None]  

Returned Values:
	"dim" value:    - 
	"single" value: - 
	Type:           - 
	Number:         - 
	Name:           -  

Conditions of use:
	The mesh has to be computed and to contain groups describing the desired boundary conditions (inlet, outlet, wall, farfield, etc.).
	

"""
	
	# Get the input shape(s)
	
	mesh = GetGUISelection(mesh, uniq = True)
	
	mesh = GetObject(mesh, "SMESH")
	
	#-
	
	# Check the input shape existence
	
	if "error" in [mesh] or None in [mesh]: return
	
	#-
	
	else:# All checks done
		
		def FindElementType(mesh_dimension, nb_nodes_in_element, boundary = False):
			
			if boundary == True: mesh_dimension -= 1
			
			line_type = 3
			triangle_type = 5
			quadrilateral_type = 9
			tetrahedral_type = 10
			hexahedral_type = 12
			wedge_type = 13
			pyramid_type = 14
			
			element_type = None
			
			if mesh_dimension == 1:
				
				if nb_nodes_in_element == 2:
					
					element_type = line_type
					
				
			
			if mesh_dimension == 2:
				
				if nb_nodes_in_element == 3:
					
					element_type = triangle_type
					
				
				if nb_nodes_in_element == 4:
					
					element_type = quadrilateral_type
					
				
			
			elif mesh_dimension == 3:
				
				if nb_nodes_in_element == 4:
					
					element_type = tetrahedral_type
					
				
				if nb_nodes_in_element == 5:
					
					element_type = pyramid_type
					
				
				if nb_nodes_in_element == 6:
					
					element_type = wedge_type
					
				
				if nb_nodes_in_element == 8:
					
					element_type = hexahedral_type
					
				
			
			return element_type
			
		
		def powerOfTen(figure):
			
			figure *= 1.0
			
			n = 0
			
			if figure != 0:
				
				if abs(figure) < 1:
					
					while abs(figure) < 1:
						
						figure *= 10
						
						n -= 1
						
					
				
				if abs(figure) >= 10:
					
					while abs(figure) >= 10:
						
						figure /= 10
						
						n += 1
						
					
				
			
			return figure, n
			
		
		if "SMESH_Mesh instance" in str(mesh) or "meshProxy instance" in str(mesh) or "Mesh object" in str(mesh):
			
			try:
				mesh = smesh.Mesh(mesh)
			except:
				pass
			
		
		else:
			
			print "[X] The input object is not a mesh or the Mesh module was not yet loaded."; return
			
		
		# Get the mesh name
		
		mesh_name = mesh.GetName()
		
		#-
		
		# Renumber elements and nodes
		
		mesh.RenumberNodes()
		mesh.RenumberElements()
		
		#-
		
		# Get nodes number and IDs
		
		nb_nodes_in_mesh = mesh.NbNodes()
		
		node_ids_in_mesh = mesh.GetNodesId()
		
		#-
		
		# Get edges IDs
		
		edge_ids_in_mesh = mesh.GetElementsByType(SMESH.EDGE)
		
		nb_edges_in_mesh = mesh.NbEdges()
		
		#-
		
		# Get faces IDs
		
		face_ids_in_mesh = mesh.GetElementsByType(SMESH.FACE)
		
		nb_faces_in_mesh = mesh.NbFaces()
		nb_triangles_in_mesh = mesh.NbTriangles()
		nb_quadrangles_in_mesh = mesh.NbQuadrangles()
		
		#-
		
		# Get volumes IDs
		
		nb_volumes_in_mesh = mesh.NbVolumes()
		
		nb_tetrahedrons_in_mesh = mesh.NbTetras()
		nb_pyramids_in_mesh = mesh.NbPyramids()
		nb_prisms_in_mesh = mesh.NbPrisms()
		nb_hexahedrons_in_mesh = mesh.NbHexas()
		
		volume_ids_in_mesh = mesh.GetElementsByType(SMESH.VOLUME)
		
		#-
		
		# Get mesh dimension
		
		if nb_volumes_in_mesh != 0:
			
			mesh_dimension = 3
			
			nb_elements_in_domain = nb_volumes_in_mesh
		
		else:
			
			mesh_dimension = 2
			
			nb_elements_in_domain = nb_faces_in_mesh
			
		
		#-
		
		# Get groups
		
		group_names = mesh.GetGroupNames()
		
		groups = mesh.GetGroups()
		
		#-
		
		# Sort groups
		
		sorted_groups = []
		
		if only != [None]:
			
			for group in groups:
				
				group_name = group.GetName()
				
				if group_name in only:
					
					sorted_groups.append(group)
					
				
			
			groups = sorted_groups
			
		
		sorted_groups = []
		
		if ignore != [None]:
			
			for group in groups:
				
				group_name = group.GetName()
				
				if group_name not in ignore:
					
					sorted_groups.append(group)
					
				
			
			groups = sorted_groups
			
		
		# Get the number of groups
		
		nb_groups = len(groups)
		
		#-
		
		# Get group types
		
		group_types = []
		
		for group in groups:
			
			group_type = str(group.GetType())
			
			group_types.append(group_type)
			
		
		#-
		
		# Open the su2 file
		
		if file == None:
			
			file = mesh_name
			
		
		su2_file = open("%s.su2"%(file), "w")
		
		su2_file.write("NDIME = %i\n"%(mesh_dimension))
		
		#-
		
		# Write the domain element definitions
		
		print "[i] Writing definition of domain elements... (%s elements)"%(nb_elements_in_domain)
		
		su2_file.write("NELEM = %i\n"%(nb_elements_in_domain))
		
		if mesh_dimension == 2:
			
			element_ids_in_domain = face_ids_in_mesh
			
		
		elif mesh_dimension == 3:
			
			element_ids_in_domain = volume_ids_in_mesh
			
		
		for element_id_in_domain in element_ids_in_domain:
			
			nb_nodes_in_element = mesh.GetElemNbNodes(element_id_in_domain)
			
			element_type = FindElementType(mesh_dimension, nb_nodes_in_element)
			
			element_definition = str(element_type)
			
			for n in range(nb_nodes_in_element):
				
				#if element_type == pyramid_type: n *= -1
				
				node_id = mesh.GetElemNodes(element_id_in_domain)[n]
				
				node_id -= 1
				
				element_definition += "\t" + str(node_id)
				
			
			element_definition += "\t" + str(element_id_in_domain)
			
			su2_file.write(element_definition + "\n")
			
		
		#-
		
		print "[i] Writing node coordinates... (%s nodes)"%(nb_nodes_in_mesh)
		
		su2_file.write("NPOIN = %i\n"%(nb_nodes_in_mesh))
		
		# Write the node coordinates
		
		for node_id in node_ids_in_mesh:
			
			node_definition = ""
			
			for n in range(mesh_dimension):
				
				node_coordinate = mesh.GetNodeXYZ(node_id)[n]
				
				[node_float_coordinate, node_coordinate_power_of_ten] = powerOfTen(node_coordinate)
				
				node_coordinate = "%.16fE%i"%(node_float_coordinate, node_coordinate_power_of_ten)
				
				node_definition += "\t" + node_coordinate
				
			
			node_id -= 1
			
			node_definition += "\t" + str(node_id)
			
			su2_file.write(node_definition + "\n")
			
		
		#-
		
		# Get the group element definition
		
		print "[i] Writing definition of group elements... (%s groups)"%(nb_groups)
		
		su2_file.write("NMARK = %i\n"%(nb_groups))
		
		for group in groups:# For each group of the mesh
			
			group_name = group.GetName()
			
			su2_file.write("MARKER_TAG = %s\n"%(group_name))
			
			element_ids_in_group = group.GetListOfID()
			
			nb_elements_in_group = len(element_ids_in_group)
			
			su2_file.write("MARKER_ELEMS = %s\n"%(nb_elements_in_group))
			
			for element_id_in_group in element_ids_in_group:
				
				nb_nodes_in_element = mesh.GetElemNbNodes(element_id_in_group)
				
				element_type = FindElementType(mesh_dimension, nb_nodes_in_element, boundary = True)
				
				element_definition = str(element_type)
				
				for n in range(nb_nodes_in_element):
					
					node_id = mesh.GetElemNodes(element_id_in_group)[n]
					
					node_id -= 1
					
					element_definition += "\t" + str(node_id)
					
				
				element_definition += "\t" + str(element_id_in_group)
				
				su2_file.write(element_definition + "\n")
			
			
		#-
		
		# Close the files
		
		su2_file.close()
		
		#-
		
	

esf = ExportSU2File

#### - ####

print "Welcome in cfdmsh!"

pv()

print "Type pdf() to see implemented functions."
