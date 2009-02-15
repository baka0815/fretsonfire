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

import midi
import Log
import Audio
import Config
import os
import re
import shutil
import Config
import sha
import binascii
import Cerealizer
import urllib
import Version
import Theme
import copy
import Part
import Difficulty

from Language import _

DEFAULT_LIBRARY        = "songs"

class SongInfo(object):
  def __init__(self, infoFileName):
    self.songName      = os.path.basename(os.path.dirname(infoFileName))
    self.fileName      = infoFileName
    #define this somewhere
    self.cacheFileName = os.path.join(os.path.dirname(self.fileName), "cache.ini")
    self.info          = Config.MyConfigParser()
    self.cache         = Config.MyConfigParser()
    self._difficulties = None
    self._parts        = None
    self._time         = None
    self._noteNum      = None
    
    try:
      self.info.read(infoFileName)
    except:
      pass

    try:
      self.cache.read(self.cacheFileName)
    except:
      pass
    
    # Read highscores and verify their hashes.
    # There ain't no security like security throught obscurity :)
    self.highScores = {}
    
    scores = self._get("scores", str, "")
    scores_ext = self._get("scores_ext", str, "")
    if scores:
      scores = Cerealizer.loads(binascii.unhexlify(scores))
      if scores_ext:
        scores_ext = Cerealizer.loads(binascii.unhexlify(scores_ext))
      for difficulty in scores.keys():
        for i, base_scores in enumerate(scores[difficulty]):
          score, stars, name, hash = base_scores
          if scores_ext != "":
            #Someone may have mixed extended and non extended
            try:
              hash_ext, stars2, notesHit, notesTotal, noteStreak, modVersion, modOptions1, modOptions2 =  scores_ext[difficulty][i]
              scoreExt = (notesHit, notesTotal, noteStreak, modVersion, modOptions1, modOptions2)
            except:
              hash_ext = 0
              scoreExt = (0, 0, 0 , "RF-mod", "Default", "Default")
          if self.getScoreHash(difficulty, score, stars, name) == hash:
            if scores_ext != "" and hash == hash_ext:
              self.addHighscore(difficulty, score, stars, name, part = Part.GUITAR_PART, scoreExt = scoreExt)
            else:
              self.addHighscore(difficulty, score, stars, name, part = Part.GUITAR_PART)
          else:
            Log.warn("Weak hack attempt detected. Better luck next time.")

    self.highScoresRhythm = {}
    
    scores = self._get("scores_rhythm", str, "")
    if scores:
      scores = Cerealizer.loads(binascii.unhexlify(scores))
      for difficulty in scores.keys():
        for score, stars, name, hash in scores[difficulty]:
          if self.getScoreHash(difficulty, score, stars, name) == hash:
            self.addHighscore(difficulty, score, stars, name, part = Part.RHYTHM_PART)
          else:
            Log.warn("Weak hack attempt detected. Better luck next time.")

    self.highScoresBass = {}
    
    scores = self._get("scores_bass", str, "")
    if scores:
      scores = Cerealizer.loads(binascii.unhexlify(scores))
      for difficulty in scores.keys():
        for score, stars, name, hash in scores[difficulty]:
          if self.getScoreHash(difficulty, score, stars, name) == hash:
            self.addHighscore(difficulty, score, stars, name, part = Part.BASS_PART)
          else:
            Log.warn("Weak hack attempt detected. Better luck next time.")

    self.highScoresLead = {}
    
    scores = self._get("scores_lead", str, "")
    if scores:
      scores = Cerealizer.loads(binascii.unhexlify(scores))
      for difficulty in scores.keys():
        for score, stars, name, hash in scores[difficulty]:
          if self.getScoreHash(difficulty, score, stars, name) == hash:
            self.addHighscore(difficulty, score, stars, name, part = Part.LEAD_PART)
          else:
            Log.warn("Weak hack attempt detected. Better luck next time.")            

    self.highScoresDrum = {}
    
    scores = self._get("scores_drum", str, "")
    if scores:
      scores = Cerealizer.loads(binascii.unhexlify(scores))
      for difficulty in scores.keys():
        for score, stars, name, hash in scores[difficulty]:
          if self.getScoreHash(difficulty, score, stars, name) == hash:
            self.addHighscore(difficulty, score, stars, name, part = Part.DRUM_PART)
          else:
            Log.warn("Weak hack attempt detected. Better luck next time.")
    
  def _set(self, attr, value):
    if not self.info.has_section("song"):
      self.info.add_section("song")
    if type(value) == unicode:
      value = value.encode(Config.encoding)
    else:
      value = str(value)
    self.info.set("song", attr, value)
    
  def getObfuscatedScores(self, part = Part.GUITAR_PART):
    s = {}
    if part == Part.GUITAR_PART:
      highScores = self.highScores
    elif part == Part.RHYTHM_PART:
      highScores = self.highScoresRhythm
    elif part == Part.BASS_PART:
      highScores = self.highScoresBass
    elif part == Part.LEAD_PART:
      highScores = self.highScoresLead
    elif part == Part.DRUM_PART:
      highScores = self.highScoresDrum
    else:
      highScores = self.highScores
      
    for difficulty in highScores.keys():
      s[difficulty] = [(score, stars, name, self.getScoreHash(difficulty, score, stars, name)) for score, stars, name, scores_ext in highScores[difficulty]]
    return binascii.hexlify(Cerealizer.dumps(s))

  def getObfuscatedScoresExt(self, part = Part.GUITAR_PART):
    s = {}
    if part == Part.GUITAR_PART:
      highScores = self.highScores
    elif part == Part.RHYTHM_PART:
      highScores = self.highScoresRhythm
    elif part == Part.BASS_PART:
      highScores = self.highScoresBass
    elif part == Part.LEAD_PART:
      highScores = self.highScoresLead
    elif part == Part.DRUM_PART:
      highScores = self.highScoresDrum
    else:
      highScores = self.highScores
      
    for difficulty in highScores.keys():
      s[difficulty] = [(self.getScoreHash(difficulty, score, stars, name), stars) + scores_ext for score, stars, name, scores_ext in highScores[difficulty]]
    return binascii.hexlify(Cerealizer.dumps(s))

  def save(self):
    if self.highScores != {}:
      myPart = Part.GUITAR_PART
      self._set("scores",        self.getObfuscatedScores(part = myPart))
      self._set("scores_ext",    self.getObfuscatedScoresExt(part = myPart))
    if self.highScoresRhythm != {}:
      myPart = Part.RHYTHM_PART
      self._set("scores_rhythm", self.getObfuscatedScores(part = myPart))
      self._set("scores_rhythm_ext", self.getObfuscatedScoresExt(part = myPart))
    if self.highScoresBass != {}:
      myPart = Part.BASS_PART
      self._set("scores_bass",   self.getObfuscatedScores(part = myPart))
      self._set("scores_bass_ext",   self.getObfuscatedScoresExt(part = myPart))
    if self.highScoresLead != {}:
      myPart = Part.LEAD_PART
      self._set("scores_lead",   self.getObfuscatedScores(part = myPart))
      self._set("scores_lead_ext",   self.getObfuscatedScoresExt(part = myPart))
    if self.highScoresDrum != {}:
      myPart = Part.DRUM_PART
      self._set("scores_drum",   self.getObfuscatedScores(part = myPart))
      self._set("scores_drum_ext",   self.getObfuscatedScoresExt(part = myPart))
      
    f = open(self.fileName, "w")
    self.info.write(f)
    f.close()
    
  def _get(self, attr, type = None, default = ""):
    try:
      v = self.info.get("song", attr)
    except:
      v = default
    if v is not None and type:
      v = type(v)
    return v

  def _cacheget(self, attr, type = None, default = ""):
    try:
      v = self.cache.get("cache", attr)
    except:
      v = default
    if v is not None and type:
      v = type(v)
    return v

  def _cacheset(self, attr, value):
    if not self.cache.has_section("cache"):
      self.cache.add_section("cache")
    if type(value) == unicode:
      value = value.encode(Config.encoding)
    else:
      value = str(value)
    self.cache.set("cache", attr, value)
    
  def cachesave(self):   
    f = open(self.cacheFileName, "w")
    self.cache.write(f)
    f.close()

  def noteInfo(self):
    try:
      noteFileName = os.path.join(os.path.dirname(self.fileName), "notes.mid")
      info = MidiInfoReader()
      midiIn = midi.MidiInFile(info, noteFileName)
      try:
        midiIn.read()
      except MidiInfoReader.Done:
        pass

      #info reader now will get both difficulties, parts and notenum
      info.difficulties.sort()
      self._difficulties = info.difficulties
      info.parts.sort()
      self._parts = info.parts
      self._noteNum = info.noteNum
      self._time = info.find_time(info.lastTime)
    except:
      info.difficulties.sort()
      self._difficulties = info.difficulties
      info.parts.sort()
      self._parts = info.parts
      self._noteNum = info.noteNum
      self._time = info.find_time(info.lastTime)
      
    #Save values in cache.ini cache
    self._cacheset("cache_diffs", binascii.hexlify(Cerealizer.dumps(self._difficulties)))
    self._cacheset("cache_parts", binascii.hexlify(Cerealizer.dumps(self._parts)))
    self._cacheset("cache_notenum", binascii.hexlify(Cerealizer.dumps(self._noteNum)))
    self._cacheset("cache_endtime", binascii.hexlify(Cerealizer.dumps(self._time)))

    self.cachesave()
    
  def getDifficulties(self):
    # Tutorials only have the medium difficulty
    if self.tutorial:
      return [Difficulty.MEDIUM_DIFFICULTY]

    if self._difficulties is not None:
      return self._difficulties

    # Read in song.ini cached info
    cache_diffs = self._cacheget("cache_diffs")
    if cache_diffs is not "":
      diffNums = Cerealizer.loads(binascii.unhexlify(cache_diffs))
      self._difficulties = diffNums

    # Otherwise do it the hard way
    else:
      self.noteInfo()
    return self._difficulties

  def getParts(self): 
    if self._parts is not None:
      return self._parts

    # Read in song.ini cached info
    cache_parts = self._cacheget("cache_parts")
    if cache_parts is not "":
      partNums = Cerealizer.loads(binascii.unhexlify(cache_parts))

      self._parts = partNums
    else:
      # Otherwise do it the hard way
      self.noteInfo()
    return self._parts

  def getNoteNum(self):
    if self._noteNum is not None:
      return self._noteNum
  
    # Read in song.ini cached info
    cache_notenum = self._cacheget("cache_notenum")
    if cache_notenum is not "":
      noteNums = Cerealizer.loads(binascii.unhexlify(cache_notenum))
      self._noteNum = noteNums
    else:
      # Otherwise do it the hard way
      self.noteInfo()
    return self._noteNum
  
  def getTime(self):
    if self._time is not None:
      return self._time
  
    # Read in song.ini cached info
    cache_time = self._cacheget("cache_endtime")
    if cache_time is not "":
      timeNum = Cerealizer.loads(binascii.unhexlify(cache_time))
      self._time = timeNum
    else:
      # Otherwise do it the hard way
      self.noteInfo()
    return self._noteNum
  
  def getName(self):
    return self._get("name")

  def setName(self, value):
    self._set("name", value)

  def getArtist(self):
    return self._get("artist")

  def getCassetteColor(self):
    c = self._get("cassettecolor")
    if c:
      return Theme.hexToColor(c)
  
  def setCassetteColor(self, color):
    self._set("cassettecolor", Theme.colorToHex(color))
  
  def setArtist(self, value):
    self._set("artist", value)
    
  def getScoreHash(self, difficulty, score, stars, name):
    return sha.sha("%d%d%d%s" % (difficulty, score, stars, name)).hexdigest()
    
  def getDelay(self):
    return self._get("delay", int, 0)
    
  def setDelay(self, value):
    return self._set("delay", value)
  
  def getFrets(self):
    return self._get("frets")

  def setFrets(self, value):
    self._set("frets", value)
    
  def getVersion(self):
    return self._get("version")

  def setVersion(self, value):
    self._set("version", value)

  def getTags(self):
    return self._get("tags")

  def setTags(self, value):
    self._set("tags", value)

  def getHopo(self):
    return self._get("hopo")

  def setHopo(self, value):
    self._set("hopo", value)

  def getEighthNoteHopo(self):
    return self._get("eighthnote_hopo")

  def setEighthNoteHopo(self, value):
    self._set("eighthnote_hopo", value)
    
  def getCount(self):
    return self._get("count")

  def setCount(self, value):
    self._set("count", value)

  def getLyrics(self):
    return self._get("lyrics")

  def setLyrics(self, value):
    self._set("lyrics", value)    

  def getComments(self):
    return self._get("comments")

  def setComments(self, value):
    self._set("comments", value)
    
  def getHighscores(self, difficulty, part = Part.parts[Part.GUITAR_PART]):
    if part == Part.parts[Part.GUITAR_PART]:
      highScores = self.highScores
    elif part == Part.parts[Part.RHYTHM_PART]:
      highScores = self.highScoresRhythm
    elif part == Part.parts[Part.BASS_PART]:
      highScores = self.highScoresBass
    elif part == Part.parts[Part.LEAD_PART]:
      highScores = self.highScoresLead
    elif part == Part.parts[Part.DRUM_PART]:
      highScores = self.highScoresDrum
    else:
      highScores = self.highScores
      
    try:
      return highScores[difficulty]
    except KeyError:
      return []
      
  def uploadHighscores(self, url, songHash, part = Part.parts[Part.GUITAR_PART]):
    try:
      d = {
        "songName": self.songName,
        "songHash": songHash,
        "scores":   self.getObfuscatedScores(part = part),
        "scores_ext": self.getObfuscatedScoresExt(part = part),
        "version":  Version.version(),
        "songPart": part
      }
      data = urllib.urlopen(url + "?" + urllib.urlencode(d)).read()
      Log.debug("Score upload result: %s" % data)
      if ";" in data:
        fields = data.split(";")
      else:
        fields = [data, "0"]
      return (fields[0] == "True", int(fields[1]))
    except Exception, e:
      Log.error(e)
      return (False, 0)
  
  def addHighscore(self, difficulty, score, stars, name, part = Part.parts[Part.GUITAR_PART], scoreExt = (0, 0, 0, "RF-mod", "Default", "Default")):
    if part == Part.parts[Part.GUITAR_PART]:
      highScores = self.highScores
    elif part == Part.parts[Part.RHYTHM_PART]:
      highScores = self.highScoresRhythm
    elif part == Part.parts[Part.BASS_PART]:
      highScores = self.highScoresBass
    elif part == Part.parts[Part.LEAD_PART]:
      highScores = self.highScoresLead
    elif part == Part.parts[Part.DRUM_PART]:
      highScores = self.highScoresDrum
    else:
      highScores = self.highScores

    #notesHit, notesTotal, noteStreak, modVersion, modOptions1, modOptions2 = scoreExt 
    if not difficulty in highScores:
      highScores[difficulty] = []
    highScores[difficulty].append((score, stars, name, scoreExt))
    highScores[difficulty].sort(lambda a, b: {True: -1, False: 1}[a[0] > b[0]])
    highScores[difficulty] = highScores[difficulty][:5]
    for i, scores in enumerate(highScores[difficulty]):
      _score, _stars, _name, _scores_ext = scores
      if _score == score and _stars == stars and _name == name:
        return i
    return -1

  def isTutorial(self):
    return self._get("tutorial", int, 0) == 1

  def findTag(self, find, value = None):
    for tag in self.tags.split(','):
      temp = tag.split('=')
      if find == temp[0]:
        
        if len(temp) == 1:
          return "True"
        elif len(temp) == 2 and value == temp[1]:
          return "True"
        elif len(temp) == 2 and value == None:
          return temp[1]

    return "False"
      
    
  name          = property(getName, setName)
  artist        = property(getArtist, setArtist)
  delay         = property(getDelay, setDelay)
  tutorial      = property(isTutorial)
  difficulties  = property(getDifficulties)
  cassetteColor = property(getCassetteColor, setCassetteColor)
  #New RF-mod Items
  parts         = property(getParts)
  notenum       = property(getNoteNum)
  time          = property(getTime)
  frets         = property(getFrets, setFrets)
  version       = property(getVersion, setVersion)
  tags          = property(getTags, setTags)
  hopo          = property(getHopo, setHopo)
  hopo8th       = property(getEighthNoteHopo, setEighthNoteHopo)
  count         = property(getCount, setCount)
  lyrics        = property(getLyrics, setLyrics)
  comments      = property(getComments, setComments)
  #May no longer be necessary
  folder        = False


class LibraryInfo(object):
  def __init__(self, libraryName, infoFileName):
    self.libraryName   = libraryName
    self.fileName      = infoFileName
    self.info          = Config.MyConfigParser()
    self.songCount     = 0

    try:
      self.info.read(infoFileName)
    except:
      pass

    # Set a default name
    if not self.name:
      self.name = os.path.basename(os.path.dirname(self.fileName))
    if Config.get("game", "disable_libcount") == True:
      return
    # Count the available songs
    libraryRoot = os.path.dirname(self.fileName)
    for name in os.listdir(libraryRoot):
      if not os.path.isdir(os.path.join(libraryRoot, name)) or name.startswith("."):
        continue
      if os.path.isfile(os.path.join(libraryRoot, name, "notes.mid")):
        self.songCount += 1

  def _set(self, attr, value):
    if not self.info.has_section("library"):
      self.info.add_section("library")
    if type(value) == unicode:
      value = value.encode(Config.encoding)
    else:
      value = str(value)
    self.info.set("library", attr, value)
    
  def save(self):
    f = open(self.fileName, "w")
    self.info.write(f)
    f.close()
    
  def _get(self, attr, type = None, default = ""):
    try:
      v = self.info.get("library", attr)
    except:
      v = default
    if v is not None and type:
      v = type(v)
    return v

  def getName(self):
    return self._get("name")

  def setName(self, value):
    self._set("name", value)

  def getColor(self):
    c = self._get("color")
    if c:
      return Theme.hexToColor(c)
  
  def setColor(self, color):
    self._set("color", Theme.colorToHex(color))
        
  def getTags(self):
    return self._get("tags")

  def setTags(self, value):
    self._set("tags", value)
    
  def findTag(self, find, value = None):
    for tag in self.tags.split(','):
      temp = tag.split('=')
      if find == temp[0]:
        
        if len(temp) == 1:
          return "True"
        elif len(temp) == 2 and value == temp[1]:
          return "True"
        elif len(temp) == 2 and value == None:
          return temp[1]

    return "False"

  name          = property(getName, setName)
  color         = property(getColor, setColor)  
  tags          = property(getTags, setTags)
  
class Event:
  def __init__(self, length):
    self.length = length

class Note(Event):
  def __init__(self, number, length, special = False, tappable = 0):
    Event.__init__(self, length)
    self.number   = number
    self.played   = False
    self.special  = special
    self.tappable = tappable
    #RF-mod
    self.hopod   = False
    self.skipped = False
    self.flameCount = 0
    self.noteBpm = 0.0
    self.jp      = False
    self.player1 = False
    self.player2 = False
    
  def __repr__(self):
    return "<#%d>" % self.number

class Tempo(Event):
  def __init__(self, bpm):
    Event.__init__(self, 0)
    self.bpm = bpm
    
  def __repr__(self):
    return "<%d bpm>" % self.bpm

class TextEvent(Event):
  def __init__(self, text, length):
    Event.__init__(self, length)
    self.text = text

  def __repr__(self):
    return "<%s>" % self.text

class PictureEvent(Event):
  def __init__(self, fileName, length):
    Event.__init__(self, length)
    self.fileName = fileName

class JPEvent(Event):
  def __init__(self, length):
    Event.__init__(self, length)
    self.triggered = False

class PlayerEvent(Event):
  def __init__(self, player, length):
    Event.__init__(self, length)
    self.triggered = False
    self.player = player
    
class Track:
  granularity = 50
  
  def __init__(self):
    self.events = []
    self.allEvents = []
    self.marked = False

  def addEvent(self, time, event):
    for t in range(int(time / self.granularity), int((time + event.length) / self.granularity) + 1):
      if len(self.events) < t + 1:
        n = t + 1 - len(self.events)
        n *= 8
        self.events = self.events + [[] for n in range(n)]
      self.events[t].append((time - (t * self.granularity), event))
    self.allEvents.append((time, event))

  def removeEvent(self, time, event):
    for t in range(int(time / self.granularity), int((time + event.length) / self.granularity) + 1):
      e = (time - (t * self.granularity), event)
      if t < len(self.events) and e in self.events[t]:
        self.events[t].remove(e)
    if (time, event) in self.allEvents:
      self.allEvents.remove((time, event))

  def getEvents(self, startTime, endTime):
    t1, t2 = [int(x) for x in [startTime / self.granularity, endTime / self.granularity]]
    if t1 > t2:
      t1, t2 = t2, t1

    events = set()
    for t in range(max(t1, 0), min(len(self.events), t2)):
      for diff, event in self.events[t]:
        time = (self.granularity * t) + diff
        events.add((time, event))
    return events

  def getAllEvents(self):
    return self.allEvents

  def reset(self):
    for eventList in self.events:
      for time, event in eventList:
        if isinstance(event, Note):
          event.played = False
          event.hopod = False
          event.skipped = False
          event.flameCount = 0
          self.noteBpm = 0.0

  def markTappable(self):
    # Determine which notes are tappable. The rules are:
    #  1. Not the first note of the track
    #  2. Previous note not the same as this one
    #  3. Previous note not a chord
    #  4. Previous note ends at most 161 ticks before this one
    bpm             = None
    ticksPerBeat    = 480
    tickThreshold   = 161
    prevNotes       = []
    currentNotes    = []
    currentTicks    = 0.0
    prevTicks       = 0.0
    epsilon         = 1e-3

    def beatsToTicks(time):
      return (time * bpm * ticksPerBeat) / 60000.0

    if not self.allEvents:
      return

    for time, event in self.allEvents + [self.allEvents[-1]]:
      if isinstance(event, Tempo):
        bpm = event.bpm
      elif isinstance(event, Note):
        # All notes are initially not tappable
        event.tappable = 0
        ticks = beatsToTicks(time)
        
        # Part of chord?
        if ticks < currentTicks + epsilon:
          currentNotes.append(event)
          continue

        """
        for i in range(5):
          if i in [n.number for n in prevNotes]:
            print " # ",
          else:
            print " . ",
        print " | ",
        for i in range(5):
          if i in [n.number for n in currentNotes]:
            print " # ",
          else:
            print " . ",
        print
        """
        
        # Previous note not a chord?
        if len(prevNotes) == 1:
          # Previous note ended recently enough?
          prevEndTicks = prevTicks + beatsToTicks(prevNotes[0].length)
          if currentTicks - prevEndTicks <= tickThreshold:
            for note in currentNotes:
              # Are any current notes the same as the previous one?
              if note.number == prevNotes[0].number:
                break
            else:
              # If all the notes are different, mark the current notes tappable
              for note in currentNotes:
                note.tappable = 2

        # Set the current notes as the previous notes
        prevNotes    = currentNotes
        prevTicks    = currentTicks
        currentNotes = [event]
        currentTicks = ticks

  def markHopo(self, hopo8th = 0):
    lastTick = 0
    lastTime  = 0
    lastEvent = Note
    
    tickDelta = 0
    noteDelta = 0

    #dtb file says 170 ticks
    if hopo8th == "1":
      hopoDelta = 250
    else:
      hopoDelta = 170
  
    chordFudge = 10
    ticksPerBeat = 480
    hopoNotes = []
    chordNotes = []
    sameNotes = []
    bpmNotes = []
    firstTime = 1

    #If already processed abort   
    if self.marked == True:
      return
    
    for time, event in self.allEvents:
      if isinstance(event, Tempo):
        bpmNotes.append([time, event])
        continue
      if not isinstance(event, Note):
        continue
      
      while bpmNotes and time >= bpmNotes[0][0]:
        #Adjust to new BPM
        #bpm = bpmNotes[0][1].bpm
        bpmTime, bpmEvent = bpmNotes.pop(0)
        bpm = bpmEvent.bpm

      tick = (time * bpm * ticksPerBeat) / 60000.0
      lastTick = (lastTime * bpm * ticksPerBeat) / 60000.0
      
      #skip first note
      if firstTime == 1:
        event.tappable = -3
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
          if not hopoNotes and lastEvent.tappable == -3:
            lastEvent.tappable = 1
          #this may be incorrect if a bpm event happened inbetween this note and last note
          hopoNotes.append([lastTime, bpmEvent])
          hopoNotes.append([lastTime, lastEvent])

        hopoNotes.append([bpmTime, bpmEvent])
        hopoNotes.append([time, event])
        
      #HOPO Over        
      if tickDelta > hopoDelta:
        if hopoNotes != []:
          #If the last event is the last HOPO note, mark it as a HOPO end
          if lastEvent.tappable != -1 and hopoNotes[-1][1] == lastEvent:
            if lastEvent.tappable >= 0:
              lastEvent.tappable = 3
            else:
              lastEvent.tappable = -1

      #This is the same note as before
      elif noteDelta == 0:
        #Add both notes to bad list even if duplicate.  Will come out in processing
        sameNotes.append(lastEvent)
        sameNotes.append(event)
        lastEvent.tappable = -2
        event.tappable = -2
            
      #This is a chord
      elif tickDelta < chordFudge:
        #Add both notes to bad list even if duplicate.  Will come out in processing
        if len(chordNotes) != 0 and chordNotes[-1] != lastEvent:
          chordNotes.append(lastEvent)
        chordNotes.append(event)
        lastEvent.tappable = -1
        event.tappable = -1
        
      lastEvent = event
      lastTime = time
    else:
      #Add last note to HOPO list if applicable
      if noteDelta != 0 and tickDelta > 1.5 and tickDelta < hopoDelta and isinstance(event, Note):
        hopoNotes.append([time, bpmEvent])
        hopoNotes.append([time, event])

    firstTime = 1
    note = None

    for note in list(chordNotes):
      #chord notes -1
      note.tappable = -1   

    for note in list(sameNotes):
      #same note in string -2
      note.tappable = -2

    bpmNotes = []
    
    for time, note in list(hopoNotes):
      if isinstance(note, Tempo):
        bpmNotes.append([time, note])
        continue
      if not isinstance(note, Note):
        continue
      while bpmNotes and time >= bpmNotes[0][0]:
        #Adjust to new BPM
        #bpm = bpmNotes[0][1].bpm
        bpmTime, bpmEvent = bpmNotes.pop(0)
        bpm = bpmEvent.bpm

      if firstTime == 1:
        if note.tappable >= 0:
          note.tappable = 1
        lastEvent = note
        firstTime = 0
        continue


#need to recompute (or carry forward) BPM at this time
      tick = (time * bpm * ticksPerBeat) / 60000.0
      lastTick = (lastTime * bpm * ticksPerBeat) / 60000.0
      tickDelta = tick - lastTick

      #current Note Invalid
      if note.tappable < 0:
        #If current note is invalid for HOPO, and previous note was start of a HOPO section, then previous note not HOPO
        if lastEvent.tappable == 1:
          lastEvent.tappable = 0
        #If current note is beginning of a same note sequence, it's valid for END of HOPO only
        #elif lastEvent.tappable == 2 and note.tappable == -2:
        #  note.tappable = 3
        #If current note is invalid for HOPO, and previous note was a HOPO section, then previous note is end of HOPO
        elif lastEvent.tappable > 0:
          lastEvent.tappable = 3
      #current note valid
      elif note.tappable >= 0:
        #String of same notes can be followed by HOPO
        if note.tappable == 3:
          #This is the end of a valid HOPO section
          if lastEvent.tappable == 1 or lastEvent.tappable == 2:
            lastEvent = note
            lastTime = time
            continue
          if lastEvent.tappable == -2:
            #If its the same note again it's invalid
            if lastEvent.number == note.number:
              note.tappable = -2
            else:
              lastEvent.tappable = 1
          elif lastEvent.tappable == 0:
            lastEvent.tappable = 1
          #If last note was invalid or end of HOPO section, and current note is end, it is really not HOPO
          elif lastEvent.tappable != 2 and lastEvent.tappable != 1:
            note.tappable = 0
          #If last event was invalid or end of HOPO section, current note is start of HOPO
          else:
            note.tappable = 1
        elif note.tappable == 2:
          if lastEvent.tappable == -2:
            note.tappable = 1
          elif lastEvent.tappable == -1:
            note.tappable = 0
        elif note.tappable == 1:
          if lastEvent.tappable == 2:
            note.tappable = 0
        else:
          if lastEvent.tappable == -2:
            if tickDelta <= hopoDelta:
              lastEvent.tappable = 1
              
          if lastEvent.tappable != 2 and lastEvent.tappable != 1:
            note.tappable = 1
          else:
            if note.tappable == 1:
              note.tappable = 1
            else:
              note.tappable = 2
      lastEvent = note
      lastTime = time
    else:
      if note != None:
        #Handle last note
        #If it is the start of a HOPO, it's not really a HOPO
        if note.tappable == 1:
          note.tappable = 0
        #If it is the middle of a HOPO, it's really the end of a HOPO
        elif note.tappable == 2:
          note.tappable = 3      
    self.marked = True

    for time, event in self.allEvents:
      if isinstance(event, Tempo):
        bpmNotes.append([time, event])
        continue
      if not isinstance(event, Note):
        continue

  def markEvents(self, jp = True, player = True):
    #If already processed abort   
    if self.marked == True:
      return

    if jp == False and player == False:
      return
    
    for time, event in self.allEvents:
      if isinstance(event, JPEvent) and jp == True:
        print "Marking jp"
        for time2, event2 in self.getEvents(time, time + event.length):
          if isinstance(event2, Note):
            event2.jp = True
      elif isinstance(event, PlayerEvent) and player == True:
        print "Marking player", event.player
        for time2, event2 in self.getEvents(time, time + event.length):
          if isinstance(event2, Note):
            event.skipped = True
            if event.player == 0:
              event2.player1 = True
            elif event.player == 1:
              event2.player2 = True 
                  
  def markEventsAuto(self, jp = True, player = True):
    tempoTime = []
    tempoBpm = []
    lastTime = 0

    print "Mark JP"

    if jp == False and player == False:
      return
    
    #get all the bpm changes and their times
    for time, event in self.allEvents:
      if isinstance(event, Tempo):
        tempoTime.append(time)
        tempoBpm.append(event.bpm)
        endBpm = event.bpm
        #Just in case there's no end event
        endTime = time + 30000
        continue
      if isinstance(event, Note):
        endTime = time + event.length + 30000
        continue
    tempoTime.append(endTime)
    tempoBpm.append(endBpm)

    #calculate and add the measures/beats/half-beats
    passes = 1  
    limit = len(tempoTime)
    time = tempoTime[0]
    THnote = 256.0 #256th note
    jurgenMeasure = False
    i = 0
    while i < (limit - 1):
      msTotal = tempoTime[i+1] - time
      if msTotal == 0:
        i += 1
        continue
      tempbpm = tempoBpm[i]
      nbars = (msTotal * (tempbpm / (240.0 / THnote) )) / 1000.0 
      inc = msTotal / nbars

      while time < tempoTime[i+1]:
        if jurgenMeasure == True:
          if (passes % (15 * THnote / 1.0) == 0.0): #2560/1
            self.addEvent(time, JPEvent((time - lastTime) / 10.0))
            #event = Bars(2) #measure
            #self.addEvent(time, event)
            lastTime = time
          
          passes = passes + 1
  
        time = time + inc
        jurgenMeasure = True

      if time > tempoTime[i+1]:
        time = time - inc
        jurgenMeasure = False
        
      i += 1
      
  def markBars(self):
    tempoTime = []
    tempoBpm = []

    #get all the bpm changes and their times
    for time, event in self.allEvents:
      if isinstance(event, Tempo):
        tempoTime.append(time)
        tempoBpm.append(event.bpm)
        endBpm = event.bpm
        #Just in case there's no end event
        endTime = time + 30000
        continue
      if isinstance(event, Note):
        endTime = time + event.length + 30000
        continue
    tempoTime.append(endTime)
    tempoBpm.append(endBpm)

    #calculate and add the measures/beats/half-beats
    passes = 0  
    limit = len(tempoTime)
    time = tempoTime[0]
    THnote = 256.0 #256th note
    drawBar = True
    i = 0
    while i < (limit - 1):
      msTotal = tempoTime[i+1] - time
      if msTotal == 0:
        i += 1
        continue
      tempbpm = tempoBpm[i]
      nbars = (msTotal * (tempbpm / (240.0 / THnote) )) / 1000.0 
      inc = msTotal / nbars

      while time < tempoTime[i+1]:
        if drawBar == True:
          if (passes % (THnote / 1.0) == 0.0): #256/1
            event = Bars(2) #measure
            self.addEvent(time, event)
          elif (passes % (THnote / 4.0) == 0.0): #256/4
            event = Bars(1) #beat
            self.addEvent(time, event)
          elif (passes % (THnote / 8.0) == 0.0): #256/8
            event = Bars(0) #half-beat
            self.addEvent(time, event)
          
          passes = passes + 1
          
        time = time + inc
        drawBar = True

      if time > tempoTime[i+1]:
        time = time - inc
        drawBar = False
        
      i += 1

    #add the last measure/beat/half-beat
    if time == tempoTime[i]:
      if (passes % (THnote / 1.0) == 0.0): #256/1
        event = Bars(2) #measure
        self.addEvent(time, event)
      elif (passes % (THnote / 4.0) == 0.0): #256/4
        event = Bars(1) #beat
        self.addEvent(time, event)
      elif (passes % (THnote / 8.0) == 0.0): #256/8
        event = Bars(0) #half-beat
        self.addEvent(time, event)     

class Bars(Event):
  def __init__(self, barType):
    Event.__init__(self, barType)
    self.barType   = barType #0 half-beat, 1 beat, 2 measure
    self.soundPlayed = False
    
  def __repr__(self):
    return "<#%d>" % self.barType
  
class Song(object):
  def __init__(self, engine, infoFileName, songTrackName, guitarTrackName, rhythmTrackName, noteFileName, scriptFileName = None, part = [Part.GUITAR_PART]):
    self.engine        = engine
    self.info          = SongInfo(infoFileName)
    self.tracks        = [[Track() for t in range(len(Difficulty.difficulties))] for i in range(len(part))]
    self.difficulty    = [Difficulty.AMAZING_DIFFICULTY for i in part]
    self._playing      = False
    self.start         = 0.0
    self.noteFileName  = noteFileName
    self.bpm           = None
    self.period        = 0
    self.parts         = part
    self.delay         = self.engine.config.get("audio", "delay")
    self.delay         += self.info.delay
    self.guitarVolume  = self.engine.config.get("audio", "guitarvol")
    self.songVolume    = self.engine.config.get("audio", "songvol")
    self.rhythmVolume  = self.engine.config.get("audio", "rhythmvol")
    self.screwUpVolume = self.engine.config.get("audio", "screwupvol")    
    self.missVolume    = self.engine.config.get("audio", "miss_volume")
    self.lastTime      = 0

    self.hasMidiLyrics = False
    self.hasJP         = 0
    self.hasPlayers    = 0
    #RF-mod skip if folder (not needed anymore?)
    #if self.info.folder == True:
    #  return

    # load the tracks
    if songTrackName:
      self.music       = Audio.Music(songTrackName)

    self.guitarTrack = None
    self.rhythmTrack = None

    try:
      if guitarTrackName:
        self.guitarTrack = Audio.StreamingSound(self.engine, self.engine.audio.getChannel(1), guitarTrackName)
    except Exception, e:
      Log.warn("Unable to load guitar track: %s" % e)

    try:
      if rhythmTrackName:
        self.rhythmTrack = Audio.StreamingSound(self.engine, self.engine.audio.getChannel(2), rhythmTrackName)
    except Exception, e:
      Log.warn("Unable to load rhythm track: %s" % e)

    # load the notes   
    if noteFileName:
      note = MidiReader(self)
      midiIn = midi.MidiInFile(note, noteFileName)
      midiIn.read()
      self.lastTime = note.lastTime
      #Duplicate in info for display purposes
      #self.info._time = self.lastTime
      #print self.lastTime
      #self.info._cacheset("cache_endtime", binascii.hexlify(Cerealizer.dumps(self.lastTime)))
      #self.info.cachesave()
    # load the script
    if scriptFileName and os.path.isfile(scriptFileName):
      scriptReader = ScriptReader(self, open(scriptFileName))
      scriptReader.read()

    # update all note tracks
    #HOPO done here (should be in guitar scene, only do the track you are playing)
    #for tracks in self.tracks:
    #  for track in tracks:
    #    track.update()

  def getHash(self):
    h = sha.new()
    f = open(self.noteFileName, "rb")
    bs = 1024
    while True:
      data = f.read(bs)
      if not data: break
      h.update(data)
    return h.hexdigest()
  
  def setBpm(self, bpm):
    self.bpm    = bpm
    self.period = 60000.0 / self.bpm

  def save(self):
    self.info.save()
    f = open(self.noteFileName + ".tmp", "wb")
    midiOut = MidiWriter(self, midi.MidiOutFile(f))
    midiOut.write()
    f.close()

    # Rename the output file after it has been succesfully written
    shutil.move(self.noteFileName + ".tmp", self.noteFileName)

  def play(self, start = 0.0):
    self.start = start
    self.music.play(0, start / 1000.0)
    #RF-mod No longer needed?
    self.music.setVolume(self.songVolume)
    if self.guitarTrack:
      assert start == 0.0
      self.guitarTrack.setVolume(self.guitarVolume)
      self.guitarTrack.play()
    if self.rhythmTrack:
      assert start == 0.0
      self.rhythmTrack.setVolume(self.rhythmVolume)
      self.rhythmTrack.play()
    self._playing = True

  def pause(self):
    self.music.pause()
    self.engine.audio.pause()

  def unpause(self):
    self.music.unpause()
    self.engine.audio.unpause()

  def setInstrumentVolume(self, volume, part):
    if part == Part.GUITAR_PART:
      self.setGuitarVolume(volume)
    else:
      self.setRhythmVolume(volume)
      
  def setGuitarVolume(self, volume):
    if self.guitarTrack:
      if volume == 0:
        self.guitarTrack.setVolume(self.missVolume)
      else:
        self.guitarTrack.setVolume(volume)
    #This is only used if there is no guitar.ogg to lower the volume of song.ogg instead of muting this track
    else:
      if volume == 0:
        self.music.setVolume(self.missVolume * 1.5)
      else:
        self.music.setVolume(volume)

  def setRhythmVolume(self, volume):
    if self.rhythmTrack:
      if volume == 0:
        self.rhythmTrack.setVolume(self.missVolume)
      else:
        self.rhythmTrack.setVolume(volume)
  
  def setBackgroundVolume(self, volume):
    self.music.setVolume(volume)
  
  def stop(self):
    for tracks in self.tracks:
      for track in tracks:
        track.reset()
      
    self.music.stop()
    self.music.rewind()
    if self.guitarTrack:
      self.guitarTrack.stop()
    if self.rhythmTrack:
      self.rhythmTrack.stop()
    self._playing = False

  def fadeout(self, time):
    for tracks in self.tracks:
      for track in tracks:
        track.reset()
    #RF-mod (not needed?)
    #if self.info.folder == True:
    #  return
    
    self.music.fadeout(time)
    if self.guitarTrack:
      self.guitarTrack.fadeout(time)
    if self.rhythmTrack:
      self.rhythmTrack.fadeout(time)
    self._playing = False

  def getPosition(self):
    if not self._playing:
      pos = 0.0
    else:
      pos = self.music.getPosition()
    if pos < 0.0:
      pos = 0.0
    return pos + self.start - self.delay

  def isPlaying(self):
    return self._playing and self.music.isPlaying()

  def getBeat(self):
    return self.getPosition() / self.period

  def update(self, ticks):
    pass

  def getTrack(self):
    return [self.tracks[i][self.difficulty[i]] for i in range(len(self.difficulty))]

  track = property(getTrack)
noteMap = {     # difficulty, note
  0x3c: (Difficulty.SUPAEASY_DIFFICULTY, 0),
  0x3d: (Difficulty.SUPAEASY_DIFFICULTY, 1),
  0x3e: (Difficulty.SUPAEASY_DIFFICULTY, 2),
  0x3f: (Difficulty.SUPAEASY_DIFFICULTY, 3),
  0x40: (Difficulty.SUPAEASY_DIFFICULTY, 4),
  0x48: (Difficulty.EASY_DIFFICULTY,     0),
  0x49: (Difficulty.EASY_DIFFICULTY,     1),
  0x4a: (Difficulty.EASY_DIFFICULTY,     2),
  0x4b: (Difficulty.EASY_DIFFICULTY,     3),
  0x4c: (Difficulty.EASY_DIFFICULTY,     4),       
  0x54: (Difficulty.MEDIUM_DIFFICULTY,   0),
  0x55: (Difficulty.MEDIUM_DIFFICULTY,   1),
  0x56: (Difficulty.MEDIUM_DIFFICULTY,   2),
  0x57: (Difficulty.MEDIUM_DIFFICULTY,   3),
  0x58: (Difficulty.MEDIUM_DIFFICULTY,   4),  
  0x60: (Difficulty.AMAZING_DIFFICULTY,  0),
  0x61: (Difficulty.AMAZING_DIFFICULTY,  1),
  0x62: (Difficulty.AMAZING_DIFFICULTY,  2),
  0x63: (Difficulty.AMAZING_DIFFICULTY,  3),
  0x64: (Difficulty.AMAZING_DIFFICULTY,  4), 
}
reverseNoteMap = dict([(v, k) for k, v in noteMap.items()])

eventMap = {     # difficulty, event
  #JP supaeasy
  0x43: (Difficulty.SUPAEASY_DIFFICULTY, 0),
  #P1 start supaeasy
  0x45: (Difficulty.SUPAEASY_DIFFICULTY, 1),
  #P2 start supaeasy
  0x46: (Difficulty.SUPAEASY_DIFFICULTY, 2),    
  #JP easy
  0x4F: (Difficulty.EASY_DIFFICULTY,     0),
  #P1 start easy
  0x51: (Difficulty.EASY_DIFFICULTY,     1),
  #P2 start easy
  0x52: (Difficulty.EASY_DIFFICULTY,     2), 
  #JP medium
  0x5b: (Difficulty.MEDIUM_DIFFICULTY,   0),
  #P1 start medium
  0x5d: (Difficulty.MEDIUM_DIFFICULTY,   1),
  #P2 start medium
  0x5e: (Difficulty.MEDIUM_DIFFICULTY,   2),  
  #JP amazing
  0x67: (Difficulty.AMAZING_DIFFICULTY,  0),
  #P1 start amazing
  0x69: (Difficulty.AMAZING_DIFFICULTY,  1),
  #P2 start amazing
  0x6a: (Difficulty.AMAZING_DIFFICULTY,  2),
  #Vocals
  0x6c: (Difficulty.AMAZING_DIFFICULTY,  9),
}

reverseEventMap = dict([(v, k) for k, v in eventMap.items()])

class MidiWriter:
  def __init__(self, song, out):
    self.song         = song
    self.out          = out
    self.ticksPerBeat = 480

  def midiTime(self, time):
    return int(self.song.bpm * self.ticksPerBeat * time / 60000.0)

  def write(self):
    self.out.header(division = self.ticksPerBeat)
    self.out.start_of_track()
    self.out.update_time(0)
    if self.song.bpm:
      self.out.tempo(int(60.0 * 10.0**6 / self.song.bpm))
    else:
      self.out.tempo(int(60.0 * 10.0**6 / 122.0))

    # Collect all events
    events = [zip([difficulty] * len(track.getAllEvents()), track.getAllEvents()) for difficulty, track in enumerate(self.song.tracks[0])]
    events = reduce(lambda a, b: a + b, events)
    events.sort(lambda a, b: {True: 1, False: -1}[a[1][0] > b[1][0]])
    heldNotes = []

    for difficulty, event in events:
      time, event = event
      if isinstance(event, Note):
        time = self.midiTime(time)

        # Turn off any held notes that were active before this point in time
        for note, endTime in list(heldNotes):
          if endTime <= time:
            self.out.update_time(endTime, relative = 0)
            self.out.note_off(0, note)
            heldNotes.remove((note, endTime))

        note = reverseNoteMap[(difficulty, event.number)]
        self.out.update_time(time, relative = 0)
        self.out.note_on(0, note, event.special and 127 or 100)
        heldNotes.append((note, time + self.midiTime(event.length)))
        heldNotes.sort(lambda a, b: {True: 1, False: -1}[a[1] > b[1]])

    # Turn off any remaining notes
    for note, endTime in heldNotes:
      self.out.update_time(endTime, relative = 0)
      self.out.note_off(0, note)
      
    self.out.update_time(0)
    self.out.end_of_track()
    self.out.eof()
    self.out.write()

class ScriptReader:
  def __init__(self, song, scriptFile):
    self.song = song
    self.file = scriptFile

  def read(self):
    for line in self.file:
      if line.startswith("#") or line.isspace(): continue
      time, length, type, data = re.split("[\t ]+", line.strip(), 3)
      time   = float(time)
      length = float(length)

      if type == "text":
        event = TextEvent(data, length)
      elif type == "pic":
        event = PictureEvent(data, length)
      else:
        continue

      for track in self.song.tracks:
        for t in track:
          t.addEvent(time, event)

class MidiReader(midi.MidiOutStream):
  def __init__(self, song):
    midi.MidiOutStream.__init__(self)
    self.song = song
    self.heldNotes = {}
    self.velocity  = {}
    self.ticksPerBeat = 480
    self.tempoMarkers = []
    self.partTrack = 0
    self.partnumber = -1
    self.lastTime = 0

    self.readTextAndLyricEvents = Config.get("game","rock_band_events")
    #self.guitarSoloStartTime = 0
    #self.guitarSoloNoteCount = [0,0,0,0]   #1 count for each of the 4 difficulties
    self.guitarSoloIndex = 0
    self.guitarSoloActive = False
    self.guitarSoloSectionMarkers = False
    
  def addEvent(self, track, event, time = None):
    if self.partnumber == -1:
      #Looks like notes have started appearing before any part information. Lets assume its part0
      self.partnumber = self.song.parts[0]
    
    if (self.partnumber == None) and isinstance(event, Note):
      return True

    if time is None:
      time = self.abs_time()
    assert time >= 0
    
    if track is None:
      for t in self.song.tracks:
        for s in t:
          s.addEvent(time, event)
    else:
      
      tracklist = [i for i,j in enumerate(self.song.parts) if self.partnumber == j]
      for i in tracklist:
        #Each track needs it's own copy of the event, otherwise they'll interfere
        eventcopy = copy.deepcopy(event)
        if track < len(self.song.tracks[i]):
          self.song.tracks[i][track].addEvent(time, eventcopy)
    if time + event.length > self.lastTime:
      self.lastTime = time + event.length

  def abs_time(self):
    def ticksToBeats(ticks, bpm):
      return (60000.0 * ticks) / (bpm * self.ticksPerBeat)
      
    if self.song.bpm:
      currentTime = midi.MidiOutStream.abs_time(self)

      # Find out the current scaled time.
      # Yeah, this is reeally slow, but fast enough :)
      scaledTime      = 0.0
      tempoMarkerTime = 0.0
      currentBpm      = self.song.bpm
      for i, marker in enumerate(self.tempoMarkers):
        time, bpm = marker
        if time > currentTime:
          break
        scaledTime += ticksToBeats(time - tempoMarkerTime, currentBpm)
        tempoMarkerTime, currentBpm = time, bpm
      return scaledTime + ticksToBeats(currentTime - tempoMarkerTime, currentBpm)
    return 0.0

  def header(self, format, nTracks, division):
    self.ticksPerBeat = division
    if nTracks == 2:
      self.partTrack = 1
    
  def tempo(self, value):
    bpm = 60.0 * 10.0**6 / value
    self.tempoMarkers.append((midi.MidiOutStream.abs_time(self), bpm))
    if not self.song.bpm:
      self.song.setBpm(bpm)
    self.addEvent(None, Tempo(bpm))

  def sequence_name(self, text):
    #if self.get_current_track() == 0:
    self.partnumber = None
    self.guitarSoloIndex = 0
    self.guitarSoloActive = False
      
    if (text == "PART GUITAR" or text == "T1 GEMS" or text == "Click" or text == "MIDI out") and Part.GUITAR_PART in self.song.parts:
      self.partnumber = Part.GUITAR_PART
    elif text == "PART RHYTHM" and Part.RHYTHM_PART in self.song.parts:
      self.partnumber = Part.RHYTHM_PART
    elif text == "PART BASS" and Part.BASS_PART in self.song.parts:
      self.partnumber = Part.BASS_PART
    elif text == "PART GUITAR COOP" and Part.LEAD_PART in self.song.parts:
      self.partnumber = Part.LEAD_PART
    elif (text == "PART DRUMS" or text == "PART DRUM") and Part.DRUM_PART in self.song.parts:
      self.partnumber = Part.DRUM_PART
    elif self.get_current_track() <= 1 and Part.GUITAR_PART in self.song.parts:
      #Oh dear, the track wasn't recognised, lets just assume it was the guitar part
      self.partnumber = Part.GUITAR_PART
      
  def note_on(self, channel, note, velocity):
    if self.partnumber == None:
      return
    self.velocity[note] = velocity
    self.heldNotes[(self.get_current_track(), channel, note)] = self.abs_time()

  def note_off(self, channel, note, velocity):
    if self.partnumber == None:
      return
    try:
      startTime = self.heldNotes[(self.get_current_track(), channel, note)]
      endTime   = self.abs_time()
      del self.heldNotes[(self.get_current_track(), channel, note)]
      if note in noteMap:
        track, number = noteMap[note]
        self.addEvent(track, Note(number, endTime - startTime, special = self.velocity[note] == 127), time = startTime)
      elif note in eventMap:
        track, number = eventMap[note]
        if number == 0:
          print "Adding JP", startTime, endTime, endTime - startTime
          self.addEvent(track, JPEvent(endTime - startTime), time = startTime)
          self.song.hasJP += 1
        elif number == 1:
          print "adding playerEvent 0", startTime, endTime, endTime - startTime
          self.addEvent(track, PlayerEvent(0, endTime - startTime), time = startTime)
          self.song.hasPlayers += 1
        elif number == 2:
          print "adding playerEvent 1", startTime, endTime, endTime - startTime
          self.addEvent(track, PlayerEvent(1, endTime - startTime), time = startTime)
          self.song.hasPlayers += 1
      else:
        print "MIDI note 0x%x (%d) at %d does not map to any game note." % (note, note, self.abs_time())
        #Log.warn("MIDI note 0x%x at %d does not map to any game note." % (note, self.abs_time()))
        pass
    except KeyError:
      Log.warn("MIDI note 0x%x on channel %d ending at %d was never started." % (note, channel, self.abs_time()))

  #myfingershurt: adding MIDI text event access
  #these events happen on their own track, and are processed after the note tracks.
  #just mark the guitar solo sections ahead of time 
  #and then write an iteration routine to go through whatever track / difficulty is being played in GuitarScene 
  #to find these markers and count the notes and add a new text event containing each solo's note count
  def btext(self, text):
    print "text", text
    if text.find("GNMIDI") < 0:   #to filter out the midi class illegal usage / trial timeout messages
      #Log.debug(str(self.abs_time()) + "-MIDI Text: " + text)
      if self.readTextAndLyricEvents > 0:
        #myfingershurt: must move the guitar solo trigger detection logic here so we can also count the notes in the section
        #self.guitarSoloStartTime = 0
        #self.guitarSoloIndex = 0
        #self.guitarSoloNoteCount = [0,0,0,0]
        #self.guitarSoloActive = False
        
        #just find solo on/off triggers, normalize them (so simple guitarscene logic - special text events GSOLO ON1 and GSOLO OFF1)
        #then set midireader global flag saying to count incoming note on's, store in another global, then when GSOLO OFF detected store note count
        
        #Will want to store GSOLO_ONx event time, so that we can add 1 tick to it and add the solo note count for this particular track/diff
        #in the format of "GCOUNT100" (with 100 being the number of notes total in the gsolo section)


        gSoloEvent = False
        #also convert all underscores to spaces so it look better
        text = text.replace("_"," ")
        if text.lower().find("section") >= 0:
          #Log.debug("Section event " + event.text + " found at time " + str(self.abs_time()) )
          self.guitarSoloSectionMarkers = True      #GH1 dont use section markers... GH2+ do
          #strip unnecessary text / chars:
          text = text.replace("section","")
          text = text.replace("[","")
          text = text.replace("]","")
          #also convert "gtr" to "Guitar"
          text = text.replace("gtr","Guitar")
          event = TextEvent("SEC: " + text, 250.0)
          #event.length = 12000
          if text.lower().find("solo") >= 0 and text.lower().find("drum") < 0 and text.lower().find("outro") < 0 and text.lower().find("organ") < 0 and text.lower().find("synth") < 0:
            gSoloEvent = True
            gSolo = True
          elif text.lower().find("guitar") >= 0 and text.lower().find("lead") >= 0:    #Foreplay Long Time "[section_gtr_lead_1]"
            gSoloEvent = True
            gSolo = True
          elif text.lower().find("guitar") >= 0 and text.lower().find("line") >= 0:   #support for REM Orange Crush style solos
            gSoloEvent = True
            gSolo = True
          elif text.lower().find("guitar") >= 0 and text.lower().find("ostinato") >= 0:   #support for Pleasure solos "[section gtr_ostinato]"
            gSoloEvent = True
            gSolo = True
          else: #this is the cue to end solos...
            gSoloEvent = True
            gSolo = False
        elif text.lower().find("solo") >= 0 and text.find("[") < 0 and text.lower().find("drum") < 0 and text.lower().find("map") < 0 and text.lower().find("play") < 0 and not self.guitarSoloSectionMarkers:
          event = TextEvent("SEC: " + text, 250.0)
          gSoloEvent = True
          if text.lower().find("off") >= 0:
            gSolo = False
          else:
            gSolo = True
        elif text.lower().find("verse") >= 0 and text.find("[") < 0 and not self.guitarSoloSectionMarkers:   #this is an alternate GH1-style solo end marker
          event = TextEvent("SEC: " + text, 250.0)
          gSoloEvent = True
          gSolo = False
        elif text.lower().find("gtr") >= 0 and text.lower().find("off") >= 0 and text.find("[") < 0 and not self.guitarSoloSectionMarkers:   #this is an alternate GH1-style solo end marker
          #also convert "gtr" to "Guitar"
          text = text.replace("gtr","Guitar")
          event = TextEvent("SEC: " + text, 100.0)
          gSoloEvent = True
          gSolo = False
        else:  #unused text event
          event = TextEvent("TXT: " + text, 250.0)
        #now, check for guitar solo status change:
        soloSlop = 150.0   
        if gSoloEvent:
          if gSolo:
            if not self.guitarSoloActive:
              self.guitarSoloActive = True
              #soloEvent = TextEvent("GSOLO" + str(self.guitarSoloIndex) + " ON", 250.0)
              soloEvent = TextEvent("GSOLO ON", 250.0)
              Log.debug("GSOLO ON event " + event.text + " found at time " + str(self.abs_time()) )
              for track in self.song.tracks:
                for t in track:
                  t.addEvent(self.abs_time()-soloSlop, soloEvent)
              #self.guitarSoloNoteCount = [0,0,0,0]
              #self.guitarSoloStartTime = self.abs_time()
          else: #this is the cue to end solos...
            if self.guitarSoloActive:
              self.guitarSoloActive = False
              #soloEvent = TextEvent("GSOLO" + str(self.guitarSoloIndex) + " OFF", 250.0)
              soloEvent = TextEvent("GSOLO OFF", 250.0)
              Log.debug("GSOLO OFF event " + event.text + " found at time " + str(self.abs_time()) )
              self.guitarSoloIndex += 1
              for track in self.song.tracks:
                for t in track:
                  t.addEvent(self.abs_time()+soloSlop, soloEvent)
              
        for track in self.song.tracks:
          for t in track:
            t.addEvent(self.abs_time(), event)
        


  #myfingershurt: adding MIDI lyric event access
  def blyric(self, text):
    if text.find("GNMIDI") < 0:   #to filter out the midi class illegal usage / trial timeout messages
      #Log.debug(str(self.abs_time()) + "-MIDI Lyric: " + text)
      if self.readTextAndLyricEvents > 0:
        print "lyric", text, self.abs_time()
        event = TextEvent("LYR: " + text, 400.0)
        self.song.hasMidiLyrics = True
        for track in self.song.tracks:
          for t in track:
            t.addEvent(self.abs_time(), event)

  
  
class MidiInfoReaderNoSections(midi.MidiOutStream):
  # We exit via this exception so that we don't need to read the whole file in
  class Done: pass
  
  def __init__(self):
    midi.MidiOutStream.__init__(self)
    self.difficulties = []
    Log.debug("MidiInfoReaderNoSections class init (song.py)...")

    #MFH: practice section support:
    self.ticksPerBeat = 480
    self.sections = []
    self.tempoMarkers = []
    self.guitarSoloSectionMarkers = False
    self.bpm = None

  def note_on(self, channel, note, velocity):
    try:
      track, number = noteMap[note]
      diff = difficulties[track]
      if not diff in self.difficulties:
        self.difficulties.append(diff)
        #ASSUMES ALL parts (lead, rhythm, bass) have same difficulties of guitar part!
        if len(self.difficulties) == len(difficulties):
           raise Done
    except KeyError:
      pass


      
class MidiInfoReader(midi.MidiOutStream):
  # We exit via this exception so that we don't need to read the whole file in
  # Now we are reading the whole file in
  #class Done: pass
  
  def __init__(self):
    midi.MidiOutStream.__init__(self)
    self.tempoMarkers = []
    self.bpm = 0
    self.ticksPerBeat = 480
    self.difficulties = []
    self.parts = []
    self.noteNum = [[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
    self.lastTime = 0
    self.curPart = Part.GUITAR_PART

  def find_time(self, currentTime):
    def ticksToBeats(ticks, bpm):
      return (60000.0 * ticks) / (bpm * self.ticksPerBeat)
   
    if self.bpm:
#      currentTime = midi.MidiOutStream.abs_time(self)
      # Find out the current scaled time.
      # Yeah, this is reeally slow, but fast enough :)
      scaledTime      = 0.0
      tempoMarkerTime = 0.0
      currentBpm      = self.bpm
      for i, marker in enumerate(self.tempoMarkers):
        time, bpm = marker
        if time > currentTime:
          break
        scaledTime += ticksToBeats(time - tempoMarkerTime, currentBpm)
        tempoMarkerTime, currentBpm = time, bpm
      return scaledTime + ticksToBeats(currentTime - tempoMarkerTime, currentBpm)
    return 0.0
  
  def note_on(self, channel, note, velocity):
    try:
      diff, number = noteMap[note]
      #diff = Difficulty.difficulties[track]
      self.noteNum[self.curPart][diff] += 1
      #self.diffTemp[diff] += 1

      if self.noteNum[self.curPart][diff] > 7:
          if not diff in self.difficulties:
            self.difficulties.append(diff)
          if not self.curPart in self.parts:
            self.parts.append(self.curPart)

        #ASSUMES ALL parts (lead, rhythm, bass) have same difficulties of guitar part!
        #if len(self.difficulties) == len(difficulties):
        #  raise Done
    except KeyError:
      pass

  def note_off(self, channel, note, velocity):
      time = midi.MidiOutStream.abs_time(self)
      if time > self.lastTime:
        self.lastTime = time 

  def tempo(self, value):
    self.bpm = 60.0 * 10.0**6 / value
    self.tempoMarkers.append((midi.MidiOutStream.abs_time(self), self.bpm))
    
  def sequence_name(self, text):
    try:
      if text == "PART GUITAR" or text == "T1 GEMS" or text == "Click":
        self.curPart = Part.GUITAR_PART
      if text == "PART RHYTHM":
        self.curPart = Part.RHYTHM_PART  
      if text == "PART BASS":
        self.curPart = Part.BASS_PART
      if text == "PART GUITAR COOP":
        self.curPart = Part.LEAD_PART
      if text == "PART DRUMS" or text == "PART DRUM":
        self.curPart = Part.DRUM_PART
    except:
      pass
        
def loadSong(engine, name, library = DEFAULT_LIBRARY, seekable = False, playbackOnly = False, notesOnly = False, part = [Part.GUITAR_PART]):
  #RF-mod (not needed?)
  #library = Config.get("game", "selected_library")
  guitarFile = engine.resource.fileName(library, name, "guitar.ogg")
  songFile   = engine.resource.fileName(library, name, "song.ogg")
  rhythmFile = engine.resource.fileName(library, name, "rhythm.ogg")
  noteFile   = engine.resource.fileName(library, name, "notes.mid", writable = True)
  infoFile   = engine.resource.fileName(library, name, "song.ini", writable = True)
  scriptFile = engine.resource.fileName(library, name, "script.txt")
  previewFile = engine.resource.fileName(library, name, "preview.ogg")
  
  if seekable:
    if os.path.isfile(guitarFile) and os.path.isfile(songFile):
      # TODO: perform mixing here
      songFile   = guitarFile
      guitarFile = None
      rhythmFile = ""
    else:
      songFile   = guitarFile
      guitarFile = None
      rhythmFile = ""
      
  if not os.path.isfile(songFile):
    songFile   = guitarFile
    guitarFile = None
  
  if not os.path.isfile(rhythmFile):
    rhythmFile = None
  
  if playbackOnly:
    noteFile = None
    if os.path.isfile(previewFile):
      songFile = previewFile
      guitarFile = None
      rhythmFile = None
      
  if notesOnly:
    songFile = None
    guitarFile = None
    rhythmFile = None
    previewFile = None

  if songFile != None and guitarFile != None:
    #check for the same file
    songStat = os.stat(songFile)
    guitarStat = os.stat(guitarFile)
    #Simply checking file size, no md5
    if songStat.st_size == guitarStat.st_size:
      guitarFile = None

  song = Song(engine, infoFile, songFile, guitarFile, rhythmFile, noteFile, scriptFile, part)
  return song

def loadSongInfo(engine, name, library = DEFAULT_LIBRARY):
  #RF-mod (not needed?)
  #library = Config.get("game", "selected_library")
  infoFile   = engine.resource.fileName(library, name, "song.ini", writable = True)
  return SongInfo(infoFile)
  
def createSong(engine, name, guitarTrackName, backgroundTrackName, rhythmTrackName = None, library = DEFAULT_LIBRARY):
  #RF-mod (not needed?)
  #library = Config.get("game", "selected_library")
  path = os.path.abspath(engine.resource.fileName(library, name, writable = True))
  os.makedirs(path)
  
  guitarFile = engine.resource.fileName(library, name, "guitar.ogg", writable = True)
  songFile   = engine.resource.fileName(library, name, "song.ogg",   writable = True)
  noteFile   = engine.resource.fileName(library, name, "notes.mid",  writable = True)
  infoFile   = engine.resource.fileName(library, name, "song.ini",   writable = True)
  
  shutil.copy(guitarTrackName, guitarFile)
  
  if backgroundTrackName:
    shutil.copy(backgroundTrackName, songFile)
  else:
    songFile   = guitarFile
    guitarFile = None

  if rhythmTrackName:
    rhythmFile = engine.resource.fileName(library, name, "rhythm.ogg", writable = True)
    shutil.copy(rhythmTrackName, rhythmFile)
  else:
    rhythmFile = None
    
  f = open(noteFile, "wb")
  m = midi.MidiOutFile(f)
  m.header()
  m.start_of_track()
  m.update_time(0)
  m.end_of_track()
  m.eof()
  m.write()
  f.close()

  song = Song(engine, infoFile, songFile, guitarFile, rhythmFile, noteFile)
  song.info.name = name
  song.save()
  
  return song

def getDefaultLibrary(engine):
  return LibraryInfo(DEFAULT_LIBRARY, engine.resource.fileName(DEFAULT_LIBRARY, "library.ini"))

def getAvailableLibraries(engine, library = DEFAULT_LIBRARY):
  # Search for libraries in both the read-write and read-only directories
  songRoots    = [engine.resource.fileName(library),
                  engine.resource.fileName(library, writable = True)]
  libraries    = []
  libraryRoots = []

  for songRoot in set(songRoots):
    if (os.path.exists(songRoot) == False):
      return libraries
    for libraryRoot in os.listdir(songRoot):
      libraryRoot = os.path.join(songRoot, libraryRoot)
      if not os.path.isdir(libraryRoot):
        continue
      if os.path.isfile(os.path.join(libraryRoot, "notes.mid")):
        continue
      if libraryRoot.startswith("."):
        continue      
      libName = library + os.path.join(libraryRoot.replace(songRoot, ""))
      libraries.append(LibraryInfo(libName, os.path.join(libraryRoot, "library.ini")))
      continue
      #does this matter?
      dirs = os.listdir(libraryRoot)
      for name in dirs:
        if os.path.isfile(os.path.join(libraryRoot, name, "song.ini")):
          if not libraryRoot in libraryRoots:
            libName = library + os.path.join(libraryRoot.replace(songRoot, ""))
            libraries.append(LibraryInfo(libName, os.path.join(libraryRoot, "library.ini")))
            libraryRoots.append(libraryRoot)

  libraries.sort(lambda a, b: cmp(a.findTag("set") + a.name.lower(), b.findTag("set") + b.name.lower()))
  return libraries

def getAvailableSongs(engine, library = DEFAULT_LIBRARY, includeTutorials = False):
  order = engine.config.get("game", "songlist_order")
  # Search for songs in both the read-write and read-only directories
  if library == None:
    return []
  songRoots = [engine.resource.fileName(library), engine.resource.fileName(library, writable = True)]
  names = []
  for songRoot in songRoots:
    if (os.path.exists(songRoot) == False):
      return []
    for name in os.listdir(songRoot):
      if name.startswith("."):
        continue  
      if not os.path.isfile(os.path.join(songRoot, name, "notes.mid")):
        continue
      if not os.path.isfile(os.path.join(songRoot, name, "song.ini")) or name.startswith("."):
        continue
      if not name in names:
        names.append(name)

  songs = [SongInfo(engine.resource.fileName(library, name, "song.ini", writable = True)) for name in names]
  if not includeTutorials:
    songs = [song for song in songs if not song.tutorial]
  songs = [song for song in songs if not song.artist == '=FOLDER=']
  if order == 1:
    songs.sort(lambda a, b: cmp(a.findTag("set") + "." + a.findTag("song").lower() + a.artist.lower() + a.version.lower(), b.findTag("set") + "." + b.findTag("song").lower() + b.artist.lower() + b.version.lower()))
  else:
    songs.sort(lambda a, b: cmp(a.findTag("set") + "." + a.findTag("song").lower() + a.name.lower() + a.version.lower(), a.findTag("set") + "." + b.findTag("song").lower() + b.name.lower() + b.version.lower()))
  return songs
