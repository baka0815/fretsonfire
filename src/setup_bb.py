from bbfreeze import Freezer

includeModules = [
  "SongChoosingScene",
  "GuitarScene",
  "GameResultsScene",
  ]
excludeModules = [
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
  "bisect",
  "difflib",
  "doctest",
  "ftplib",
  "getpass",
  "gopherlib",
  "heapq",
  "macpath",
  "macurl2path",
  "GimpGradientFile",
  "GimpPaletteFile",
  "PaletteFile",
  "macosx",
  "win32com",
  "win32comext",
  "_dotblas"
  ]
    
f = Freezer("woop2", includes=includeModules, excludes=excludeModules)
f.addScript("FretsOnFire.py")

f()    # starts the freezing process