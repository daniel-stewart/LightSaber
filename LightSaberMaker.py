'''
Copyright 2019, Daniel Stewart

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import bpy
import bmesh
from math import *

def createMeshFromData(name, origin, verts, edges, faces):
    # Create mesh and object
    mesh = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, mesh)
    ob.location = origin
    ob.show_name = False
    # Link object to scene and make active
    bpy.context.collection.objects.link(ob)
    ob.select_set(True)
    # Create mesh from given verts, faces.
    mesh.from_pydata(verts, edges, faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    mesh.update()
    bm.clear()

    bm.free()
    # Update mesh with new data
    mesh.update()

def createCircularPolys(VerticesPerLoop, verts, faces, radius, zoffset, startVert, startFace, joinVert, joinFace):
    angle = 0
    for i in range(VerticesPerLoop):
        angle = i * 2 * pi / VerticesPerLoop
        x = radius * cos(angle)
        y = radius * sin(angle)
        z = zoffset
       
        verts[startVert + i][0] = x
        verts[startVert + i][1] = y
        verts[startVert + i][2] = z
   
    for i in range(VerticesPerLoop - 1):
        faces[startFace + i][0] = startVert + i
        faces[startFace + i][1] = startVert + i + 1
        faces[startFace + i][2] = joinVert + 1 + i
        faces[startFace + i][3] = joinVert + i
   
    faces[startFace + VerticesPerLoop - 1][0] = startVert + VerticesPerLoop - 1
    faces[startFace + VerticesPerLoop - 1][1] = startVert
    faces[startFace + VerticesPerLoop - 1][2] = joinVert
    faces[startFace + VerticesPerLoop - 1][3] = joinVert + VerticesPerLoop - 1
   
def joinCircularPolys(VerticesPerLoop, verts, faces, startVert, startFace, joinVert):
    for i in range(VerticesPerLoop - 1):
        faces[startFace + i][0] = startVert + i
        faces[startFace + i][1] = startVert + i + 1
        faces[startFace + i][2] = joinVert + 1 + i
        faces[startFace + i][3] = joinVert + i
   
    faces[startFace + VerticesPerLoop - 1][0] = startVert + VerticesPerLoop - 1
    faces[startFace + VerticesPerLoop - 1][1] = startVert
    faces[startFace + VerticesPerLoop - 1][2] = joinVert
    faces[startFace + VerticesPerLoop - 1][3] = joinVert + VerticesPerLoop - 1

def createThreads(VerticesPerLoop, verts, faces, startVert, startFace, Loops, R, r, h1, h2, h3, h4, falloffRate, zoffset, femaleThreads = False):
    # Code
    H = h1 + h2 + h3 + h4

    #build array of profile points
    ProfilePoints = []
    ProfilePoints.append( [r, 0, 0] )
    ProfilePoints.append( [R, 0, h1] )
    if h2 > 0:
        ProfilePoints.append( [R, 0, h1 + h2] )
    ProfilePoints.append( [r, 0, h1 + h2 + h3] )
    if h4 > 0:
        ProfilePoints.append( [r, 0, h1 + h2 + h3 + h4] )

    N = len(ProfilePoints)

    # Create the bottom row
    angle = 0
    for i in range(VerticesPerLoop):
        angle = i * 2 * pi / VerticesPerLoop
        radius = r
        x = radius * cos(angle)
        y = radius * sin(angle)
        z = zoffset
       
        verts[startVert + i][0] = x
        verts[startVert + i][1] = y
        verts[startVert + i][2] = z

    faces[startFace][0] = startVert
    faces[startFace][1] = startVert + VerticesPerLoop
    faces[startFace][2] = startVert + VerticesPerLoop + N
    faces[startFace][3] = startVert + 1

    for i in range(1,VerticesPerLoop-1):
        faces[startFace + i][0] = startVert + i
        faces[startFace + i][1] = startVert + i * N + VerticesPerLoop
        faces[startFace + i][2] = startVert + i * N + VerticesPerLoop + N
        faces[startFace + i][3] = startVert + i + 1

    # Just to ensure we have the right size
    faces[startFace + VerticesPerLoop - 1] = [0 for _ in range(N+2)]
   
    # This one face has N + 2 vertices, not just 4.
    faces[startFace + VerticesPerLoop - 1][0] = startVert + VerticesPerLoop - 1
    faces[startFace + VerticesPerLoop - 1][1] = startVert + (VerticesPerLoop - 2) * N + VerticesPerLoop + N
    for i in range(1,N):
        faces[startFace + VerticesPerLoop - 1][i+1] =  startVert + VerticesPerLoop + (N - i)
    faces[startFace + VerticesPerLoop - 1][N+1] = startVert + VerticesPerLoop

    # Here we actually create the threads.
    # go around a circle. for each point in ProfilePoints array, create a vertex
    angle = 0
    zMax = ProfilePoints[N-1][2] + (Loops - 1) * H + zoffset
    for i in range(VerticesPerLoop * Loops + 1):
        for j in range(N):
            angle = i * 2 * pi / VerticesPerLoop
            # falloff applies to outer rings only
            u = i / (VerticesPerLoop * Loops)
            radius = r + (R - r) * (1 - 6*(pow(2 * u - 1, falloffRate * 4)/2 - pow(2 * u - 1, falloffRate * 6)/3)) if ProfilePoints[j][0] == R else r

            x = radius * cos(angle)
            y = radius * sin(angle)
            z = ProfilePoints[j][2] + i / VerticesPerLoop * H + zoffset
            # Check for maxing out if necessary
            if femaleThreads and (z > zMax):
                z = zMax

            verts[startVert + N*i + j + VerticesPerLoop][0] = x
            verts[startVert + N*i + j + VerticesPerLoop][1] = y
            verts[startVert + N*i + j + VerticesPerLoop][2] = z
    # now build face array
    for i in range(VerticesPerLoop * Loops):
        for j in range(N - 1):
            faces[startFace + (N - 1) * i + j + VerticesPerLoop][0] = startVert + N * i + j + VerticesPerLoop
            faces[startFace + (N - 1) * i + j + VerticesPerLoop][1] = startVert + N * i + 1 + j + VerticesPerLoop
            faces[startFace + (N - 1) * i + j + VerticesPerLoop][2] = startVert + N * (i + 1) + 1 + j + VerticesPerLoop
            faces[startFace + (N - 1) * i + j + VerticesPerLoop][3] = startVert + N * (i + 1) + j + VerticesPerLoop

    # Now create the top edge
    angle = 0
    for i in range(VerticesPerLoop):
        angle = i * 2 * pi / VerticesPerLoop
        radius = r
        x = radius * cos(angle)
        y = radius * sin(angle)
        if femaleThreads:
            z = Loops * H + zoffset
        else:
            z = (Loops + 1)*H + zoffset
       
        verts[startVert + N * (VerticesPerLoop * Loops + 1) + i + VerticesPerLoop][0] = x
        verts[startVert + N * (VerticesPerLoop * Loops + 1) + i + VerticesPerLoop][1] = y
        verts[startVert + N * (VerticesPerLoop * Loops + 1) + i + VerticesPerLoop][2] = z

    # Just to ensure we have the right size
    faces[startFace + (N-1) * VerticesPerLoop * Loops + VerticesPerLoop] = [0 for _ in range(N+2)]
   
    # This one face has N + 2 vertices, not just 4.
    faces[startFace + (N-1) * VerticesPerLoop * Loops + VerticesPerLoop][0] = startVert + N * VerticesPerLoop * (Loops - 1) + (N - 1) + VerticesPerLoop
    faces[startFace + (N-1) * VerticesPerLoop * Loops + VerticesPerLoop][1] = startVert + N * VerticesPerLoop * (Loops - 1) + 2*N - 1 + VerticesPerLoop
    faces[startFace + (N-1) * VerticesPerLoop * Loops + VerticesPerLoop][2] = startVert +N * (VerticesPerLoop * Loops + 1) + 1 + VerticesPerLoop
    for i in range(1,N):
        faces[startFace + (N-1) * VerticesPerLoop * Loops + VerticesPerLoop][2+i] = startVert + N * (VerticesPerLoop * Loops + 1) + VerticesPerLoop - i

    for i in range(1,VerticesPerLoop-1):
        faces[startFace + (N-1) * VerticesPerLoop * Loops + i + VerticesPerLoop][0] = startVert + N * VerticesPerLoop * (Loops - 1) + (N - 1) + i*N + VerticesPerLoop
        faces[startFace + (N-1) * VerticesPerLoop * Loops + i + VerticesPerLoop][1] = startVert + N * VerticesPerLoop * (Loops - 1) + 2*N - 1 + i*N + VerticesPerLoop
        faces[startFace + (N-1) * VerticesPerLoop * Loops + i + VerticesPerLoop][2] = startVert + N * (VerticesPerLoop * Loops + 1) + 1 + i + VerticesPerLoop
        faces[startFace + (N-1) * VerticesPerLoop * Loops + i + VerticesPerLoop][3] = startVert + N * (VerticesPerLoop * Loops + 1) + i + VerticesPerLoop

    faces[startFace + (N-1) * VerticesPerLoop * Loops + 2 * VerticesPerLoop - 1][0] = startVert + VerticesPerLoop * (N * Loops + 1) - 1
    faces[startFace + (N-1) * VerticesPerLoop * Loops + 2 * VerticesPerLoop - 1][1] = startVert + N * (VerticesPerLoop * Loops + 1) + 2 * VerticesPerLoop - 1
    faces[startFace + (N-1) * VerticesPerLoop * Loops + 2 * VerticesPerLoop - 1][2] = startVert + N * (VerticesPerLoop * Loops + 1) + VerticesPerLoop
    faces[startFace + (N-1) * VerticesPerLoop * Loops + 2 * VerticesPerLoop - 1][3] = startVert + N * (VerticesPerLoop * Loops + 1) + VerticesPerLoop - 1

def createBladeBase(VerticesPerLoop, numMaleLoops, R, r, h1, h2, h3, h4, falloffRate, maleOffset, maleThickness=2, femaleThickness=3):
    # Code
    H = h1 + h2 + h3 + h4
    N = 3
    if h2 > 0:
        N = N + 1
    if h4 > 0:
        N = N + 1

    verts = [[0, 0, 0] for _ in range(N * (VerticesPerLoop * numMaleLoops + 1) + 9*VerticesPerLoop)]
    faces = [[0, 0, 0, 0] for _ in range(( N - 1) * VerticesPerLoop * numMaleLoops + 10*VerticesPerLoop) ]
   
    startVert = 0
    startFace = 0
    femaleThreads = False
    createThreads(VerticesPerLoop, verts, faces, startVert, startFace, numMaleLoops, R, r, h1, h2, h3, h4, falloffRate, maleOffset, femaleThreads)
   
    radius = r - maleThickness - .5
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + 2 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + 2 * VerticesPerLoop
    joinVert = 0
    joinFace = 0
    zHeight = maleOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
   
    radius = r - maleThickness - .5
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + 3 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + 3 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + 2 * VerticesPerLoop
    joinFace = 0
    zHeight = (numMaleLoops + 1)* H + maleOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = r - maleThickness - 0.5
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + 4 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + 4 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + 3 * VerticesPerLoop
    zHeight = (numMaleLoops + 1)* H + maleOffset + 11.5
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = 12.8
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + 5 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + 5 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + 4 * VerticesPerLoop
    zHeight = (numMaleLoops + 1)* H + maleOffset + 11.5
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = 12.8
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + 6 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + 6 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + 5 * VerticesPerLoop
    zHeight = (numMaleLoops + 1)* H + maleOffset + 15.5
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = R + femaleThickness
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + 7 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + 7 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + 1 * VerticesPerLoop
    zHeight = (numMaleLoops + 1)* H + maleOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = R + femaleThickness
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + 8 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + 8 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + 7 * VerticesPerLoop
    zHeight = (numMaleLoops + 1)* H + maleOffset + 15.5
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + 8 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + 9 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + 6 * VerticesPerLoop
    joinCircularPolys(VerticesPerLoop, verts, faces, startVert, startFace, joinVert)
    
    return verts, faces

def createCPFemaleBase(VerticesPerLoop, numTopLoops, numBottomLoops, RTop, rTop, RBottom, rBottom, h1, h2, h3, h4, falloffRate, topOffset, bottomOffset, thickness = 3):
    # Code
    H = h1 + h2 + h3 + h4
    N = 3
    if h2 > 0:
        N = N + 1
    if h4 > 0:
        N = N + 1

    verts = [[0, 0, 0] for _ in range(N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 15*VerticesPerLoop)]
    faces = [[0, 0, 0, 0] for _ in range(( N - 1) * VerticesPerLoop * numTopLoops + ( N - 1) * VerticesPerLoop * numBottomLoops  + 17*VerticesPerLoop) ]
   
    startVert = 0
    startFace = 0
    createThreads(VerticesPerLoop, verts, faces, startVert, startFace, numTopLoops, RTop, rTop, h1, h2, h3, h4, falloffRate, topOffset, True)
   
    radius = rTop
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + 2 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + 2 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + 1 * VerticesPerLoop
    joinFace = 0
    zHeight = (numTopLoops) * H + topOffset + 0.2
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = RTop + thickness
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + 3 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + 3 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + 2 * VerticesPerLoop
    joinFace = 0
    zHeight = (numTopLoops) * H + topOffset + 0.2
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = RTop + thickness
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + 4 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + 4 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + 3 * VerticesPerLoop
    joinFace = 0
    zHeight = topOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + 5 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + 5 * VerticesPerLoop
    createThreads(VerticesPerLoop, verts, faces, startVert, startFace, numBottomLoops, RBottom, rBottom, h1, h2, h3, h4, falloffRate, bottomOffset, True)
    
    radius = rBottom
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 7 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 7 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + 5 * VerticesPerLoop
    joinFace = 0
    zHeight = bottomOffset - 0.2
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = RBottom + thickness
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 8 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 8 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 7 * VerticesPerLoop
    joinFace = 0
    zHeight = bottomOffset - 0.2
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = RBottom + thickness
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 9 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 9 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 8 * VerticesPerLoop
    joinFace = 0
    zHeight = numBottomLoops * H + bottomOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = RBottom + thickness
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 10 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 10 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 9 * VerticesPerLoop
    joinFace = 0
    zHeight = bottomOffset + (numBottomLoops + 1) * H
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    
    radius = rBottom
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 11 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 11 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 6 * VerticesPerLoop
    joinFace = 0
    zHeight = bottomOffset + (numBottomLoops + 1) * H
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = rBottom
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 12 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 12 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + + N * (VerticesPerLoop * numBottomLoops + 1) + 11 * VerticesPerLoop
    joinFace = 0
    zHeight = (topOffset - (bottomOffset + (numBottomLoops + 1) * H))/2 + (bottomOffset + (numBottomLoops + 1) * H)
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = RBottom + thickness
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 13 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 13 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 10 * VerticesPerLoop
    joinFace = 0
    zHeight = 2 * (topOffset - (bottomOffset + (numBottomLoops + 1) * H))/3 + (bottomOffset + (numBottomLoops + 1) * H)
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    
    radius = rTop - 2
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 14 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 14 * VerticesPerLoop
    joinVert = 0
    joinFace = 0
    zHeight = topOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    '''
    radius = RTop + thickness
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 13 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 13 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + 3 * VerticesPerLoop
    joinFace = 0
    zHeight = 2*(topOffset - bottomOffset)/3 + bottomOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = rBottom
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 14 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 14 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 10 * VerticesPerLoop
    joinFace = 0
    zHeight = (topOffset - bottomOffset)/2 + bottomOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    '''
    
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 14 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 15 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 12 * VerticesPerLoop
    joinCircularPolys(VerticesPerLoop, verts, faces, startVert, startFace, joinVert)
    
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 13 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 16 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + 4 * VerticesPerLoop
    joinCircularPolys(VerticesPerLoop, verts, faces, startVert, startFace, joinVert)
    
    return verts, faces

def createCPMaleBase(VerticesPerLoop, numTopLoops, numBottomLoops, RTop, rTop, RBottom, rBottom, h1, h2, h3, h4, falloffRate, topOffset, bottomOffset, thickness=3):
    # Code
    H = h1 + h2 + h3 + h4
    N = 3
    if h2 > 0:
        N = N + 1
    if h4 > 0:
        N = N + 1

    verts = [[0, 0, 0] for _ in range(N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 13*VerticesPerLoop)]
    faces = [[0, 0, 0, 0] for _ in range(( N - 1) * VerticesPerLoop * numTopLoops + ( N - 1) * VerticesPerLoop * numBottomLoops  + 15*VerticesPerLoop) ]
   
    startVert = 0
    startFace = 0
    createThreads(VerticesPerLoop, verts, faces, startVert, startFace, numTopLoops, RTop, rTop, h1, h2, h3, h4, falloffRate, topOffset, False)
    
    radius = rTop - thickness
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + 2 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + 2 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + 1 * VerticesPerLoop
    joinFace = 0
    zHeight = (numTopLoops + 1) * H + topOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = rTop - thickness
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + 3 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + 3 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + 2 * VerticesPerLoop
    joinFace = 0
    zHeight = topOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + 4 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + 4 * VerticesPerLoop
    createThreads(VerticesPerLoop, verts, faces, startVert, startFace, numBottomLoops, RBottom, rBottom, h1, h2, h3, h4, falloffRate, bottomOffset, False)
    
    radius = rBottom - 7
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 6 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 6 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + 4 * VerticesPerLoop
    joinFace = 0
    zHeight = bottomOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = rBottom - 7
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 7 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 7 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 6 * VerticesPerLoop
    joinFace = 0
    zHeight = (numBottomLoops + 1) * H + bottomOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = rBottom - 7
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 8 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 8 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 7 * VerticesPerLoop
    joinFace = 0
    zHeight = (topOffset - bottomOffset)/2 + bottomOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    
    radius = rTop - thickness
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 9 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 9 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + 3 * VerticesPerLoop
    joinFace = 0
    zHeight = (topOffset - bottomOffset) / 2 + bottomOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    
    radius = rBottom
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 10 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 10 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) +  N * (VerticesPerLoop * numBottomLoops + 1) + 5 * VerticesPerLoop
    joinFace = 0
    zHeight = 2 * (topOffset - bottomOffset)/3 + bottomOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = rBottom - 7
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 11 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 11 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 10 * VerticesPerLoop
    joinFace = 0
    zHeight = 2 * (topOffset - bottomOffset)/3 + bottomOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = rTop
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 12 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 12 * VerticesPerLoop
    joinVert = 0
    joinFace = 0
    zHeight = 2 * (topOffset - bottomOffset)/3 + bottomOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)

    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 9 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 13 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 8 * VerticesPerLoop
    joinCircularPolys(VerticesPerLoop, verts, faces, startVert, startFace, joinVert)
    
    startVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 11 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numTopLoops + (N-1) * VerticesPerLoop * numBottomLoops + 14 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numTopLoops + 1) + N * (VerticesPerLoop * numBottomLoops + 1) + 12 * VerticesPerLoop
    joinCircularPolys(VerticesPerLoop, verts, faces, startVert, startFace, joinVert)
    
    return verts, faces

def createHiltBase(VerticesPerLoop, numMaleLoops, numFemaleLoops, R, r, h1, h2, h3, h4, falloffRate, femaleOffset, maleOffset, radiiDiff, femaleThreads = False, numMaleThreads = 3, maleThickness = 2, femaleThickness = 3, locking = False):
    # Code
    H = h1 + h2 + h3 + h4
    N = 3
    if h2 > 0:
        N = N + 1
    if h4 > 0:
        N = N + 1

    verts = [[0, 0, 0] for _ in range(N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 12*VerticesPerLoop)]
    faces = [[0, 0, 0, 0] for _ in range(( N - 1) * VerticesPerLoop * numMaleLoops + ( N - 1) * VerticesPerLoop * numFemaleLoops  + 14*VerticesPerLoop) ]
   
    startVert = 0
    startFace = 0
    femaleThreads = False
    createThreads(VerticesPerLoop, verts, faces, startVert, startFace, numMaleLoops, R - radiiDiff, r - radiiDiff, h1, h2, h3, h4, falloffRate, maleOffset, femaleThreads)
   
    radius = r - maleThickness - radiiDiff
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + 2 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + 2 * VerticesPerLoop
    joinVert = 0
    joinFace = 0
    zHeight = maleOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
   
    radius = r - maleThickness - radiiDiff
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + 3 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + 3 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + 2 * VerticesPerLoop
    joinFace = 0
    zHeight = (numMaleLoops + 1)* H + maleOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
   
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + 4 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + 4 * VerticesPerLoop
    femaleThreads = True
    createThreads(VerticesPerLoop, verts, faces, startVert, startFace, numFemaleLoops, R, r, h1, h2, h3, h4, 1000, femaleOffset, femaleThreads)
   
    # For  female threads...
    radius = r
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 6 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + (N-1) * VerticesPerLoop * numFemaleLoops + 6 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 5 * VerticesPerLoop
    joinFace = 0
    zHeight = numFemaleLoops * H + femaleOffset + 0.2
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
   
    radius = R + femaleThickness
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 7 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + (N-1) * VerticesPerLoop * numFemaleLoops + 7 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 6 * VerticesPerLoop
    joinFace = 0
    zHeight = numFemaleLoops * H + femaleOffset + 0.2
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
   
    radius = R + femaleThickness
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 8 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + (N-1) * VerticesPerLoop * numFemaleLoops + 8 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 7 * VerticesPerLoop
    joinFace = 0
    zHeight = femaleOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
   
    radius = R + femaleThickness
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 9 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + (N-1) * VerticesPerLoop * numFemaleLoops + 9 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 8 * VerticesPerLoop
    joinFace = 0
    zHeight = maleOffset + (numMaleLoops + 1) * H
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    if locking:
        radius = r - maleThickness - radiiDiff
    else:
        radius = r
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 10 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + (N-1) * VerticesPerLoop * numFemaleLoops + 10 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + 4 * VerticesPerLoop
    joinFace = 0
    if locking:
        zHeight = femaleOffset
    else:
        zHeight = maleOffset + (numMaleLoops + 1) * H + 3
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    # Using previous radius for this loop
    radius = r - maleThickness - radiiDiff
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 11 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + (N-1) * VerticesPerLoop * numFemaleLoops + 11 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + 3 * VerticesPerLoop
    joinFace = 0
    zHeight = maleOffset + (numMaleLoops + 1) * H + 1
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 9 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + (N-1) * VerticesPerLoop * numFemaleLoops + 12 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + VerticesPerLoop
    joinCircularPolys(VerticesPerLoop, verts, faces, startVert, startFace, joinVert)
    
    startVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 10* VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numMaleLoops + (N-1) * VerticesPerLoop * numFemaleLoops + 13 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numMaleLoops + 1) + N * (VerticesPerLoop * numFemaleLoops + 1) + 11 * VerticesPerLoop
    joinCircularPolys(VerticesPerLoop, verts, faces, startVert, startFace, joinVert)
    
    return verts, faces

def createPommelBase(VerticesPerLoop, numFemaleLoops, R, r, h1, h2, h3, h4, falloffRate, femaleOffset, thickness):
    # Code
    H = h1 + h2 + h3 + h4
    N = 3
    if h2 > 0:
        N = N + 1
    if h4 > 0:
        N = N + 1

    verts = [[0, 0, 0] for _ in range(N * (VerticesPerLoop * numFemaleLoops + 1) + 7*VerticesPerLoop)]
    faces = [[0, 0, 0, 0] for _ in range(( N - 1) * VerticesPerLoop * numFemaleLoops  + 7*VerticesPerLoop) ]
   
    startVert = 0
    startFace = 0
    createThreads(VerticesPerLoop, verts, faces, startVert, startFace, numFemaleLoops, R, r, h1, h2, h3, h4, falloffRate, femaleOffset + 10, True)
   
    # For  female threads...
    radius = r
    startVert = N * (VerticesPerLoop * numFemaleLoops + 1) + 2 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numFemaleLoops + 2 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numFemaleLoops + 1) + VerticesPerLoop
    joinFace = 0
    zHeight = numFemaleLoops * H + femaleOffset + 10 + 0.2
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
   
    radius = R + thickness
    startVert = N * (VerticesPerLoop * numFemaleLoops + 1) + 3 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numFemaleLoops + 3 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numFemaleLoops + 1) + 2 * VerticesPerLoop
    joinFace = 0
    zHeight = numFemaleLoops * H + femaleOffset + 10 + 0.2
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
   
    radius = R + thickness
    startVert = N * (VerticesPerLoop * numFemaleLoops + 1) + 4 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numFemaleLoops + 4 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numFemaleLoops + 1) + 3 * VerticesPerLoop
    joinFace = 0
    zHeight = femaleOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    radius = r
    startVert = N * (VerticesPerLoop * numFemaleLoops + 1) + 5 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numFemaleLoops + 5 * VerticesPerLoop
    joinVert = N * (VerticesPerLoop * numFemaleLoops + 1) + 4 * VerticesPerLoop
    joinFace = 0
    zHeight = femaleOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    startVert = N * (VerticesPerLoop * numFemaleLoops + 1) + 6 * VerticesPerLoop
    startFace = (N-1) * VerticesPerLoop * numFemaleLoops + 6 * VerticesPerLoop
    joinVert = 0
    joinFace = 0
    zHeight = femaleOffset
    createCircularPolys(VerticesPerLoop, verts, faces, radius, zHeight, startVert, startFace, joinVert, joinFace)
    
    return verts, faces

def createBladeHolder(VerticesPerLoop, numMaleThreads, Rmale, rmale, h1, h2, h3, h4, maleThickness, femaleThickness):
    maleOffset = 100
    verts, faces = createBladeBase(VerticesPerLoop, numMaleThreads, Rmale, rmale, h1,  h2, h3, h4, 1, maleOffset, maleThickness, femaleThickness)
    createMeshFromData( 'BladeHolder', [0, 0, 0], verts, [], faces )

def createCPFemaleToFemale(VerticesPerLoop, numTopThreads, numBottomThreads, RTop, rTop, RBottom, rBottom, h1, h2, h3, h4, thickness):
    topOffset = 100
    bottomOffset = 70
    verts, faces = createCPFemaleBase(VerticesPerLoop, numTopThreads, numBottomThreads, RTop, rTop, RBottom, rBottom, h1,  h2, h3, h4, 1000, topOffset, bottomOffset, thickness)
    createMeshFromData( 'CPFemaleHolder', [0, 0, 0], verts, [], faces )

def createCPMaleToMale(VerticesPerLoop, numTopThreads, numBottomThreads, RTop, rTop, RBottom, rBottom, h1, h2, h3, h4, thickness):
    topOffset = 70
    bottomOffset = 45
    verts, faces = createCPMaleBase(VerticesPerLoop, numTopThreads, numBottomThreads, RTop, rTop, RBottom, rBottom, h1,  h2, h3, h4, 1, topOffset, bottomOffset, thickness)
    createMeshFromData( 'CPMaleHolder', [0, 0, 0], verts, [], faces )

def createHilt(VerticesPerLoop, numMaleThreads, numFemaleThreads, RFemale, rFemale, h1, h2, h3, h4, radiiDiff, maleThickness, femaleThickness, locking=False):
    femaleOffset = 150
    maleOffset = 0
    verts, faces = createHiltBase(VerticesPerLoop, numMaleThreads, numFemaleThreads, RFemale, rFemale, h1,  h2, h3, h4, 1, femaleOffset, maleOffset, radiiDiff, True, numMaleThreads, maleThickness, femaleThickness, locking)
    createMeshFromData( 'Hilt', [0, 0, 0], verts, [], faces )

def createPommel(VerticesPerLoop, numFemaleThreads, RFemale, rFemale, h1, h2, h3, h4, thickness):
    femaleOffset = 0
    verts, faces = createPommelBase(VerticesPerLoop, numFemaleThreads, RFemale, rFemale, h1,  h2, h3, h4, 1000, femaleOffset, thickness)
    createMeshFromData( 'Pommel', [0, 0, 0], verts, [], faces )
    
# The Blade Holder should have a thread radius of 18.5 and 17.2 in order to  hold the circuit board holder correctly.
createBladeHolder(256, 2, 18.5, 17.2, 0.8, 0.2, 0.8, 0.3, 2, 3)
#createCPFemaleToFemale(256, 3, 3, 18.5, 17.2, 30.0, 28.7, 0.8, 0.2, 0.8, 0.3, 1)
#createCPMaleToMale(256, 3, 3, 19.0, 17.7, 29.5, 28.2, 0.8, 0.2, 0.8, 0.3, 2)
createHilt(256, 3, 5, 19.5, 18.2, 0.8, 0.2, 0.8, 0.3, 0.5, 2, 2, False)
createPommel(256, 5, 19.5, 18.2, 0.8, 0.2, 0.8, 0.3, 2)
