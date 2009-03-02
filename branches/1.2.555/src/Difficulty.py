#####################################################################
# -*- coding: iso-8859-1 -*-                                        #
# Frets on Fire                                                     #
# Copyright (C) 2006-2009                                           #
#               Sami Kyöstilä                                       #
#               Alex Samonte                                        #
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

from Language import _

class Difficulty:
  def __init__(self, id, text):
    self.id   = id
    self.text = text
    
  def __str__(self):
    return self.text

  def __repr__(self):
    return self.text

AMAZING_DIFFICULTY      = 0
MEDIUM_DIFFICULTY       = 1
EASY_DIFFICULTY         = 2
SUPAEASY_DIFFICULTY     = 3

difficulties = {
  SUPAEASY_DIFFICULTY: Difficulty(SUPAEASY_DIFFICULTY, _("Supaeasy")),
  EASY_DIFFICULTY:     Difficulty(EASY_DIFFICULTY,     _("Easy")),
  MEDIUM_DIFFICULTY:   Difficulty(MEDIUM_DIFFICULTY,   _("Medium")),
  AMAZING_DIFFICULTY:  Difficulty(AMAZING_DIFFICULTY,  _("Amazing")),
}


