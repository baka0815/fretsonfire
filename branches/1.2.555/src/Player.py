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

import pygame
import Config
import Profile
import Part
import Difficulty

from Language import _

PLAYER_1_LEFT    = 0x000001
PLAYER_1_RIGHT   = 0x000002
PLAYER_1_UP      = 0x000004
PLAYER_1_DOWN    = 0x000008
PLAYER_1_CANCEL  = 0x000010
PLAYER_1_ACTION1 = 0x000020
PLAYER_1_ACTION2 = 0x000040
PLAYER_1_KEY1    = 0x000090
PLAYER_1_KEY2    = 0x000100
PLAYER_1_KEY3    = 0x000200
PLAYER_1_KEY4    = 0x000400
PLAYER_1_KEY5    = 0x000800

PLAYER_2_LEFT    = 0x001000
PLAYER_2_RIGHT   = 0x002000
PLAYER_2_UP      = 0x004000
PLAYER_2_DOWN    = 0x008000
PLAYER_2_CANCEL  = 0x010000
PLAYER_2_ACTION1 = 0x020000
PLAYER_2_ACTION2 = 0x040000
PLAYER_2_KEY1    = 0x080000
PLAYER_2_KEY2    = 0x100000
PLAYER_2_KEY3    = 0x200000
PLAYER_2_KEY4    = 0x400000
PLAYER_2_KEY5    = 0x800000


LEFTS    = [PLAYER_1_LEFT,PLAYER_2_LEFT]
RIGHTS   = [PLAYER_1_RIGHT,PLAYER_2_RIGHT]
UPS      = [PLAYER_1_UP,PLAYER_2_UP]
DOWNS    = [PLAYER_1_DOWN,PLAYER_2_DOWN]
ACTION1S = [PLAYER_1_ACTION1,PLAYER_2_ACTION1]
ACTION2S = [PLAYER_1_ACTION2,PLAYER_2_ACTION2]
CANCELS  = [PLAYER_1_CANCEL,PLAYER_2_CANCEL]
KEY5S    = [PLAYER_1_KEY5,PLAYER_2_KEY5]
KEY1S    = [PLAYER_1_KEY1,PLAYER_2_KEY1]
KEY2S    = [PLAYER_1_KEY2,PLAYER_2_KEY2]
KEY3S    = [PLAYER_1_KEY3,PLAYER_2_KEY3]
KEY4S    = [PLAYER_1_KEY4,PLAYER_2_KEY4]
KEY5S    = [PLAYER_1_KEY5,PLAYER_2_KEY5]

PLAYER_1_KEYS    = [PLAYER_1_KEY1, PLAYER_1_KEY2, PLAYER_1_KEY3, PLAYER_1_KEY4, PLAYER_1_KEY5]
PLAYER_1_ACTIONS = [PLAYER_1_ACTION1, PLAYER_1_ACTION2]

PLAYER_2_KEYS    = [PLAYER_2_KEY1, PLAYER_2_KEY2, PLAYER_2_KEY3, PLAYER_2_KEY4, PLAYER_2_KEY5]
PLAYER_2_ACTIONS = [PLAYER_2_ACTION1, PLAYER_2_ACTION2]

SCORE_MULTIPLIER = [0, 10, 20, 30]

# define profile keys
Profile.define("general", "nav_left",     str, "K_LEFT",     text = _("Move left"))
Profile.define("general", "nav_right",    str, "K_RIGHT",    text = _("Move right"))
Profile.define("general", "nav_up",       str, "K_UP",       text = _("Move up"))
Profile.define("general", "nav_down",     str, "K_DOWN",     text = _("Move down"))
Profile.define("general", "nav_cancel",   str, "K_ESCAPE",   text = _("Cancel"))

Profile.define("guitarX", "key_action1",  str, "K_PAGEDOWN", text = _("Pick"))
Profile.define("guitarX", "key_action2",  str, "K_PAGEUP",   text = _("Secondary Pick"))
Profile.define("guitarX", "key_1",        str, "K_F8",       text = _("Fret #1"))
Profile.define("guitarX", "key_2",        str, "K_F9",       text = _("Fret #2"))
Profile.define("guitarX", "key_3",        str, "K_F10",      text = _("Fret #3"))
Profile.define("guitarX", "key_4",        str, "K_F11",      text = _("Fret #4"))
Profile.define("guitarX", "key_5",        str, "K_F12",      text = _("Fret #5"))

Profile.define("drumX", "key_action1",    str, "K_PAGEDOWN", text = _("Pedal"))
Profile.define("drumX", "key_action2",    str, "K_PAGEUP",   text = _("Secondary Pedal"))
Profile.define("drumX", "key_1",          str, "K_F8",       text = _("Head #1"))
Profile.define("drumX", "key_2",          str, "K_F9",       text = _("Head #2"))
Profile.define("drumX", "key_3",          str, "K_F10",      text = _("Head #3"))
Profile.define("drumX", "key_4",          str, "K_F11",      text = _("Head #4"))
Profile.define("drumX", "key_5",          str, "K_F12",      text = _("Head #5"))

Profile.define("general", "name",         str, "",           text = _("Player Name"))
Profile.define("instrument", "selected",  str, "guitar1",    text = _("Instrument"), options = {"guitar1": _("Guitar 1"), "guitar2": _("Guitar 2"), "guitar3": _("Guitar 3"), "drum1": _("Drum 1"), "drum2": _("Drum 2"), "drum3": _("Drum 3")})

Profile.define("song", "difficulty",      int, Difficulty.EASY_DIFFICULTY)
Profile.define("song", "part",            int, Part.GUITAR_PART)

class Controls:
  def __init__(self, profileList):
    self.profileList = profileList

    def navcode(name, player):
      playerNum = player - 1
      k = self.profileList[playerNum].get("general", name)
      try:
        return int(k)
      except:
        return getattr(pygame, k)
      
    def keycode(name, player):
      playerNum = player - 1
      instrument = self.profileList[playerNum].get("instrument", "selected")
      k = self.profileList[playerNum].get(instrument, name)      
      if k == "None":
        genericSection = instrument[:-1]
        genericSection += "X"
        k = self.profileList[playerNum].get(genericSection, name)

      try:
        return int(k)
      except:
        return getattr(pygame, k)
    
    self.flags = 0

    self.controlMapping = {
      navcode("nav_left", 1):      PLAYER_1_LEFT,
      navcode("nav_right", 1):     PLAYER_1_RIGHT,
      navcode("nav_up", 1):        PLAYER_1_UP,
      navcode("nav_down", 1):      PLAYER_1_DOWN,
      navcode("nav_cancel", 1):    PLAYER_1_CANCEL,

      keycode("key_action1", 1):   PLAYER_1_ACTION1,
      keycode("key_action2", 1):   PLAYER_1_ACTION2,
      keycode("key_1", 1):         PLAYER_1_KEY1,
      keycode("key_2", 1):         PLAYER_1_KEY2,
      keycode("key_3", 1):         PLAYER_1_KEY3,
      keycode("key_4", 1):         PLAYER_1_KEY4,
      keycode("key_5", 1):         PLAYER_1_KEY5,

   
      navcode("nav_left", 2):      PLAYER_2_LEFT,
      navcode("nav_right", 2):     PLAYER_2_RIGHT,
      navcode("nav_up", 2):        PLAYER_2_UP,
      navcode("nav_down", 2):      PLAYER_2_DOWN,
      navcode("nav_cancel", 2):    PLAYER_2_CANCEL,

      keycode("key_action1", 2):   PLAYER_2_ACTION1,
      keycode("key_action2", 2):   PLAYER_2_ACTION2,
      keycode("key_1", 2):         PLAYER_2_KEY1,
      keycode("key_2", 2):         PLAYER_2_KEY2,
      keycode("key_3", 2):         PLAYER_2_KEY3,
      keycode("key_4", 2):         PLAYER_2_KEY4,
      keycode("key_5", 2):         PLAYER_2_KEY5,
    }  
    
    self.reverseControlMapping = dict((value, key) for key, value in self.controlMapping.iteritems() )
      
    # Multiple key support
    self.heldKeys = {}

  def getMapping(self, key):
    return self.controlMapping.get(key)
  def getReverseMapping(self, control):
    return self.reverseControlMapping.get(control)

  def keyPressed(self, key):
    c = self.getMapping(key)
    if c:
      self.toggle(c, True)
      if c in self.heldKeys and not key in self.heldKeys[c]:
        self.heldKeys[c].append(key)
      return c
    return None

  def keyReleased(self, key):
    c = self.getMapping(key)
    if c:
      if c in self.heldKeys:
        if key in self.heldKeys[c]:
          self.heldKeys[c].remove(key)
          if not self.heldKeys[c]:
            self.toggle(c, False)
            return c
        return None
      self.toggle(c, False)
      return c
    return None

  def toggle(self, control, state):
    prevState = self.flags
    if state:
      self.flags |= control
      return not prevState & control
    else:
      self.flags &= ~control
      return prevState & control

  def getState(self, control):
    return self.flags & control

class Player(object):
  def __init__(self, profileList, owner, name, number):
    self.owner    = owner
    self.controls = Controls(profileList)
    self.reset()
   
    self.profile = profileList[number]
    
  def reset(self):
    self.score         = 0
    self._streak       = 0
    self.notesHit      = 0
    self.longestStreak = 0
    self.cheating      = False
    self.twoChord      = 0
    self.lastExtraScore = 0
    
  def getName(self):
    return self.profile.get("general", "name")
    
  def setName(self, name):
    self.profile.set("general", "name", name)
    
  name = property(getName, setName)
  
  def getStreak(self):
    return self._streak
    
  def setStreak(self, value):
    self._streak = value
    self.longestStreak = max(self._streak, self.longestStreak)
    
  streak = property(getStreak, setStreak)
    
  def getDifficulty(self):
    return self.profile.get("song", "difficulty")
    
  def setDifficulty(self, difficulty):
    self.profile.set("song", "difficulty", difficulty)

  def getPart(self):
    return self.profile.get("song", "part")
    
  def setPart(self, part):
    self.profile.set("song", "part", part)    
    
  difficulty = property(getDifficulty, setDifficulty)
  part = property(getPart, setPart)
  
  def addScore(self, score):
    self.score += score * self.getScoreMultiplier()
    
  def getScoreMultiplier(self):
    try:
      return SCORE_MULTIPLIER.index((self.streak / 10) * 10) + 1
    except ValueError:
      return len(SCORE_MULTIPLIER)
