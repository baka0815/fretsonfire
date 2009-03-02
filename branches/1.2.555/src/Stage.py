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

import Config
from OpenGL.GL import *
import math
import Log
import Theme
import Part
from Audio import Sound
import random

MAXLAYERS = 96
class Layer(object):
  """
  A graphical stage layer that can have a number of animation effects associated with it.
  """
  def __init__(self, stage, drawing):
    """
    Constructor.

    @param stage:     Containing Stage
    @param drawing:   SvgDrawing for this layer. Make sure this drawing is rendered to
                      a texture for performance reasons.
    """
    self.num         = 0
    self.stage       = stage
    self.drawing     = drawing
    self.position    = (0.0, 0.0)
    self.angle       = 0.0
    self.scale       = (1.0, 1.0)
    self.color       = (1.0, 1.0, 1.0, 1.0)
    self.display     = 1
    self.type        = 0
    self.srcBlending = GL_SRC_ALPHA
    self.dstBlending = GL_ONE_MINUS_SRC_ALPHA
    self.effects     = []

  def render(self, visibility):
    if self.type == 1:
      self.renderDrawing(visibility)
    elif self.type == 2:
      self.renderFont(visibility)
    elif self.type == 3:
      self.renderSound(visibility)
      
  def renderDrawing(self, visibility):
    """
    Render the layer.

    @param visibility:  Floating point visibility factor (1 = opaque, 0 = invisibile)
    """
    w, h, = self.stage.engine.view.geometry[2:4]
    v = 1.0 - visibility ** 2
    self.drawing.transform.reset()
    self.drawing.transform.translate(w / 2, h / 2)
    if v > .01:
      self.color = (self.color[0], self.color[1], self.color[2], visibility)
      if self.position[0] < -.25:
        self.drawing.transform.translate(-v * w, 0)
      elif self.position[0] > .25:
        self.drawing.transform.translate(v * w, 0)
    self.drawing.transform.scale(self.scale[0], -self.scale[1])
    self.drawing.transform.translate(self.position[0] * w / 2, -self.position[1] * h / 2)
    self.drawing.transform.rotate(self.angle)

    # Blend in all the effects
    for effect in self.effects:
      effect.apply()
    
    glBlendFunc(self.srcBlending, self.dstBlending)
    if self.display == 1:
      self.drawing.draw(color = self.color)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

  def renderFont(self, visibility):
    """
    Render the layer.

    @param visibility:  Floating point visibility factor (1 = opaque, 0 = invisibile)
    """
    w, h, = self.stage.engine.view.geometry[2:4]
  
    v = 1.0 - visibility ** 2

    #if v > .01:
    #  self.color = (self.color[0], self.color[1], self.color[2], visibility)
    glColor4f(*(self.color))
        # Blend in all the effects
    for effect in self.effects:
      effect.apply()

    w1 = 0.0
    
    if self.fontJustify == True:
      w1, h1 = self.drawing.getStringSize(self.text, self.scale[0] * 0.002)
    
    fontPosition = (((self.position[0] / 2.0) + 0.5 - w1), (((self.position[1] / 2.0) + 0.5) * (float(h) / float(w))))

    glBlendFunc(self.srcBlending, self.dstBlending)
    if self.display == 1:
      if self.text != "":
        self.drawing.render(self.text, fontPosition, scale = self.scale[0] * 0.002)
      #self.stage.engine.data.font.render(self.text, self.position, scale = self.scale[0] * 0.002)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   

  def renderSound(self, visibility):
    """
    Render the layer.

    @param visibility:  Floating point visibility factor (1 = opaque, 0 = invisibile)
    """

    for effect in self.effects:
      effect.apply() 

class Effect(object):
  """
  An animation effect that can be attached to a Layer.
  """
  def __init__(self, layer, options):
    """
    Constructor.

    @param layer:     Layer to attach this effect to.
    @param options:   Effect options (default in parens):
                        intensity - Floating point effect intensity (1.0)
                        trigger   - Effect trigger, one of "none", "beat",
                                    "quarterbeat", "pick", "miss" ("none")
                        period    - Trigger period in ms (500.0)
                        delay     - Trigger delay in periods (0.0)
                        profile   - Trigger profile, one of "step", "linstep",
                                    "smoothstep"
    """
    self.num         = 0
    self.layer       = layer
    self.stage       = layer.stage
    self.intensity   = float(options.get("intensity", 1.0))
    self.trigger     = getattr(self, "trigger" + options.get("trigger", "none").capitalize())
    self.period      = float(options.get("period", 500.0))
    self.delay       = float(options.get("delay", 0.0))

    self.start       = float(options.get("start", -0.5))
    self.stop        = float(options.get("stop", -0.5))
    self.show        = float(options.get("show", -0.5))
    self.mod         = int(options.get("mod", 0))
    self.modCap      = int(options.get("modcap", -1))
    if self.stage.players == 1:
      self.player      = int(options.get("player", 0))      
    else:
      self.player      = int(options.get("player", -1))
    self.part        = options.get("part")
    
    self.triggerProf = getattr(self, options.get("profile", "linstep"))

  def apply(self):
    pass

  def triggerNone(self, player = 0):
    return 0.0

  def triggerBeat(self, player = 0):
    if not self.stage.lastBeatPos:
      return 0.0
    t = self.stage.pos - self.delay * self.stage.beatPeriod - self.stage.lastBeatPos
    return self.intensity * (1.0 - self.triggerProf(0, self.stage.beatPeriod, t))

  def triggerQuarterbeat(self, player = 0):
    if not self.stage.lastQuarterBeatPos:
      return 0.0
    t = self.stage.pos - self.delay * (self.stage.beatPeriod / 4) - self.stage.lastQuarterBeatPos
    return self.intensity * (1.0 - self.triggerProf(0, self.stage.beatPeriod / 4, t))

  def triggerPick(self, player = 0):
    if not self.stage.lastPickPos[player]:
      return 0.0
    t = self.stage.pos - self.delay * self.period - self.stage.lastPickPos[player]
    return self.intensity * (1.0 - self.triggerProf(0, self.period, t))

  def triggerMiss(self, player = 0):
    if not self.stage.lastMissPos[player]:
      return 0.0
    t = self.stage.pos - self.delay * self.period - self.stage.lastMissPos[player]
    return self.intensity * (1.0 - self.triggerProf(0, self.period, t))

  def triggerRockwinner(self, player = 0):
    if not self.stage.lastRockValue[0] or not self.stage.lastRockValue[1]:
      return 0.0
    winning = self.stage.lastRockValue[1] - self.stage.lastRockValue[0]
    winning /= 2
    winning += .5
    return winning
  
  def triggerRock(self, player = 0):        
    if not self.stage.lastRockValue[player]:
      return 0.0
    return self.stage.lastRockValue[player]

  def triggerJurgen(self, player = 0):        
    if not self.stage.lastJurgenValue[player]:
      return 0.0
    return self.stage.lastJurgenValue[player]
  
  def triggerMult(self, player = 0):
    if not self.stage.lastMultValue[player]:
      return 0
    return self.stage.lastMultValue[player]

  def triggerStreak(self, player = 0):
    if not self.stage.lastStreakValue[player]:
      return 0.0
    return self.stage.lastStreakValue[player]

  def triggerTimer(self, player = 0):
    if not self.stage.lastTimerValue:
      return ""
    return self.stage.lastTimerValue

  def triggerParty(self, player = 0):
    if not self.stage.lastPartyValue:
      return ""
    return self.stage.lastPartyValue
  
  def triggerScore(self, player = 0):
    if not self.stage.lastScoreValue[player]:
      return 0.0
    return self.stage.lastScoreValue[player]
  
  def step(self, threshold, x):
    return (x > threshold) and 1 or 0

  def linstep(self, min, max, x):
    if x < min:
      return 0
    if x > max:
      return 1
    return (x - min) / (max - min)

  def smoothstep(self, min, max, x):
    if x < min:
      return 0
    if x > max:
      return 1
    def f(x):
      return -2 * x**3 + 3*x**2
    return f((x - min) / (max - min))

  def sinstep(self, min, max, x):
    return math.cos(math.pi * (1.0 - self.linstep(min, max, x)))

  def getNoteColor(self, note):
    if note >= len(Theme.fretColors) - 1:
      return Theme.fretColors[-1]
    elif note <= 0:
      return Theme.fretColors[0]
    f2  = note % 1.0
    f1  = 1.0 - f2
    c1 = Theme.fretColors[int(note)]
    c2 = Theme.fretColors[int(note) + 1]
    return (c1[0] * f1 + c2[0] * f2, \
            c1[1] * f1 + c2[1] * f2, \
            c1[2] * f1 + c2[2] * f2)

class LightEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.lightNumber = int(options.get("light_number", 0))
    self.ambient     = float(options.get("ambient", 0.5))
    self.contrast    = float(options.get("contrast", 0.5))

  def apply(self):
    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)

    if len(self.stage.averageNotes[curPlayer]) < self.lightNumber + 2:
      self.layer.color = (0.0, 0.0, 0.0, 0.0)
      return
  
    t = self.ambient + self.contrast * t

    c = self.getNoteColor(self.stage.averageNotes[curPlayer][self.lightNumber])
    self.layer.color = (c[0] * t, c[1] * t, c[2] * t, self.intensity)

class RotateEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.angle     = math.pi / 180.0 * float(options.get("angle",  45))

  def apply(self):
    #if not self.stage.lastMissPos:
    #  return
    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)
          
    self.layer.drawing.transform.rotate(t * self.angle)

class WiggleEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.freq     = float(options.get("frequency",  6))
    self.xmag     = float(options.get("xmagnitude", 0.1))
    self.ymag     = float(options.get("ymagnitude", 0.1))

  def apply(self):

    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)    
    
    w, h = self.stage.engine.view.geometry[2:4]
    p = t * 2 * math.pi * self.freq
    s, c = t * math.sin(p), t * math.cos(p)
    self.layer.drawing.transform.translate(self.xmag * w * s, self.ymag * h * c)

class ScaleEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.xmag     = float(options.get("xmagnitude", .1))
    self.ymag     = float(options.get("ymagnitude", .1))
    self.xfactor  = float(options.get("xfactor", 1.0))
    self.yfactor  = float(options.get("yfactor", 1.0))
    self.nextScale = 0

  def apply(self):
    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)    

    self.layer.drawing.transform.scale(self.xfactor + self.xmag * t, self.yfactor + self.ymag * t)

class DisplayEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)


  def apply(self):

    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)    
    
    if self.mod != 0:
      if self.modCap == -1 or t < self.modCap:
        t = t % self.mod
    if self.show != -0.5:
      if self.show != t:
        self.layer.display = 0
      else:
        self.layer.display = 1

    if self.start != -0.5 and self.stop != -0.5:
      if t < self.start or t > self.stop:
        self.layer.display = 0
      else:
        self.layer.display = 1

class ColorEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.rcol     = float(options.get("rcol", 0.0))
    self.gcol     = float(options.get("gcol", 0.0))
    self.bcol     = float(options.get("bcol", 0.0))
    self.defaultColor     = int(options.get("defaultcolor", 0))
    
  def apply(self):

    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)    
    
    if t != "":
      try:
        t = float(t)
      except:
        pass
    if self.mod != 0:
      t = t % self.mod
    if self.show != -0.5:
      if self.show != t:
        return
      else:
        if self.defaultColor == 0:
          self.layer.color = (self.rcol, self.gcol, self.bcol, self.intensity)
        else:
          self.layer.color = Theme.getSelectedColor()

    if self.start != -0.5 and self.stop != -0.5:
      if t < self.start or t > self.stop:
        return
      else:
        if self.defaultColor == 0:
          self.layer.color = (self.rcol, self.gcol, self.bcol, self.intensity)
        else:
          self.layer.color = Theme.getSelectedColor()

class PulseEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.xmag     = float(options.get("xmagnitude", .1))
    self.ymag     = float(options.get("ymagnitude", .1))
    self.xfactor  = float(options.get("xfactor", 1.0))
    self.yfactor  = float(options.get("yfactor", 1.0))
    self.length   = float(options.get("length", 1.0))
    self.lastTrigger = 1
    self.lastPulsePos = 0
    self.pulsing = 0
    self.lastDisplay = self.layer.display
    self.lastColor = self.layer.color

  def apply(self):

    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)    
    
    factor = 1
    diff = 0
    if t > self.lastTrigger or self.pulsing == 1:
      diff = self.stage.pos - self.lastTriggerPos
      if t > self.lastTrigger:
        self.pulsing = 1
        self.lastTriggerPos = self.stage.pos
        self.lastTrigger = t
        self.lastDisplay = self.layer.display
        self.lastColor = self.layer.color
      elif diff > 0 and diff < (self.stage.beatPeriod * self.length):
        if self.show == -0.5 or self.show == t:
          self.layer.display = 1
        factor = .5 + .5 * (diff / self.stage.beatPeriod) ** self.length
        self.layer.color = (self.layer.color[0], self.layer.color[1], self.layer.color[2], min(1, self.length - factor))
        self.layer.drawing.transform.scale(factor, factor)
      else:
        self.lastTriggerPos = 0
        self.pulsing = 0
        self.layer.display = self.lastDisplay
        self.layer.color = self.lastColor
    else:
        self.lastTriggerPos = 0
        self.lastTrigger = t
        self.pulsing = 0
        self.layer.display = self.lastDisplay
        self.layer.color = self.lastColor        

class FlashEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.rcol     = float(options.get("rcol", 0.0))
    self.gcol     = float(options.get("gcol", 0.0))
    self.bcol     = float(options.get("bcol", 0.0))    
    self.length   = float(options.get("length", 1.0))
    self.lastTrigger = 1
    self.lastPulsePos = 0
    self.flashing = 0
    self.lastColor = self.layer.color

  def apply(self):

    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)    
    
    factor = 1
    diff = 0
    if t > self.lastTrigger or self.flashing == 1:
      diff = self.stage.pos - self.lastTriggerPos
      if t > self.lastTrigger:
        self.flashing = 1
        self.lastTriggerPos = self.stage.pos
        self.lastTrigger = t
        self.lastColor = self.layer.color
      elif diff > 0 and diff < (self.stage.beatPeriod * self.length):
        if self.show == -0.5 or self.show == t:
          factor = (1.0 - abs(self.stage.beatPeriod * 1 - diff) / (self.stage.beatPeriod * 1)) ** self.length
          glBegin(GL_TRIANGLE_STRIP)
          glColor4f(self.rcol, self.gcol, self.bcol, (factor - .5) * 1)
          glVertex2f(0, 0)
          glColor4f(self.rcol, self.gcol, self.bcol, (factor - .5) * 1)
          glVertex2f(1, 0)
          glColor4f(self.rcol, self.gcol, self.bcol, (factor - .5) * .25)
          glVertex2f(0, 1)
          glColor4f(self.rcol, self.gcol, self.bcol, (factor - .5) * .25)
          glVertex2f(1, 1)
          glEnd()
      else:
        self.lastTriggerPos = 0
        self.lastTriggerPos = 0
        self.flashing = 0
        self.layer.color = self.lastColor
    else:
        self.lastTriggerPos = 0
        self.lastTrigger = t
        self.flashing = 0
        self.layer.color = self.lastColor
        
class TranslateEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.xend     = float(options.get("xend", 0.0))
    self.yend     = float(options.get("yend", 0.0))
          
    self.xdelta   = (self.xend + self.layer.relxpos - self.layer.position[0]) / 2
    self.ydelta   = (self.yend + self.layer.relypos - self.layer.position[1]) / 2

    self.w, self.h, = self.stage.engine.view.geometry[2:4]
    
  def apply(self):

    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)    
    
    self.layer.drawing.transform.translate(self.xdelta * self.w * t, -self.ydelta * self.h * t)

class TextEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.format     = options.get("format")
    
  def apply(self):

    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)    
    
    if self.format != None:
      self.layer.text = self.format % (t)
    else:
      self.layer.text = t

class TextPulseEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.length     = float(options.get("length", 1.0))
    if self.layer.type != 2:
      raise "Not Font Layer"
    self.lastTrigger = 0
    self.lastTriggerPos = 0
    self.origScale = self.layer.scale
    self.pulsing = 0


  def apply(self):

    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)    
    
    factor = 1
    diff = 0
    if t > self.lastTrigger or self.pulsing == 1:
      diff = self.stage.pos - self.lastTriggerPos
      if t > self.lastTrigger:
        self.pulsing = 1
        self.lastTriggerPos = self.stage.pos
        self.lastTrigger = t
        self.layer.scale = self.origScale      
      elif diff > 0 and diff < (self.stage.beatPeriod * self.length):
        factor += .25 * (1.0 - (diff / (self.stage.beatPeriod * self.length))) ** 2
        self.layer.scale = (factor, factor)
      else:
        self.lastTriggerPos = 0
        self.pulsing = 0
        self.layer.scale = self.origScale
    else:
        self.lastTriggerPos = 0
        self.lastTrigger = t
        self.pulsing = 0
        self.layer.scale = self.origScale

class TextFadeEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.length     = float(options.get("length", 1.0))
    if self.layer.type != 2:
      raise "Not Font Layer"
    self.lastTrigger = 0
    self.lastTriggerPos = 0
    self.fading = 0
    self.origDisplay = self.layer.display


  def apply(self):

    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)    
    
    factor = 1
    diff = 0
    if t > self.lastTrigger or self.fading == 1:
      diff = self.stage.pos - self.lastTriggerPos
      if t > self.lastTrigger:
        self.fading = 1
        self.lastTriggerPos = self.stage.pos
        self.lastTrigger = t     
      elif diff > 0 and diff < (self.stage.beatPeriod * self.length):
        self.layer.display = 1
        factor = (1.0 - (diff / (self.stage.beatPeriod * self.length))) ** 2
        newcolor = (self.layer.color[0], self.layer.color[1], self.layer.color[2], factor)
        glColor4f(*(newcolor))
      else:
        self.lastTriggerPos = 0
        self.fading = 0
        self.layer.display = self.origDisplay
    else:
        self.lastTriggerPos = 0
        self.lastTrigger = t
        self.fading = 0
        self.layer.display = self.origDisplay

class PlayEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    if self.layer.type != 3:
      raise "Not Sound Layer"
    self.soundFile     = options.get("soundfile")
    self.lastSound  = [0.0, 0.0]
    self.stage.engine.resource.load(self, "effectSound", self.loadEffectSound)

    
  def apply(self):

    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)
      
    #Dont play if a part has been set and its not my part
    if self.part and self.part != str(Part.parts.get(self.stage.part[curPlayer])):
      return
    #Only play if the trigger is less than last time
    if t > 0.0 and t >= self.lastSound[curPlayer]:
      if self.effectSound and self.stage.screwUpVolume > 0.0:
        self.stage.sfxChannel.setVolume(self.stage.screwUpVolume)
        self.stage.sfxChannel.play(self.effectSound)
    #Reset timer
    if t > 0.0:
      self.lastSound[curPlayer] = t
    if t == 0.0:
      self.lastSound[curPlayer] = 0.0

  def loadEffectSound(self):
    return Sound(self.stage.engine.resource.fileName(self.soundFile))
  

class PlayRandomEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    if self.layer.type != 3:
      raise "Not Sound Layer"
    if self.stop - self.start < 1:
      raise "random sounds need more than 1 sound"
    self.soundFile     = options.get("soundfile")
    self.lastSound  = [0.0, 0.0]
    self.stage.engine.resource.load(self, "effectSounds", self.loadEffectSounds)

    
  def apply(self):

    if self.player == -1:
      t1 = self.trigger(player = 0)
      t2 = self.trigger(player = 1)
      if t1 >= t2:
        t = t1
        curPlayer = 0
      else:
        t = t2
        curPlayer = 1
    else:
      curPlayer = self.player
      t = self.trigger(player = curPlayer)
      
    #Dont play if a part has been set and its not my part
    if self.part and self.part != str(Part.parts.get(self.stage.part[curPlayer])):
      return
    #Only play if the trigger is less than last time
    if t > 0.0 and t >= self.lastSound[curPlayer]:
      if self.effectSounds and self.stage.screwUpVolume > 0.0:
        self.stage.sfxChannel.setVolume(self.stage.screwUpVolume)
        self.stage.sfxChannel.play(random.choice(self.effectSounds))
    #Reset timer
    if t > 0.0:
      self.lastSound[curPlayer] = t
    if t == 0.0:
      self.lastSound[curPlayer] = 0.0

  def loadEffectSounds(self):
    return [Sound(self.stage.engine.resource.fileName(self.soundFile % i)) for i in range(int(self.start), int(self.stop) + 1)]
  
class Stage(object):
  def __init__(self, guitarScene, configFileNameBase, players = 1, player1Part = 0, player2Part = 0):
    self.scene            = guitarScene
    self.engine           = guitarScene.engine
    self.sfxChannel       = self.engine.audio.getChannel(self.engine.audio.getChannelCount() - 1)
    self.screwUpVolume    = self.engine.config.get("audio", "screwupvol")
    self.players          = players
    self.part             = [player1Part, player2Part]
    self.backgroundLayers = [[],[],[]]
    self.foregroundLayers = [[],[],[]]
    self.textures         = {}
    self.fonts            = {}
    self.reset()


    for i in range(3):
      if i == 0:
        type = ""
      elif i == 1:
        type = "score"
      elif i == 2:
        type = "sound"
        
      if players == 1:
        text = ""
      else:
        text = "-2p"
      configFileName = self.engine.resource.fileName("%s%s%s.ini" % (configFileNameBase, type, text))

      self.buildLayers(configFileName, self.backgroundLayers[i], self.foregroundLayers[i])

  def buildLayers(self, configFileName, backgroundLayers, foregroundLayers):
    typeConfig           = Config.MyConfigParser()

    typeConfig.read(configFileName)    
    # Build the layers
    for i in range(MAXLAYERS):
      drawing = None
      section = "layer%d" % i
      if typeConfig.has_section(section):
        def get(value, type = str, default = None):
          if typeConfig.has_option(section, value):
            return type(typeConfig.get(section, value))
          return default
        
        xres       = get("xres", int, 256)
        yres       = get("yres", int, 256)
        texture    = get("texture")
        font       = get("font")
        sound      = get("sound")
        fontSize   = get("fontsize", int, 22)
        fontScale  = get("xscale", float, 1.0)
        fontRev    = get("fontreversed", bool, False)
        fontAscii  = get("fontasciionly", bool, False)
        fontJustify  = get("fontjustify", bool, False)
        
        if texture != None:
          try:
            drawing = self.textures[texture]
          except KeyError:
            drawing = self.engine.loadSvgDrawing(self, None, texture, textureSize = (xres, yres))
            self.textures[texture] = drawing
        elif font != None:
          try:
            drawing = self.fonts[font]
          except KeyError:
            drawing = self.engine.loadFont(self, None, font, fontSize, fontScale, fontRev, not fontAscii)
            self.fonts[font] = drawing

        elif sound != None:
          drawing = 1
          
        if drawing == None:
          continue
        
        layer = Layer(self, drawing)

        if texture != None:
          layer.type = 1
        elif font != None:
          layer.type = 2
          layer.fontJustify = fontJustify
        elif sound != None:
          layer.type = 3
          
        layer.relative    = get("relative", int)
        layer.num         = i

        if layer.relative == None:
          layer.relxpos = 0.0
          layer.relypos = 0.0
        else:
          layer.relxpos = float(typeConfig.get("layer%d" % layer.relative, "xpos"))
          layer.relypos = float(typeConfig.get("layer%d" % layer.relative, "ypos"))
          
        layer.position    = (get("xpos",   float, 0.0) + layer.relxpos, get("ypos",   float, 0.0) + layer.relypos)
        layer.scale       = (get("xscale", float, 1.0), get("yscale", float, 1.0))
        layer.angle       = math.pi * get("angle", float, 0.0) / 180.0
        layer.srcBlending = globals()["GL_%s" % get("src_blending", str, "src_alpha").upper()]
        layer.dstBlending = globals()["GL_%s" % get("dst_blending", str, "one_minus_src_alpha").upper()]
        layer.color       = (get("color_r", float, 1.0), get("color_g", float, 1.0), get("color_b", float, 1.0), get("color_a", float, 1.0))
        if layer.type == 2:
          if layer.color == (1.0, 1.0, 1.0, 1.0):
            layer.color = Theme.getSelectedColor()
        layer.display     = get("display", int, 1)
        layer.text        = get("text", str, "")

        # Load any effects
        fxClasses = {
          "light":          LightEffect,
          "rotate":         RotateEffect,
          "wiggle":         WiggleEffect,
          "scale":          ScaleEffect,
          "display":        DisplayEffect,
          "color":          ColorEffect,
          "pulse":          PulseEffect,
          "flash":          FlashEffect,
          "translate":      TranslateEffect,
          "text":           TextEffect,
          "textpulse":      TextPulseEffect,
          "textfade":       TextFadeEffect,
          "play":           PlayEffect,
          "playrandom":     PlayRandomEffect,
      
        }
        
        for j in range(MAXLAYERS):
          fxSection = "layer%d:fx%d" % (i, j)
          if typeConfig.has_section(fxSection):
            type = typeConfig.get(fxSection, "type")

            if not type in fxClasses:
              continue

            options = typeConfig.options(fxSection)
            options = dict([(opt, typeConfig.get(fxSection, opt)) for opt in options])

            fx = fxClasses[type](layer, options)
            fx.num = j
            layer.effects.append(fx)

        if get("foreground", int):
          foregroundLayers.append(layer)
        else:
          backgroundLayers.append(layer)

  def reset(self):
    self.lastBeatPos        = None
    self.lastQuarterBeatPos = None
    self.lastMissPos        = [0.0, 0.0]
    self.lastPickPos        = [0.0, 0.0]
    self.beat               = 0
    self.quarterBeat        = 0
    self.pos                = 0.0
    self.playedNotes        = [[],[]]
    self.averageNotes       = [[0.0], [0.0]]
    self.beatPeriod         = 0.0
    self.lastRockValue      = [0.5, 0.5]
    self.lastJurgenValue    = [0.0, 0.0]
    self.lastMultValue      = [1, 1]
    self.lastStreakValue    = [0, 0]
    self.lastTimerValue     = 0
    self.lastPartyValue     = 0
    self.lastScoreValue     = [0, 0]

  def triggerPick(self, pos, notes, player = 0):
    if notes:
      self.lastPickPos[player]      = pos
      self.playedNotes[player]      = self.playedNotes[player][-3:] + [sum(notes) / float(len(notes))]
      self.averageNotes[player][-1] = sum(self.playedNotes[player]) / float(len(self.playedNotes[player]))

  def triggerRock(self, value, player = 0):
    self.lastRockValue[player] = value

  def triggerJurgen(self, value, player = 0):
    self.lastJurgenValue[player] = value
    
  def triggerMult(self, value, player = 0):
    self.lastMultValue[player] = value

  def triggerStreak(self, value, player = 0):
    self.lastStreakValue[player] = value

  def triggerTimer(self, value, player = 0):
    self.lastTimerValue = value

  def triggerParty(self, value, player = 0):
    self.lastPartyValue = value
    
  def triggerScore(self, value, player = 0):
    self.lastScoreValue[player] = value
    
  def triggerMiss(self, pos, player = 0):
    self.lastMissPos[player] = pos

  def triggerQuarterBeat(self, pos, quarterBeat, player = 0):
    self.lastQuarterBeatPos = pos
    self.quarterBeat        = quarterBeat

  def triggerBeat(self, pos, beat, player = 0):
    self.lastBeatPos  = pos
    self.lastBeatPos  = pos
    self.beat         = beat
    player = 0
    self.averageNotes[player] = self.averageNotes[player][-4:] + self.averageNotes[player][-1:]
    player = 1
    self.averageNotes[player] = self.averageNotes[player][-4:] + self.averageNotes[player][-1:]
    
  def _renderLayers(self, layers, visibility):
    self.engine.view.setOrthogonalProjection(normalize = True)
    try:
      for layer in layers:
          layer.render(visibility)
    finally:
      self.engine.view.resetProjection()

  def run(self, pos, period):
    self.pos        = pos
    self.beatPeriod = period
    quarterBeat = int(4 * pos / period)

    if quarterBeat > self.quarterBeat:
      self.triggerQuarterBeat(pos, quarterBeat)

    beat = quarterBeat / 4

    if beat > self.beat:
      self.triggerBeat(pos, beat)

  def render(self, visibility):
    for i in range(3):
      self._renderLayers(self.backgroundLayers[i], visibility)
    self.scene.renderGuitar()
    for i in range(3):
      self._renderLayers(self.foregroundLayers[i], visibility)
