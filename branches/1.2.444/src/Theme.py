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

from OpenGL.GL import *
import Config

DEFAULT_COLOR_BACKGROUND = "#330000"
DEFAULT_COLOR_BASE       = "#FFFF80"
DEFAULT_COLOR_SELECTED   = "#FFBF00"
DEFAULT_COLOR_FRET0      = "#22FF22"
DEFAULT_COLOR_FRET1      = "#FF2222"
DEFAULT_COLOR_FRET2      = "#FFFF22"
DEFAULT_COLOR_FRET3      = "#3333FF"
DEFAULT_COLOR_FRET4      = "#FF22FF"

DEFAULT_COLOR_HOPO       = "#00AAAA"
DEFAULT_COLOR_SPOT       = "#FFFFFF"
DEFAULT_COLOR_KEY        = "#333333"
DEFAULT_COLOR_KEY2       = "#000000"
DEFAULT_COLOR_TRACKS     = "#FFFF80"
DEFAULT_COLOR_BARS       = "#FFFF80"

DEFAULT_COLOR_FLAME0_1X   = "#BF6006"
DEFAULT_COLOR_FLAME1_1X   = "#BF6006"
DEFAULT_COLOR_FLAME2_1X   = "#BF6006"
DEFAULT_COLOR_FLAME3_1X   = "#BF6006"
DEFAULT_COLOR_FLAME4_1X   = "#BF6006"
DEFAULT_COLOR_FLAME0_2X   = "#BF6006"
DEFAULT_COLOR_FLAME1_2X   = "#BF6006"
DEFAULT_COLOR_FLAME2_2X   = "#BF6006"
DEFAULT_COLOR_FLAME3_2X   = "#BF6006"
DEFAULT_COLOR_FLAME4_2X   = "#BF6006"
DEFAULT_COLOR_FLAME0_3X   = "#BF6006"
DEFAULT_COLOR_FLAME1_3X   = "#BF6006"
DEFAULT_COLOR_FLAME2_3X   = "#BF6006"
DEFAULT_COLOR_FLAME3_3X   = "#BF6006"
DEFAULT_COLOR_FLAME4_3X   = "#BF6006"
DEFAULT_COLOR_FLAME0_4X   = "#BF6006"
DEFAULT_COLOR_FLAME1_4X   = "#BF6006"
DEFAULT_COLOR_FLAME2_4X   = "#BF6006"
DEFAULT_COLOR_FLAME3_4X   = "#BF6006"
DEFAULT_COLOR_FLAME4_4X   = "#BF6006"

DEFAULT_SIZE_FLAME0_1X   = 0.075
DEFAULT_SIZE_FLAME1_1X   = 0.075
DEFAULT_SIZE_FLAME2_1X   = 0.075
DEFAULT_SIZE_FLAME3_1X   = 0.075
DEFAULT_SIZE_FLAME4_1X   = 0.075
DEFAULT_SIZE_FLAME0_2X   = 0.075
DEFAULT_SIZE_FLAME1_2X   = 0.075
DEFAULT_SIZE_FLAME2_2X   = 0.075
DEFAULT_SIZE_FLAME3_2X   = 0.075
DEFAULT_SIZE_FLAME4_2X   = 0.075
DEFAULT_SIZE_FLAME0_3X   = 0.075
DEFAULT_SIZE_FLAME1_3X   = 0.075
DEFAULT_SIZE_FLAME2_3X   = 0.075
DEFAULT_SIZE_FLAME3_3X   = 0.075
DEFAULT_SIZE_FLAME4_3X   = 0.075
DEFAULT_SIZE_FLAME0_4X   = 0.075
DEFAULT_SIZE_FLAME1_4X   = 0.075
DEFAULT_SIZE_FLAME2_4X   = 0.075
DEFAULT_SIZE_FLAME3_4X   = 0.075
DEFAULT_SIZE_FLAME4_4X   = 0.075

# read the color scheme from the config file
Config.define("theme", "background_color",  str, DEFAULT_COLOR_BACKGROUND)
Config.define("theme", "base_color",        str, DEFAULT_COLOR_BASE)
Config.define("theme", "selected_color",    str, DEFAULT_COLOR_SELECTED)
Config.define("theme", "fret0_color",       str, DEFAULT_COLOR_FRET0)
Config.define("theme", "fret1_color",       str, DEFAULT_COLOR_FRET1)
Config.define("theme", "fret2_color",       str, DEFAULT_COLOR_FRET2)
Config.define("theme", "fret3_color",       str, DEFAULT_COLOR_FRET3)
Config.define("theme", "fret4_color",       str, DEFAULT_COLOR_FRET4)
Config.define("theme", "hopo_color",        str, DEFAULT_COLOR_HOPO)
Config.define("theme", "spot_color",        str, DEFAULT_COLOR_SPOT)
Config.define("theme", "key_color",         str, DEFAULT_COLOR_KEY)
Config.define("theme", "key2_color",        str, DEFAULT_COLOR_KEY2)
Config.define("theme", "tracks_color",      str, DEFAULT_COLOR_TRACKS)
Config.define("theme", "bars_color",        str, DEFAULT_COLOR_BARS)

Config.define("theme", "flame0_1X_color",    str, DEFAULT_COLOR_FLAME0_1X)
Config.define("theme", "flame1_1X_color",    str, DEFAULT_COLOR_FLAME1_1X)
Config.define("theme", "flame2_1X_color",    str, DEFAULT_COLOR_FLAME2_1X)
Config.define("theme", "flame3_1X_color",    str, DEFAULT_COLOR_FLAME3_1X)
Config.define("theme", "flame4_1X_color",    str, DEFAULT_COLOR_FLAME4_1X)
Config.define("theme", "flame0_2X_color",    str, DEFAULT_COLOR_FLAME0_2X)
Config.define("theme", "flame1_2X_color",    str, DEFAULT_COLOR_FLAME1_2X)
Config.define("theme", "flame2_2X_color",    str, DEFAULT_COLOR_FLAME2_2X)
Config.define("theme", "flame3_2X_color",    str, DEFAULT_COLOR_FLAME3_2X)
Config.define("theme", "flame4_2X_color",    str, DEFAULT_COLOR_FLAME4_2X)
Config.define("theme", "flame0_3X_color",    str, DEFAULT_COLOR_FLAME0_3X)
Config.define("theme", "flame1_3X_color",    str, DEFAULT_COLOR_FLAME1_3X)
Config.define("theme", "flame2_3X_color",    str, DEFAULT_COLOR_FLAME2_3X)
Config.define("theme", "flame3_3X_color",    str, DEFAULT_COLOR_FLAME3_3X)
Config.define("theme", "flame4_3X_color",    str, DEFAULT_COLOR_FLAME4_3X)
Config.define("theme", "flame0_4X_color",    str, DEFAULT_COLOR_FLAME0_4X)
Config.define("theme", "flame1_4X_color",    str, DEFAULT_COLOR_FLAME1_4X)
Config.define("theme", "flame2_4X_color",    str, DEFAULT_COLOR_FLAME2_4X)
Config.define("theme", "flame3_4X_color",    str, DEFAULT_COLOR_FLAME3_4X)
Config.define("theme", "flame4_4X_color",    str, DEFAULT_COLOR_FLAME4_4X)

Config.define("theme", "flame0_1X_size",     float, DEFAULT_SIZE_FLAME0_1X)
Config.define("theme", "flame1_1X_size",     float, DEFAULT_SIZE_FLAME1_1X)
Config.define("theme", "flame2_1X_size",     float, DEFAULT_SIZE_FLAME2_1X)
Config.define("theme", "flame3_1X_size",     float, DEFAULT_SIZE_FLAME3_1X)
Config.define("theme", "flame4_1X_size",     float, DEFAULT_SIZE_FLAME4_1X)
Config.define("theme", "flame0_2X_size",     float, DEFAULT_SIZE_FLAME0_2X)
Config.define("theme", "flame1_2X_size",     float, DEFAULT_SIZE_FLAME1_2X)
Config.define("theme", "flame2_2X_size",     float, DEFAULT_SIZE_FLAME2_2X)
Config.define("theme", "flame3_2X_size",     float, DEFAULT_SIZE_FLAME3_2X)
Config.define("theme", "flame4_2X_size",     float, DEFAULT_SIZE_FLAME4_2X)
Config.define("theme", "flame0_3X_size",     float, DEFAULT_SIZE_FLAME0_3X)
Config.define("theme", "flame1_3X_size",     float, DEFAULT_SIZE_FLAME1_3X)
Config.define("theme", "flame2_3X_size",     float, DEFAULT_SIZE_FLAME2_3X)
Config.define("theme", "flame3_3X_size",     float, DEFAULT_SIZE_FLAME3_3X)
Config.define("theme", "flame4_3X_size",     float, DEFAULT_SIZE_FLAME4_3X)
Config.define("theme", "flame0_4X_size",     float, DEFAULT_SIZE_FLAME0_4X)
Config.define("theme", "flame1_4X_size",     float, DEFAULT_SIZE_FLAME1_4X)
Config.define("theme", "flame2_4X_size",     float, DEFAULT_SIZE_FLAME2_4X)
Config.define("theme", "flame3_4X_size",     float, DEFAULT_SIZE_FLAME3_4X)
Config.define("theme", "flame4_4X_size",     float, DEFAULT_SIZE_FLAME4_4X)

def hexToColor(color):
  if color[0] == "#":
    color = color[1:]
    if len(color) == 3:
      return (int(color[0], 16) / 15.0, int(color[1], 16) / 15.0, int(color[2], 16) / 15.0)
    return (int(color[0:2], 16) / 255.0, int(color[2:4], 16) / 255.0, int(color[4:6], 16) / 255.0)
  return (0, 0, 0)
    
def colorToHex(color):
  return "#" + ("".join(["%02x" % int(c * 255) for c in color]))

backgroundColor = None
baseColor       = None
selectedColor   = None
fretColors      = None

hopoColor       = None
spotColor       = None
keyColor        = None
key2Color       = None
tracksColor     = None
barsColor       = None
flameColors     = None
flameSizes      = None
loadingPhrase   = None
resultsPhrase   = None
startingPhrase  = None

def open(config):
  global backgroundColor, baseColor, selectedColor, fretColors
  global hopoColor, spotColor
  global keyColor, key2Color
  global tracksColor, barsColor
  global flameColors, flameSizes
  global loadingPhrase, resultsPhrase

  #special cases for theme.ini in mod directories

  temp = config.get("theme", "background_color")
  if backgroundColor == None or temp != DEFAULT_COLOR_BACKGROUND:
    backgroundColor = hexToColor(temp)  

  temp = config.get("theme", "base_color")
  if baseColor == None or temp != DEFAULT_COLOR_BASE:
    baseColor = hexToColor(temp)

  temp = config.get("theme", "selected_color")
  if selectedColor == None or temp != DEFAULT_COLOR_SELECTED:
    selectedColor = hexToColor(temp)    

  loadingPhrase = config.get("theme", "loading_phrase")
  resultsPhrase = config.get("theme", "results_phrase")
  
  if fretColors == None:
    fretColors = [hexToColor(config.get("theme", "fret%d_color" % i)) for i in range(5)]
  else:
    temp = config.get("theme", "fret0_color")
    if temp != DEFAULT_COLOR_FRET0:
      fretColors[0] = hexToColor(temp)

    temp = config.get("theme", "fret1_color")
    if temp != DEFAULT_COLOR_FRET1:
      fretColors[1] = hexToColor(temp)

    temp = config.get("theme", "fret2_color")
    if temp != DEFAULT_COLOR_FRET2:
      fretColors[2] = hexToColor(temp)

    temp = config.get("theme", "fret3_color")
    if temp != DEFAULT_COLOR_FRET3:
      fretColors[3] = hexToColor(temp)

    temp = config.get("theme", "fret4_color")
    if temp != DEFAULT_COLOR_FRET4:
      fretColors[4] = hexToColor(temp)

  temp = config.get("theme", "hopo_color")
  if temp.lower() == "fret":
    hopoColor = temp.lower()
  elif hopoColor == None or temp != DEFAULT_COLOR_HOPO:
    hopoColor = hexToColor(temp)

  temp = config.get("theme", "spot_color")
  if spotColor == None or temp != DEFAULT_COLOR_SPOT:
    spotColor = hexToColor(temp)

  temp = config.get("theme", "key_color")
  if keyColor == None or temp != DEFAULT_COLOR_KEY:
    keyColor = hexToColor(temp)

  temp = config.get("theme", "key2_color")
  if key2Color == None or temp != DEFAULT_COLOR_KEY2:
    key2Color = hexToColor(temp)    

  temp = config.get("theme", "tracks_color")
  if temp.lower() == "off":
    tracksColor = temp.lower()
  elif tracksColor == None or temp != DEFAULT_COLOR_TRACKS:
    tracksColor = hexToColor(temp)

  temp = config.get("theme", "bars_color")
  if temp.lower() == "off":
    barsColor = temp.lower()
  elif barsColor == None or temp != DEFAULT_COLOR_BARS:
    barsColor = hexToColor(temp)

  if flameColors == None:
    flameColors = [[hexToColor(config.get("theme", "flame%d_1X_color" % i)) for i in range(5)]]
    flameColors.append([hexToColor(config.get("theme", "flame%d_2X_color" % i)) for i in range(5)])
    flameColors.append([hexToColor(config.get("theme", "flame%d_3X_color" % i)) for i in range(5)])
    flameColors.append([hexToColor(config.get("theme", "flame%d_4X_color" % i)) for i in range(5)])
  else:
    temp = config.get("theme", "flame0_1X_color")
    if temp != DEFAULT_COLOR_FLAME0_1X:
      flameColors[0][0] = hexToColor(temp)

    temp = config.get("theme", "flame1_1X_color")
    if temp != DEFAULT_COLOR_FLAME1_1X:
      flameColors[0][1] = hexToColor(temp)

    temp = config.get("theme", "flame2_1X_color")
    if temp != DEFAULT_COLOR_FLAME2_1X:
      flameColors[0][2] = hexToColor(temp)

    temp = config.get("theme", "flame3_1X_color")
    if temp != DEFAULT_COLOR_FLAME3_1X:
      flameColors[0][3] = hexToColor(temp)

    temp = config.get("theme", "flame4_1X_color")
    if temp != DEFAULT_COLOR_FLAME4_1X:
      flameColors[0][4] = hexToColor(temp)
      
    temp = config.get("theme", "flame0_2X_color")
    if temp != DEFAULT_COLOR_FLAME0_2X:
      flameColors[1][0] = hexToColor(temp)

    temp = config.get("theme", "flame1_2X_color")
    if temp != DEFAULT_COLOR_FLAME1_2X:
      flameColors[1][1] = hexToColor(temp)

    temp = config.get("theme", "flame2_2X_color")
    if temp != DEFAULT_COLOR_FLAME2_2X:
      flameColors[1][2] = hexToColor(temp)

    temp = config.get("theme", "flame3_2X_color")
    if temp != DEFAULT_COLOR_FLAME3_2X:
      flameColors[1][3] = hexToColor(temp)

    temp = config.get("theme", "flame4_2X_color")
    if temp != DEFAULT_COLOR_FLAME4_2X:
      flameColors[1][4] = hexToColor(temp)
      
    temp = config.get("theme", "flame0_3X_color")
    if temp != DEFAULT_COLOR_FLAME0_3X:
      flameColors[2][0] = hexToColor(temp)

    temp = config.get("theme", "flame1_3X_color")
    if temp != DEFAULT_COLOR_FLAME1_3X:
      flameColors[2][1] = hexToColor(temp)

    temp = config.get("theme", "flame2_3X_color")
    if temp != DEFAULT_COLOR_FLAME2_3X:
      flameColors[2][2] = hexToColor(temp)

    temp = config.get("theme", "flame3_3X_color")
    if temp != DEFAULT_COLOR_FLAME3_3X:
      flameColors[2][3] = hexToColor(temp)

    temp = config.get("theme", "flame4_3X_color")
    if temp != DEFAULT_COLOR_FLAME4_3X:
      flameColors[2][4] = hexToColor(temp)

    temp = config.get("theme", "flame0_4X_color")
    if temp != DEFAULT_COLOR_FLAME0_4X:
      flameColors[3][0] = hexToColor(temp)

    temp = config.get("theme", "flame1_4X_color")
    if temp != DEFAULT_COLOR_FLAME1_4X:
      flameColors[3][1] = hexToColor(temp)

    temp = config.get("theme", "flame2_4X_color")
    if temp != DEFAULT_COLOR_FLAME2_4X:
      flameColors[3][2] = hexToColor(temp)

    temp = config.get("theme", "flame3_4X_color")
    if temp != DEFAULT_COLOR_FLAME3_4X:
      flameColors[3][3] = hexToColor(temp)

    temp = config.get("theme", "flame4_4X_color")
    if temp != DEFAULT_COLOR_FLAME4_4X:
      flameColors[3][4] = hexToColor(temp)

  if flameSizes == None:
    flameSizes = [[config.get("theme", "flame%d_1X_size" % i) for i in range(5)]]
    flameSizes.append([config.get("theme", "flame%d_2X_size" % i) for i in range(5)])
    flameSizes.append([config.get("theme", "flame%d_3X_size" % i) for i in range(5)])
    flameSizes.append([config.get("theme", "flame%d_4X_size" % i) for i in range(5)])
  else:
    temp = config.get("theme", "flame0_1X_size")
    if temp != DEFAULT_SIZE_FLAME0_1X:
      flameSizes[0][0] = temp
      
    temp = config.get("theme", "flame1_1X_size")
    if temp != DEFAULT_SIZE_FLAME1_1X:
      flameSizes[0][1] = temp
      
    temp = config.get("theme", "flame2_1X_size")
    if temp != DEFAULT_SIZE_FLAME2_1X:
      flameSizes[0][2] = temp
      
    temp = config.get("theme", "flame3_1X_size")
    if temp != DEFAULT_SIZE_FLAME3_1X:
      flameSizes[0][3] = temp
      
    temp = config.get("theme", "flame4_1X_size")
    if temp != DEFAULT_SIZE_FLAME4_1X:
      flameSizes[0][4] = temp

    temp = config.get("theme", "flame0_2X_size")
    if temp != DEFAULT_SIZE_FLAME0_2X:
      flameSizes[1][0] = temp
      
    temp = config.get("theme", "flame1_2X_size")
    if temp != DEFAULT_SIZE_FLAME1_2X:
      flameSizes[1][1] = temp
      
    temp = config.get("theme", "flame2_2X_size")
    if temp != DEFAULT_SIZE_FLAME2_2X:
      flameSizes[1][2] = temp
      
    temp = config.get("theme", "flame3_2X_size")
    if temp != DEFAULT_SIZE_FLAME3_2X:
      flameSizes[1][3] = temp
      
    temp = config.get("theme", "flame4_2X_size")
    if temp != DEFAULT_SIZE_FLAME4_2X:
      flameSizes[1][4] = temp

    temp = config.get("theme", "flame0_3X_size")
    if temp != DEFAULT_SIZE_FLAME0_3X:
      flameSizes[2][0] = temp
      
    temp = config.get("theme", "flame1_3X_size")
    if temp != DEFAULT_SIZE_FLAME1_3X:
      flameSizes[2][1] = temp
      
    temp = config.get("theme", "flame2_3X_size")
    if temp != DEFAULT_SIZE_FLAME2_3X:
      flameSizes[2][2] = temp
      
    temp = config.get("theme", "flame3_3X_size")
    if temp != DEFAULT_SIZE_FLAME3_3X:
      flameSizes[2][3] = temp
      
    temp = config.get("theme", "flame4_3X_size")
    if temp != DEFAULT_SIZE_FLAME4_3X:
      flameSizes[2][4] = temp

    temp = config.get("theme", "flame0_4X_size")
    if temp != DEFAULT_SIZE_FLAME0_4X:
      flameSizes[3][0] = temp
      
    temp = config.get("theme", "flame1_4X_size")
    if temp != DEFAULT_SIZE_FLAME1_4X:
      flameSizes[3][1] = temp
      
    temp = config.get("theme", "flame2_4X_size")
    if temp != DEFAULT_SIZE_FLAME2_4X:
      flameSizes[3][2] = temp
      
    temp = config.get("theme", "flame3_4X_size")
    if temp != DEFAULT_SIZE_FLAME3_4X:
      flameSizes[3][3] = temp
      
    temp = config.get("theme", "flame4_4X_size")
    if temp != DEFAULT_SIZE_FLAME4_4X:
      flameSizes[3][4] = temp
    
def setSelectedColor(alpha = 1.0):
  glColor4f(*(selectedColor + (alpha,)))

def setBaseColor(alpha = 1.0):
  glColor4f(*(baseColor + (alpha,)))
