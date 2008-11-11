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

from Scene import SceneServer, SceneClient
import Player
import Dialogs
import Song
import Config
import Difficulty
import Part
from Language import _

import os
# save chosen song into config file
Config.define("game", "selected_library",  str, "")
Config.define("game", "selected_song",     str, "")

class SongChoosingScene:
  pass

class SongChoosingSceneServer(SongChoosingScene, SceneServer):
  pass

class SongChoosingSceneClient(SongChoosingScene, SceneClient):
  def createClient(self, libraryName = None, songName = None):
    self.wizardStarted = False
    self.libraryName   = libraryName
    self.songName      = songName

  def freeResources(self):
    self.songs = None
    self.cassette = None
    self.folder = None
    self.label = None
    self.song = None
    self.background = None
    
  def run(self, ticks):
    SceneClient.run(self, ticks)
    players = 1

    if not self.wizardStarted:
      self.wizardStarted = True


      if self.engine.cmdPlay == 1:
        self.songName = Config.get("game", "selected_song")
        self.libraryName = Config.get("game", "selected_library")
        self.engine.cmdPlay = 2
        
      if not self.songName:
        finished = False
        escape = False
        while not finished:
          self.libraryName, self.songName = \
            Dialogs.chooseSong(self.engine, \
                               selectedLibrary = Config.get("game", "selected_library"),
                               selectedSong    = Config.get("game", "selected_song"))

          if self.libraryName == None:
            newPath = Dialogs.chooseFile(self.engine, masks = ["*/songs"], prompt = _("Choose a new songs directory."), dirSelect = True)
            if newPath != None:
              Config.set("game", "base_library", os.path.dirname(newPath))
              Config.set("game", "selected_library", "songs")
              Config.set("game", "selected_song", "")
            
          if not self.songName:
            self.session.world.finishGame()
            return

          Config.set("game", "selected_library", self.libraryName)
          Config.set("game", "selected_song",    self.songName)
          
          info = Song.loadSongInfo(self.engine, self.songName, library = self.libraryName)

          diffList = []
          for diff in info.difficulties:
            diffList.append(Difficulty.difficulties.get(diff))
                            
          partList = []
          for part in info.parts:
            partList.append(Part.parts.get(part))
                                
          escape = False
          
          while not finished:
            p1Part = None
            if len(info.parts) > 1:
              choice = Dialogs.chooseItem(self.engine, partList, "%s \n %s" % (info.name, _("Player 1 Choose a part:")), selected = self.player.part)
              escape = False
              for part in info.parts:
                print Part.parts.get(part), choice, Part.parts.get(part) == choice
                if Part.parts.get(part) == choice:
                  p1Part = part
            else:
              if escape == True:
                break
              p1Part = Part.GUITAR_PART
            if p1Part != None:
              self.player.part = p1Part
            else:
              break;

            while not finished:
              p1Diff = None
              if len(info.difficulties) > 1:
                choice = Dialogs.chooseItem(self.engine, diffList, "%s \n %s" % (info.name, _("Player 1 Choose a difficulty:")), selected = self.player.difficulty)
                escape = False
                for diff in info.difficulties:
                  if Difficulty.difficulties.get(diff) == choice:
                    p1Diff = diff
              else:
                if escape == True:
                  break
                p1Diff = Difficulty.AMAZING_DIFFICULTY
            
              if p1Diff != None:
                self.player.difficulty = p1Diff
              else:
                escape = True
                break

              while not finished:
                p2Part = None
                if self.engine.config.get("game", "players") > 1:               
                  choice = Dialogs.chooseItem(self.engine, partList + [Part.parts.get(Part.PARTY_PART)] + [Part.parts.get(Part.NO_PART)], "%s \n %s" % (info.name, _("Player 2 Choose a part:")), selected = self.player2.part)
                  escape = False
                  print choice
 
                  if choice == Part.parts.get(Part.NO_PART):
                    p2Part = Part.NO_PART
                    players = 1
                    self.player2.part = p2Part
                  elif choice == Part.parts.get(Part.PARTY_PART):
                    p2Part = Part.PARTY_PART
                    players = Part.PARTY_PART
                    selected = True
                    self.player2.part = p2Part
                  elif choice != None and choice != Part.parts.get(Part.NO_PART) and choice != Part.parts.get(Part.PARTY_PART):
                    players = 2
                    for part in info.parts:
                      if Part.parts.get(part) == choice:
                        p2Part = part
                        
                  if p2Part != None:
                    if escape == True:
                      break
                    self.player2.part = p2Part
                  else:
                    escape = True
                    break

                  while not finished:
                    p2Diff = None
                    if len(info.difficulties) > 1 and self.player2.part >= 0:
                      choice = Dialogs.chooseItem(self.engine, diffList, "%s \n %s" % (info.name, _("Player 2 Choose a difficulty:")), selected = self.player2.difficulty)
                      escape = False
                      
                      for diff in info.difficulties:
                        if Difficulty.difficulties.get(diff) == choice:
                          p2Diff = diff
                    else:
                      if escape == True:
                        break
                      p2Diff = Difficulty.AMAZING_DIFFICULTY
                    if p2Diff != None:
                      self.player2.difficulty = p2Diff
                      finished = True
                    else:
                      escape = True
                      break

                else:
                  finished = True

      else:
        info = Song.loadSongInfo(self.engine, self.songName, library = self.libraryName)
    
      if self.engine.cmdPlay == 2:
        if len(info.difficulties) >= self.engine.cmdDiff:
          self.player.difficulty = info.difficulties[self.engine.cmdDiff]
        if len(info.parts) >= self.engine.cmdPart:
          self.player.part = info.parts[self.engine.cmdPart]

      print "player1 diff", self.player.difficulty
      print "player1 part", self.player.part

      print "player2 diff", self.player2.difficulty
      print "player2 part", self.player2.part

      print "info part", info.parts      
      
      # Make sure the difficulty we chose is available
      if not self.player.difficulty in info.difficulties:
        self.player.difficulty = info.difficulties[0]
      if not self.player.part in info.parts:
        self.player.part = info.parts[0]

      if not self.player.difficulty in info.difficulties:
        self.player.difficulty = info.difficulties[0]
      if not self.player.part in info.parts:
        self.player.part = info.parts[0]   

      print "player1 diff", self.player.difficulty
      print "player1 part", self.player.part

      print "player2 diff", self.player2.difficulty
      print "player2 part", self.player2.part
      
      self.session.world.deleteScene(self)
      self.session.world.createScene("GuitarScene", libraryName = self.libraryName, songName = self.songName, Players = players)
