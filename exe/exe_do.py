#!/usr/bin/python
# -*- coding: utf-8 -*-
# ===========================================================================
# eXe
# Copyright 2011-2012, Pedro Peña Pérez
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# ===========================================================================

import os
import sys
import optparse
import json
import logging

# Make it so we can import our own nevow and twisted etc.
if os.name == 'posix':
    sys.path.insert(0, '/usr/share/exe')

# Try to work even with no python path
try:
    from exe.application import Application
except ImportError, error:
    if str(error) == "No module named exe.application":
        exePath = os.path.abspath(sys.argv[0])
        exeDir = os.path.dirname(exePath)
        pythonPath = os.path.split(exeDir)[0]
        sys.path.insert(0, pythonPath)
        from exe.application import Application
    else:
        import traceback
        traceback.print_exc()
        sys.exit(1)
from exe.export.cmdlineexporter import CmdlineExporter
from exe.importers.cmdlineimporter import CmdlineImporter
from exe.engine.package import Package
from exe.engine.path import Path, TempDirPath

ENCODING = sys.stdout.encoding or "UTF-8"


class CustomHelpFormatter(optparse.IndentedHelpFormatter):
    def format_usage(self, usage):
        return usage


class CustomOptionParser(optparse.OptionParser):
    def set_usage(self, usage):
        self.usage = usage

    def print_help(self, f=None):
        if f is None:
            f = sys.stdout
        f.write(self.format_help())


def prepareParser():
    usage = _(u"%prog, the commandline version of eXe.\n\
Usage: %prog [options] input_file [output_file]\n\nTo show \
help:\n%prog -h").encode(ENCODING)
    parser = CustomOptionParser(usage=usage, formatter=CustomHelpFormatter())
   
    parser.add_option("-a", "--append",
                      action="store_true",dest='a',
                      help=_(u"Append  <input_file> elp package to <output_file> elp package").encode(ENCODING))
    
 
    parser.add_option("-s", "--set",
                      action="store", type='string', dest='set_options', metavar='field=value,<field=value>...',
                      help=_(u"Set ELP field values. Example: -s style=Default,root.title='Root Node'").encode(ENCODING))

    group = optparse.OptionGroup(parser,
                     _(u"Set ELP field values options").encode(ENCODING),
                     _(u"Once you have chosen Set ELP field values option using '-s <values>' or \
    '--set <values>', it's possible to configure the following options:").encode(ENCODING))

    group.add_option("-w", "--write_package",
                    action="store_true", dest="set_options_write",
                    help=_(u"Write field values to ELP").encode(ENCODING))

    parser.add_option_group(group)

    parser.add_option("-r", "--report",
                      action="store_true", dest='report',
                      help=_(u"Generates resource info report to text <output_file> \
from <input_file> elp package").encode(ENCODING))

    parser.add_option("-l", "--checker_logfile",
                      dest='checker_logfile',
                      metavar='LOGFILE')

    parser.add_option("-x", "--export",
                  action="store", dest="x", metavar="format",
                  choices=['xml', 'scorm12', 'scorm2004',
                           'ims', 'website', 'webzip', 'singlepage',
                           'xliff', 'epub3','text'],
                  help=_(u"Export <input_file> elp package to optional \
<output_file> on one of the given formats: xml, scorm12, scorm2004, ims, \
website, webzip, singlepage, xliff, text or epub3.").encode(ENCODING))
    parser.add_option("-i", "--import",
                  action="store", dest="i", metavar="format",
                  choices=['xml', 'xliff'],
                  help=_(u"Import to <output_file> elp package, <input_file> \
in one of the given formats: xml or xliff.")\
.encode(ENCODING))
    parser.add_option("-f", "--force",
                  action="store_true", dest="f",
                  help=_(u"Force overwrite of <output_file>").encode(ENCODING))
    parser.add_option("--editable",
                     action="store_true",
                     dest="editable",
                     help=_(u"Add the required files to generate a export editable by \
eXeLearning").encode(ENCODING),
                     default=False)

    group = optparse.OptionGroup(parser,
                        _(u"XLIFF export options").encode(ENCODING),
                        _(u"Once you have chosen XLIFF export option using '-x xliff' or \
'--export xliff', it's possible to configure the following export options:").encode(ENCODING))
    group.add_option("--no-copy-source",
                     action="store_false",
                     dest="copy",
                     help=_(u"Don't copy source in target").encode(ENCODING),
                     default=True)
    group.add_option("--wrap-cdata",
                     action="store_true",
                     dest="wrap",
                     help=_(u"Wrap fields in CDATA").encode(ENCODING),
                     default=False)
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser,
                        _(u"XLIFF import options").encode(ENCODING),
                        _(u"Once you have chosen XLIFF import option using  '-i xliff' \
or '--import xliff', it's possible to configure the following import options:").encode(ENCODING))
    group.add_option("--from-source",
                     action="store_true",
                     dest="from_source",
                     help=_(u"Import from source language").encode(ENCODING),
                     default=False)
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser,
                        _(u"SCORM export options").encode(ENCODING),
                        _(u"Once you have chosen one SCORM export option using '-x scorm12' or \
'-x scorm2004' or 'x agrega', it's possible to configure the following export options:").encode(ENCODING))
    group.add_option("--single-page",
                     action="store_true",
                     dest="single",
                     help=_(u"Include Single Page export file").encode(ENCODING),
                     default=False)
    group.add_option("--website",
                     action="store_true",
                     dest="website",
                     help=_(u"Include Web Site export files").encode(ENCODING),
                     default=False)
    parser.add_option_group(group)

    return parser

if __name__ == "__main__":
    application = Application()
    application.loadConfiguration()
    optparse._ = application.config.locales[application.config.locale].gettext

    parser = prepareParser()
    options, args = parser.parse_args()

    if options.x and options.i:
        parser.error(_(u'Options --export and --import are mutually \
exclusive.').encode(ENCODING))
    if options.x and options.a:
        parser.error(_(u'Options --export and --append are mutually \
exclusive.').encode(ENCODING))
    if options.i and options.a:
        parser.error(_(u'Options --import and --append are mutually \
exclusive.').encode(ENCODING))
        
    if not options.a and not options.x and not options.i and not options.set_options and not options.report:
        parser.error(_(u'No --append --export, --import, --set or --report option supplied.')\
.encode(ENCODING))

    if not args:
        parser.error(_(u'No file input supplied.').encode(ENCODING))

    if options.a:          
            if len(args) != 2:
                parser.error(_(u'Bad number of arguments supplied').encode(ENCODING))
                    
            try:                
                pkg1 = Package.load(args[1],True,None,None)
                pkg2 = Package.load(args[0],False,pkg1,None)
                pkg2.root.copyToPackage(pkg1,pkg1.root)             
                pkg1.save()
                print _(u"Successfully appended '%s' to '%s'.") % (args[0],args[1])                       
            except:
                print _(u"exe_do: error: Unable to append elp")
                print sys.exc_value
                exit()                
    else:
    
        inputf = args[0]
        try:
            outputf = args[1]
        except IndexError:
            outputf = None
    
        if len(args) > 2:
            parser.error(_(u'Bad number of arguments supplied').encode(ENCODING))
    
        if options.checker_logfile:
            logfile = Path(options.checker_logfile)
            if logfile.abspath().dirname().exists():
                handler = logging.FileHandler(logfile.abspath(), 'a+')
                handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
                logging.getLogger('exe.engine.checker').addHandler(handler)
    
        tempdir = TempDirPath()
        if options.set_options:
            try:
                path = Path(inputf)
                path.copy(tempdir)
                inputf = tempdir / path.basename()
                pkg = Package.load(inputf)
                if not pkg:
                    error = _(u"Invalid input package")
                    raise Exception(error.encode(ENCODING))
                set_options = options.set_options.split(',')
                for set_option in set_options:
                    name, value = set_option.split('=')
                    names = name.split('.')
                    obj = pkg
                    try:
                        value = json.loads(value)
                    except:
                        pass
                    for name in names[:-1]:
                        obj = getattr(obj, name)
                    name = names[-1]
                    setattr(obj, name, value)
                pkg.save()
                if options.set_options_write:
                    inputf.move(path)
                    inputf = path
            except:
                print _(u"exe_do: error: Unable to set values from '%s'.\nThe \
    error was:") % (path)
                print sys.exc_value
                exit()
    
        if options.report:
            options.x = 'report'
    
        if options.x:
            x = CmdlineExporter(application.config, {"export": options.x,
                                                     "overwrite": options.f,
                                                     "copy-source": options.copy,
                                                     "wrap-cdata": options.wrap,
                                                     "single-page": options.single,
                                                     "website": options.website,
                                                     "editable": options.editable})
            try:
                outputf = x.do_export(inputf, outputf)
                print _(u"Successfully exported '%s' from '%s'.") % (outputf, \
    inputf)
            except:
                print _(u"exe_do: error: Unable to export from '%s'.\nThe \
    error was:") % (inputf)
                print sys.exc_value
        if options.i:
            i = CmdlineImporter(application.config, {"import": options.i,
                                                     "from-source": options.from_source})
            try:
                outputf = i.do_import(inputf, outputf)
                print _(u"File '%s' successfully imported to '%s'.") % (inputf, \
    outputf)
            except:
                print _(u"exe_do: error: Unable to import '%s'.\nThe \
    error was:") % (inputf)
                print unicode(sys.exc_value)
