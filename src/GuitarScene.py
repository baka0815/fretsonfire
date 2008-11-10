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

from Scene import SceneServer, SceneClient
from Song import Note, Tempo, TextEvent, PictureEvent, loadSong
from Menu import Menu
from Guitar import Guitar, PLAYER1KEYS, PLAYER2KEYS, PLAYER1ACTIONS, PLAYER2ACTIONS
from Language import _
import Player
import Dialogs
import Data
import Theme
import View
import Audio
import Stage
import Settings
import Song

import math
import pygame
import random
import os
from OpenGL.GL import *

class GuitarScene:
  pass

class GuitarSceneServer(GuitarScene, SceneServer):
  pass

class GuitarSceneClient(GuitarScene, SceneClient):
  def createClient(self, libraryName, songName, Players):
    self.playerList   = [self.player]
    self.keysList     = [PLAYER1KEYS]
    self.partyMode    = False
    if Players == -1:
      self.partyMode  = True
      Players         = 1
    if Players == 2:
      self.playerList = self.playerList + [self.player2]
      self.keysList   = self.keysList + [PLAYER2KEYS]

    self.guitars          = [Guitar(self.engine,False,i) for i,player in enumerate(self.playerList)]
    
    self.screwUpVolume    = self.engine.config.get("audio", "screwupvol")
    for i,guitar in enumerate(self.guitars):
      guitar.leftyMode = self.engine.config.get("player%d" % (i), "leftymode")
      guitar.twoChordMax  = self.engine.config.get("player%d" % (i), "two_chord_max")
    #RF-mod (not needed?)
    #self.disableFlame1    = self.engine.config.get("video", "disable_flame1")
    #self.disableFlame2    = self.engine.config.get("video", "disable_flame2")
    self.disableStats     = self.engine.config.get("video", "disable_stats")
    self.hopoType         = self.engine.config.get("game", "hopo_type")
    self.lastSwitch       = 0
    self.partyTime        = 30
    self.partyPlayer      = 0

    
    self.visibility       = 0.0
    self.libraryName      = libraryName
    self.songName         = songName
    self.done             = False
    self.sfxChannel       = self.engine.audio.getChannel(self.engine.audio.getChannelCount() - 1)
    self.lastMultTime     = [None for i in self.playerList]
    self.cheatCodes       = [
      ([117, 112, 116, 111, 109, 121, 116, 101, 109, 112, 111], self.toggleAutoPlay),
      ([102, 97, 115, 116, 102, 111, 114, 119, 97, 114, 100],   self.goToResults)
    ]
    self.enteredCode      = []
    self.song             = None
    self.autoPlay         = False
    self.lastPickPos      = [None for i in self.playerList]
    self.lastSongPos      = 0.0
    self.keyBurstTimeout  = [None for i in self.playerList]
    self.keyBurstPeriod   = 30
    self.camera.target    = (0, 0, 4)
    self.camera.origin    = (0, 3, -3)

    #new
    self.loadSettings()
    self.engine.resource.load(self, "song",          lambda: loadSong(self.engine, songName, library = libraryName, part = [player.part for player in self.playerList]), onLoad = self.songLoaded)
    
    self.stage            = Stage.Stage(self, self.engine.resource.fileName("stage.ini"))
    
    self.engine.loadSvgDrawing(self, "fx2x",   "2x.svg", textureSize = (256, 256))
    self.engine.loadSvgDrawing(self, "fx3x",   "3x.svg", textureSize = (256, 256))
    self.engine.loadSvgDrawing(self, "fx4x",   "4x.svg", textureSize = (256, 256))

    #new
    Dialogs.showLoadingScreen(self.engine, lambda: self.song, text = _("Tuning Guitar..."))

    settingsMenu = Settings.GameSettingsMenu(self.engine)
    settingsMenu.fadeScreen = True

    self.menu = Menu(self.engine, [
      (_("Restart Song"),      self.restartSong),
      (_("Change Song"),       self.changeSong),
      (_("End Song"),          self.endSong),
      (_("Settings"),          settingsMenu),
      (_("Quit to Main Menu"), self.quit),
    ], fadeScreen = True, onClose = self.resumeGame)

    self.restartSong()

  def pauseGame(self):
    if self.song:
      self.song.pause()

  def resumeGame(self):
    self.loadSettings()
    self.setCamera()
    if self.song:
      self.song.unpause()

  def setCamera(self):
    if self.pov == 1:
      self.camera.target    = (1, 1, 1)
      self.camera.origin    = (0, 5, -5)
    elif self.pov == 2:
      self.camera.target    = (0, 0, 4)
      self.camera.origin    = (0, 2, -2)
    else:
      self.camera.target    = (0, 0, 4)
      self.camera.origin    = (0, 3, -3)
      
  #RF-mod (not needed?)
  def freeResources(self):
    self.song = None
    #self.screwUpSounds = None
    # Why can't I free these?
    #self.fx2x = None
    #self.fx3x = None
    #self.fx4x = None
    #self.flame1 = None
    #self.flame2 = None
    self.menu = None
    
  def loadSettings(self):
    #self.delay            = self.engine.config.get("audio", "delay")
    self.screwUpVolume    = self.engine.config.get("audio", "screwupvol")
    self.guitarVolume     = self.engine.config.get("audio", "guitarvol")
    self.songVolume       = self.engine.config.get("audio", "songvol")
    self.rhythmVolume     = self.engine.config.get("audio", "rhythmvol")
    self.pov              = self.engine.config.get("game", "pov")
    #self.guitar.leftyMode = self.engine.config.get("game",  "leftymode")

    if self.song:
      self.song.setBackgroundVolume(self.songVolume)
      self.song.setRhythmVolume(self.rhythmVolume)
    
  def songLoaded(self, song):

    for i,player in enumerate(self.playerList):
      song.difficulty[i] = player.difficulty
    #self.delay += song.info.delay

    # If tapping is disabled, remove the tapping indicators
    if not self.engine.config.get("game", "tapping"):
      for time, event in self.song.track.getAllEvents():
        if isinstance(event, Note):
          event.tappable = False

  def endSong(self):
    self.engine.view.popLayer(self.menu)
    self.freeResources()
    self.goToResults()

  def quit(self):
    if self.song:
      self.song.stop()
    self.done = True
    self.engine.view.popLayer(self.menu)
    self.freeResources()
    self.session.world.finishGame()

  def changeSong(self):
    if self.song:
      self.song.stop()
      self.song  = None
    self.engine.view.popLayer(self.menu)
    self.session.world.deleteScene(self)
    self.session.world.createScene("SongChoosingScene")

  def restartSong(self):
    self.engine.data.startSound.play()
    self.engine.view.popLayer(self.menu)
    for player in self.playerList:
      player.reset()
    self.stage.reset()
    self.enteredCode     = []
    self.autoPlay        = False
    for guitar in self.guitars:
      guitar.twoChord = 0
      guitar.hopoActive = False
      guitar.hopoLast = -1

    self.engine.collectGarbage()

    self.setCamera()
    
    if not self.song:
      return
      
    self.countdown    = 8.0
    self.lastSwitch = 0
    for i,guitar in enumerate(self.guitars):
      guitar.endPick(i)
    self.song.stop()

    for i, guitar in enumerate(self.guitars):
      if self.hopoType == 1 or (self.hopoType == 2 and self.song.info.hopo == "on"):
        self.doHopo(i)
    
    if self.disableStats != True:
      lastEventList = [len(self.song.track[i].getAllEvents()) for i in range(len(self.guitars))]
      pos = []
      for i,lastEvent in enumerate(lastEventList):
        if lastEvent > 0:
          posi,event = self.song.track[i].getAllEvents()[lastEvent-1]
          pos = pos + [[posi,event]]
      if len(pos) > 0:
        pos.sort(lambda x,y: int(y[0]-x[0]))
        self.lastEvent = pos[len(pos)-1][0] + pos[len(pos)-1][1].length + 1000
        self.lastEvent = round(self.lastEvent / 1000) * 1000
        self.notesCum = 0
        self.noteLastTime = 0
      else:
        self.lastEvent = 0
        self.notesCum = 0
        self.noteLastTime = 0

  def doHopo(self, num):
    lastTick = 0
    lastTime  = 0
    lastEvent = Note
    
    tickDelta = 0
    noteDelta = 0

    hopoDelta = 161
    chordFudge = 10
    ticksPerBeat = 480
    hopoNotes = []
    chordNotes = []
    sameNotes = []
    bpmNotes = []
    firstTime = 1

    for time, event in self.song.track[num].getAllEvents():
      if isinstance(event, Tempo):
        bpmNotes.append([time, event])
        continue
      if not isinstance(event, Note):
        continue
      
      while bpmNotes and time >= bpmNotes[0][0]:
        #Adjust to new BPM
        bpm = bpmNotes[0][1].bpm
        bpmNotes.pop(0)

      tick = (time * bpm * ticksPerBeat) / 60000.0
      lastTick = (lastTime * bpm * ticksPerBeat) / 60000.0
      
      #skip first note
      if firstTime == 1:
        #If already processed abort
        if event.hopo != 0:
          return
        chordNotes.append(event)
        event.hopo = -3
        lastEvent = event
        lastTime  = time
        firstTime = 0
        continue
        
      tickDelta = tick - lastTick        
      noteDelta = event.number - lastEvent.number
        
      #previous note and current note HOPOable      
      if tickDelta <= hopoDelta:
        #Add both notes to HOPO list even if duplicate.  Will come out in processing
        if (not hopoNotes) or not (hopoNotes[-1][0] == lastTime and hopoNotes[-1][1] == lastEvent):
          #special case for first marker note.  Change it to a HOPO start
          if not hopoNotes and lastEvent.hopo == -3:
            lastEvent.hopo = 1
          hopoNotes.append([lastTime, lastEvent])

        hopoNotes.append([time, event])
        
      #HOPO Over        
      if tickDelta >= hopoDelta:
        if hopoNotes != []:
          #If the last event is the last HOPO note, mark it as a HOPO end
          if lastEvent.hopo != -1 and hopoNotes[-1][1] == lastEvent:
            if lastEvent.hopo >= 0:
              lastEvent.hopo = 3
            else:
              lastEvent.hopo = -1

      #This is the same note as before
      elif noteDelta == 0:
        #Add both notes to bad list even if duplicate.  Will come out in processing
        sameNotes.append(lastEvent)
        sameNotes.append(event)
        lastEvent.hopo = -2
        event.hopo = -2
            
      #This is a chord
      elif tickDelta < chordFudge:
        #Add both notes to bad list even if duplicate.  Will come out in processing
        if chordNotes[-1] != lastEvent:
          chordNotes.append(lastEvent)
        chordNotes.append(event)
        lastEvent.hopo = -1
        event.hopo = -1
        
      lastEvent = event
      lastTime = time
    else:
      #Add last note to HOPO list if applicable
      if noteDelta != 0 and tickDelta > 1.5 and tickDelta < hopoDelta:
        hopoNotes.append([time, event])

    firstTime = 1
    note = None
             
    for time, note in list(hopoNotes):
      if firstTime == 1:
        if note.hopo >= 0:
          note.hopo = 1
        lastEvent = note
        firstTime = 0
        continue

      #current Note Invalid      
      if note.hopo < 0:
        #If current note is invalid for HOPO, and previous note was start of a HOPO section, then previous note not HOPO
        if lastEvent.hopo == 1:
          lastEvent.hopo = 0
        #If current note is invalid for HOPO, and previous note was a HOPO section, then previous note is end of HOPO
        elif lastEvent.hopo > 0:
          lastEvent.hopo = 3
      #current note valid
      elif note.hopo >= 0:
        #String of same notes can be followed by HOPO
        if note.hopo == 3:
          #This is the end of a valid HOPO section
          if lastEvent.hopo == 1 or lastEvent.hopo == 2:
            lastEvent = note
            lastTime = time
            continue
          if lastEvent.hopo == -2:
            #If its the same note again it's invalid
            if lastEvent.number == note.number:
              note.hopo = -2
            else:
              lastEvent.hopo = 1
          elif lastEvent.hopo == 0:
            lastEvent.hopo = 1
          #If last note was invalid or end of HOPO section, and current note is end, it is really not HOPO
          elif lastEvent.hopo != 2 and lastEvent.hopo != 1:
            note.hopo = 0
          #If last event was invalid or end of HOPO section, current note is start of HOPO
          else:
            note.hopo = 1
        elif note.hopo == 2:
          if lastEvent.hopo == -2:
            note.hopo = 1
          elif lastEvent.hopo == -1:
            note.hopo = 0
        elif note.hopo == 1:
          if lastEvent.hopo == 2:
            note.hopo = 0
        else:
          if lastEvent.hopo == -2:
            lastEvent.hopo = 1
            
          if lastEvent.hopo != 2 and lastEvent.hopo != 1:
            note.hopo = 1
          else:
            note.hopo = 2
      lastEvent = note
      lastTime = time
    else:
      if note != None:
        #Handle last note
        #If it is the start of a HOPO, it's not really a HOPO
        if note.hopo == 1:
          note.hopo = 0
        #If it is the middle of a HOPO, it's really the end of a HOPO
        elif note.hopo == 2:
          note.hopo = 3      
       
  def run(self, ticks):
    SceneClient.run(self, ticks)
    pos = self.getSongPosition()

    # update song
    if self.song:
      # update stage
      self.stage.run(pos, self.guitars[0].currentPeriod)

      if self.countdown <= 0 and not self.song.isPlaying() and not self.done:
        self.goToResults()
        return
        
      if self.autoPlay:
        for i,guitar in enumerate(self.guitars):
          notes = guitar.getRequiredNotes(self.song, pos)
          notes = [note.number for time, note in notes]
          changed = False
          held = 0
          for n, k in enumerate(self.keysList[i]):
            if n in notes and not self.controls.getState(k):
              changed = True
              self.controls.toggle(k, True)
            elif not n in notes and self.controls.getState(k):
              changed = True
              self.controls.toggle(k, False)
            if self.controls.getState(k):
              held += 1
          if changed and held:
            self.doPick(i)
      
      self.song.update(ticks)
      if self.countdown > 0:
        for guitar in self.guitars:
          guitar.setBPM(self.song.bpm)
        self.countdown = max(self.countdown - ticks / self.song.period, 0)
        if not self.countdown:
          #RF-mod should we collect garbage when we start?
          self.engine.collectGarbage()
          self.song.setGuitarVolume(self.guitarVolume)
          self.song.setBackgroundVolume(self.songVolume)
          self.song.setRhythmVolume(self.rhythmVolume)
          #Lower volume of non played part to emhpasize what you are playing
          if len(self.playerList) == 1:
            if `self.player.part` == "Bass Guitar" or `self.player.part` == "Rhythm Guitar" :
              self.song.setGuitarVolume(self.guitarVolume * 0.6)
            else:
              self.song.setRhythmVolume(self.rhythmVolume * 0.6)

          self.song.play()

    # update board
    for i,guitar in enumerate(self.guitars):
      if not guitar.run(ticks, pos, self.controls):
        # done playing the current notes
        self.endPick(i)

      # missed some notes?
      if self.playerList[i].streak > 0 and guitar.getMissedNotes(self.song, pos):
        self.playerList[i].streak = 0
        guitar.hopoLast = -1
        if not guitar.playedNotes:
          self.song.setInstrumentVolume(0.0, self.playerList[i].part)
          guitar.hopoActive = False
      # late pick
      if self.keyBurstTimeout[i] is not None and self.engine.timer.time > self.keyBurstTimeout[i]:
        self.keyBurstTimeout[i] = None

        #RF-mod new HOPO stuff?
        notes = self.guitars[i].getRequiredNotes(self.song, pos)
        if self.guitars[i].controlsMatchNotes(self.controls, notes):
          self.doPick(i)

  def endPick(self, num):
    score = self.getExtraScoreForCurrentlyPlayedNotes(num)
    if not self.guitars[num].endPick(self.song.getPosition()):
      self.song.setInstrumentVolume(0.0, self.players[num].part)
    if score != 0:
      self.players[num].addScore(score)

  def render3D(self):
    self.stage.render(self.visibility)
    
  def renderGuitar(self):
    for i in range(len(self.playerList)):
      self.engine.view.setViewport(len(self.playerList),i)
      self.guitars[i].render(self.visibility, self.song, self.getSongPosition(), self.controls)
      
    self.engine.view.setViewport(1,0)

  def getSongPosition(self):
    if self.song:
      if not self.done:
        self.lastSongPos = self.song.getPosition()
        return self.lastSongPos - self.countdown * self.song.period
      else:
        # Nice speeding up animation at the end of the song
        return self.lastSongPos + 4.0 * (1 - self.visibility) * self.song.period
    return 0.0


    
  def doPick(self, num):
    if not self.song:
      return

    pos = self.getSongPosition()
    
    if self.guitars[num].playedNotes:
      # If all the played notes are tappable, there are no required notes and
      # the last note was played recently enough, ignore this pick
      if self.guitars[num].areNotesTappable(self.guitars[num].playedNotes) and \
         not self.guitars[num].getRequiredNotes(self.song, pos) and \
         pos - self.lastPickPos[num] <= self.song.period / 2:
        return
      self.endPick(num)

    self.lastPickPos[num] = pos

    if self.guitars[num].startPick(self.song, pos, self.controls):
      self.song.setInstrumentVolume(self.guitarVolume, self.playerList[num].part)
      self.playerList[num].streak += 1
      self.playerList[num].notesHit += len(self.guitars[num].playedNotes)
      self.playerList[num].addScore(len(self.guitars[num].playedNotes) * 50)
      self.stage.triggerPick(pos, [n[1].number for n in self.guitars[num].playedNotes])
      if self.playerList[num].streak % 10 == 0:
        self.lastMultTime[num] = pos
    else:
      self.song.setInstrumentVolume(0.0, self.playerList[num].part)
      self.playerList[num].streak = 0
      self.stage.triggerMiss(pos)
      self.sfxChannel.play(self.engine.data.screwUpSound)
      self.sfxChannel.setVolume(self.screwUpVolume)

  def doPick2(self, num, hopo = False):
    if not self.song:
      return
  
    pos = self.getSongPosition()
    #clear out any missed notes before this pick since they are already missed by virtue of the pick
    missedNotes = self.guitars[num].getMissedNotes(self.song, pos, catchup = True)
    if len(missedNotes) > 0:
      self.playerList[num].streak = 0
      self.guitars[num].hopoActive = False
      self.guitars[num].hopoLast = -1
      if hopo == True:
        return

    #hopo fudge
    hopoFudge = abs(self.guitars[num].hopoActive) - pos
    if hopoFudge > 0 and hopoFudge < self.guitars[num].lateMargin:
      for k in self.guitars[num].actions:
        if self.controls.getState(k):
          return
    
    if self.guitars[num].startPick(self.song, pos, self.controls, hopo):
      self.song.setInstrumentVolume(1.0, self.playerList[num].part)
      if self.guitars[num].playedNotes:
        self.playerList[num].streak += 1
      self.playerList[num].notesHit += len(self.guitars[num].playedNotes)
      self.stage.triggerPick(pos, [n[1].number for n in self.guitars[num].playedNotes])    
      self.players[num].addScore(len(self.guitars[num].playedNotes) * 50)
      if self.players[num].streak % 10 == 0:
        self.lastMultTime[num] = self.getSongPosition()
        self.doTwang()
    else:
      self.guitars[num].hopoActive = False
      self.guitars[num].hopoLast = -1
      self.song.setInstrumentVolume(0.0, self.playerList[num].part)
      self.playerList[num].streak = 0
      self.stage.triggerMiss(pos)

      if self.screwUpSounds and self.screwUpVolume > 0.0:
        self.sfxChannel.play(self.engine.data.screwUpSound)
        self.sfxChannel.setVolume(self.screwUpVolume)
      
  def toggleAutoPlay(self):
    self.autoPlay = not self.autoPlay
    if self.autoPlay:
      Dialogs.showMessage(self.engine, _("Jurgen will show you how it is done."))
    else:
      Dialogs.showMessage(self.engine, _("Jurgen has left the building."))
    return self.autoPlay

  def goToResults(self):
    if self.song:
      self.song.stop()
      self.done  = True
      self.session.world.deleteScene(self)
      self.freeResources()
      for i,guitar in enumerate(self.guitars):
        self.playerList[i].twoChord = guitar.twoChord
      self.session.world.createScene("GameResultsScene", libraryName = self.libraryName, songName = self.songName, players = self.playerList)

  def keyPressed(self, key, unicode, control = None):
    if not control:
      control = self.controls.keyPressed(key)

    num = self.getPlayerNum(control)
      
    if control in (self.guitars[num].actions):
      for k in self.keysList[num]:
        if self.controls.getState(k):
          self.keyBurstTimeout[num] = None
          break
      else:
        self.keyBurstTimeout[num] = self.engine.timer.time + self.keyBurstPeriod
        return True

    if control in (self.guitars[num].actions) and self.song:
      self.doPick(num)
    elif control in self.keysList[num] and self.song:
      # Check whether we can tap the currently required notes
      pos   = self.getSongPosition()
      notes = self.guitars[num].getRequiredNotes(self.song, pos)
      print "tapcheckPress", self.playerList[num].streak, self.guitars[num].areNotesTappable(notes), self.guitars[num].controlsMatchNotes(self.controls, notes)

      if self.playerList[num].streak > 0 and \
         self.guitars[num].areNotesTappable(notes) and \
         self.guitars[num].controlsMatchNotes(self.controls, notes):
        self.doPick(num)
    elif control in Player.CANCELS:
      self.pauseGame()
      self.engine.view.pushLayer(self.menu)
      return True
    elif key >= ord('a') and key <= ord('z'):
      # cheat codes
      n = len(self.enteredCode)
      for code, func in self.cheatCodes:
        if n < len(code):
          if key == code[n]:
            self.enteredCode.append(key)
            if self.enteredCode == code:
              self.enteredCode     = []
              self.player.cheating = True
              func()
            break
      else:
        self.enteredCode = []

  def keyPressed2(self, key, unicode, control = None):
    hopo = False
    if not control:
      control = self.controls.keyPressed(key)
    else:
      hopo = True
      
    if True:
      pressed = -1
      if control in (self.guitars[0].actions):
        hopo = False
        pressed = 0;  
      elif len(self.playerList) > 1 and control in (self.guitars[1].actions):
        hopo = False
        pressed = 1;

      numpressed = [len([1 for k in guitar.keys if self.controls.getState(k)]) for guitar in self.guitars]

      if control in (self.guitars[0].keys) and self.song and numpressed[0] >= 1:
        if self.guitars[0].hopoActive > 0:
          hopo = True
          pressed = 0;
      elif len(self.playerList) > 1 and control in (self.guitars[1].keys) and numpressed[1] >= 1:
        if self.guitars[1].hopoActive > 0:
          hopo = True
          pressed = 1;

      if pressed >= 0:
        for k in self.keysList[pressed]:
          if self.controls.getState(k):
            self.keyBurstTimeout[pressed] = None
            break
        else:
          self.keyBurstTimeout[pressed] = self.engine.timer.time + self.keyBurstPeriod
          return True

      if pressed >= 0 and self.song:
        self.doPick(pressed, hopo)
      
    if control == Player.CANCEL:
      self.pauseGame()
      self.engine.view.pushLayer(self.menu)
      return True
    elif key >= ord('a') and key <= ord('z'):
      # cheat codes
      n = len(self.enteredCode)
      for code, func in self.cheatCodes:
        if n < len(code):
          if key == code[n]:
            self.enteredCode.append(key)
            if self.enteredCode == code:
              self.enteredCode     = []
              for player in self.playerList:
                player.cheating = True
              func()
            break
      else:
        self.enteredCode = []
   
  def getExtraScoreForCurrentlyPlayedNotes(self, num):
    if not self.song:
      return 0
 
    noteCount  = len(self.guitars[num].playedNotes)
    pickLength = self.guitars[num].getPickLength(self.getSongPosition())
    if pickLength > 1.1 * self.song.period / 4:
      return int(.1 * pickLength * noteCount)
    return 0

  def keyReleased(self, key):
    control = self.controls.keyReleased(key)

    num = self.getPlayerNum(control) 

    if control in self.keysList[num] and self.song:
      # Check whether we can tap the currently required notes
      pos   = self.getSongPosition()
      notes = self.guitars[num].getRequiredNotes(self.song, pos)
      print "tapcheckRelease", self.playerList[num].streak, self.guitars[num].areNotesTappable(notes), self.guitars[num].controlsMatchNotes(self.controls, notes)

      if self.playerList[num].streak > 0 and \
         self.guitars[num].areNotesTappable(notes) and \
         self.guitars[num].controlsMatchNotes(self.controls, notes):
        self.doPick(num)
      # Otherwise we end the pick if the notes have been playing long enough
      elif self.lastPickPos[num] is not None and pos - self.lastPickPos[num] > self.song.period / 2:
        self.endPick(num)

  def keyReleased2(self, key):
    control = self.controls.keyReleased(key)
    for i, keys in enumerate(self.keysList):
      if control in keys and self.song:
        for time, note in self.guitars[i].playedNotes:
          if self.guitars[i].hopoActive == False or (self.guitars[i].hopoActive < 0 and control == self.keysList[i][note.number]):
        #if self.guitars[i].hopoActive >= 0 and not self.guitars[i].playedNotes:
            self.endPick(i)
        #pass 
    
    for i, guitar in enumerate(self.guitars):
      activeList = [k for k in self.keysList[i] if self.controls.getState(k) and k != control]
      if len(activeList) != 0 and guitar.hopoActive and activeList[0] != self.keysList[i][guitar.hopoLast] and control in self.keysList[i]:
        self.keyPressed(None, 0, activeList[0])

  def getPlayerNum(self, control):
    if control in (self.guitars[0].keys + self.guitars[0].actions):
      return(0) 
    elif len(self.playerList) > 1 and control in (self.guitars[1].keys + self.guitars[1].actions):
      return(1)
    else:
      return(-1)
        
  def render(self, visibility, topMost):
    SceneClient.render(self, visibility, topMost)
    
    font    = self.engine.data.font
    bigFont = self.engine.data.bigFont
      
    self.visibility = v = 1.0 - ((1 - visibility) ** 2)

    self.engine.view.setOrthogonalProjection(normalize = True)
    try:
      # show countdown
      if self.countdown > 1:
        Theme.setBaseColor(min(1.0, 3.0 - abs(4.0 - self.countdown)))
        text = _("Get Ready to Rock")
        w, h = font.getStringSize(text)
        font.render(text,  (.5 - w / 2, .3))
        if self.countdown < 6:
          scale = 0.002 + 0.0005 * (self.countdown % 1) ** 3
          text = "%d" % (self.countdown)
          w, h = bigFont.getStringSize(text, scale = scale)
          Theme.setSelectedColor()
          bigFont.render(text,  (.5 - w / 2, .45 - h / 2), scale = scale)

      w, h = font.getStringSize(" ")
      y = .05 - h / 2 - (1.0 - v) * .2

      # show song name
      if self.countdown and self.song:
        Theme.setBaseColor(min(1.0, 4.0 - abs(4.0 - self.countdown)))
        extra = ""
        if self.song.info.frets:
          extra += " \n Fretted by: " + self.song.info.frets
        if self.song.info.version:
          extra += " \n v" + self.song.info.version
        Dialogs.wrapText(font, (.05, .05 - h / 2), self.song.info.name + " \n " + self.song.info.artist + extra, rightMargin = .6, scale = 0.0015)
      else:
        if self.disableStats != True:
          now = self.getSongPosition()
          pos = self.lastEvent - now
          if pos < 0:
            pos = 0
          
          Theme.setSelectedColor()
          t = "%d:%02d" % (pos / 60000, (pos % 60000) / 1000)
          w, h = font.getStringSize(t)
          font.render(t,  (.5 - w / 2, y))
          #Not ready for 2player yet
          if self.notesCum:
            f = int(100 * (float(self.playerList[0].notesHit) / self.notesCum))

            font.render("%d%%" % f, (.5 - w / 2, y + h))

        #Party mode
        if self.partyMode == True:
          now = self.getSongPosition()
          timeleft = (now - self.lastSwitch) / 1000
          if timeleft > self.partyTime:
            self.lastSwitch = now
            if self.partyPlayer == 0:
              self.guitars[0].keys = PLAYER2KEYS
              self.guitars[0].actions = PLAYER2ACTIONS
              self.partyPlayer = 1
            else:
              self.guitars[0].keys = PLAYER1KEYS
              self.guitars[0].actions = PLAYER1ACTIONS
              self.partyPlayer = 0
          t = "%d" % (self.partyTime - timeleft + 1)
          if self.partyTime - timeleft < 5:
            glColor3f(1, 0, 0)
          elif self.lastSwitch != 0 and timeleft < 1:
            t = "Switch"
            glColor3f(0, 1, 0)
          w, h = font.getStringSize(t)
          font.render(t,  (.5 - w / 2, y + h))

      for i,player in enumerate(self.playerList):
        self.engine.view.setViewportHalf(len(self.playerList),i)
        Theme.setSelectedColor()
        if len(self.playerList) > 1 and i == 0:
          font.render("%d" % (player.score + self.getExtraScoreForCurrentlyPlayedNotes(i)),  (.03, y))
          font.render("%dx" % player.getScoreMultiplier(), (.03, y + h))
        else:
          font.render("%d" % (player.score + self.getExtraScoreForCurrentlyPlayedNotes(i)),  (.61, y))
          font.render("%dx" % player.getScoreMultiplier(), (.61, y + h))
          
        
        # show the streak counter and miss message
        if player.streak > 0 and self.song:
          text = _("%d hit") % player.streak
          factor = 0.0
          if self.lastPickPos[i]:
              diff = self.getSongPosition() - self.lastPickPos[i]
              if diff > 0 and diff < self.song.period * 2:
                factor = .25 * (1.0 - (diff / (self.song.period * 2))) ** 2
          factor = (1.0 + factor) * 0.002
          tw, th = font.getStringSize(text, scale = factor)
          if len(self.playerList) > 1 and i == 0:
            font.render(text, (.72 - tw / 2, y + h / 2 - th / 2), scale = factor)
          elif len(self.playerList) > 1 and i == 1:
            font.render(text, (.26 - tw / 2, y + h / 2 - th / 2), scale = factor)
          else:
            font.render(text, (.16 - tw / 2, y + h / 2 - th / 2), scale = factor)
        elif self.lastPickPos[i] is not None and self.countdown <= 0:
          diff = self.getSongPosition() - self.lastPickPos[i]
          alpha = 1.0 - diff * 0.005
          if alpha > .1:
            Theme.setSelectedColor(alpha)
            glPushMatrix()
            glTranslate(.1, y + 0.000005 * diff ** 2, 0)
            glRotatef(math.sin(self.lastPickPos[i]) * 25, 0, 0, 1)
            if len(self.playerList) > 1 and i == 0:
              font.render(_("Missed!"), (.55, 0))
            elif len(self.playerList) > 1 and i == 1:
              font.render(_("Missed!"), (.08, 0))
            else:
              font.render(_("Missed!"), (0, 0))
            glPopMatrix()

        # show the streak balls
        if player.streak >= 30:
          glColor3f(.5, .5, 1)
        elif player.streak >= 20:
          glColor3f(1, 1, .5)
        elif player.streak >= 10:
          glColor3f(1, .5, .5)
        else:
          glColor3f(.5, 1, .5)
        
        s = min(39, player.streak) % 10 + 1
        if len(self.playerList) > 1 and i == 0:
          font.render(Data.BALL2 * s + Data.BALL1 * (10 - s),   (.1, y + h * 1.3), scale = 0.0011)
        else:
          font.render(Data.BALL2 * s + Data.BALL1 * (10 - s),   (.67, y + h * 1.3), scale = 0.0011)
          
        # show multiplier changes
        if self.song and self.lastMultTime[i] is not None:
          diff = self.getSongPosition() - self.lastMultTime[i]
          if diff > 0 and diff < self.song.period * 2:
            m = player.getScoreMultiplier()
            c = (1, 1, 1)
            if player.streak >= 40:
              texture = None
            elif m == 1:
              texture = None
            elif m == 2:
              texture = self.fx2x.texture
              c = (1, .5, .5)
            elif m == 3:
              texture = self.fx3x.texture
              c = (1, 1, .5)
            elif m == 4:
              texture = self.fx4x.texture
              c = (.5, .5, 1)
            
            f = (1.0 - abs(self.song.period * 1 - diff) / (self.song.period * 1)) ** 2
          
            # Flash the screen
            glBegin(GL_TRIANGLE_STRIP)
            glColor4f(c[0], c[1], c[2], (f - .5) * 1)
            glVertex2f(0, 0)
            glColor4f(c[0], c[1], c[2], (f - .5) * 1)
            glVertex2f(1, 0)
            glColor4f(c[0], c[1], c[2], (f - .5) * .25)
            glVertex2f(0, 1)
            glColor4f(c[0], c[1], c[2], (f - .5) * .25)
            glVertex2f(1, 1)
            glEnd()
            
            if texture:
              glPushMatrix()
              glEnable(GL_TEXTURE_2D)
              texture.bind()
              size = (texture.pixelSize[0] * .002, texture.pixelSize[1] * .002)
            
              glTranslatef(.5, .15, 0)
              glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            
              f = .5 + .5 * (diff / self.song.period) ** 3
              glColor4f(1, 1, 1, min(1, 2 - f))
              glBegin(GL_TRIANGLE_STRIP)
              glTexCoord2f(0.0, 0.0)
              glVertex2f(-size[0] * f, -size[1] * f)
              glTexCoord2f(1.0, 0.0)
              glVertex2f( size[0] * f, -size[1] * f)
              glTexCoord2f(0.0, 1.0)
              glVertex2f(-size[0] * f,  size[1] * f)
              glTexCoord2f(1.0, 1.0)
              glVertex2f( size[0] * f,  size[1] * f)
              glEnd()
            
              glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
              glPopMatrix()

      self.engine.view.setViewport(1,0)  
      # show the comments
      if self.song and self.song.info.tutorial:
        glColor3f(1, 1, 1)
        pos = self.getSongPosition()
        for time, event in self.song.track.getEvents(pos - self.song.period * 2, pos + self.song.period * 4):
          if isinstance(event, PictureEvent):
            if pos < time or pos > time + event.length:
              continue
            
            try:
              picture = event.picture
            except:
              self.engine.loadSvgDrawing(event, "picture", os.path.join(self.libraryName, self.songName, event.fileName))
              picture = event.picture
              
            w, h, = self.engine.view.geometry[2:4]
            fadePeriod = 500.0
            f = (1.0 - min(1.0, abs(pos - time) / fadePeriod) * min(1.0, abs(pos - time - event.length) / fadePeriod)) ** 2
            picture.transform.reset()
            picture.transform.translate(w / 2, (f * -2 + 1) * h / 2)
            picture.transform.scale(1, -1)
            picture.draw()
          elif isinstance(event, TextEvent):
            if pos >= time and pos <= time + event.length:
              text = _(event.text)
              w, h = font.getStringSize(text)
              font.render(text, (.5 - w / 2, .67))
    finally:
      self.engine.view.resetProjection()
