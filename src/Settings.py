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
import Mod
import Audio

import pygame

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

class KeyConfigChoice(Menu.Choice):
  def __init__(self, engine, config, section, option):
    self.engine  = engine
    self.config  = config
    self.section = section
    self.option  = option
    self.changed = False
    self.value   = None

    #Load alternate keyset
    useAltKeySet = self.engine.config.get("game", "alt_keys")                   
    if not useAltKeySet == True:
       self.option = self.option
    else:
      self.option = "a%s" % (self.option)
      
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


class SettingsMenu(Menu.Menu):
  def __init__(self, engine):
    applyItem = [(_("Apply New Settings"), self.applySettings)]

    modSettings = [
      ConfigChoice(engine.config, "mods",  "mod_" + m) for m in Mod.getAvailableMods(engine)
    ] + applyItem
    
    gameSettings = [
      (_("Mod settings"), modSettings),
      ConfigChoice(engine.config, "game",  "language"),
      ConfigChoice(engine.config, "game",  "leftymode", autoApply = True),
      ConfigChoice(engine.config, "game",  "tapping", autoApply = True),
      ConfigChoice(engine.config, "game",  "uploadscores", autoApply = True),
    ]
    gameSettingsMenu = Menu.Menu(engine, gameSettings + applyItem)

    keySettings = [
      (_("Test Keys"), lambda: Dialogs.testKeys(engine)),
      KeyConfigChoice(engine, engine.config, "player0", "key_action1"),
      KeyConfigChoice(engine, engine.config, "player0", "key_action2"),
      KeyConfigChoice(engine, engine.config, "player0", "key_1"),
      KeyConfigChoice(engine, engine.config, "player0", "key_2"),
      KeyConfigChoice(engine, engine.config, "player0", "key_3"),
      KeyConfigChoice(engine, engine.config, "player0", "key_4"),
      KeyConfigChoice(engine, engine.config, "player0", "key_5"),
      KeyConfigChoice(engine, engine.config, "player0", "key_left"),
      KeyConfigChoice(engine, engine.config, "player0", "key_right"),
      KeyConfigChoice(engine, engine.config, "player0", "key_up"),
      KeyConfigChoice(engine, engine.config, "player0", "key_down"),
      KeyConfigChoice(engine, engine.config, "player0", "key_cancel"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_action1"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_action2"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_1"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_2"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_3"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_4"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_5"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_left"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_right"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_up"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_down"),
      KeyConfigChoice(engine, engine.config, "player1", "player_2_key_cancel"),
    ]
    keySettingsMenu = Menu.Menu(engine, keySettings)
    
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

    rfModPlayer0Settings = [
      ConfigChoice(engine.config, "player0",  "two_chord_max", autoApply = True),
      ConfigChoice(engine.config, "player0",  "leftymode", autoApply = True),
    ]
    rfModPlayer0SettingsMenu = Menu.Menu(engine, rfModPlayer0Settings)

    rfModPlayer1Settings = [
      ConfigChoice(engine.config, "player1",  "two_chord_max", autoApply = True),
      ConfigChoice(engine.config, "player1",  "leftymode", autoApply = True),
    ]
    rfModPlayer1SettingsMenu = Menu.Menu(engine, rfModPlayer1Settings)    
    
    rfModGameSettings = [
      ConfigChoice(engine.config, "game",  "alt_keys", autoApply = True),
      ConfigChoice(engine.config, "game",  "hopo_type", autoApply = True),
      #ConfigChoice(engine.config, "game",  "strum_burst", autoApply = True),
      ConfigChoice(engine.config, "game",  "sort_order", autoApply = True),
      ConfigChoice(engine.config, "game",  "disable_vbpm", autoApply = True),
      ConfigChoice(engine.config, "audio", "miss_volume", autoApply = True),
    ]
    rfModGameSettingsMenu = Menu.Menu(engine, rfModGameSettings)
    
    rfModPerfSettings = [
      ConfigChoice(engine.config, "engine",  "game_priority", autoApply = True),
      ConfigChoice(engine.config, "audio", "disable_preview", autoApply = True),
      ConfigChoice(engine.config, "video", "disable_stats", autoApply = True),
      ConfigChoice(engine.config, "video", "disable_notesfx", autoApply = True),
      ConfigChoice(engine.config, "video", "disable_fretsfx", autoApply = True),
      ConfigChoice(engine.config, "video", "disable_flame1", autoApply = True),
      ConfigChoice(engine.config, "video", "disable_flame2", autoApply = True),
    ]
    rfModPerfSettingsMenu = Menu.Menu(engine, rfModPerfSettings)

    rfModSettings = [
      ConfigChoice(engine.config, "game",  "players", autoApply = True),
      (_("Game settings"), rfModGameSettingsMenu),
      (_("Performance settings"), rfModPerfSettingsMenu),
      (_("Player 1 settings"), rfModPlayer0SettingsMenu),
      (_("Player 2 settings"), rfModPlayer1SettingsMenu),
    ]
    rfModSettingsMenu = Menu.Menu(engine, rfModSettings)

    settings = [
      (_("Game Settings"),     gameSettingsMenu),
      (_("Key Settings"),      keySettingsMenu),
      (_("Video Settings"),    videoSettingsMenu),
      (_("Audio Settings"),    audioSettingsMenu),
      (_("RF-mod Settings"),   rfModSettingsMenu),
    ]
  
    self.settingsToApply = settings + \
                           videoSettings + \
                           audioSettings + \
                           volumeSettings + \
                           gameSettings + \
                           modSettings

    Menu.Menu.__init__(self, engine, settings)
    
  def applySettings(self):
    for option in self.settingsToApply:
      if isinstance(option, ConfigChoice):
        option.apply()
    self.engine.restart()

class GameSettingsMenu(Menu.Menu):
  def __init__(self, engine):
    settings = [
      VolumeConfigChoice(engine, engine.config, "audio",  "guitarvol", autoApply = True),
      VolumeConfigChoice(engine, engine.config, "audio",  "songvol", autoApply = True),
      VolumeConfigChoice(engine, engine.config, "audio",  "rhythmvol", autoApply = True),
      VolumeConfigChoice(engine, engine.config, "audio",  "screwupvol", autoApply = True),
    ]
    Menu.Menu.__init__(self, engine, settings)
