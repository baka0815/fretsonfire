#####################################################################
#####################################################################
# -*- coding: iso-8859-1 -*-                                        #
#                                                                   #
# Frets on Fire                                                     #
# Copyright (C) 2006 Sami Ky�stil�                                  #
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
import pygame
import os
import sys

from Engine import Engine, Task
from Video import Video
from Audio import Audio
from View import View
from Input import Input, KeyListener, SystemEventListener
from Resource import Resource
from Data import Data
from Server import Server
from Session import ClientSession
from Svg import SvgContext, SvgDrawing, LOW_QUALITY, NORMAL_QUALITY, HIGH_QUALITY
from Debug import DebugLayer
from Language import _
import Network
import Log
import Config
import Dialogs
import Theme
import Version
import Skin

# define configuration keys
Config.define("engine", "tickrate",     float, 1.0)
Config.define("engine", "highpriority", bool,  True)
Config.define("game",   "uploadscores", bool,  False, text = _("Upload Highscores"),    options = {False: _("No"), True: _("Yes")})
Config.define("game",   "uploadurl",    str,   "http://www.prison.net/worldcharts/play")
Config.define("game",   "leftymode",    bool,  False, text = _("Lefty mode"),           options = {False: _("No"), True: _("Yes")})
Config.define("game",   "tapping",      int,   0,  text = _("HO/PO"),       options = {0: _("Yes"), 1: _("No")})
Config.define("video",  "fullscreen",   bool,  True,  text = _("Fullscreen Mode"),      options = {False: _("No"), True: _("Yes")})
Config.define("video",  "multisamples", int,   4,     text = _("Antialiasing Quality"), options = {0: _("None"), 2: _("2x"), 4: _("4x"), 6: _("6x"), 8: _("8x")})
Config.define("video",  "resolution",   str,   "640x480")
Config.define("video",  "fps",          int,   80,    text = _("Frames per Second"), options = dict([(n, n) for n in range(1, 120)]))
Config.define("opengl", "svgquality",   int,   NORMAL_QUALITY,  text = _("SVG Quality"), options = {LOW_QUALITY: _("Low"), NORMAL_QUALITY: _("Normal"), HIGH_QUALITY: _("High")})
Config.define("audio",  "frequency",    int,   44100, text = _("Sample Frequency"), options = [8000, 11025, 22050, 32000, 44100, 48000])
Config.define("audio",  "bits",         int,   16,    text = _("Sample Bits"), options = [16, 8])
Config.define("audio",  "stereo",       bool,  True)
Config.define("audio",  "buffersize",   int,   2048,  text = _("Buffer Size"), options = [256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536])
Config.define("audio",  "delay",        int,   100,   text = _("A/V delay"), options = dict([(n, n) for n in range(0, 1001)]))
Config.define("audio",  "screwupvol", float,   0.25,  text = _("Screw Up Sounds"), options = {0.0: _("Off"), .25: _("Quiet"), .5: _("Loud"), 1.0: _("Painful")})
Config.define("audio",  "gamevol",    float,   0.25,  text = _("Game Sounds"), options = {0.0: _("Off"), .25: _("Quiet"), .5: _("Loud"), 1.0: _("Painful")})
Config.define("audio",  "guitarvol",  float,    1.0,  text = _("Guitar Volume"),   options = dict([(n / 100.0, "%02d/10" % (n / 9)) for n in range(0, 110, 10)]))
Config.define("audio",  "songvol",    float,    1.0,  text = _("Song Volume"),     options = dict([(n / 100.0, "%02d/10" % (n / 9)) for n in range(0, 110, 10)]))
Config.define("audio",  "rhythmvol",  float,    1.0,  text = _("Rhythm Volume"),   options = dict([(n / 100.0, "%02d/10" % (n / 9)) for n in range(0, 110, 10)]))
Config.define("video",  "fontscale",  float,    1.0,  text = _("Text scale"),      options = dict([(n / 100.0, "%3d%%" % n) for n in range(50, 260, 10)]))

#RF-mod items
Config.define("engine", "game_priority",       int,   2,      text = _("Priority"), options = {0: _("0 Idle"), 1: _("1 Low"), 2: _("2 Normal"), 3:_("3 Above Normal"), 4:_("4 High"), 5:_("5 Realtime")})
Config.define("game",   "alt_keys",            bool,  False,  text = _("Alternate Controller"), options = {False: _("No"), True: _("Yes")})
Config.define("game",   "margin",              int,   0,      text = _("Hit Margin"), options = {0: _("FoF"), 1: _("Capo")})
Config.define("game",   "hopo_mark",           int,   1,      text = _("HO/PO Note Marks"), options = {0: _("FoF"), 1: _("RFmod")})
Config.define("game",   "hopo_style",          int,   2,      text = _("HO/PO Key Style"), options = {0: _("FoF"), 1: _("RFmod"), 2: _("RFmod2")})
Config.define("game",   "disable_vbpm",        bool,  False,  text = _("Disable Variable BPM"),  options = {False: _("No"), True: _("Yes")})
Config.define("game",   "board_speed",         int,   0,      text = _("Board Speed"), options = {0: _("BPM based"), 1: _("Difficulty based")})
Config.define("game",   "sort_order",          int,   0,      text = _("Sort Order"), options = {0: _("Title"), 1: _("Artist"), 2: _("Tag")})
Config.define("game",   "pov",                 int,   0,      text = _("Point Of View"), options = {0: _("FoF"), 1: _("Arcade"), 2: _("Custom")})
Config.define("game",   "players",             int,   1,      text = _("Number of players"),  options = {1: _("1"), 2: _("2")})
Config.define("game",   "party_time",          int,   30,     text = _("Party Mode Timer"), options = dict([(n, n) for n in range(1, 99)]))
Config.define("game",   "disable_libcount",    bool,  False,  text = _("Disable Library Count"),    options = {False: _("No"), True: _("Yes")})
Config.define("game",   "disable_librotation", bool,  False,  text = _("Disable Library Rotation"),    options = {False: _("No"), True: _("Yes")})
Config.define("game",   "songlist_render",     bool,  True,   text = _("Songlist Type"), options = {False: _("List"), True: _("Cassettes")})
Config.define("game",   "songlist_items",      int,   3,      text = _("Songlist Number"),  options = dict([(n, "%d" % n) for n in range(3, 12, 2)]))
Config.define("game",   "tracks_type",         int,   0,      text = _("Tracks Type"),    options = {0: _("Middle of Notes"), 1: _("Between Notes")})
Config.define("game",   "disable_spinny",      bool,  False,  text = _("Disable Spinning BGs"),    options = {False: _("No"), True: _("Yes")})
Config.define("video",  "disable_stats",       bool,  False,  text = _("Disable Stats"),    options = {False: _("No"), True: _("Yes")})
Config.define("video",  "disable_notesfx",     bool,  False,  text = _("Disable Note SFX"),    options = {False: _("No"), True: _("Yes")})
Config.define("video",  "disable_notewavessfx",bool,  False,  text = _("Disable Note Waves SFX"),    options = {False: _("No"), True: _("Yes")})
Config.define("video",  "disable_fretsfx",     bool,  False,  text = _("Disable Fret SFX"),    options = {False: _("No"), True: _("Yes")})
Config.define("video",  "disable_flamesfx",    bool,  False,  text = _("Disable Flame SFX"),    options = {False: _("No"), True: _("Yes")})
Config.define("audio",  "disable_preview",     bool,  False,  text = _("Disable Preview"),    options = {False: _("No"), True: _("Yes")})
Config.define("audio",  "miss_volume",         float, 0.2,    text = _("Miss Volume"), options = dict([(n / 100.0, "%d%%" % n) for n in range(0, 100, 10)]))
Config.define("player0","two_chord_max",       bool,  False,  text = _("P1 Two Key Chord helper"),  options = {False: _("No"), True: _("Yes")})
Config.define("player0","leftymode",           bool,  False,  text = _("P2 Lefty mode"),           options = {False: _("No"), True: _("Yes")})
Config.define("player1","two_chord_max",       bool,  False,  text = _("P2 Two Key Chord helper"),  options = {False: _("No"), True: _("Yes")})
Config.define("player1","leftymode",           bool,  False,  text = _("P2 Lefty mode"),           options = {False: _("No"), True: _("Yes")})

Config.define("failing",  "failing",           bool,  True,   text = _("Failing"), options = {False: _("No"), True: _("Yes")})
Config.define("failing",  "difficulty",        int,   1,      text = _("Failing Difficulty"), options = {1: _("Easy"), 2: _("Medium"), 3: _("Amazing"), 4: _("Custom")})
Config.define("failing",  "jurgen",            bool,  True,   text = _("Jurgen Power"), options = {False: _("No"), True: _("Yes")})
Config.define("failing",  "jurgen_volume",     float, 0.0,    text = _("Jurgen Power Sound gain"), options = dict([(n / 100.0, "%d%%" % n) for n in range(0, 100, 10)]))

#Config.define("failing",  "changenotecolor",   bool,  True, text = _("Change note color"), options = {False: _("No"), True: _("Yes")})
#Config.define("game",  "drawfailing",          int,  1, text = _("Draw Failing meter"), options = {1: _("Rock meter"),2: _("Simple bar"), 3: _("Hide")})
#Config.define("game",  "selected_players",     int,   1, text = _("Selected players"), options = {1: _("Single Player"),2: _("2 Player Coop"), 3: _("2 Player Versus"), -1: _("Pary Mode")})
#Config.define("game",  "boardspeed",           float,  1.0,  text = _("Board Speed"),  options = dict([(n / 100.0, "%d%%" % n) for n in range(25, 400, 5)]))
#Config.define("game",  "songlist_items",       int,  1,  text = _("Songlist items"),  options = dict([(n, "%d" % n) for n in range(3, 16, 2)]))
#Config.define("video",  "flashing",            bool,  True, text = _("Screen Flashing"), options = {False: _("No"), True: _("Yes")})
Config.define("failing", "drop",               int,   20,  text = _("-Points for a mistake"),  options = dict([(n, n) for n in range (1, 50)]))
Config.define("failing", "gain",               int,   4,  text = _("+Points for a hit"),  options = dict([(n, n) for n in range (1, 50)]))
Config.define("failing", "multiply",           bool,   True,  text = _("+Points * multiplier"),  options = {False: _("No"), True: _("Yes")})
Config.define("failing", "maximum",            int,  500,  text = _("Maximum points"),  options = dict([(n, "%d" % n) for n in range(50, 2000, 10)]))
Config.define("failing", "jgain",              int,   15,  text = _("Notes for 1 Jurgen point"),  options = dict([(n, n) for n in range (1, 50)]))
Config.define("failing", "jmultiplier",        int,   4,  text = _("Jurgen multiplier"),  options = dict([(n, n) for n in range (2, 11)]))
Config.define("failing", "jmax",               int,   15,  text = _("Maximum Jurgen points"),  options = dict([(n, n) for n in range (1, 50)]))



class FullScreenSwitcher(KeyListener):
  """
  A keyboard listener that looks for special built-in key combinations,
  such as the fullscreen toggle (Alt-Enter).
  """
  def __init__(self, engine):
    self.engine = engine
    self.altStatus = False
  
  def keyPressed(self, key, unicode):
    if key == pygame.K_LALT:
      self.altStatus = True
    elif key == pygame.K_RETURN and self.altStatus:
      if not self.engine.toggleFullscreen():
        Log.error("Unable to toggle fullscreen mode.")
      return True
    elif key == pygame.K_d and self.altStatus:
      self.engine.setDebugModeEnabled(not self.engine.isDebugModeEnabled())
      return True
    elif key == pygame.K_g and self.altStatus and self.engine.isDebugModeEnabled():
      self.engine.debugLayer.gcDump()
      return True

  def keyReleased(self, key):
    if key == pygame.K_LALT:
      self.altStatus = False
      
class SystemEventHandler(SystemEventListener):
  """
  A system event listener that takes care of restarting the game when needed
  and reacting to screen resize events.
  """
  def __init__(self, engine):
    self.engine = engine

  def screenResized(self, size):
    self.engine.resizeScreen(size[0], size[1])
    
  def restartRequested(self):
    self.engine.restart()
    
  def quit(self):
    self.engine.quit()

class GameEngine(Engine):
  """The main game engine."""
  def __init__(self, config = None):
    """
    Constructor.

    @param config:  L{Config} instance for settings
    """

    if not config:
      config = Config.load()
      
    self.config  = config
    
    fps          = self.config.get("video", "fps")
    tickrate     = self.config.get("engine", "tickrate")
    Engine.__init__(self, fps = fps, tickrate = tickrate)
    
    #pygame.init()
    
    self.title             = _("Frets on Fire")
    self.restartRequested  = False
    self.handlingException = False
    self.video             = Video(self.title)
    self.audio             = Audio()

    Log.debug("Initializing audio.")
    frequency    = self.config.get("audio", "frequency")
    bits         = self.config.get("audio", "bits")
    stereo       = self.config.get("audio", "stereo")
    bufferSize   = self.config.get("audio", "buffersize")
    
    self.audio.pre_open(frequency = frequency, bits = bits, stereo = stereo, bufferSize = bufferSize)
    self.audio.open(frequency = frequency, bits = bits, stereo = stereo, bufferSize = bufferSize)
    
    pygame.init()
    
    Log.debug("Initializing video.")
    width, height = [int(s) for s in self.config.get("video", "resolution").split("x")]
    fullscreen    = self.config.get("video", "fullscreen")
    multisamples  = self.config.get("video", "multisamples")
    self.video.setMode((width, height), fullscreen = fullscreen, multisamples = multisamples)

    # Enable the high priority timer if configured
    if self.config.get("engine", "highpriority"):
      Log.debug("Enabling high priority timer.")
      self.timer.highPriority = True

    viewport = glGetIntegerv(GL_VIEWPORT)
    h = viewport[3] - viewport[1]
    w = viewport[2] - viewport[0]
    geometry = (0, 0, w, h)
    self.svg = SvgContext(geometry)
    self.svg.setRenderingQuality(self.config.get("opengl", "svgquality"))
    glViewport(*viewport)

    self.input     = Input()
    self.view      = View(self, geometry)
    self.resizeScreen(w, h)

    self.resource  = Resource(Version.dataPath())
    self.server    = None
    self.sessions  = []
    self.mainloop  = self.loading

    # Load default theme
    theme = Config.load(self.resource.fileName("theme.ini"))
    self.theme = theme
    Theme.open(self.theme)
    
    # Load game skins
    Skin.init(self)
    
    self.addTask(self.input, synchronized = False)
    self.addTask(self.view)
    self.addTask(self.resource, synchronized = False)
    self.data = Data(self.resource, self.svg)
    
    self.input.addKeyListener(FullScreenSwitcher(self), priority = True)
    self.input.addSystemEventListener(SystemEventHandler(self))

    self.debugLayer         = None
    self.startupLayer       = None
    self.loadingScreenShown = False
    
    Log.debug("Ready.")

  def setStartupLayer(self, startupLayer):
    """
    Set the L{Layer} that will be shown when the all
    the resources have been loaded. See L{Data}

    @param startupLayer:    Startup L{Layer}
    """
    self.startupLayer = startupLayer

  def isDebugModeEnabled(self):
    return bool(self.debugLayer)
    
  def setDebugModeEnabled(self, enabled):
    """
    Show or hide the debug layer.

    @type enabled: bool
    """
    if enabled:
      self.debugLayer = DebugLayer(self)
    else:
      self.debugLayer = None
    
  def toggleFullscreen(self):
    """
    Toggle between fullscreen and windowed mode.

    @return: True on success
    """
    if not self.video.toggleFullscreen():
      # on windows, the fullscreen toggle kills our textures, se we must restart the whole game
      self.input.broadcastSystemEvent("restartRequested")
      self.config.set("video", "fullscreen", not self.video.fullscreen)
      return True
    self.config.set("video", "fullscreen", self.video.fullscreen)
    return True
    
  def restart(self):
    """Restart the game."""
    if not self.restartRequested:
      self.restartRequested = True
      self.input.broadcastSystemEvent("restartRequested")
    else:
      self.quit()
    
  def resizeScreen(self, width, height):
    """
    Resize the game screen.

    @param width:   New width in pixels
    @param height:  New height in pixels
    """
    self.view.setGeometry((0, 0, width, height))
    self.svg.setGeometry((0, 0, width, height))
    
  def isServerRunning(self):
    return bool(self.server)

  def startServer(self):
    """Start the game server."""
    if not self.server:
      Log.debug("Starting server.")
      self.server = Server(self)
      self.addTask(self.server, synchronized = False)

  def connect(self, host):
    """
    Connect to a game server.

    @param host:  Name of host to connect to
    @return:      L{Session} connected to remote server
    """
    Log.debug("Connecting to host %s." % host)
    session = ClientSession(self)
    session.connect(host)
    self.addTask(session, synchronized = False)
    self.sessions.append(session)
    return session

  def stopServer(self):
    """Stop the game server."""
    if self.server:
      Log.debug("Stopping server.")
      self.removeTask(self.server)
      self.server = None

  def disconnect(self, session):
    """
    Disconnect a L{Session}

    param session:    L{Session} to disconnect
    """
    if session in self.sessions:
      Log.debug("Disconnecting.")
      self.removeTask(session)
      self.sessions.remove(session)

  def loadSvgDrawing(self, target, name, fileName, textureSize = None):
    """
    Load an SVG drawing synchronously.
    
    @param target:      An object that will own the drawing
    @param name:        The name of the attribute the drawing will be assigned to
    @param fileName:    The name of the file in the data directory
    @param textureSize  Either None or (x, y), in which case the file will
                        be rendered to an x by y texture
    @return:            L{SvgDrawing} instance
    """
    return self.data.loadSvgDrawing(target, name, fileName, textureSize)

  def loadFont(self, target, name, fileName, size, scale, reversed, systemFont):
    """
    Load an Font synchronously.
    
    @param target:      An object that will own the drawing
    @param name:        The name of the attribute the drawing will be assigned to
    @param fileName:    The name of the file in the data directory
    @param textureSize  Either None or (x, y), in which case the file will
                        be rendered to an x by y texture
    @return:            L{SvgDrawing} instance
    """
    return self.data.loadFont(target, name, fileName, size, scale, reversed, systemFont)
  
  def loading(self):
    """Loading state loop."""
    done = Engine.run(self)
    self.clearScreen()
    
    if self.data.essentialResourcesLoaded():
      if not self.loadingScreenShown:
        self.loadingScreenShown = True
        Dialogs.showLoadingScreen(self, self.data.resourcesLoaded)
        if self.startupLayer:
          self.view.pushLayer(self.startupLayer)
        self.mainloop = self.main
      self.view.render()
    self.video.flip()
    return done

  def clearScreen(self):
    self.svg.clear(*Theme.backgroundColor)

  def main(self):
    """Main state loop."""

    # Tune the scheduler priority so that transitions are as smooth as possible
    if self.view.isTransitionInProgress():
      self.boostBackgroundThreads(False)
    else:
      self.boostBackgroundThreads(True)
    
    done = Engine.run(self)
    self.clearScreen()
    self.view.render()
    if self.debugLayer:
      self.debugLayer.render(1.0, True)
    self.video.flip()
    return done

  def run(self):
    try:
      return self.mainloop()
    except KeyboardInterrupt:
      sys.exit(0)
    except SystemExit:
      sys.exit(0)
    except Exception, e:
      def clearMatrixStack(stack):
        try:
          glMatrixMode(stack)
          for i in range(16):
            glPopMatrix()
        except:
          pass

      if self.handlingException:
        # A recursive exception is fatal as we can't reliably reset the GL state
        sys.exit(1)

      self.handlingException = True
      Log.error("%s: %s" % (e.__class__, e))
      import traceback
      traceback.print_exc()

      clearMatrixStack(GL_PROJECTION)
      clearMatrixStack(GL_MODELVIEW)
      
      Dialogs.showMessage(self, unicode(e))
      self.handlingException = False
      return True
