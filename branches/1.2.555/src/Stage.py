#####################################################################
# -*- coding: iso-8859-1 -*-                                        #
#                                                                   #
# Frets on Fire                                                     #
# Copyright (C) 2006 Sami Kyöstilä                                  #
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

MAXLAYERS = 64
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

    #fontPosition = ((self.position[0] + 0.5) * w / 2, (self.position[1] + 0.5) * h / 2)      
    glBlendFunc(self.srcBlending, self.dstBlending)
    if self.display == 1:
      #self.drawing.render(self.text, fontPosition, scale = self.scale[0])
      self.stage.engine.data.font.render(self.text, self.position, scale = self.scale[0] * 0.002)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    

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
    
    self.triggerProf = getattr(self, options.get("profile", "linstep"))

  def apply(self):
    pass

  def triggerNone(self):
    return 0.0

  def triggerBeat(self):
    if not self.stage.lastBeatPos:
      return 0.0
    t = self.stage.pos - self.delay * self.stage.beatPeriod - self.stage.lastBeatPos
    return self.intensity * (1.0 - self.triggerProf(0, self.stage.beatPeriod, t))

  def triggerQuarterbeat(self):
    if not self.stage.lastQuarterBeatPos:
      return 0.0
    t = self.stage.pos - self.delay * (self.stage.beatPeriod / 4) - self.stage.lastQuarterBeatPos
    return self.intensity * (1.0 - self.triggerProf(0, self.stage.beatPeriod / 4, t))

  def triggerPick(self):
    if not self.stage.lastPickPos:
      return 0.0
    t = self.stage.pos - self.delay * self.period - self.stage.lastPickPos
    return self.intensity * (1.0 - self.triggerProf(0, self.period, t))

  def triggerMiss(self):
    if not self.stage.lastMissPos:
      return 0.0
    t = self.stage.pos - self.delay * self.period - self.stage.lastMissPos
    return self.intensity * (1.0 - self.triggerProf(0, self.period, t))

  def triggerRock(self):
    if not self.stage.lastRockValue:
      return 0.0
    return self.stage.lastRockValue

  def triggerMult(self):
    if not self.stage.lastMultValue:
      return 0.0
    return self.stage.lastMultValue

  def triggerStreak(self):
    if not self.stage.lastStreakValue:
      return 0.0
    return self.stage.lastStreakValue

  def triggerTimer(self):
    if not self.stage.lastTimerValue:
      return 0.0
    return self.stage.lastTimerValue

  def triggerScore(self):
    if not self.stage.lastScoreValue:
      return 0.0
    return self.stage.lastScoreValue
  
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
    if len(self.stage.averageNotes) < self.lightNumber + 2:
      self.layer.color = (0.0, 0.0, 0.0, 0.0)
      return

    t = self.trigger()
    t = self.ambient + self.contrast * t
    c = self.getNoteColor(self.stage.averageNotes[self.lightNumber])
    self.layer.color = (c[0] * t, c[1] * t, c[2] * t, self.intensity)

class RotateEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.angle     = math.pi / 180.0 * float(options.get("angle",  45))

  def apply(self):
    #if not self.stage.lastMissPos:
    #  return
    
    t = self.trigger()
    self.layer.drawing.transform.rotate(t * self.angle)

class WiggleEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.freq     = float(options.get("frequency",  6))
    self.xmag     = float(options.get("xmagnitude", 0.1))
    self.ymag     = float(options.get("ymagnitude", 0.1))

  def apply(self):
    t = self.trigger()
    
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
    t = self.trigger()
    self.layer.drawing.transform.scale(self.xfactor + self.xmag * t, self.yfactor + self.ymag * t)

class DisplayEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)


  def apply(self):
    t = float(self.trigger())
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

  def apply(self):
    t = float(self.trigger())
    if self.mod != 0:
      t = t % self.mod
    if self.show != -0.5:
      if self.show != t:
        return
      else:
        self.layer.color = (self.rcol, self.gcol, self.bcol, self.intensity)

    if self.start != -0.5 and self.stop != -0.5:
      if t < self.start or t > self.stop:
        return
      else:
        self.layer.color = (self.rcol, self.gcol, self.bcol, self.intensity)

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

  def apply(self):
    t = float(self.trigger())
    factor = 1
    diff = 0
    if t > self.lastTrigger or self.pulsing == 1:
      diff = self.stage.pos - self.lastTriggerPos
      if t > self.lastTrigger:
        self.pulsing = 1
        self.lastTriggerPos = self.stage.pos
        self.lastTrigger = t
        self.lastDisplay = self.layer.display
      elif diff > 0 and diff < (self.stage.beatPeriod * self.length):
        if self.show == -0.5 or self.show == t:
          self.layer.display = 1
        factor = .5 + .5 * (diff / self.stage.beatPeriod) ** self.length 
        self.layer.drawing.transform.scale(factor, factor)      
      else:
        self.lastTriggerPos = 0
        self.pulsing = 0
        self.layer.display = self.lastDisplay
    else:
        self.lastTriggerPos = 0
        self.lastTrigger = t
        self.pulsing = 0
        self.layer.display = self.lastDisplay
        

class TranslateEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.xend     = float(options.get("xend", 0.0))
    self.yend     = float(options.get("yend", 0.0))

    self.xdelta   = (self.xend - self.layer.position[0]) / 2
    self.ydelta   = (self.yend - self.layer.position[1]) / 2

    self.w, self.h, = self.stage.engine.view.geometry[2:4]
    
  def apply(self):
    t = self.trigger()

    self.layer.drawing.transform.translate(self.xdelta * self.w * t, -self.ydelta * self.h * t)

class TextEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.format     = options.get("format")
    
  def apply(self):
    t = self.trigger()

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
    t = float(self.trigger())
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
                      
class Stage(object):
  def __init__(self, guitarScene, configFileName):
    self.scene            = guitarScene
    self.engine           = guitarScene.engine
    self.config           = Config.MyConfigParser()
    self.backgroundLayers = []
    self.foregroundLayers = []
    self.textures         = {}
    self.fonts            = {}
    self.reset()

    self.config.read(configFileName)

    # Build the layers
    for i in range(MAXLAYERS):
      drawing = None
      section = "layer%d" % i
      if self.config.has_section(section):
        def get(value, type = str, default = None):
          if self.config.has_option(section, value):
            return type(self.config.get(section, value))
          return default
        
        xres       = get("xres", int, 256)
        yres       = get("yres", int, 256)
        texture    = get("texture")
        font       = get("font")
        fontSize   = get("fontsize", int, 1)
        fontScale  = get("xscale", float, 1.0)
        fontRev    = get("fontreversed", bool, False)
        fontAscii  = get("fontasciionly", bool, False)
             
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

        if drawing == None:
          continue
        
        layer = Layer(self, drawing)

        if texture != None:
          layer.type = 1
        elif font != None:
          layer.type = 2
          
        layer.relative    = get("relative", int)
        if layer.relative == None:
          relxpos = 0.0
          relypos = 0.0
        else:
          relxpos = float(self.config.get("layer%d" % layer.relative, "xpos"))
          relypos = float(self.config.get("layer%d" % layer.relative, "ypos"))
          
        layer.position    = (get("xpos",   float, 0.0) + relxpos, get("ypos",   float, 0.0) + relypos)
        layer.scale       = (get("xscale", float, 1.0), get("yscale", float, 1.0))
        layer.angle       = math.pi * get("angle", float, 0.0) / 180.0
        layer.srcBlending = globals()["GL_%s" % get("src_blending", str, "src_alpha").upper()]
        layer.dstBlending = globals()["GL_%s" % get("dst_blending", str, "one_minus_src_alpha").upper()]
        layer.color       = (get("color_r", float, 1.0), get("color_g", float, 1.0), get("color_b", float, 1.0), get("color_a", float, 1.0))
        layer.display     = get("display", int, 1)
        layer.text        = get("text")

        # Load any effects
        fxClasses = {
          "light":          LightEffect,
          "rotate":         RotateEffect,
          "wiggle":         WiggleEffect,
          "scale":          ScaleEffect,
          "display":        DisplayEffect,
          "color":          ColorEffect,
          "pulse":          PulseEffect,
          "translate":      TranslateEffect,
          "text":           TextEffect,
          "textpulse":      TextPulseEffect,
        
        }
        
        for j in range(MAXLAYERS):
          fxSection = "layer%d:fx%d" % (i, j)
          if self.config.has_section(fxSection):
            type = self.config.get(fxSection, "type")

            if not type in fxClasses:
              continue

            options = self.config.options(fxSection)
            options = dict([(opt, self.config.get(fxSection, opt)) for opt in options])

            fx = fxClasses[type](layer, options)
            layer.effects.append(fx)

        if get("foreground", int):
          self.foregroundLayers.append(layer)
        else:
          self.backgroundLayers.append(layer)

  def reset(self):
    self.lastBeatPos        = None
    self.lastQuarterBeatPos = None
    self.lastMissPos        = 0
    self.lastPickPos        = 0
    self.beat               = 0
    self.quarterBeat        = 0
    self.pos                = 0.0
    self.playedNotes        = []
    self.averageNotes       = [0.0]
    self.beatPeriod         = 0.0
    self.lastRockValue      = 0.5
    self.lastMultValue      = 1
    self.lastStreakValue    = 0
    self.lastTimerValue     = 0.0
    self.lastScoreValue     = 0

  def triggerPick(self, pos, notes):
    if notes:
      self.lastPickPos      = pos
      self.playedNotes      = self.playedNotes[-3:] + [sum(notes) / float(len(notes))]
      self.averageNotes[-1] = sum(self.playedNotes) / float(len(self.playedNotes))

  def triggerRock(self, value):
    self.lastRockValue = value

  def triggerMult(self, value):
    self.lastMultValue = value

  def triggerStreak(self, value):
    self.lastStreakValue = value

  def triggerTimer(self, value):
    self.lastTimerValue = value
    
  def triggerScore(self, value):
    self.lastScoreValue = value
    
  def triggerMiss(self, pos):
    self.lastMissPos = pos

  def triggerQuarterBeat(self, pos, quarterBeat):
    self.lastQuarterBeatPos = pos
    self.quarterBeat        = quarterBeat

  def triggerBeat(self, pos, beat):
    self.lastBeatPos  = pos
    self.beat         = beat
    self.averageNotes = self.averageNotes[-4:] + self.averageNotes[-1:]

  def _renderLayers(self, layers, visibility):
    self.engine.view.setOrthogonalProjection(normalize = True)
    try:
      for i, layer in enumerate(layers):
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
    self._renderLayers(self.backgroundLayers, visibility)
    self.scene.renderGuitar()
    self._renderLayers(self.foregroundLayers, visibility)
