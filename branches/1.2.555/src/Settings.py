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

import Menu
from Language import _
import Dialogs
import Config
import Skin
import Audio

import pygame
import os

class ConfigChoice(Menu.Choice):
  def __init__(self, config, section, option, autoApply = False):
    self.config    = config
    self.section   = section
    self.option    = option
    self.changed   = False
    self.value     = None
    self.autoApply = autoApply
    o = config.prototype[section][option]
    v = config.get(section, option)
    if isinstance(o.options, dict):
      values     = o.options.values()
      values.sort()
      try:
        valueIndex = values.index(o.options[v])
      except KeyError:
        valueIndex = 0
    elif isinstance(o.options, list):
      values     = o.options
      try:
        valueIndex = values.index(v)
      except ValueError:
        valueIndex = 0
    else:
      raise RuntimeError("No usable options for %s.%s." % (section, option))
    Menu.Choice.__init__(self, text = o.text, callback = self.change, values = values, valueIndex = valueIndex)
    
  def change(self, value):
    o = self.config.prototype[self.section][self.option]
    
    if isinstance(o.options, dict):
      for k, v in o.options.items():
        if v == value:
          value = k
          break
    
    self.changed = True
    self.value   = value
    
    if self.autoApply:
      self.apply()

  def apply(self):
    if self.changed:
      self.config.set(self.section, self.option, self.value)

class VolumeConfigChoice(ConfigChoice):
  def __init__(self, engine, config, section, option, autoApply = False):
    ConfigChoice.__init__(self, config, section, option, autoApply)
    self.engine = engine

  def change(self, value):
    ConfigChoice.change(self, value)
    sound = self.engine.data.screwUpSound
    sound.setVolume(self.value)
    sound.play()

class ProfileChoice(ConfigChoice):
  def __init__(self, engine, player, section, option, autoApply = False):
    self.engine = engine

    playerNum = player - 1
    self.config = self.engine.profileList[playerNum]

    ConfigChoice.__init__(self, self.config, section, option, autoApply)

class InstrumentProfileChoice(ProfileChoice):
  def change(self, value):
    ProfileChoice.change(self, value)
    self.engine.input.reloadControls()
      
class NavProfileChoice(Menu.Choice):
  def __init__(self, engine, player, section, option, autoApply = False):
    self.engine  = engine
    self.section = section
    self.option  = option
    self.changed = False
    self.value   = None

    playerNum = player - 1
    self.config = self.engine.profileList[playerNum]
  
    Menu.Choice.__init__(self, text = "", callback = self.change)

  def getText(self, selected):
    def keycode(k):
      try:
        return int(k)
      except:
        return getattr(pygame, k)
    o = self.config.prototype[self.section][self.option]
    v = self.config.get(self.section, self.option)
    return "%s: %s" % (o.text, pygame.key.name(keycode(v)).capitalize())
    
  def change(self):
    o = self.config.prototype[self.section][self.option]

    if isinstance(o.options, dict):
      for k, v in o.options.items():
        if v == value:
          value = k
          break

    key = Dialogs.getKey(self.engine, _("Press a key for '%s' or Escape to cancel.") % (o.text))

    if key:
      self.config.set(self.section, self.option, key)
      self.engine.input.reloadControls()

  def apply(self):
    pass

class KeyProfileChoice(NavProfileChoice):
  def __init__(self, profileList, player, option, autoApply = False):

    playerNum = player - 1
    self.config = self.profileList[playerNum]
    instrument = self.config.get("instrument", "selected")
    NavProfileChoice.__init__(self, engine, player, instrument, option, autoApply)

  def getText(self, selected):
    def keycode(k):
      try:
        return int(k)
      except:
        return getattr(pygame, k)
    genericSection = self.section[:-1]
    genericSection += "X"

    o = self.config.prototype[genericSection][self.option]
    v = self.config.get(self.section, self.option)
    if v == "None":
      v = self.config.get(genericSection, self.option)
    return "%s: %s" % (o.text, pygame.key.name(keycode(v)).capitalize())

  def change(self):
    genericSection = self.section[:-1]
    genericSection += "X"
    o = self.config.prototype[genericSection][self.option]

    if isinstance(o.options, dict):
      for k, v in o.options.items():
        if v == value:
          value = k
          break

    key = Dialogs.getKey(self.engine, _("Press a key for '%s' or Escape to cancel.") % (o.text))

    if key:
      self.config.set(self.section, self.option, key)
      self.engine.input.reloadControls()
      
class HopoConfigChoice(ConfigChoice):
  def __init__(self, config, section, option, autoApply = False):
    ConfigChoice.__init__(self, config, section, option, autoApply)

  def change(self, value):
    ConfigChoice.change(self, value)
    if value == "FoF":
      self.config.set(self.section, "hopo_mark", self.value)
      self.config.set(self.section, "hopo_style", self.value)

      

class SettingsMenu(Menu.Menu):
  def getSkinSettingsMenu(self, engine, skindir=None):
    menu = []
    for w in Skin.getAvailableSkinDirs(engine, dir=skindir):
      menu.append((_("%s" % (w)), self.getSkinSettingsMenu(engine, skindir=w)))
    for m in Skin.getAvailableSkins(engine, dir=skindir):
      if skindir == None:
        menu.append(ConfigChoice(engine.config, "skins",  "skin_" + m, autoApply = True))
      else:
        menu.append(ConfigChoice(engine.config, "skins",  "skin_%s/" % (skindir) + m, autoApply = True))
    return menu


  
  def __init__(self, engine):
    applyItem = [(_("Apply New Settings"), self.applySettings)]

    skinSettings = self.getSkinSettingsMenu(engine) + applyItem
  
    gameSettings = [
      (_("Skin settings"), skinSettings),
      ConfigChoice(engine.config, "game",  "language"),
      ConfigChoice(engine.config, "game",  "uploadscores", autoApply = True),
    ]
    gameSettingsMenu = Menu.Menu(engine, gameSettings + applyItem)

    player1NavSettings = [
      NavProfileChoice(engine, 1, "general", "nav_left"),
      NavProfileChoice(engine, 1, "general", "nav_right"),
      NavProfileChoice(engine, 1, "general", "nav_up"),
      NavProfileChoice(engine, 1, "general", "nav_down"),
      NavProfileChoice(engine, 1, "general", "nav_cancel"),
    ]
    player1NavSettingsMenu = Menu.Menu(engine, player1NavSettings)

    player2NavSettings = [
      NavProfileChoice(engine, 2, "general", "nav_left"),
      NavProfileChoice(engine, 2, "general", "nav_right"),
      NavProfileChoice(engine, 2, "general", "nav_up"),
      NavProfileChoice(engine, 2, "general", "nav_down"),
      NavProfileChoice(engine, 2, "general", "nav_cancel"),
    ]
    player2NavSettingsMenu = Menu.Menu(engine, player2NavSettings)
 
    modes = engine.video.getVideoModes()
    modes.reverse()
    Config.define("video",  "resolution", str,   "640x480", text = _("Video Resolution"), options = ["%dx%d" % (m[0], m[1]) for m in modes])
    videoSettings = [
      ConfigChoice(engine.config, "video",  "resolution"),
      ConfigChoice(engine.config, "video",  "fullscreen"),
      ConfigChoice(engine.config, "video",  "fps"),
      ConfigChoice(engine.config, "video",  "multisamples"),
      #ConfigChoice(engine.config, "opengl", "svgshaders"),    # shaders broken at the moment
      ConfigChoice(engine.config, "opengl", "svgquality"),
      ConfigChoice(engine.config, "video", "fontscale"),
    ]
    videoSettingsMenu = Menu.Menu(engine, videoSettings + applyItem)

    volumeSettings = [
      VolumeConfigChoice(engine, engine.config, "audio",  "guitarvol"),
      VolumeConfigChoice(engine, engine.config, "audio",  "songvol"),
      VolumeConfigChoice(engine, engine.config, "audio",  "rhythmvol"),
      VolumeConfigChoice(engine, engine.config, "audio",  "screwupvol"),
      VolumeConfigChoice(engine, engine.config, "audio",  "gamevol"),
    ]
    volumeSettingsMenu = Menu.Menu(engine, volumeSettings + applyItem)

    audioSettings = [
      (_("Volume Settings"), volumeSettingsMenu),
      ConfigChoice(engine.config, "audio",  "delay"),
      ConfigChoice(engine.config, "audio",  "frequency"),
      ConfigChoice(engine.config, "audio",  "bits"),
      ConfigChoice(engine.config, "audio",  "buffersize"),
    ]
    audioSettingsMenu = Menu.Menu(engine, audioSettings + applyItem)
    
    player1Settings = [
      (_("Navigation Settings"), player1NavSettingsMenu),
      (_("Key Settings >"), self.player1KeySettingsMenu),
      InstrumentProfileChoice(engine, 1, "instrument",  "selected", autoApply = True),
      ProfileChoice(engine, 1, "instrument",  "two_chord_max", autoApply = True),
      ProfileChoice(engine, 1, "instrument",  "leftymode", autoApply = True),
    ]
    player1SettingsMenu = Menu.Menu(engine, player1Settings)    

    player2Settings = [
      (_("Navigation Settings"), player2NavSettingsMenu),
      (_("Key Settings >"), self.player2KeySettingsMenu),
      InstrumentProfileChoice(engine, 2, "instrument",  "selected", autoApply = True),
      ProfileChoice(engine, 2, "instrument",  "two_chord_max", autoApply = True),
      ProfileChoice(engine, 2, "instrument",  "leftymode", autoApply = True),
    ]
    player2SettingsMenu = Menu.Menu(engine, player2Settings)  

    playerSettings = [
      ConfigChoice(engine.config, "game",  "players", autoApply = True),
      (_("Player 1"), player1SettingsMenu),
      (_("Player 2"), player2SettingsMenu),      
    ]
    playerSettingsMenu = Menu.Menu(engine, playerSettings)
    
    rfModHOPOSettings = [
      ConfigChoice(engine.config, "game",  "tapping", autoApply = True),
      HopoConfigChoice(engine.config, "game",  "hopo_mark", autoApply = True),
      HopoConfigChoice(engine.config, "game",  "hopo_style", autoApply = True),
    ]
    rfModHOPOSettingsMenu = Menu.Menu(engine, rfModHOPOSettings)    

    rfModGameSettings = [
      (_("Select Song Library >"), self.baseLibrarySelect), 
      ConfigChoice(engine.config, "game",  "sort_order", autoApply = True),
      ConfigChoice(engine.config, "game",  "margin", autoApply = True),
      ConfigChoice(engine.config, "game",  "disable_vbpm", autoApply = True),
      ConfigChoice(engine.config, "game",  "board_speed", autoApply = True),
      ConfigChoice(engine.config, "game", "pov", autoApply = True),
      ConfigChoice(engine.config, "game", "tracks_type", autoApply = True),
      ConfigChoice(engine.config, "game", "party_time", autoApply = True),
      ConfigChoice(engine.config, "audio", "miss_volume", autoApply = True),
    ]
    rfModGameSettingsMenu = Menu.Menu(engine, rfModGameSettings)

    rfModFailSettings = [ 
      ConfigChoice(engine.config, "failing",  "failing", autoApply = True),
      ConfigChoice(engine.config, "failing",  "difficulty", autoApply = True),
      ConfigChoice(engine.config, "failing",  "jurgen", autoApply = True),
      ConfigChoice(engine.config, "failing",  "jurgen_volume", autoApply = True),
    ]
    rfModFailSettingsMenu = Menu.Menu(engine, rfModFailSettings)

    rfModPerfGameSettings = [
      ConfigChoice(engine.config, "video", "disable_stats", autoApply = True),
      ConfigChoice(engine.config, "video", "disable_notesfx", autoApply = True),
      ConfigChoice(engine.config, "video", "disable_notewavessfx", autoApply = True),
      ConfigChoice(engine.config, "video", "disable_fretsfx", autoApply = True),
      ConfigChoice(engine.config, "video", "disable_flamesfx", autoApply = True),
    ]
    rfModPerfGameSettingsMenu = Menu.Menu(engine, rfModPerfGameSettings)
    
    rfModPerfMenuSettings = [
      ConfigChoice(engine.config, "game", "songlist_render", autoApply = True),
      ConfigChoice(engine.config, "game", "songlist_items", autoApply = True),
      ConfigChoice(engine.config, "audio", "disable_preview", autoApply = True),
      ConfigChoice(engine.config, "game", "disable_spinny", autoApply = True),
      ConfigChoice(engine.config, "game", "disable_libcount", autoApply = True),
      ConfigChoice(engine.config, "game", "disable_librotation", autoApply = True),
    ]
    rfModPerfMenuSettingsMenu = Menu.Menu(engine, rfModPerfMenuSettings)

    rfModPerfSettings = [
      ConfigChoice(engine.config, "engine",  "game_priority", autoApply = True),
      (_("Game Performance"), rfModPerfGameSettingsMenu),
      (_("Menu Performance"), rfModPerfMenuSettingsMenu),      
    ]
    rfModPerfSettingsMenu = Menu.Menu(engine, rfModPerfSettings)
    
    rfModSettings = [
      (_("Game settings"), rfModGameSettingsMenu),
      (_("HO/PO settings"), rfModHOPOSettingsMenu),
      (_("Failing settings"), rfModFailSettingsMenu),
      (_("Performance settings"), rfModPerfSettingsMenu),
 #     (_("Player settings"), rfModPlayerSettingsMenu),
    ]
    rfModSettingsMenu = Menu.Menu(engine, rfModSettings)

    settings = [
      (_("Game Settings"),     gameSettingsMenu),
      (_("Player Settings"),   playerSettingsMenu),
      (_("Video Settings"),    videoSettingsMenu),
      (_("Audio Settings"),    audioSettingsMenu),
      (_("RF-mod Settings"),   rfModSettingsMenu),
    ]

    self.settingsToApply = settings + \
                           videoSettings + \
                           audioSettings + \
                           volumeSettings + \
                           gameSettings + \
                           skinSettings

    Menu.Menu.__init__(self, engine, settings)
    
  def applySettings(self):
    for option in self.settingsToApply:
      if isinstance(option, ConfigChoice):
        option.apply()
    self.engine.restart()

  def player1KeySettingsMenu(self):
    keySettings = [
      (_("Test Keys"), lambda: Dialogs.testKeys(self.engine)),
      KeyProfileChoice(self.engine, 1, "key_action1"),
      KeyProfileChoice(self.engine, 1, "key_action2"),
      KeyProfileChoice(self.engine, 1, "key_1"),
      KeyProfileChoice(self.engine, 1, "key_2"),
      KeyProfileChoice(self.engine, 1, "key_3"),
      KeyProfileChoice(self.engine, 1, "key_4"),
      KeyProfileChoice(self.engine, 1, "key_5"),
    ]
    keySettingsMenu = Menu.Menu(self.engine, keySettings, onClose = lambda: self.engine.view.popLayer(self))
    self.engine.view.pushLayer(keySettingsMenu)

  def player2KeySettingsMenu(self):
    keySettings = [
      (_("Test Keys"), lambda: Dialogs.testKeys(self.engine)),
      KeyProfileChoice(self.engine, 2, "key_action1"),
      KeyProfileChoice(self.engine, 2, "key_action2"),
      KeyProfileChoice(self.engine, 2, "key_1"),
      KeyProfileChoice(self.engine, 2, "key_2"),
      KeyProfileChoice(self.engine, 2, "key_3"),
      KeyProfileChoice(self.engine, 2, "key_4"),
      KeyProfileChoice(self.engine, 2, "key_5"),
    ]
    keySettingsMenu = Menu.Menu(self.engine, keySettings, onClose = lambda: self.engine.view.popLayer(self))
    self.engine.view.pushLayer(keySettingsMenu)
    
  def baseLibrarySelect(self):
    newPath = Dialogs.chooseFile(self.engine, masks = ["*/songs"], prompt = _("Choose a new songs directory."), extraItem = "[Accept Directory]")
    if newPath != None:
      dirName = os.path.dirname(newPath)
      baseName = os.path.basename(newPath)
      dirName2 = os.path.dirname(dirName)
      baseName2 = os.path.basename(dirName)
      
      if baseName2 == "songs":
        Config.set("game", "base_library", dirName2)
        Config.set("game", "selected_library", baseName2)
        Config.set("game", "selected_song", "")
      else:
        if os.path.exists(os.path.join(dirName, "songs")):
          Config.set("game", "base_library", dirName)
          Config.set("game", "selected_library", "songs")
          Config.set("game", "selected_song", "")
        else:
          Dialogs.showMessage(self.engine, _("No songs directory found."))

class GameSettingsMenu(Menu.Menu):
  def __init__(self, engine):
    settings = [
      VolumeConfigChoice(engine, engine.config, "audio",  "guitarvol", autoApply = True),
      VolumeConfigChoice(engine, engine.config, "audio",  "songvol", autoApply = True),
      VolumeConfigChoice(engine, engine.config, "audio",  "rhythmvol", autoApply = True),
      VolumeConfigChoice(engine, engine.config, "audio",  "screwupvol", autoApply = True),
    ]
    Menu.Menu.__init__(self, engine, settings)
