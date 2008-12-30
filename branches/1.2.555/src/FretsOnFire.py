#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#####################################################################
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

"""
Main game executable.
"""

# Register the latin-1 encoding
import codecs
import encodings.iso8859_1
import encodings.utf_8
codecs.register(lambda encoding: encodings.iso8859_1.getregentry())
codecs.register(lambda encoding: encodings.utf_8.getregentry())
assert codecs.lookup("iso-8859-1")
assert codecs.lookup("utf-8")

from GameEngine import GameEngine
from MainMenu import MainMenu
import Log
import Config
import Version

import getopt
import sys
import os 
import Resource

usage = """%(prog)s [options]
Options:
  --verbose, -v                     Verbose messages
  --debug,   -d                     Write Debug file
  --config=, -c [configfile]        Use this instead of fretsonfire.ini
  --play=,   -p [SongDir]           Play a song from the commandline
  --diff=,   -D [difficulty number] Use this difficulty
  --part=,   -P [part number]       Use this part
  --diff2=,  -E [difficulty number] Use this difficulty for player 2
  --part2=,  -Q [part number]       Use this part for player 2  
""" % {"prog": sys.argv[0] }

if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:], "vdc:p:D:P:E:Q:", ["verbose", "debug", "config=", "play=", "diff=", "part=", "diff2=", "part2="])
  except getopt.GetoptError:
    print usage
    sys.exit(1)
    
  playing = None
  configFile = None
  debug = False
  diff1 = 0
  part1 = 0
  diff2 = -1
  part2 = -1
  
  for opt, arg in opts:
    if opt in ["--verbose", "-v"]:
      Log.quiet = False
    if opt in ["--debug", "-d"]:
      debug = True
    if opt in ["--config", "-c"]:
      configFile = arg
    if opt in ["--play", "-p"]:
      playing = arg
    if opt in ["--diff", "-D"]:
      diff1 = arg      
    if opt in ["--part", "-P"]:
      part1 = arg
    if opt in ["--diff2", "-E"]:
      diff2 = arg      
    if opt in ["--part2", "-Q"]:
      part2 = arg
      
  while True:
    if configFile != None:
      if configFile.lower() == "reset":
        fileName = os.path.join(Resource.getWritableResourcePath(), Version.appName() + ".ini")
        os.remove(fileName)
        config = Config.load(Version.appName() + ".ini", setAsDefault = True)
      else:
        config = Config.load(configFile, setAsDefault = True)
    else:
      config = Config.load(Version.appName() + ".ini", setAsDefault = True)
    engine = GameEngine(config)
    engine.cmdPlay = 0
    
    if playing != None:
      Config.set("game", "selected_library", "songs")
      Config.set("game", "selected_song", playing)
      engine.cmdPlay = 1
      #engine.cmdDiff = int(difficulty)
      #engine.cmdPart = int(part)
      engine.cmdPlay = (playing, [int(diff1), int(diff2)], [int(part1), int(part2)])
                        
    if debug == True:
      engine.setDebugModeEnabled(not engine.isDebugModeEnabled())
      engine.debugLayer.debugOut(engine)
      engine.quit()
      break
      
    encoding = Config.get("game", "encoding")
    if encoding != None:
      reload(sys)
      sys.setdefaultencoding(encoding)

    menu   = MainMenu(engine, songName = playing)
    engine.setStartupLayer(menu)


    try:
      import psyco
      psyco.profile()
    except:
      Log.warn("Unable to enable psyco.")

    try:
      while engine.run():
        pass
    except KeyboardInterrupt:
        pass
    if engine.restartRequested:
      Log.notice("Restarting.")
      engine.audio.close()
      try:
        # Determine whether were running from an exe or not
        if hasattr(sys, "frozen"):
          if os.name == "nt":
            os.execl("FretsOnFire.exe", "FretsOnFire.exe", *sys.argv[1:])
          else:
            os.execl("./FretsOnFire", "./FretsOnFire", *sys.argv[1:])
        else:
          if os.name == "nt":
            bin = "c:/python24/python"
          else:
            bin = "/usr/bin/python"
          os.execl(bin, bin, "FretsOnFire.py", *sys.argv[1:])
      except:
        Log.warn("Restart failed.")
        raise
      break
    else:
      break
  engine.quit()
