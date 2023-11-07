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
from exe.engine.jsidevice import JsIdevice
from exe.webui.blockfactory import g_blockFactory
from webassets.utils import common_path_prefix
from exe.engine.idevice import Idevice
"""
JsBlock can render and process JsIdevices as XHTML
"""

import logging
from exe.webui.block import Block
from exe.webui.elementfactory import g_elementFactory
from exe.webui import common

from exe import globals as G
from exe.engine.path import Path

log = logging.getLogger(__name__)


# ===========================================================================
class JsBlock(Block):
    """
    JsBlockIdevice can render and process JsIdevices as XHTML
    """

    def __init__(self, parent, idevice):
        Block.__init__(self, parent, idevice)
        self.elements = []
        for field in self.idevice:
            self.elements.append(g_elementFactory.createElement(field))
        if not hasattr(self.idevice, 'undo'):
            self.idevice.undo = True

    def process(self, request):
        """
        Process the request arguments from the web server
        """
        is_cancel = common.requestHasCancel(request)

        Block.process(self, request)
        if ("action" not in request.args or
                request.args["action"][0] != "delete"):
            for element in self.elements:
                element.process(request)

        if "title" + self.id in request.args \
                and not is_cancel:
            self.idevice.title = request.args["title" + self.id][0]

        if "iconiDevice" + self.id in request.args \
                and not is_cancel:
            self.idevice.icon = request.args["iconiDevice" + self.id][0]

        if not is_cancel:
            if self.idevice.title != '' or self.idevice.icon != '':
                self.idevice.emphasis = Idevice.SomeEmphasis
            else:
                self.idevice.emphasis = Idevice.NoEmphasis

    def renderEdit(self, style):
        """
        Returns an XHTML string with the form element for editing this block
        """
        html = '<div>'
        html += '<span class="js-idevice-title-label">'
        html += '<label for="title' + self.id + \
            '">' + _('Title') + ':</label> '
        html += common.elementInstruc(
            _('The title and the icon are not required. If you leave them empty the iDevice will have no emphasis.'))
        html += '</span>'
        html += common.hiddenField("iconiDevice" + self.id, self.idevice.icon)
        html += '<a class="js-show-icon-panel-button" href="javascript:showMessageBox(\'iconpanel\');" title="%s"><img src="/images/stock-insert-image.png" alt="%s" width="16" height="16" /></a>' % (
            _('Select an icon'), _('Choose an Image'))

        # Get icon source (if it exists)
        icon = self.idevice.icon
        icon_exists = False
        if icon != '':
            idevice_icon = Path(
                G.application.config.stylesDir /
                style /
                'icon_' +
                self.idevice.icon +
                '.gif')
            if idevice_icon.exists():
                icon_exists = True
            else:
                idevice_icon = Path(
                    G.application.config.stylesDir /
                    style /
                    "icon_" +
                    self.idevice.icon +
                    ".png")
                if idevice_icon.exists():
                    icon_exists = True
                else:
                    idevice_icon = Path(
                        G.application.config.stylesDir /
                        style /
                        "icon_" +
                        self.idevice.icon +
                        ".svg")
                    if idevice_icon.exists():
                        icon_exists = True

        # Icon HTML element
        html += '<img class="js-idevide-icon-preview" name="iconiDevice%s" id="iconiDevice"' % (
            self.id)
        if icon_exists:
            html += ' src="/style/%s/icon_%s%s"' % (
                style, icon, idevice_icon.ext)
        else:
            html += ' src="/images/empty.gif"'
        html += '/>'

        # Delete button
        html += '<a href="javascript:deleteIcon(%s);" id="deleteIcon%s" class="deleteIcon" title="%s"' % (
            self.id, self.id, _('Delete'))
        # If the icon doesn't exists
        if not icon_exists:
            html += ' style="display: none;"'
        html += '>'
        html += '<img class="js-delete-icon" alt="%s" src="%s"/>' % (
            _('Delete'), '/images/stock-delete.png')
        html += '</a>'

        html += common.textInput("title" + self.id, self.idevice.title)

        html += '<div class="js-icon-panel-container">'
        html += '<div id="iconpaneltitle">%s</div>' % _("Icons")
        html += '<div id="iconpanelcontent">'
        html += self.__renderIcons(style)
        html += '</div>'

        html += "</div>"

        for element in self.elements:
            html += element.renderEdit()

        html += self.renderEditButtons()
        html += "</div>"

        return html

    def __renderIcons(self, style):
        """
        Return xhtml string for dispay all icons
        """
        iconpath = Path(G.application.config.stylesDir / style)
        iconfiles = iconpath.files("icon_*")
        html = '<div id="styleIcons"><div style="height:300px;overflow:auto">'

        for iconfile in iconfiles:
            iconname = iconfile.namebase
            icon = iconname.split("_", 1)[1]

            iconExists = False
            iconExtension = "gif"
            myIcon = Path(
                G.application.config.stylesDir /
                style /
                iconname +
                ".gif")
            if myIcon.exists():
                iconExists = True
                iconValue = icon + '.' + iconExtension
                iconSrc = '/style/%s/icon_%s' % (style, iconValue)
            else:
                myIcon = Path(
                    G.application.config.stylesDir /
                    style /
                    iconname +
                    ".png")
                if myIcon.exists():
                    iconExists = True
                    iconExtension = "png"
                    iconValue = icon + '.' + iconExtension
                    iconSrc = '/style/%s/icon_%s' % (style, iconValue)
                else:
                    myIcon = Path(
                        G.application.config.stylesDir /
                        style /
                        iconname +
                        ".svg")
                    if myIcon.exists():
                        iconExists = True
                        iconExtension = "svg"
                        iconValue = icon + '.' + iconExtension
                        iconSrc = '/style/%s/icon_%s' % (style, iconValue)

            if iconExists:
                filename = "/style/%s/%s.%s" % (style, iconname, iconExtension)
                html += '<div style="float:left; text-align:center; width:105px;\n'
                html += 'margin-right:10px; margin-bottom:15px" > '
                html += '<img src="%s" \n' % filename
                html += "style=\"border:1px solid #E8E8E8;padding:5px;cursor:pointer;max-width:60px;max-height:60px;height:auto\" onclick=\"window[0].selectStyleIcon('%s',this, '%s', '%s')\" title=\"%s.%s\">\n" % (
                    icon, iconSrc, self.id, icon, iconExtension)
                html += '<br /><span style="display:inline-block;width:100px;overflow:hidden;text-overflow:ellipsis">%s.%s</span></div>\n' % (
                    icon, iconExtension)

        html += '</div></div>'

        return html

    def renderPreview(self, style):
        """
        Returns an XHTML string for previewing this block during editing
        """
        html = common.ideviceHeader(self, style, "preview")
        for element in self.elements:
            html += element.renderPreview()
        html += common.ideviceFooter(self, style, "preview")
        return html

    def renderXML(self, style):
        aTitle = self.idevice.title
        aIcon = self.idevice.icon
        xml = ""
        if len(self.elements) > 0:
            return self.elements[0].renderXML(
                None, "idevice", self.idevice.id, title=aTitle, icon=aIcon)
        return xml

    def renderView(self, style):
        """
        Returns an XHTML string for viewing this block,
        i.e. when exported as a webpage or SCORM package
        """
        html = common.ideviceHeader(self, style, "view")
        for element in self.elements:
            html += element.renderView()
        html += common.ideviceFooter(self, style, "view")
        return html


g_blockFactory.registerBlockType(JsBlock, JsIdevice)

# ===========================================================================
