# ===========================================================================
# eXe
# Copyright 2004-2006, University of Auckland
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# ===========================================================================
"""
Functions for handling persistance in eXe
"""

import logging

import io

from twisted.persisted.styles import Versioned
from twisted.spread import jelly, banana

log = logging.getLogger(__name__)

# Choose between cBanana and banana
try:
    from twisted.spread import cBanana
    banana.cBanana = cBanana
    Banana = banana.Canana
    log.info('Using cBanana')
except ImportError:
    Banana = banana.Banana
    log.info('Using pyBanana')


class Persistable(jelly.Jellyable, jelly.Unjellyable, Versioned):
    """
    Base class for persistent classes
    """
    # List of variables to avoid persisting
    nonpersistant = []

    def getStateFor(self, jellier):
        """
        Call Versioned.__getstate__ to store
        persistenceVersion etc...
        """
        return self.__getstate__()

    def __getstate__(self):
        """
        Return which variables we should persist
        """
        toPersist = {key: value for key, value in self.__dict__.items()
                     if key not in self.nonpersistant}
        return Versioned.__getstate__(self, toPersist)

    def afterUpgrade(self):
        """
        Called after all items being loaded have been loaded
        and upgraded.
        """


def encodeObject(toEncode):
    """
    Take an object and turn it into a string representation.
    """
    log.debug("encodeObject")

    encoder = Banana()
    encoder.connectionMade()
    encoder._selectDialect("none")
    str_buffer = io.BytesIO()  # Updated to BytesIO for byte handling
    encoder.transport = str_buffer
    encoder.sendEncoded(jelly.jelly(toEncode))

    return str_buffer.getvalue()


def decodeToList(toDecode):
    """
    Decodes an object to a list of jelly strings, but doesn't unjelly them.
    """
    log.debug("decodeObjectRaw starting decodeToList")
    decoder = Banana()
    decoder.connectionMade()
    decoder._selectDialect("none")
    jelly_data = []
    decoder.expressionReceived = jelly_data.append
    decoder.dataReceived(toDecode)
    log.debug("decodeObjectRaw ending decodeToList")
    return jelly_data


def fixDataForMovedObjects(jellyData):
    """
    Fixes the jelly data so that IDevices that have moved can still be loaded.
    Removes 'exe.engine' from the module path, so that you can add their 'dir'
    to 'sys.path' and then jelly will just load them
    """
    for i, element in enumerate(jellyData):
        if isinstance(element, list):
            # Recurse
            fixDataForMovedObjects(element)
        elif isinstance(element, str):
            if element in ('flashmovieidevice.FlashMovieIdevice',
                           'quiztestidevice.QuizTestIdevice',
                           'quiztestidevice.TestQuestion',
                           'quiztestidevice.AnswerOption',
                           'appletidevice.AppletIdevice'):
                mod, cls = element.split('.')
                jellyData[i] = 'exe.engine.%s.%s' % (mod, cls)


def decodeObjectRaw(toDecode):
    """
    Decodes the object the same as decodeObject but doesn't upgrade it.
    """
    jellyData = decodeToList(toDecode)
    fixDataForMovedObjects(jellyData)
    decoded = jelly.unjelly(jellyData[0])
    return decoded


def decodeObject(toDecode):
    """
    Take a string and turn it into an object.
    """
    decoded = decodeObjectRaw(toDecode)
    doUpgrade()
    return decoded
