#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------
""" Defines the HTML "editor" for the wxPython user interface toolkit.
    HTML editors interpret and display HTML-formatted text, but do not
    modify it.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os.path
import base64
import webbrowser
import sys



# webview may require setting an environment variable
#  GIO_MODULE_DIR for gio/modules to enable https
from traits.api import Str

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.html_editor file.
from traitsui.editors.html_editor import ToolkitEditorFactory

from .editor import Editor

def image_to_string(imgfile):
    with open(imgfile, "rb") as imageFile:
        imgstr = base64.b64encode(imageFile.read())
    return imgstr.decode("utf-8")

def html_image(imgfile, size=None):
    filename, file_extension = os.path.splitext(imgfile)
    prefix='<img src="data:image/'+file_extension+';base64,'
    the_size=' '
    if size is not None:
        if isinstance(size,tuple):
           the_size='width="'+str(size[0])+'" height="'+str(size[1])+'"'
        else:
           the_size='width="'+str(size)+'"'
    return prefix + image_to_string(imgfile)+'"'  + the_size+'>'


#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

"""
Rene Roos Nov 2019: wxPython 4.0.6 is built against gtk3 for Windows and gtk2 for Linux because of several optical
issues on Linux. wx.html2 is based on gtk3 technology and therefore wx.html is used on Linux.
This should become obsolete once wxPython is built against gtk3 on all OS.
"""
if sys.platform == 'win32':
    import wx.html2 as webview
    class SimpleEditor ( Editor ):
        """ Simple style of editor for HTML, which displays interpreted HTML.
        """
        #---------------------------------------------------------------------------
        #  Trait definitions:
        #---------------------------------------------------------------------------

        # Is the HTML editor scrollable? This values override the default.
        scrollable = True

        # External objects referenced in the HTML are relative to this URL
        base_url = Str

        #---------------------------------------------------------------------------
        #  Finishes initializing the editor by creating the underlying toolkit
        #  widget:
        #---------------------------------------------------------------------------

        def init ( self, parent ):
            """ Finishes initializing the editor by creating the underlying toolkit
                widget.
            """
            self.control = webview.WebView.New(parent)

            #self.control.SetBorders( 2 )

            self.base_url = self.factory.base_url

            self.sync_value( self.factory.base_url_name, 'base_url', 'from' )
        #---------------------------------------------------------------------------
        #  Updates the editor when the object trait changes external to the editor:
        #---------------------------------------------------------------------------

        def update_editor ( self ):
            """ Updates the editor when the object trait changes external to the
                editor.
            """
            text = self.str_value
            if self.factory.format_text:
                text = self.factory.parse_text( text )
            self.control.SetPage( text, self.base_url )




        #-- Event Handlers ---------------------------------------------------------

        def _base_url_changed(self):
            url = self.base_url
            if not url.endswith( '/' ):
                rl += '/'
            #self.control.base_url = url
            self.update_editor()

else:
    # previous wx.html version
    #-------------------------------------------------------------------------------
    #  URLResolvingHtmlWindow class:
    #-------------------------------------------------------------------------------

    import wx.html as wh
    class URLResolvingHtmlWindow(wh.HtmlWindow):
        """ Overrides OnOpeningURL method of HtmlWindow to append the base URL
            local links.
        """

        def __init__(self, parent, open_externally, base_url):
            wh.HtmlWindow.__init__(self, parent)
            self.open_externally = open_externally
            self.base_url = base_url

        def OnLinkClicked(self, link_info):
            """ Handle the base url and opening in a new browser window for links.
            """
            if self.open_externally:
                url = link_info.GetHref()
                if (self.base_url and not url.startswith(('http://', 'https://'))):
                    url = self.base_url + url
                if not url.startswith(('file://', 'http://', 'https://')):
                    url = 'file://' + url
                webbrowser.open_new(url)

        def OnOpeningURL(self, url_type, url):
            """ According to the documentation, this method is supposed to be called
                for both images and link clicks, but it appears to only be called
                for image loading, hence the base url handling code in
                OnLinkClicked.
            """
            if (self.base_url and not os.path.isabs(url) and not url.startswith(
                ('http://', 'https://', self.base_url))):
                return self.base_url + url
            else:
                return wh.HTML_OPEN



    class SimpleEditor(Editor):
        """ Simple style of editor for HTML, which displays interpreted HTML.
        """
        #---------------------------------------------------------------------------
        #  Trait definitions:
        #---------------------------------------------------------------------------

        # Is the HTML editor scrollable? This values override the default.
        scrollable = True

        # External objects referenced in the HTML are relative to this URL
        base_url = Str

        #---------------------------------------------------------------------------
        #  Finishes initializing the editor by creating the underlying toolkit
        #  widget:
        #---------------------------------------------------------------------------

        def init(self, parent):
            """ Finishes initializing the editor by creating the underlying toolkit
                widget.
            """
            self.control = URLResolvingHtmlWindow(
                parent, self.factory.open_externally, self.base_url)
            self.control.SetBorders(2)

            self.base_url = self.factory.base_url
            self.sync_value(self.factory.base_url_name, 'base_url', 'from')

        #---------------------------------------------------------------------------
        #  Updates the editor when the object trait changes external to the editor:
        #---------------------------------------------------------------------------

        def update_editor(self):
            """ Updates the editor when the object trait changes external to the
                editor.
            """
            text = self.str_value
            if self.factory.format_text:
                text = self.factory.parse_text(text)
            self.control.SetPage(text)

        #-- Event Handlers ---------------------------------------------------------

        def _base_url_changed(self):
            url = self.base_url
            if not url.endswith('/'):
                url += '/'
            self.control.base_url = url
            self.update_editor()


#--EOF-------------------------------------------------------------------------
