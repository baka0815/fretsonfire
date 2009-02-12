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

from Config import MyConfigParser
from Config import Option
from Config import Config
import Log
import Resource
import os

encoding  = "iso-8859-1"
profile   = None
prototype = {}

class MyProfileParser(MyConfigParser):
 pass
        
class ProfileOption(Option):
 pass
      
def define(section, option, type, default = None, text = None, options = None, prototype = prototype):
  """
  Define a configuration key.
  
  @param section:    Section name
  @param option:     Option name
  @param type:       Key type (e.g. str, int, ...)
  @param default:    Default value for the key
  @param text:       Text description for the key
  @param options:    Either a mapping of values to text descriptions
                    (e.g. {True: 'Yes', False: 'No'}) or a list of possible values
  @param prototype:  Configuration prototype mapping
  """
  if not section in prototype:
    prototype[section] = {}
    
  if type == bool and not options:
    options = [True, False]
    
  prototype[section][option] = ProfileOption(type = type, default = default, text = text, options = options)

def load(fileName = None, setAsDefault = False):
  """Load a configuration with the default prototype"""
  global profile
  p = Profile(prototype, fileName)
  if setAsDefault and not config:
    profile = p
  return p

class Profile(Config):
  pass 

  
def get(section, option):
  """
  Read the value of a global configuration key.
  
  @param section:   Section name
  @param option:    Option name
  @return:          Key value
  """
  global profile
  return profile.get(section, option)
  
def set(section, option, value):
  """
  Write the value of a global configuration key.
  
  @param section:   Section name
  @param option:    Option name
  @param value:     New key value
  """
  global profile
  return profile.set(section, option, value)
