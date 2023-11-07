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
BuiltInBlocks imports the iDevice blocks which are built-in (i.e. not
plugins) to eXe
"""

from webui.freetextblock import FreeTextBlock
from webui.genericblock import GenericBlock
from webui.jsblock import JsBlock
from webui.multichoiceblock import MultichoiceBlock
from webui.reflectionblock import ReflectionBlock
from webui.casestudyblock import CasestudyBlock
from webui.truefalseblock import TrueFalseBlock
from webui.imagewithtextblock import ImageWithTextBlock
from webui.wikipediablock import WikipediaBlock
from webui.attachmentblock import AttachmentBlock
from webui.galleryblock import GalleryBlock
from webui.clozeblock import ClozeBlock
# from webui.clozelangblock             import ClozelangBlock
from webui.flashwithtextblock import FlashWithTextBlock
from webui.externalurlblock import ExternalUrlBlock
from webui.imagemagnifierblock import ImageMagnifierBlock
from webui.mathblock import MathBlock
from webui.multimediablock import MultimediaBlock
from webui.rssblock import RssBlock
from webui.multiselectblock import MultiSelectBlock
from webui.appletblock import AppletBlock
from webui.flashmovieblock import FlashMovieBlock
from webui.quiztestblock import QuizTestBlock
from webui.listablock import ListaBlock
from webui.notablock import NotaBlock

from webui.sortblock import SortBlockInc
from webui.hangmanblock import HangmanBlockInc
from webui.clickinorderblock import ClickInOrderBlockInc
from webui.memorymatchblock import MemoryMatchBlockInc
from webui.placetheobjectsblock import PlaceTheObjectsBlockInc
from webui.fileattachblock import FileAttachBlockInc
# JR
# Necesarios para la FPD
from webui.clozefpdblock import ClozefpdBlock
from webui.clozelangfpdblock import ClozelangfpdBlock
from webui.reflectionfpdblock import ReflectionfpdBlock
from webui.reflectionfpdmodifblock import ReflectionfpdmodifBlock
from webui.parasabermasfpdblock import ParasabermasfpdBlock
from webui.debesconocerfpdblock import DebesconocerfpdBlock
from webui.citasparapensarfpdblock import CitasparapensarfpdBlock
from webui.recomendacionfpdblock import RecomendacionfpdBlock
from webui.verdaderofalsofpdblock import VerdaderofalsofpdBlock
from webui.seleccionmultiplefpdblock import SeleccionmultiplefpdBlock
from webui.eleccionmultiplefpdblock import EleccionmultiplefpdBlock
from webui.casopracticofpdblock import CasopracticofpdBlock
from webui.ejercicioresueltofpdblock import EjercicioresueltofpdBlock
from webui.destacadofpdblock import DestacadofpdBlock
# from webui.correccionfpdblock	import CorreccionfpdBlock
from webui.orientacionesalumnadofpdblock import OrientacionesalumnadofpdBlock
from webui.orientacionestutoriafpdblock import OrientacionestutoriafpdBlock
from webui.freetextfpdblock import FreeTextfpdBlock

# ===========================================================================
