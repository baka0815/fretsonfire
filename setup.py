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

import sys 
sys.path.append("src")
from distutils.core import setup
import sys, SceneFactory, Version, glob, os
import distutils.command.sdist

try:
  import py2exe
except ImportError:
  pass

options = {
  "py2exe": {
    "dist_dir":  "dist/win32",
    "includes":  SceneFactory.scenes,
    "excludes":  [
      "OpenGL",   # OpenGL must be excluded and handled manually due to a py2exe bug
      "glew.gl.apple",
      "glew.gl.ati",
      "glew.gl.atix",
      "glew.gl.hp",
      "glew.gl.ibm",
      "glew.gl.ingr",
      "glew.gl.intel",
      "glew.gl.ktx",
      "glew.gl.mesa",
      "glew.gl.oml",
      "glew.gl.pgi",
      "glew.gl.rend",
      "glew.gl.s3",
      "glew.gl.sgi",
      "glew.gl.sgis",
      "glew.gl.sgix",
      "glew.gl.sun",
      "glew.gl.sunx",
      "glew.gl.threedfx",
      "glew.gl.win",
      "ode",
      "_ssl",
      "bz2",
      "email",
      "calendar",
      "doctest",
      "ftplib",
      "getpass",
      "gopherlib",
      "macpath",
      "macurl2path",
      "GimpGradientFile",
      "GimpPaletteFile",
      "PaletteFile",
      "macosx",
      "matplotlib",
      "Tkinter",
      "curses",
    ],
    "optimize":  2,
  }
}

# Reuse the manifest file from "python setup.py sdist"
try:
  dataFiles = []
  ignoreExts = [".po", ".py", ".pot"]
  for line in open("MANIFEST").readlines():
    fn = line.strip()
    if any([fn.endswith(e) for e in ignoreExts]): continue
    if fn in ["Makefile", "MANIFEST", "MANIFEST.in"]: continue
    dataFiles.append((os.path.dirname(fn), [fn]))
except IOError:
  print "Unable to open MANIFEST. Please run python setup.py sdist -o to generate it."
  dataFiles = []

if os.name == "nt":
  setup(version = Version.version(),
        description = "Rockin' it Oldskool!",
        name = "Frets on Fire",
        url = "http://www.unrealvoodoo.org",
        windows = [
          {
            "script":          "src/FretsOnFire.py",
            "icon_resources":  [(1, "data/icon.ico")]
          }
        ],
        zipfile = "data/library.zip",
        author = "Unreal Voodoo",
        author_email = "contact@unrealvoodoo.org",
        description = "Frets on Fire is a game of musical skill and fast fingers. The aim of the game is to play guitar with the keyboard as accurately as possible.",
        data_files = dataFiles,
        options = options)
else:
  setup(version = Version.version(),
        description = "Rockin' it Oldskool!",
        name = "FretsOnFire",
        url = "http://www.unrealvoodoo.org",
        author = "Unreal Voodoo",
        author_email = "contact@unrealvoodoo.org",
        data_files = dataFiles,
        license = "GPLv2",
        description = "Frets on Fire is a game of musical skill and fast fingers. The aim of the game is to play guitar with the keyboard as accurately as possible.",
        options = options)
