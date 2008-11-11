#####################################################################
# -*- coding: iso-8859-1 -*-                                        #
#                                                                   #
# Frets on Fire                                                     #
# Copyright (C) 2006 Sami Kyostila                                  #
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

import Player
from Song import Note, Tempo, Bars
from Mesh import Mesh
import Theme

from OpenGL.GL import *
import math

#KEYS = [Player.KEY1, Player.KEY2, Player.KEY3, Player.KEY4, Player.KEY5]
PLAYER1KEYS    = [Player.KEY1, Player.KEY2, Player.KEY3, Player.KEY4, Player.KEY5]
PLAYER1ACTIONS = [Player.ACTION1, Player.ACTION2]
PLAYER2KEYS    = [Player.PLAYER_2_KEY1, Player.PLAYER_2_KEY2, Player.PLAYER_2_KEY3, Player.PLAYER_2_KEY4, Player.PLAYER_2_KEY5]
PLAYER2ACTIONS = [Player.PLAYER_2_ACTION1, Player.PLAYER_2_ACTION2]


class Guitar:
  def __init__(self, engine, editorMode = False, player = 0):
    self.engine         = engine
    self.boardWidth     = 4.0
    self.boardLength    = 12.0
    self.beatsPerBoard  = 5.0
    self.strings        = 5
    self.stringsOffset  = 0
    self.fretWeight     = [0.0] * self.strings
    self.fretActivity   = [0.0] * self.strings
    self.fretColors     = Theme.fretColors
    self.playedNotes    = []
    self.missedNotes    = []
    self.editorMode     = editorMode
    self.selectedString = 0
    self.time           = 0.0
    self.pickStartPos   = 0
    self.leftyMode      = False
    self.currentBpm     = 50.0
    self.currentPeriod  = 60000.0 / self.currentBpm
    self.targetPeriod   = self.currentPeriod
    self.targetBpm      = self.currentBpm
    self.tempoBpm       = self.currentBpm
    self.lastBpmChange  = -1.0
    self.baseBeat       = 0.0

    self.twoChord       = 0
    self.hopoActive     = 0
    self.hopoLast       = -1
    self.hopoColor      = (0, .5, .5)
    self.player         = player
    self.scoreMultiplier = 1
    self.boardspeedMultiplier = 1.0
    
    if player == 0:
      self.keys = PLAYER1KEYS
      self.actions = PLAYER1ACTIONS
    else:
      self.keys = PLAYER2KEYS
      self.actions = PLAYER2ACTIONS  
    
    engine.resource.load(self,  "noteMesh", lambda: Mesh(engine.resource.fileName("note.dae")))
    engine.resource.load(self,  "keyMesh",  lambda: Mesh(engine.resource.fileName("key.dae")))
    engine.loadSvgDrawing(self, "glowDrawing", "glow.svg",  textureSize = (128, 128))
    engine.loadSvgDrawing(self, "neckDrawing", "neck.svg",  textureSize = (256, 256))
    engine.loadSvgDrawing(self, "hitflames1Drawing", "hitflames1.svg",  textureSize = (128, 128))
    engine.loadSvgDrawing(self, "hitflames2Drawing", "hitflames2.svg",  textureSize = (128, 128))
    engine.loadSvgDrawing(self, "hitglowDrawing", "hitglow.svg",  textureSize = (128, 128))
    engine.loadSvgDrawing(self, "hitglow2Drawing", "hitglow2.svg",  textureSize = (128, 128))


    self.hopoColor  = Theme.hopoColor
    self.spotColor = Theme.spotColor   
    self.keyColor = Theme.keyColor
    self.key2Color = Theme.key2Color
    self.tracksColor = Theme.tracksColor
    self.barsColor = Theme.barsColor
    self.flameColors = Theme.flameColors
    self.flameSizes = Theme.flameSizes
    self.glowColor  = Theme.glowColor

    self.tailWidth      = Theme.tailWidth      ## Width of the tails
    self.tailHeight     = Theme.tailHeight     ## Height of the tails
    self.tailRoundness  = Theme.tailRoundness  ## Roundness of the tails, higher number for smoother curves (consumes more cpu too)
    self.tail2Size      = Theme.tail2Size      ## Size for the second part of the tail (the end/tip),
                                               ## if the second part of the tail increases in size, the first part will be shorter
    self.initTails()  ## Initialize the vectors for the tail    
    
    self.twoChordMax = self.engine.config.get("player%d" % (player), "two_chord_max")
    self.disableVBPM  = self.engine.config.get("game", "disable_vbpm")
    self.disableNoteSFX  = self.engine.config.get("video", "disable_notesfx")
    self.disableFretSFX  = self.engine.config.get("video", "disable_fretsfx")
    self.disableFlameSFX  = self.engine.config.get("video", "disable_flamesfx")
    self.disableNoteWavesSFX = self.engine.config.get("video", "disable_notewavessfx")
    self.tracksType  = self.engine.config.get("game", "tracks_type")

    self.boardSpeed  = self.engine.config.get("game", "board_speed")

    self.marginType  = self.engine.config.get("game", "margin")
    self.marginCap = 110.0      

    self.flameLimit = 10
    self.setBPM(self.currentBpm)
    
  def selectPreviousString(self):
    self.selectedString = (self.selectedString - 1) % self.strings

  def selectString(self, string):
    self.selectedString = string % self.strings

  def selectNextString(self):
    self.selectedString = (self.selectedString + 1) % self.strings

  def setBPM(self, bpm):
    self.baseBeat          = 0.0
    self.targetBpm         = bpm
    self.targetPeriod      = round(60000.0 / (self.targetBpm * self.boardspeedMultiplier), 4)
    self.setDynamicBPM(bpm)

  def setDynamicBPM(self, bpm):
    self.currentBpm        = bpm
    self.currentPeriod     = round(60000.0 / (self.currentBpm * self.boardspeedMultiplier), 4)
    self.setMargin(bpm)
    
  def setMargin(self, bpm):
    marginBPM = bpm
    if self.marginType == 1: 
      if bpm > self.marginCap:
        marginBPM = self.marginCap
    
    self.earlyMargin       = 60000.0 / marginBPM / 3.5
    self.lateMargin        = 60000.0 / marginBPM / 3.5
    self.noteReleaseMargin = 60000.0 / marginBPM / 2

  def updateBPM(self):
    diff = self.targetBpm - self.currentBpm
    if diff == 0:
      return
    #max 30bpm change per
    if abs(diff) > 40:
      diff = 40 * (diff/abs(diff))
    elif abs(diff) < .025:
      diff = 0
    if (round((diff * .03), 4) != 0):
      self.currentBpm = round(self.currentBpm + (diff * .025), 4)
    else:
      self.currentBpm = self.targetBpm
      self.targetPeriod = round(60000.0 / (self.targetBpm * self.boardspeedMultiplier), 4)

    if self.currentBpm != self.targetBpm:
      self.setDynamicBPM(self.currentBpm)
      
  def setMultiplier(self, multiplier):
    self.scoreMultiplier = multiplier
    
  def renderNeck(self, visibility, song, pos):
    if not song:
      return

    def project(beat):
      return .5 * beat / beatsPerUnit

    v            = visibility
    w            = self.boardWidth
    l            = self.boardLength

    beatsPerUnit = self.beatsPerBoard / self.boardLength
    offset       = ((pos - self.lastBpmChange) / self.currentPeriod) + self.baseBeat

    glEnable(GL_TEXTURE_2D)
    self.neckDrawing.texture.bind()
    
    glBegin(GL_TRIANGLE_STRIP)
    glColor4f(1, 1, 1, 0)
    glTexCoord2f(0.0, project(offset - 2 * beatsPerUnit))
    glVertex3f(-w / 2, 0, -2)
    glTexCoord2f(1.0, project(offset - 2 * beatsPerUnit))
    glVertex3f( w / 2, 0, -2)
    
    glColor4f(1, 1, 1, v)
    glTexCoord2f(0.0, project(offset - 1 * beatsPerUnit))
    glVertex3f(-w / 2, 0, -1)
    glTexCoord2f(1.0, project(offset - 1 * beatsPerUnit))
    glVertex3f( w / 2, 0, -1)
    
    glTexCoord2f(0.0, project(offset + l * beatsPerUnit * .7))
    glVertex3f(-w / 2, 0, l * .7)
    glTexCoord2f(1.0, project(offset + l * beatsPerUnit * .7))
    glVertex3f( w / 2, 0, l * .7)
    
    glColor4f(1, 1, 1, 0)
    glTexCoord2f(0.0, project(offset + l * beatsPerUnit))
    glVertex3f(-w / 2, 0, l)
    glTexCoord2f(1.0, project(offset + l * beatsPerUnit))
    glVertex3f( w / 2, 0, l)
    glEnd()
    
    glDisable(GL_TEXTURE_2D)
    
  def renderTracks(self, visibility):
    if self.tracksColor[0] == -1:
      return
    w = self.boardWidth / self.strings
    v = 1.0 - visibility

    if self.editorMode:
      x = (self.strings - self.stringsOffset / 2 - self.selectedString) * w
      s = 2 * w / self.strings
      z1 = -0.5 * visibility ** 2
      z2 = (self.boardLength - 0.5) * visibility ** 2
      
      glColor4f(1, 1, 1, .15)
      
      glBegin(GL_TRIANGLE_STRIP)
      glVertex3f(x - s, 0, z1)
      glVertex3f(x + s, 0, z1)
      glVertex3f(x - s, 0, z2)
      glVertex3f(x + s, 0, z2)
      glEnd()

#string width
    sw = 0.025
#    sw = 0.01

    if self.tracksType == 1:
      c = 0.4 * 5 / self.strings
      c2 = 1
    else:
      c = 0.0
      c2 = 0

      
    for n in range(self.stringsOffset, self.strings + c2 + self.stringsOffset):
      x = ((self.strings - n + self.stringsOffset) - (((self.strings % 2)) * 1) - (self.strings / 2) - ((not(self.strings % 2)) * 0.5)) * w    
      glBegin(GL_TRIANGLE_STRIP)
      glColor4f(self.tracksColor[0], self.tracksColor[1], self.tracksColor[2], 0)
      glVertex3f(c + x - sw, -v, -2)
      glVertex3f(c + x + sw, -v, -2)
      glColor4f(self.tracksColor[0], self.tracksColor[1], self.tracksColor[2], (1.0 - v) * .75)
      glVertex3f(c + x - sw, -v, -1)
      glVertex3f(c + x + sw, -v, -1)
      glColor4f(self.tracksColor[0], self.tracksColor[1], self.tracksColor[2], (1.0 - v) * .75)
      glVertex3f(c + x - sw, -v, self.boardLength * .7)
      glVertex3f(c + x + sw, -v, self.boardLength * .7)
      glColor4f(self.tracksColor[0], self.tracksColor[1], self.tracksColor[2], 0)
      glVertex3f(c + x - sw, -v, self.boardLength)
      glVertex3f(c + x + sw, -v, self.boardLength)
      glEnd()
      v *= 2
      
  def renderBars(self, visibility, song, pos):
    if not song or self.tracksColor[0] == -1:
      return
    
    w            = self.boardWidth
    v            = 1.0 - visibility
    sw           = 0.02
    beatsPerUnit = self.beatsPerBoard / self.boardLength
    pos         -= self.lastBpmChange
    offset       = pos / self.currentPeriod * beatsPerUnit
    currentBeat  = pos / self.currentPeriod
    beat         = int(currentBeat)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glPushMatrix()
    while beat < currentBeat + self.beatsPerBoard:
      z = (beat - currentBeat) / beatsPerUnit

      if z > self.boardLength * .8:
        c = (self.boardLength - z) / (self.boardLength * .2)
      elif z < 0:
        c = max(0, 1 + z)
      else:
        c = 1.0
        
      glRotate(v * 90, 0, 0, 1)

      if (beat % 1.0) < 0.001:
        glColor4f(self.barsColor[0], self.barsColor[1], self.barsColor[2], visibility * c * .75)
      else:
        glColor4f(self.barsColor[0], self.barsColor[1], self.barsColor[2], visibility * c * .5)

      glBegin(GL_TRIANGLE_STRIP)
      glVertex3f(-(w / 2), -v, z + sw)
      glVertex3f(-(w / 2), -v, z - sw)
      glVertex3f(w / 2,    -v, z + sw)
      glVertex3f(w / 2,    -v, z - sw)
      glEnd()
      
      if self.editorMode:
        beat += 1.0 / 4.0
      else:
        beat += 1
    glPopMatrix()

    Theme.setSelectedColor(visibility * .5)
    glBegin(GL_TRIANGLE_STRIP)
    glVertex3f(-w / 2, 0,  sw)
    glVertex3f(-w / 2, 0, -sw)
    glVertex3f(w / 2,  0,  sw)
    glVertex3f(w / 2,  0, -sw)
    glEnd()

  def renderBars2(self, visibility, song, pos):
    if not song or self.barsColor[0] == -1:
      return

    w            = self.boardWidth
    beatsPerUnit = self.beatsPerBoard / self.boardLength
    track = song.track[self.player]

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    for time, event in track.getEvents(pos - self.currentPeriod * 2, pos + self.currentPeriod * self.beatsPerBoard):
      if not isinstance(event, Bars):
        continue   

      glPushMatrix()

      z  = ((time - pos) / self.currentPeriod) / beatsPerUnit
      z2 = ((time + event.length - pos) / self.currentPeriod) / beatsPerUnit

      if z > self.boardLength:
        f = (self.boardLength - z) / (self.boardLength * .2)
      elif z < 0:
        f = min(1, max(0, 1 + z2))
      else:
        f = 1.0
        
      if event.barType == 0: #half-beat
        barColorMod0 = 0.64795918367346938775510204081633
        barColorMod1 = 0.6791443850267379679144385026738
        barColorMod2 = 0.75595238095238095238095238095238
        c = (self.barsColor[0] * barColorMod0, self.barsColor[1] * barColorMod1, self.barsColor[2] * barColorMod2)
        sw  = 0.020 #width
        v = 0.0     #height
        color = (.1 + .8 * c[0], .1 + .8 * c[1], .1 + .8 * c[2], .8 * visibility * f)
      elif event.barType == 1: #beat
        barColorMod0 = 1.0
        barColorMod1 = 1.0
        barColorMod2 = 1.0
        c = (self.barsColor[0] * barColorMod0, self.barsColor[1] * barColorMod1, self.barsColor[2] * barColorMod2)
        sw  = 0.025 #width
        v = 0.010   #height
        color = (.1 + .8 * c[0], .1 + .8 * c[1], .1 + .8 * c[2], .8 * visibility * f)
      elif event.barType == 2: #measure
        barColorMod0 = 0.93367346938775510204081632653061
        barColorMod1 = 0.97860962566844919786096256684492
        barColorMod2 = 1.0892857142857142857142857142857
        c = (self.barsColor[0] * barColorMod0, self.barsColor[1] * barColorMod1, self.barsColor[2] * barColorMod2)
        sw  = 0.035 #width
        v = 0.025   #height
        color = (.1 + .8 * c[0], .1 + .8 * c[1], .1 + .8 * c[2], 1 * visibility * f)
        
      glColor4f(*color)
      glBegin(GL_TRIANGLE_STRIP)
      glVertex3f(-(w / 2), v, z + sw)
      glVertex3f(-(w / 2), 0, z - sw)
      glVertex3f(w / 2,    v, z + sw)
      glVertex3f(w / 2,    0, z - sw)
      glEnd()
      glPopMatrix()

  def renderNote(self, length, color, flat = False, tailOnly = False, isTappable = False):
    if not self.noteMesh:
      return

    glColor4f(*color)

    if flat:
      glScalef(1, .1, 1)

    size = (.1, length + 0.00001)
    glBegin(GL_TRIANGLE_STRIP)
    glVertex3f(-size[0], 0, 0)
    glVertex3f( size[0], 0, 0)
    glVertex3f(-size[0], 0, size[1])
    glVertex3f( size[0], 0, size[1])
    glEnd()

    if tailOnly:
      return

    #mesh = outer ring (black) 
    #mesh_001 = main note (key color) 
    #mesh_002 = top (spot or hopo if no mesh_003) 
    #mesh_003 = hopo bump (hopo color)
    
    glPushMatrix()
    glEnable(GL_DEPTH_TEST)
    glDepthMask(1)
    glShadeModel(GL_SMOOTH)

    self.noteMesh.render("Mesh_001")
    glColor3f(self.spotColor[0], self.spotColor[1], self.spotColor[2])
    if isTappable:
      if self.hopoColor[0] == -2:
        glColor4f(*color)
      else:
        glColor3f(self.hopoColor[0], self.hopoColor[1], self.hopoColor[2])
      if(self.noteMesh.find("Mesh_003")) == True:
        self.noteMesh.render("Mesh_003")
        glColor3f(self.spotColor[0], self.spotColor[1], self.spotColor[2])
    self.noteMesh.render("Mesh_002")
    glColor3f(0, 0, 0)
    self.noteMesh.render("Mesh")



    glDepthMask(0)
    glPopMatrix()

  def renderNote2(self, visibility, f, length, sustain, color, colortail, tailOnly = False, playedstart = False, playedcontinue = False, isTappable = False):
    if not self.noteMesh:
      return

    if playedstart == True and playedcontinue == False:
      colortail = (.2 + .4, .2 + .4, .2 + .4, .5 * visibility * f)

    glColor4f(*colortail)

    if sustain:
      size = length + 0.00001

      ## Draw the first part of the tail
      self.polygon1(size - self.tail2Size, colortail)

      ## Draw the second part of the tail
      self.polygon2(size - self.tail2Size, colortail)

    if tailOnly:
      return

    #mesh = outer ring (black) 
    #mesh_001 = main note (key color) 
    #mesh_002 = top (spot or hopo if no mesh_003) 
    #mesh_003 = hopo bump (hopo color)

    glColor4f(*color)
    
    glPushMatrix()
    glEnable(GL_DEPTH_TEST)
    glDepthMask(1)
    glShadeModel(GL_SMOOTH)

    self.noteMesh.render("Mesh_001")
    glColor3f(self.spotColor[0], self.spotColor[1], self.spotColor[2])
    if isTappable:
      if self.hopoColor[0] == -2:
        glColor4f(*color)
      else:
        glColor3f(self.hopoColor[0], self.hopoColor[1], self.hopoColor[2])
      if(self.noteMesh.find("Mesh_003")) == True:
        self.noteMesh.render("Mesh_003")
        glColor3f(self.spotColor[0], self.spotColor[1], self.spotColor[2])
    self.noteMesh.render("Mesh_002")
    glColor3f(0, 0, 0)
    self.noteMesh.render("Mesh")

    glDepthMask(0)
    glPopMatrix()

  def renderNotes(self, visibility, song, pos):
    if not song:
      return

    # Update dynamic period
    self.currentPeriod = round(60000.0 / (self.currentBpm * self.boardspeedMultiplier), 4)
      
    beatsPerUnit = self.beatsPerBoard / self.boardLength
    w = self.boardWidth / self.strings
    track = song.track[self.player]

    for time, event in track.getEvents(pos - self.currentPeriod * 2, pos + self.currentPeriod * self.beatsPerBoard):
      if isinstance(event, Tempo):
        if self.lastBpmChange > 0 and self.disableVBPM == True:
            continue
        if (pos - time > self.currentPeriod or self.lastBpmChange < 0) and time > self.lastBpmChange:
          self.baseBeat         += (time - self.lastBpmChange) / self.currentPeriod
          self.targetBpm         = event.bpm
          self.targetPeriod      = round(60000.0 / (self.targetBpm * self.boardspeedMultiplier), 4)
          self.lastBpmChange     = time
          #self.setDynamicBPM(self.targetBpm)
        continue
      
      if not isinstance(event, Note):
        continue
        
      c = self.fretColors[event.number]

      x  = (self.strings / 2 - event.number) * w
      x = ((self.strings - event.number) - (((self.strings % 2)) * 1) - (self.strings / 2) - ((not(self.strings % 2)) * 0.5)) * w    
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
      flat       = False
      tailOnly   = False


      if event.tappable < 2:
        isTappable = False
      else:
        isTappable = True
      
      # Clip the played notes to the origin
      if z < 0:
        if event.played or event.hopod:
          tailOnly = True
          length += z
          z = 0
          if length <= 0:
            continue
        else:
          color = (.2 + .4, .2 + .4, .2 + .4, .5 * visibility * f)
          flat  = True

      if z + length < -1.0:
        continue
      glPushMatrix()
      glTranslatef(x, (1.0 - visibility) ** (event.number + 1), z)
        
      self.renderNote(length, color = color, flat = flat, tailOnly = tailOnly, isTappable = isTappable)
      glPopMatrix()


    # Draw a waveform shape over the currently playing notes

    if self.disableNoteSFX == True:
      return
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    for time, event in self.playedNotes:
      step  = self.currentPeriod / 16
      t     = time + event.length
      x     = (self.strings / 2 - event.number) * w
      x = ((self.strings - event.number) - (((self.strings % 2)) * 1) - (self.strings / 2) - ((not(self.strings % 2)) * 0.5)) * w    
      c     = self.fretColors[event.number]
      s     = t
      proj  = 1.0 / self.currentPeriod / beatsPerUnit
      zStep = step * proj

      def waveForm(t):
        u = ((t - time) * -.1 + pos - time) / 64.0 + .0001
        return (math.sin(event.number + self.time * -.01 + t * .03) + math.cos(event.number + self.time * .01 + t * .02)) * .1 + .1 + math.sin(u) / (5 * u)

      glBegin(GL_TRIANGLE_STRIP)
      f1 = 0
      while t > time:
        z  = (t - pos) * proj
        if z < 0:
          break
        f2 = min((s - t) / (6 * step), 1.0)
        a1 = waveForm(t) * f1
        a2 = waveForm(t - step) * f2
        glColor4f(c[0], c[1], c[2], .5)
        glVertex3f(x - a1, 0, z)
        glVertex3f(x - a2, 0, z - zStep)
        glColor4f(1, 1, 1, .75)
        glVertex3f(x, 0, z)
        glVertex3f(x, 0, z - zStep)
        glColor4f(c[0], c[1], c[2], .5)
        glVertex3f(x + a1, 0, z)
        glVertex3f(x + a2, 0, z - zStep)
        glVertex3f(x + a2, 0, z - zStep)
        glVertex3f(x - a2, 0, z - zStep)
        t -= step
        f1 = f2
      glEnd()
      
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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

  def renderNoteSFX(self, time, pos, visibility, event):
    beatsPerUnit = self.beatsPerBoard / self.boardLength
    w = self.boardWidth / self.strings
    c = self.fretColors[event.number]


    x = (self.strings / 2 - event.number) * w
    x = ((self.strings - event.number + self.stringsOffset) - (((self.strings % 2)) * 1) - (self.strings / 2) - ((not(self.strings % 2)) * 0.5)) * w    
    z = ((time - pos) / self.currentPeriod) / beatsPerUnit
    length     = event.length / self.currentPeriod / beatsPerUnit
    tailOnly   = False

    if event.played or event.hopod:
      tailOnly = True
      length += z
      z = 0
      if length <= 0:
        return -1

    sustain = False
    if event.length > (1.4 * (60000.0 / event.noteBpm) / 4):
      sustain = True
    else:
      return -1
    
    glPushMatrix()
    glTranslatef(x, 0, z)
    for x in range(10):
      glScalef(1.05, 1, 1)
      glTranslatef(0, .005, 0)
      f = 1.0 - (x / 10.0)
      color = (f * c[0], f * c[1], f * c[2], 1)
      self.renderNote2(visibility, f, length, sustain, color = color, colortail = color, tailOnly = tailOnly)
    glPopMatrix()

  def renderNoteWave(self, time, pos, visibility, event):
    if event.length <= (1.4 * (60000.0 / event.noteBpm) / 4):
      return -1

    beatsPerUnit = self.beatsPerBoard / self.boardLength
    w = self.boardWidth / self.strings     
    step  = self.currentPeriod / 16
    t     = time + event.length
    x     = (self.strings / 2 - event.number) * w
    x = ((self.strings - event.number + self.stringsOffset) - (((self.strings % 2)) * 1) - (self.strings / 2) - ((not(self.strings % 2)) * 0.5)) * w    
    c     = self.fretColors[event.number]
    s     = t
    proj  = 1.0 / self.currentPeriod / beatsPerUnit
    zStep = step * proj
    def waveForm(t):
      u = ((t - time) * -.1 + pos - time) / 64.0 + .0001
      return (math.sin(event.number + self.time * -.01 + t * .03) + math.cos(event.number + self.time * .01 + t * .02)) * .1 + .1 + math.sin(u) / (5 * u)
    glBegin(GL_TRIANGLE_STRIP)
    f1 = 0
    while t > time:
      z  = (t - pos) * proj
      if z < 0:
        break
      f2 = min((s - t) / (6 * step), 1.0)
      a1 = waveForm(t) * f1
      a2 = waveForm(t - step) * f2
      glColor4f(c[0], c[1], c[2], .5)
      glVertex3f(x - a1, 0, z)
      glVertex3f(x - a2, 0, z - zStep)
      glColor4f(1, 1, 1, .75)
      glVertex3f(x, 0, z)
      glVertex3f(x, 0, z - zStep)
      glColor4f(c[0], c[1], c[2], .5)
      glVertex3f(x + a1, 0, z)
      glVertex3f(x + a2, 0, z - zStep)
      glVertex3f(x + a2, 0, z - zStep)
      glVertex3f(x - a2, 0, z - zStep)
      t -= step
      f1 = f2
    glEnd()
    
  def renderNotes2(self, visibility, song, pos):
    if not song:
      return

    # Update dynamic period
    self.currentPeriod = round(60000.0 / (self.currentBpm * self.boardspeedMultiplier), 4)

    if self.boardSpeed == 1:
      self.currentPeriod = self.targetPeriod

    beatsPerUnit = self.beatsPerBoard / self.boardLength
    w = self.boardWidth / self.strings
    track = song.track[self.player]

    for time, event in track.getEvents(pos - self.currentPeriod * 2, pos + self.currentPeriod * self.beatsPerBoard):
      if isinstance(event, Tempo):
        if self.boardSpeed == 1 or (self.lastBpmChange > 0 and self.disableVBPM == True):
            continue
        self.tempoBpm = event.bpm
        if (pos - time > self.currentPeriod or self.lastBpmChange < 0) and time > self.lastBpmChange:
          self.baseBeat         += (time - self.lastBpmChange) / self.currentPeriod
          self.targetBpm         = event.bpm
          self.targetPeriod      = round(60000.0 / (self.targetBpm * self.boardspeedMultiplier), 4)
          self.lastBpmChange     = time
          #self.setDynamicBPM(self.targetBpm)
        continue
      
      if not isinstance(event, Note):
        continue

      if (event.noteBpm == 0.0):
        event.noteBpm = self.tempoBpm      

      if (self.renderNoteBody(time, pos, visibility, event) == -1):
        continue

    if self.disableNoteSFX != True:
      glBlendFunc(GL_ONE, GL_ONE)
      for time, event in self.playedNotes:
        if (self.renderNoteSFX(time, pos, visibility, event) == -1):
          continue
      glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
      
    # Draw a waveform shape over the currently playing notes
    if self.disableNoteWavesSFX != True:
      glBlendFunc(GL_SRC_ALPHA, GL_ONE)
      for time, event in self.playedNotes:
        if (self.renderNoteWave(time, pos, visibility, event) == -1):
          continue
      glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

  def renderFretKey(self, v, controls, string):
    w = self.boardWidth / self.strings
    f = self.fretWeight[string]
    c = self.fretColors[string]

    if f and (controls.getState(self.actions[0]) or controls.getState(self.actions[1])):
      f += 0.25

    glColor4f(.1 + .8 * c[0] + f, .1 + .8 * c[1] + f, .1 + .8 * c[2] + f, 1 - v)
    y = v + f / 6
    #x = (self.strings / 2 - n) * w
    x = ((self.strings - string + self.stringsOffset) - (((self.strings % 2)) * 1) - (self.strings / 2) - ((not(self.strings % 2)) * 0.5)) * w
    if self.keyMesh:
      glPushMatrix()
      glTranslatef(x, y + v * 6, 0)
      glDepthMask(1)
      glEnable(GL_LIGHTING)
      glEnable(GL_LIGHT0)
      glShadeModel(GL_SMOOTH)
      glRotatef(90, 0, 1, 0)
      glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 10.0, -10.0, 0.0))
      glLightfv(GL_LIGHT0, GL_AMBIENT,  (.2, .2, .2, 0.0))
      glLightfv(GL_LIGHT0, GL_DIFFUSE,  (1.0, 1.0, 1.0, 0.0))
      glRotatef(-90, 1, 0, 0)
      glRotatef(-90, 0, 0, 1)
      glColor4f(.1 + .8 * c[0] + f, .1 + .8 * c[1] + f, .1 + .8 * c[2] + f, 1 - v)

      #Mesh - Main fret
      #Key_001 - Top of fret (key_color)
      #Key_002 - Bottom of fret (key2_color)
      #Glow_001 - Only rendered when a note is hit along with the glow.svg
      
      if(self.keyMesh.find("Glow_001")) == True:
        self.keyMesh.render("Mesh")
        glColor3f(self.keyColor[0], self.keyColor[1], self.keyColor[2])
        self.keyMesh.render("Key_001")
        glColor3f(self.key2Color[0], self.key2Color[1], self.key2Color[2])
        self.keyMesh.render("Key_002")
      else:
        self.keyMesh.render()
        
      glDisable(GL_LIGHTING)
      glDisable(GL_LIGHT0)
      glDepthMask(0)
      glPopMatrix()

    return self.fretActivity[string]

  def renderFretGlow(self, v, string):
    size = (.22, .22)
    w = self.boardWidth / self.strings
    f = self.fretWeight[string]
    c = self.fretColors[string]

    x = ((self.strings - string + self.stringsOffset) - (((self.strings % 2)) * 1) - (self.strings / 2) - ((not(self.strings % 2)) * 0.5)) * w
    y = v + f / 6
    
    if self.glowColor[0] == -1:
      s = 1.0
    else:
      s = 0.0
          
    while s < 1:
      ms = s * (math.sin(self.time) * .25 + 1)
      if self.glowColor[0] == -2:
        glColor3f(c[0] * (1 - ms), c[1] * (1 - ms), c[2] * (1 - ms))
      else:
        glColor3f(self.glowColor[0] * (1 - ms), self.glowColor[1] * (1 - ms), self.glowColor[2] * (1 - ms))
            
      glPushMatrix()
      glTranslate(x, y, 0)
      glScalef(1 + .6 * ms * f, 1 + .6 * ms * f, 1 + .6 * ms * f)
      glRotatef( 90, 0, 1, 0)
      glRotatef(-90, 1, 0, 0)
      glRotatef(-90, 0, 0, 1)
      if(self.keyMesh.find("Glow_001")) == True:
        self.keyMesh.render("Glow_001")
      else:
       self.keyMesh.render()
      glPopMatrix()
      s += 0.2
    glColor3f(c[0], c[1], c[2])
    glEnable(GL_TEXTURE_2D)
    self.glowDrawing.texture.bind()
    f += 2

    glPushMatrix()
    glTranslate(x, y, 0)
    glRotate(f * 90 + self.time, 0, 1, 0)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-size[0] * f, 0, -size[1] * f)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( size[0] * f, 0, -size[1] * f)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-size[0] * f, 0,  size[1] * f)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( size[0] * f, 0,  size[1] * f)
    glEnd()
    glPopMatrix()
        
    glDisable(GL_TEXTURE_2D)
  def renderFrets(self, visibility, song, controls):
    v = 1.0 - visibility
    
    glEnable(GL_DEPTH_TEST)
    
    for n in range(self.stringsOffset, self.strings + self.stringsOffset):
      f = self.renderFretKey(v, controls, n)

      if f and self.disableFretSFX != True:
        glBlendFunc(GL_ONE, GL_ONE)
        if self.glowColor[0] != -1:
          self.renderFretGlow(v, n)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
      v *= 1.5
      
    glDisable(GL_DEPTH_TEST)

  def renderFlameSpark(self, v, string):

    w = self.boardWidth / self.strings
    ms = math.sin(self.time) * 0.25 + 1
    f = self.fretActivity[string]
    ff = f
    ff += 1.2
    x = ((self.strings - string + self.stringsOffset) - (((self.strings % 2)) * 1) - (self.strings / 2) - ((not(self.strings % 2)) * 0.5)) * w    
    y = v + f / 6 
      
    glBlendFunc(GL_ONE, GL_ONE)
        
    flameSize = self.flameSizes[self.scoreMultiplier - 1][string]        
    flameColor = self.flameColors[self.scoreMultiplier - 1][string]
    if flameColor[0] == -2:
      flameColor = self.fretColors[string]
      
    flameColorMod0 = 1.1973333333333333333333333333333
    flameColorMod1 = 1.9710526315789473684210526315789
    flameColorMod2 = 10.592592592592592592592592592593

    glColor3f(flameColor[0] * flameColorMod0, flameColor[1] * flameColorMod1, flameColor[2] * flameColorMod2)          
    glEnable(GL_TEXTURE_2D)
    self.hitglowDrawing.texture.bind()    
    glPushMatrix()
    glTranslate(x, y + 0.125, 0)
    glRotate(90, 1, 0, 0)
    glScalef(0.5 + 0.6 * ms * ff, 1.5 + 0.6 * ms * ff, 1 + 0.6 * ms * ff)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-flameSize * ff, 0,  flameSize * ff)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( flameSize * ff, 0,  flameSize * ff)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)

    ff += .3

    #flameSize = self.flameSizes[self.scoreMultiplier - 1][n]
    #flameColor = self.flameColors[self.scoreMultiplier - 1][n]

    flameColorMod0 = 1.1973333333333333333333333333333
    flameColorMod1 = 1.7842105263157894736842105263158
    flameColorMod2 = 12.222222222222222222222222222222
          
    glColor3f(flameColor[0] * flameColorMod0, flameColor[1] * flameColorMod1, flameColor[2] * flameColorMod2)
    glEnable(GL_TEXTURE_2D)
    self.hitglow2Drawing.texture.bind()    
    glPushMatrix()
    glTranslate(x, y + .25, .05)
    glRotate(90, 1, 0, 0)
    glScalef(.40 + .6 * ms * ff, 1.5 + .6 * ms * ff, 1 + .6 * ms * ff)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-flameSize * ff, 0,  flameSize * ff)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( flameSize * ff, 0,  flameSize * ff)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)
          
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

  def renderFlameBurst1(self, v, string, flameCount):
    w = self.boardWidth / self.strings
    ms = math.sin(self.time) * .25 + 1
    ff = 1.25
    x = ((self.strings - string + self.stringsOffset) - (((self.strings % 2)) * 1) - (self.strings / 2) - ((not(self.strings % 2)) * 0.5)) * w    
    y = v + ff / 6

    ff += 1.5
      
    flameSize = self.flameSizes[self.scoreMultiplier - 1][string]        
    flameColor = self.flameColors[self.scoreMultiplier - 1][string]
    if flameColor[0] == -2:
      flameColor = self.fretColors[string]

    #print "one", x, y, ff, ms, self.fretWeight[string], self.fretActivity[string], flameCount, flameSize  
    #print "two", 0.25 + 0.6 * ms * ff, flameCount/6.0 + 0.6 * ms * ff, flameCount / 6.0 + 0.6 * ms * ff          
    glColor3f(flameColor[0], flameColor[1], flameColor[2])
    glEnable(GL_TEXTURE_2D)
    self.hitflames2Drawing.texture.bind()    
    glPushMatrix()
    glTranslate(x, y + .20, 0)
    glRotate(90, 1, 0, 0)
    glScalef(0.25 + 0.6 * ms * ff, flameCount/6.0 + 0.6 * ms * ff, flameCount / 6.0 + 0.6 * ms * ff)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-flameSize * ff, 0,  flameSize * ff)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( flameSize * ff, 0,  flameSize * ff)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D) 

    glColor3f(flameColor[0], flameColor[1], flameColor[2])           
    glEnable(GL_TEXTURE_2D)
    self.hitflames2Drawing.texture.bind()    
    glPushMatrix()
    glTranslate(x - .005, y + .25 + .005, 0)
    glRotate(90, 1, 0, 0)
    glScalef(.30 + .6 * ms * ff, (flameCount + 1) / 5.5 + .6 * ms * ff, (flameCount + 1) / 5.5 + .6 * ms * ff)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-flameSize * ff, 0,  flameSize * ff)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( flameSize * ff, 0,  flameSize * ff)
    glEnd()
    glPopMatrix()	  
    glDisable(GL_TEXTURE_2D)

    glColor3f(flameColor[0], flameColor[1], flameColor[2])
    glEnable(GL_TEXTURE_2D)
    self.hitflames2Drawing.texture.bind()    
    glPushMatrix()
    glTranslate(x+.005, y +.25 +.005, 0)
    glRotate(90, 1, 0, 0)
    glScalef(.35 + .6 * ms * ff, (flameCount + 1) / 5.0 + .6 * ms * ff, (flameCount + 1) / 5.0 + .6 * ms * ff)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-flameSize * ff, 0,  flameSize * ff)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( flameSize * ff, 0,  flameSize * ff)
    glEnd()
    glPopMatrix()	  
    glDisable(GL_TEXTURE_2D)

    glColor3f(flameColor[0], flameColor[1], flameColor[2])  
    glEnable(GL_TEXTURE_2D)
    self.hitflames2Drawing.texture.bind()    
    glPushMatrix()
    glTranslate(x, y +.25 +.005, 0)
    glRotate(90, 1, 0, 0)
    glScalef(.40 + .6 * ms * ff, (flameCount + 1)/ 4.7 + .6 * ms * ff, (flameCount + 1) / 4.7 + .6 * ms * ff)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-flameSize * ff, 0,  flameSize * ff)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( flameSize * ff, 0,  flameSize * ff)
    glEnd()
    glPopMatrix()	  
    glDisable(GL_TEXTURE_2D)


  def renderFlameBurst2(self, v, string, flameCount):
    w = self.boardWidth / self.strings
    ms = math.sin(self.time) * .25 + 1
    ff = 1.25
    x = ((self.strings - string + self.stringsOffset) - (((self.strings % 2)) * 1) - (self.strings / 2) - ((not(self.strings % 2)) * 0.5)) * w    
    y = v + ff / 6
    ff += 1.5
    
    flameSize = self.flameSizes[self.scoreMultiplier - 1][string]        
    flameColor = self.flameColors[self.scoreMultiplier - 1][string]
    if flameColor[0] == -2:
      flameColor = self.fretColors[string]

    #print "one", x, y, ff, ms, self.fretWeight[string], self.fretActivity[string], flameCount, flameSize  
    #print "two", 0.25 + 0.6 * ms * ff, flameCount/6.0 + 0.6 * ms * ff, flameCount / 6.0 + 0.6 * ms * ff          
   
    flameColorMod0 = 0.1 * (self.flameLimit - flameCount)
    flameColorMod1 = 0.1 * (self.flameLimit - flameCount)
    flameColorMod2 = 0.1 * (self.flameLimit - flameCount)
            
    glColor3f(flameColor[0] * flameColorMod0, flameColor[1] * flameColorMod1, flameColor[2] * flameColorMod2)
    glEnable(GL_TEXTURE_2D)
    self.hitflames1Drawing.texture.bind()    
    glPushMatrix()
    glTranslate(x, y + .35, 0)
    glRotate(90, 1, 0, 0)
    glScalef(.25 + .6 * ms * ff, flameCount / 3.0 + .6 * ms * ff, flameCount / 3.0 + .6 * ms * ff)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-flameSize * ff, 0,  flameSize * ff)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( flameSize * ff, 0,  flameSize * ff)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)

    flameColorMod0 = 0.1 * (self.flameLimit - flameCount)
    flameColorMod1 = 0.1 * (self.flameLimit - flameCount)
    flameColorMod2 = 0.1 * (self.flameLimit - flameCount)
            
    glColor3f(flameColor[0] * flameColorMod0, flameColor[1] * flameColorMod1, flameColor[2] * flameColorMod2)      
    glEnable(GL_TEXTURE_2D)
    self.hitflames1Drawing.texture.bind()    
    glPushMatrix()
    glTranslate(x - .005, y + .40 + .005, 0)
    glRotate(90, 1, 0, 0)
    glScalef(.30 + .6 * ms * ff, (flameCount + 1)/ 2.5 + .6 * ms * ff, (flameCount + 1) / 2.5 + .6 * ms * ff)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-flameSize * ff, 0,  flameSize * ff)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( flameSize * ff, 0,  flameSize * ff)
    glEnd()
    glPopMatrix()  
    glDisable(GL_TEXTURE_2D)

    flameColorMod0 = 0.1 * (self.flameLimit - flameCount)
    flameColorMod1 = 0.1 * (self.flameLimit - flameCount)
    flameColorMod2 = 0.1 * (self.flameLimit - flameCount)
            
    glColor3f(flameColor[0] * flameColorMod0, flameColor[1] * flameColorMod1, flameColor[2] * flameColorMod2)
    glEnable(GL_TEXTURE_2D)
    self.hitflames1Drawing.texture.bind()    
    glPushMatrix()
    glTranslate(x + .005, y + .35 + .005, 0)
    glRotate(90, 1, 0, 0)
    glScalef(.35 + .6 * ms * ff, (flameCount + 1) / 2.0 + .6 * ms * ff, (flameCount + 1) / 2.0 + .6 * ms * ff)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-flameSize * ff, 0,  flameSize * ff)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( flameSize * ff, 0,  flameSize * ff)
    glEnd()
    glPopMatrix()  
    glDisable(GL_TEXTURE_2D)

    flameColorMod0 = 0.1 * (self.flameLimit - flameCount)
    flameColorMod1 = 0.1 * (self.flameLimit - flameCount)
    flameColorMod2 = 0.1 * (self.flameLimit - flameCount)
            
    glColor3f(flameColor[0] * flameColorMod0, flameColor[1] * flameColorMod1, flameColor[2] * flameColorMod2)
    glEnable(GL_TEXTURE_2D)
    self.hitflames1Drawing.texture.bind()    
    glPushMatrix()
    glTranslate(x+.005, y +.35 +.005, 0)
    glRotate(90, 1, 0, 0)
    glScalef(.40 + .6 * ms * ff, (flameCount + 1) / 1.7 + .6 * ms * ff, (flameCount + 1) / 1.7 + .6 * ms * ff)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( flameSize * ff, 0, -flameSize * ff)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-flameSize * ff, 0,  flameSize * ff)
    glTexCoord2f(1.0, 1.0)
    glVertex3f( flameSize * ff, 0,  flameSize * ff)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)
    
  def renderFlames(self, visibility, song, pos, controls):
    if not song or self.flameColors[0][0][0] == -1:
      return

    track = song.track[self.player]
    v = 1.0 - visibility

    if self.disableFlameSFX != True:
      for n in range(self.stringsOffset, self.strings + self.stringsOffset):   
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
            self.renderFlameBurst1(v, event.number, event.flameCount)
          else:
            self.renderFlameBurst2(v, event.number, event.flameCount)            
         
          glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
          event.flameCount += 1

  def initTails(self):
    width = self.tailWidth            
    height = self.tailHeight  
    v1 = [0 for i in range(4)]
    v2 = [0 for i in range(4)]

    ##Init. vectors for the first part of the tail
    v1[0] = self.CREATE_VECTOR(-width, 0, 0)
    v1[1] = self.CREATE_VECTOR(-width, height, 0)
    v1[2] = self.CREATE_VECTOR(width, height, 0)
    v1[3] = self.CREATE_VECTOR(width, 0, 0)

    self.SMixBezier1(v1, 3)

    ##Init. vectors for the second part of the tail
    v1[0] = self.CREATE_VECTOR(-width, 0, 0)
    v1[1] = self.CREATE_VECTOR(-width, height, 0)
    v1[2] = self.CREATE_VECTOR(width, height, 0)
    v1[3] = self.CREATE_VECTOR(width, 0, 0)
    
    v2[0] = self.CREATE_VECTOR(-width, 0, 0)
    v2[1] = self.CREATE_VECTOR(-width, 0, self.tail2Size)
    v2[2] = self.CREATE_VECTOR(width, 0, self.tail2Size)
    v2[3] = self.CREATE_VECTOR(width, 0, 0)

    self.SMixBezier2(v1, 3, v2, 3)    
    

  def CREATE_VECTOR(self, x, y, z):
    C = [0 for i in range(4)]
    C[0]=x
    C[1]=y
    C[2]=z
    C[3]=1
    return C

  def Bern(self, s, j, n):
    return (self.fac(n)/(self.fac(n-j)*self.fac(j)))*pow(1-s, n-j)*pow(s,j)

  def fac(self, n):
    resul = 1  
    if n == 0:
      resul = 1
    else :
      resul = self.fac(n-1) * n     
    return  resul

  def PtBezier(self, s, p, np):
    V = self.CREATE_VECTOR(0, 0, 0)
    k = 0
    while k <= np:
      V = self.addV(V, self.mulV(self.Bern(s, k, np), p[k]))
      k += 1 
    return V

  def SMixBezier1(self, p, m1):
    N = self.tailRoundness   
    self.pp1 = [0 for i in range((N+1)*2)]
    a = 0.0
    b = 1.0
    c = 0.0
    d = 1.0

    ## Vectors for the first part of the tail (Incomplete, more vectors will be added
    ## when the size of the tail is known)
    j = 0
    i = 0
    v = c + (d - c) * j / N
    k = 0
    while k <= N:
      u1 = a+((b-a)*k)/N
      u2 = c+((d-c)*k)/N
      self.pp1[i] = self.mulV((1-v), self.PtBezier(u1, p, m1)) 
      k += 1
      i += 1

  def SMixBezier2(self, p, m1, q, m2):
    N = self.tailRoundness  
    vv = [0 for i in range((N+1)*(N+1))]
    a = 0.0
    b = 1.0
    c = 0.0
    d = 1.0

    ## Vectors for the second part of the tail (Complete, but unorganized)
    ## CURVE ON EACH HORIZONTAL********************
    j = 0
    i = 0
    while j <= N:
      v = c + (d - c) * j / N
      k = 0
      while k <= N:
        u1 = a+((b-a)*k)/N
        u2 = c+((d-c)*k)/N
        vv[i] = self.addV(self.mulV((1-v), self.PtBezier(u1, p, m1)), self.mulV(v, self.PtBezier(u2, q, m2))) 
        k += 1
        i += 1
      j += 1

    dd = (N+1)*(N+1) + N*(N-1)
    start = [0 for i in range(N+1)]
    i = 0
    while i <= N:
      start[i] = i*(N+1)
      i += 1
    self.pp2 = [0 for i in range(dd)]

    ## Rearrange vectors so that they form triangles and can be drawn
    i = 0
    k = 0
    mm = 0
    lim = 0
    while mm <= N-1:
      if lim == 0:
        lim = N
        var1 = k
        var2 = lim
        adj = -2
        inc = 1
      else:
        lim = 0
        var1 = lim
        var2 = k
        adj = 2
        inc = -1
      while var1 <= var2:
        self.pp2[i] = vv[start[k] + mm]
        self.pp2[i+1] = vv[start[k] + mm + 1]
        if var1 == var2 and (i+2) != dd:
          self.pp2[i+2] = vv[start[k] + mm + 2]
        k += inc
        i += 2
        if lim == N:
          var1 = k
        else:
          var2 = k
      i += 1
      k += adj
      mm += 1


  def addV(self, c, v):
    return self.CREATE_VECTOR(c[0]+v[0], c[1]+v[1], c[2]+v[2])


  def  mulV(self, s, u):
    C = [0 for i in range(4)]
    C[0] = s * u[0]
    C[1] = s * u[1]
    C[2] = s * u[2]
    C[3] = 1
    return  C


  def polygon1(self, size, colortail):
    if size < 0:
        return
    
    V = self.CREATE_VECTOR(0, 0, size)
    N = len(self.pp1) / 2 - 1

    ## Complete the vectors for the first part of the tail, unorganized
    i = 0
    while i <= N:
      self.pp1[i+N+1] = self.addV(V, self.pp1[i]) 
      i += 1

    dd = ((N+1)*2) + (N-1)
    start = [0 for i in range(2)]
    i = 0
    while i <= 1:
      start[i] = i*(N+1)
      i += 1
    vv = [0 for i in range(dd)]

    ## Rearrange the vectors so that they form triangles and can be drawn
    i = 0
    k = 0
    mm = 0
    lim = 0
    while mm <= N-1:
      if lim == 0:
        lim = 1
        var1 = k
        var2 = lim
        adj = -2
        inc = 1
      else:
        lim = 0
        var1 = lim
        var2 = k
        adj = 2
        inc = -1
      while var1 <= var2:
        vv[i] = self.pp1[start[k] + mm]
        vv[i+1] = self.pp1[start[k] + mm + 1]
        if var1 == var2 and (i+2) != dd:
          vv[i+2] = self.pp1[start[k] + mm + 2]
        k += inc
        i += 2
        if lim == 1:
          var1 = k
        else:
          var2 = k
      i += 1
      k += adj
      mm += 1    

    ## Draw the first part of the tail
    j = 0
    glBegin(GL_TRIANGLE_STRIP)
    while j <= (dd - 1):
      u = vv[j]
      if u[0] > (self.tailWidth*2.0/3.0):
        glColor4f(0.7*colortail[0], 0.7*colortail[1], 0.7*colortail[2], colortail[3])
      elif u[0] < (-self.tailWidth*2.0/3.0):
        glColor4f(*colortail)
      else:
        glColor4f(1.5*colortail[0], 1.5*colortail[1], 1.5*colortail[2], colortail[3])
      glVertex3f(u[0], u[1], u[2])
      j += 1
    glEnd()


  def polygon2(self, size, colortail):
    V = self.CREATE_VECTOR(0, 0, size)
    vv = [0 for i in range(len(self.pp2))]

    ## Move all the vectors in the z axis to their corresponding location
    i = 0
    while i <= len(self.pp2)-1:
      vv[i] = self.addV(V, self.pp2[i])
      i += 1

    ## Draw the second part of the tail
    j = 0
    glBegin(GL_TRIANGLE_STRIP)
    while j <= len(vv)-1:
      u = vv[j]
      if u[0] > (self.tailWidth*2.0/3.0):
        glColor4f(0.7*colortail[0], 0.7*colortail[1], 0.7*colortail[2], colortail[3])
      elif u[0] < (-self.tailWidth*2.0/3.0):
        glColor4f(*colortail)
      else:
        glColor4f(1.5*colortail[0], 1.5*colortail[1], 1.5*colortail[2], colortail[3])
      if u[2] < 0:
        glColor4f(0.0, 0.0, 0.0, 0.0)
      glVertex3f(u[0], u[1], u[2])
      j += 1
    glEnd()
        
  def render(self, visibility, song, pos, controls):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_COLOR_MATERIAL)
    if self.leftyMode:
      glScale(-1, 1, 1)

    self.renderNeck(visibility, song, pos)
    self.renderTracks(visibility)
    self.renderBars2(visibility, song, pos)
    self.renderNotes2(visibility, song, pos)
    self.renderFrets(visibility, song, controls)
    self.renderFlames(visibility, song, pos, controls)
    
    if self.leftyMode:
      glScale(-1, 1, 1)

  def getMissedNotes(self, song, pos, catchup = False):
    if not song:
      return

    m1      = self.lateMargin
    m2      = self.lateMargin * 2

    #if catchup == True:
    #  m2 = 0
      
    track   = song.track[self.player]
    notes   = [(time, event) for time, event in track.getEvents(pos - m1, pos - m2) if isinstance(event, Note)]
    notes   = [(time, event) for time, event in notes if (time >= (pos - m2)) and (time <= (pos - m1))]
    notes   = [(time, event) for time, event in notes if not event.played and not event.hopod and not event.skipped]

    if catchup == True:
      for time, event in notes:
        event.skipped = True

    return sorted(notes, key=lambda x: x[1].number)        
    #return notes

  def getRequiredNotes(self, song, pos):
    track   = song.track[self.player]
    notes = [(time, event) for time, event in track.getEvents(pos - self.lateMargin, pos + self.earlyMargin) if isinstance(event, Note)]
    notes = [(time, event) for time, event in notes if not event.played]
    notes = [(time, event) for time, event in notes if (time >= (pos - self.lateMargin)) and (time <= (pos + self.earlyMargin))]
    if notes:
      t     = min([time for time, event in notes])
      notes = [(time, event) for time, event in notes if time - t < 1e-3]
    return sorted(notes, key=lambda x: x[1].number)

  def getRequiredNotes2(self, song, pos, hopo = False):

    track   = song.track[self.player]
    notes = [(time, event) for time, event in track.getEvents(pos - self.lateMargin, pos + self.earlyMargin) if isinstance(event, Note)]
    notes = [(time, event) for time, event in notes if not (event.hopod or event.played)]
    notes = [(time, event) for time, event in notes if (time >= (pos - self.lateMargin)) and (time <= (pos + self.earlyMargin))]
    if notes:
      t     = min([time for time, event in notes])
      notes = [(time, event) for time, event in notes if time - t < 1e-3]
      
    return sorted(notes, key=lambda x: x[1].number)
    
  def getRequiredNotes3(self, song, pos, hopo = False):

    track   = song.track[self.player]
    notes = [(time, event) for time, event in track.getEvents(pos - self.lateMargin, pos + self.earlyMargin) if isinstance(event, Note)]
    notes = [(time, event) for time, event in notes if not (event.hopod or event.played or event.skipped)]
    notes = [(time, event) for time, event in notes if (time >= (pos - self.lateMargin)) and (time <= (pos + self.earlyMargin))]
    #if notes:
    #  t     = min([time for time, event in notes])
    #  notes = [(time, event) for time, event in notes if time - t < 1e-3]

    return sorted(notes, key=lambda x: x[1].number)

  def controlsMatchNotes(self, controls, notes):
    # no notes?
    if not notes:
      return False
  
    # check each valid chord
    chords = {}
    for time, note in notes:
      if not time in chords:
        chords[time] = []
      chords[time].append((time, note))

    #Make sure the notes are in the right time order
    chordlist = chords.values()
    chordlist.sort(lambda a, b: cmp(a[0][0], b[0][0]))

    twochord = 0
    for chord in chordlist:
      # matching keys?
      requiredKeys = [note.number for time, note in chord]
      requiredKeys = self.uniqify(requiredKeys)
      
      if len(requiredKeys) > 2 and self.twoChordMax == True:
        twochord = 0
        for n, k in enumerate(self.keys):
          if controls.getState(k):
            twochord += 1
        if twochord == 2:
          skipped = len(requiredKeys) - 2
          requiredKeys = [min(requiredKeys), max(requiredKeys)]
        else:
          twochord = 0

      for n, k in enumerate(self.keys):
        if n in requiredKeys and not controls.getState(k):
          return False
        if not n in requiredKeys and controls.getState(k):
          # The lower frets can be held down
          if n > max(requiredKeys):
            return False
      if twochord != 0:
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
    if twochord == 2:
      self.twoChord += skipped

    return True

  def controlsMatchNotes2(self, controls, notes, hopo = False):
    # no notes?
    if not notes:
      return False

    # check each valid chord
    chords = {}
    for time, note in notes:
      if note.hopod == True and controls.getState(self.keys[note.number]):
      #if hopo == True and controls.getState(self.keys[note.number]):
        self.playedNotes = []
        return True
      if not time in chords:
        chords[time] = []
      chords[time].append((time, note))

    #Make sure the notes are in the right time order
    chordlist = chords.values()
    chordlist.sort(lambda a, b: cmp(a[0][0], b[0][0]))

    twochord = 0
    for chord in chordlist:
      # matching keys?
      requiredKeys = [note.number for time, note in chord]
      requiredKeys = self.uniqify(requiredKeys)

      if len(requiredKeys) > 2 and self.twoChordMax == True:
        twochord = 0
        for n, k in enumerate(self.keys):
          if controls.getState(k):
            twochord += 1
        if twochord == 2:
          skipped = len(requiredKeys) - 2
          requiredKeys = [min(requiredKeys), max(requiredKeys)]
        else:
          twochord = 0
        
      for n, k in enumerate(self.keys):
        if n in requiredKeys and not controls.getState(k):
          return False
        if not n in requiredKeys and controls.getState(k):
          # The lower frets can be held down
          if hopo == False and n >= min(requiredKeys):
            return False
      if twochord != 0:
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
        
    if twochord == 2:
      self.twoChord += skipped
      
    return True

  def controlsMatchNotes3(self, controls, notes, hopo = False):
    # no notes?
    if not notes:
      return False

    # check each valid chord
    chords = {}
    for time, note in notes:
      if note.hopod == True and controls.getState(self.keys[note.number]):
      #if hopo == True and controls.getState(self.keys[note.number]):
        self.playedNotes = []
        return True
      if not time in chords:
        chords[time] = []
      chords[time].append((time, note))

    #Make sure the notes are in the right time order
    chordlist = chords.values()
    chordlist.sort(lambda a, b: cmp(a[0][0], b[0][0]))

    self.missedNotes = []
    twochord = 0
    for chord in chordlist:
      # matching keys?
      requiredKeys = [note.number for time, note in chord]
      requiredKeys = self.uniqify(requiredKeys)

      if len(requiredKeys) > 2 and self.twoChordMax == True:
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

  def uniqify(self, seq, idfun=None): 
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result
  
  def controlsMatchNote3(self, controls, chordTuple, requiredKeys, hopo):
    if len(chordTuple) > 1:
    #Chords must match exactly
      for n, k in enumerate(self.keys):
        if (n in requiredKeys and not controls.getState(k)) or (n not in requiredKeys and controls.getState(k)):
          return False
    else:
    #Single Note must match that note
      requiredKey = requiredKeys[0]
      if not controls.getState(self.keys[requiredKey]):
        return False
      if hopo == False:
      #Check for higher numbered frets if not a HOPO
        for n, k in enumerate(self.keys):
          if n > requiredKey:
          #higher numbered frets cannot be held
            if controls.getState(k):
              return False
    return True

  def areNotesTappable(self, notes):
    if not notes:
      return
    for time, note in notes:
      if note.tappable > 1:
        return True
    return False
  
  def startPick(self, song, pos, controls, hopo = False):
    if hopo == True:
      res = startPick2(song, pos, controls, hopo)
      return res
    if not song:
      return False
    
    self.playedNotes = []
    
    notes = self.getRequiredNotes(song, pos)

    if self.controlsMatchNotes(controls, notes):
      self.pickStartPos = pos
      for time, note in notes:
        if note.skipped == True:
          continue
        self.pickStartPos = max(self.pickStartPos, time)
        note.played       = True
        self.playedNotes.append([time, note])
      return True
    return False

  def startPick2(self, song, pos, controls, hopo = False):
    if not song:
      return False
    
    self.playedNotes = []
    
    notes = self.getRequiredNotes2(song, pos, hopo)

    if self.controlsMatchNotes2(controls, notes, hopo):
      self.pickStartPos = pos
      for time, note in notes:
        if note.skipped == True:
          continue
        self.pickStartPos = max(self.pickStartPos, time)
        if hopo:
          note.hopod        = True
        else:
          note.played       = True
        if note.tappable == 1 or note.tappable == 2:
          self.hopoActive = time
        elif note.tappable == 3:
          self.hopoActive = -time
        else:
          self.hopoActive = 0
        self.playedNotes.append([time, note])
      self.hopoLast     = note.number
      return True
    return False

  def startPick3(self, song, pos, controls, hopo = False):
    if not song:
      return False
    
    self.playedNotes = []
    
    notes = self.getRequiredNotes3(song, pos, hopo)

    self.controlsMatchNotes3(controls, notes, hopo)
    for time, note in notes:
      if note.played != True:
        continue
      self.pickStartPos = pos
      self.pickStartPos = max(self.pickStartPos, time)
      if hopo:
        note.hopod        = True
      else:
        note.played       = True
      if note.tappable == 1 or note.tappable == 2:
        self.hopoActive = time
      elif note.tappable == 3:
        self.hopoActive = -time
      else:
        self.hopoActive = 0
      self.hopoLast     = note.number
      self.playedNotes.append([time, note])
    if len(self.playedNotes) != 0:
      return True
    return False

  def endPick(self, pos):
    for time, note in self.playedNotes:
      if time + note.length > pos + self.noteReleaseMargin:
        self.playedNotes = []
        return False
      
    self.playedNotes = []
    return True
    
  def getPickLength(self, pos):
    if not self.playedNotes:
      return 0.0
    
    # The pick length is limited by the played notes
    pickLength = pos - self.pickStartPos
    for time, note in self.playedNotes:
      pickLength = min(pickLength, note.length)
    return pickLength

  def run(self, ticks, pos, controls):
    self.time += ticks
    
    # update frets
    if self.editorMode:
      if (controls.getState(self.actions[0]) or controls.getState(self.actions[1])):
        activeFrets = [i for i, k in enumerate(self.keys) if controls.getState(k)] or [self.selectedString]
      else:
        activeFrets = []
    else:
      activeFrets = [note.number for time, note in self.playedNotes]
    
    for n in range(self.stringsOffset, self.strings + self.stringsOffset):
      if controls.getState(self.keys[n]) or (self.editorMode and self.selectedString == n):
        self.fretWeight[n] = 0.5
      else:
        self.fretWeight[n] = max(self.fretWeight[n] - ticks / 64.0, 0.0)
      if n in activeFrets:
        self.fretActivity[n] = min(self.fretActivity[n] + ticks / 32.0, 1.0)
      else:
        self.fretActivity[n] = max(self.fretActivity[n] - ticks / 64.0, 0.0)

    for time, note in self.playedNotes:
      if pos > time + note.length:
        return False

    # update bpm
    self.updateBPM()  
    return True
