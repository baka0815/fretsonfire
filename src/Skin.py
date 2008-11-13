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

import os
import Config
import Theme
from Language import _

def _getSkinPath(engine):
  return engine.resource.fileName("skins")

def initLevel(engine, dir=None):
  for w in getAvailableSkinDirs(engine, dir=dir):
    initLevel(engine, dir=w)
  for m in getAvailableSkins(engine, dir):
    if dir == None:
      Config.define("skins", "skin_" + m, bool, False, text = m,  options = {False: _("Off"), True: _("On")})
    else:
      Config.define("skins", "skin_%s/" % (dir) + m, bool, False, text = m,  options = {False: _("Off"), True: _("On")})
      
def init(engine):
  # define configuration keys for all available skins
  initLevel(engine)

  # init all active skins
  for m in getActiveSkins(engine):
    activateSkin(engine, m)

def getAvailableSkins(engine, dir=None):
  if dir == None:
    skinPath = _getSkinPath(engine)
  else:
    skinPath = os.path.join(_getSkinPath(engine), dir)
  skins = []
  for m in os.listdir(skinPath):
    subSkinPath = os.path.join(skinPath, m)
    if os.path.isdir(subSkinPath) and not m.startswith("."):
      for n in os.listdir(subSkinPath):
        if not n.startswith(".") and os.path.isdir(os.path.join(subSkinPath, n)):
          break;
      else:
        if os.listdir(subSkinPath) != []:         
          skins.append(m)
  return skins

def getAvailableSkinDirs(engine, dir=None):
  if dir == None:
    skinPath = _getSkinPath(engine)
  else:
    skinPath = os.path.join(_getSkinPath(engine), dir)
  skins = []
  for m in os.listdir(skinPath):
    subSkinPath = os.path.join(skinPath, m)
    if os.path.isdir(subSkinPath) and not m.startswith("."):
      for n in os.listdir(subSkinPath):
        if not n.startswith(".") and os.path.isfile(os.path.join(subSkinPath, n)):
          break;
      else:
        #if os.listdir(subSkinPath) != []:         
        skins.append(m)
  return skins

def getActiveSkins(engine, dir=None):
  skins = []
  for d in getAvailableSkinDirs(engine, dir=dir):
    skins += getActiveSkins(engine, dir=d)
  for skin in getAvailableSkins(engine, dir=dir):
    if dir == None:
      if engine.config.get("skins", "skin_" + skin):
        skins.append(skin)
    else:
      if engine.config.get("skins", "skin_%s/" % (dir) + skin):
        skins.append("%s/" % (dir) + skin)
  skins.sort()
  return skins

def activateSkin(engine, skinName):
  skinPath = _getSkinPath(engine)
  m = os.path.join(skinPath, skinName)
  t = os.path.join(m, "theme.ini")
  if os.path.isdir(m):
    engine.resource.addDataPath(m)
    if os.path.isfile(t):
      theme = Config.load(t)
      Theme.open(theme)


def deactivateSkin(engine, skinName):
  skinPath = _getSkinPath(engine)
  m = os.path.join(skinPath, skinName)
  engine.resource.removeDataPath(m)
