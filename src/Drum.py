#####################################################################
# -*- coding: iso-8859-1 -*-                                        #
# Frets on Fire                                                     #
# Copyright (C) 2006-2009                                           #
#               Sami Kyöstilä                                       #
#               Alex Samonte                                        #
#                                                                   #
# This program is free software; you can redistribute it and/or     #
# modify it under the terms of the GNU General Public License       #
# as published by the Free Software Foundation; either version 2    #
# of the License, or (at your option) any later version.            #
#                                                                   #
# This program is distributed in the hope that it will be useful,   #
# but WITHOUT ANY WARRANTY; without even the implied warranty of    #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     #
# GNU General Public License for more details.                      #
#                                                                   #
# You should have received a copy of the GNU General Public License #
# along with this program; if not, write to the Free Software       #
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,        #
# MA  02110-1301, USA.                                              #
#####################################################################

from Guitar import Guitar
from OpenGL.GL import *
from Mesh import Mesh
from Song import Note, Tempo
import math

class Drum(Guitar):
  def __init__(self, engine, editorMode = False, player = 0):
    Guitar.__init__(self, engine, editorMode, player)
    self.strings = 4
    self.stringsOffset = 1
    engine.resource.load(self,  "openNoteMesh", lambda: Mesh(engine.resource.fileName("opennote.dae")))


    #Drums are colored differently
    temp = self.fretColors[0]
    #self.fretColors[0] = self.fretColors[4]
    #self.fretColors[1] = self.fretColors[2]
    #self.fretColors[2] = self.fretColors[3]
    self.fretColors[4] = temp
    
  def renderOpenNote(self, visibility, f, color):
    if not self.openNoteMesh:
      return

    #mesh = Main Bar (color) 
    #mesh_001 = Bar tips (white) 
    #mesh_002 = top (spot or hopo if no mesh_003) 


    glColor4f(*color)
    
    glPushMatrix()
    glEnable(GL_DEPTH_TEST)
    glDepthMask(1)
    glShadeModel(GL_SMOOTH)

    glRotatef(-90, 0, 1, 0)
    glRotatef(-90, 1, 0, 0)
    glTranslatef(0, -2.5, 0)
    p = 1
    #glColor3f(0.25 * p * color[0], 0.25 * p * color[1], 0.25 * p * color[2])
    self.openNoteMesh.render("Mesh")
    p = 1
    glColor3f(1, 1, 1)
    self.openNoteMesh.render("Mesh_001")
    glColor3f(0.25 * p * color[0], 0.25 * p * color[1], 0.25 * p * color[2])
    #self.openNoteMesh.render("Mesh_002")
    
    glDepthMask(0)
    glPopMatrix()

  def renderNoteBody(self, time, pos, visibility, event): 
    beatsPerUnit = self.beatsPerBoard / self.boardLength
    w = self.boardWidth / self.strings
    c = self.fretColors[event.number]

    x  = (self.strings / 2 - event.number) * w
    x = ((self.strings - event.number + self.stringsOffset) - (((self.strings % 2)) * 1) - (self.strings / 2) - ((not(self.strings % 2)) * 0.5)) * w
    z  = ((time - pos) / self.currentPeriod) / beatsPerUnit
    z2 = ((time + event.length - pos) / self.currentPeriod) / beatsPerUnit

    if z > self.boardLength * .8:
      f = (self.boardLength - z) / (self.boardLength * .2)
    elif z < 0:
      f = min(1, max(0, 1 + z2))
    else:
      f = 1.0
    
    color      = (.1 + .8 * c[0], .1 + .8 * c[1], .1 + .8 * c[2], 1 * visibility * f)
    length     = event.length / self.currentPeriod / beatsPerUnit
    tailOnly   = False
    colortail  = color
    playedstart = False
    playedcontinue = False
    if event.tappable < 2:
      isTappable = False
    else:
      isTappable = True

    if event.number == 0 and not event.played:
      glPushMatrix()
      glTranslatef(x, (1.0 - visibility) ** (event.number + 1), z)
      self.renderOpenNote(visibility, f, color)
      glPopMatrix()
      return
    
    # Clip the played notes to the origin
    if event.played or event.hopod:
      playedstart = True
      tailOnly = True
      length += z
      z = 0
      if length <= 0:
        return -1
    if z < 0 and not (event.played or event.hopod):   
      colortail = (.2 + .4, .2 + .4, .2 + .4, .5 * visibility * f)
    if z + length < -1.0:
      return -1
    sustain = False
    if event.length > (1.4 * (60000.0 / event.noteBpm) / 4):
      sustain = True

    e = event.number
    if playedstart == True:
      for time, event in self.playedNotes:
        if e == event.number:
          playedcontinue = True        
    
    glPushMatrix()
    glTranslatef(x, (1.0 - visibility) ** (e + 1), z)
    self.renderNote2(visibility, f, length, sustain = sustain, color = color, colortail = colortail, tailOnly = tailOnly, playedstart = playedstart, playedcontinue = playedcontinue, isTappable = isTappable)
    glPopMatrix()
    return 1

  def renderFlames(self, visibility, song, pos, controls):
    if not song or self.flameColors[0][0][0] == -1:
      return

    track = song.track[self.player]
    v = 1.0 - visibility

    if self.disableFlameSFX == True:
      for n in range(self.stringsOffset, elf.strings + self.stringsOffset):   
        #Spark
        if self.fretActivity[n]:
          self.renderFlameSpark(v, n)

    #Burst
    if self.disableFlameSFX != True:
      flameLimit = self.flameLimit
      flameLimitHalf = round(self.flameLimit / 2.0)

      for time, event in track.getEvents(pos - self.currentPeriod * 2, pos + self.currentPeriod * self.beatsPerBoard):
        if isinstance(event, Tempo):
          continue
        
        if not isinstance(event, Note):
          continue
        
        if (event.played or event.hopod) and event.flameCount < flameLimit:
          glBlendFunc(GL_ONE, GL_ONE)
                  
          if event.flameCount < flameLimitHalf:
            if event.number == 0:
              for n in range(self.stringsOffset, self.strings + self.stringsOffset):
                self.renderFlameBurst1(v, n, event.flameCount)
            else:
              self.renderFlameBurst1(v, event.number, event.flameCount)
          else:
            if event.number == 0:
              for n in range(self.stringsOffset, self.strings + self.stringsOffset):
                self.renderFlameBurst2(v, n, event.flameCount)
            else:
              self.renderFlameBurst2(v, event.number, event.flameCount)            
         
          glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
          event.flameCount += 1

  def controlsMatchNotes3(self, controls, notes, hopo = False):
    # no notes?
    if not notes:
      return False

    # check each valid chord
    chords = {}
    n = 0
    twochord = 0
    for time, note in notes:
      if note.hopod == True and controls.getState(self.keys[note.number]):
      #if hopo == True and controls.getState(self.keys[note.number]):
        self.playedNotes = []
        return True
      #drums have no chords, treat them individually (this does potentially change how quickly you can gain a multiplier)
      if not time in chords:
        chords[n] = []
      chords[n].append((time, note))
      n += 1

    #Make sure the notes are in the right time order
    chordlist = chords.values()
    chordlist.sort(lambda a, b: cmp(a[0][0], b[0][0]))

    self.missedNotes = []
    for chord in chordlist:
      # matching keys?
      requiredKeys = [note.number for time, note in chord]
      requiredKeys = self.uniqify(requiredKeys)

#No need for twochord in drums
      if len(requiredKeys) > 2 and self.twoChordMax == "NOMATCH":
        twochord = 0
        for n, k in enumerate(self.keys):
          if controls.getState(k):
            twochord += 1
        if twochord == 2:
          skipped = len(requiredKeys) - 2
          requiredKeys = [min(requiredKeys), max(requiredKeys)]
        else:
          twochord = 0
          
      if (self.controlsMatchNote3(controls, chord, requiredKeys, hopo)):
        if twochord != 2:
          for time, note in chord:
            note.played = True
        else:
          for time, note in chord:
            note.skipped = True
          chord[0][1].skipped = False
          chord[-1][1].skipped = False
          chord[0][1].played = True
          chord[-1][1].played = True
        break
      if hopo == True:
        break
      self.missedNotes.append(chord)
    else:
      self.missedNotes = []
    
    for chord in self.missedNotes:
      for time, note in chord:
        note.skipped = True
        note.played = False
    if twochord == 2:
      self.twoChord += skipped
      
    return True
