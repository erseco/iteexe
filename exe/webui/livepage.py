# -- coding: utf-8 --
# ===========================================================================
# eXe
# Copyright 2012, Pedro Peña Pérez, Open Phoenix IT
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
import logging
import itertools
from exe.webui.renderable import _RenderablePage
import nevow
from nevow.athena import LivePage
from nevow import inevow, tags, compy, flat

log = logging.getLogger(__name__)


class DefaultClientHandleFactory:
    def __init__(self):
        self.handleCounter = itertools.count()


def jquote(jscript):
    return jscript.replace(
        '\\',
        '\\\\').replace(
        "'",
        "\\'").replace(
            '\n',
        '\\n')


class IClientHandle(compy.Interface):
    def hookupOutput(self, output, finisher=None):
        """hook up an output conduit to this live evil instance.
        """

    def sendScript(self, script):
        """send a script through the output conduit to the browser.
        If no output conduit is yet hooked up, buffer the script
        until one is.
        """

    def handleInput(self, identifier, *args):
        """route some input from the browser to the appropriate
        destination.
        """


class ClientHandle(object):
    """An object which represents the client-side webbrowser.
    """
    __implements__ = IClientHandle,

    outputConduit = None

    def __init__(self, handleId, refreshInterval, targetTimeoutCount):
        self.refreshInterval = refreshInterval
        self.targetTimeoutCount = targetTimeoutCount
        self.timeoutCount = 0
        self.handleId = handleId
        self.events = events.EventNotification()
        self.outputBuffer = []
        self.closed = False
        self.closeNotifications = []
        self.firstTime = True
        self.timeoutLoop = LoopingCall(self.checkTimeout)
        self.timeoutLoop.start(self.refreshInterval)

    def setOutput(self, output):
        self.timeoutCount = 0
        self.outputConduit = output
        if self.outputBuffer:
            self.sendScript('\n'.join(map(str, self.outputBuffer)))
            self.outputBuffer = []

    def checkTimeout(self):
        if self.firstTime:
            self.firstTime = False
            return
        if self.outputConduit is not None:
            # The browser is waiting for us, send a noop.
            self.sendScript('null;')
        self.timeoutCount += 1
        if self.timeoutCount >= self.targetTimeoutCount:
            # This connection timed out.
            self.outputGone(None, self.outputConduit)

    def outputGone(self, failure, output):
        assert output == self.outputConduit
        if failure:
            log.err(failure)
        else:
            self.outputConduit = None
            self._closeComplete(failure)
        return None

    def _closeComplete(self, failure=None):
        self.closed = True
        if self.timeoutLoop:
            self.timeoutLoop.stop()
        self.timeoutLoop = None
        for notify in self.closeNotifications[:]:
            if failure is not None:
                notify.errback(failure)
            else:
                notify.callback(None)
        self.closeNotifications = []

    def sendScript(self, script):
        """Send a JavaScript string, 'script', to the browser represented by
        this mind, and evaluate it in the context of the browser window.
        """
        output = str(script)
        if len(output) and output[0] == '<':
            # import pdb; pdb.Pdb().set_trace()
            # This will catch exception pages, html pages written as javascript
            # to this response, etc
            err = "ERROR: Attempting to send invalid javascript to browser: %s" % output
            log.err(RuntimeError(err))
            return
        if self.outputConduit:
            if DEBUG:
                print("SENDING SCRIPT", script)
            output = str(script)
            self.outputConduit.callback(output)
            self.outputConduit = None
        else:
            self.outputBuffer.append(script)
            if DEBUG:
                print("Output buffered!", script)

    def handleInput(self, identifier, *args):
        if self.closed:
            log.msg("Hey, got input on a closed ClientHandle")
            return
        self.timeoutCount = 0
        if identifier == 'close':
            # the nevow_closeLive that we sent causes the glue to not renew
            # the output-side xmlhttp request, so .outputConduit will be
            # None and stay that way. This means we don't need to worry
            # about self.outputGone firing later on.
            if DEBUG:
                print("CLIENT ACKED CLOSE")
            # This happens in a callLater(0) from the original request
            self._closeComplete(None)
            return
        if DEBUG:
            print("Dispatching event to observer", identifier, args)
        try:
            self.events.publish(identifier, *(self, ) + args)
        except BaseException:
            log.err()

    def notifyOnClose(self):
        """This will return a Deferred that will be fired when the
        connection is closed 'normally', i.e. in response to handle.close()
        . If the connection is lost in any other way (because the browser
        navigated to another page, the browser was shut down, the network
        connection was lost, or the timeout was reached), this will errback
        instead."""
        d = defer.Deferred()
        self.closeNotifications.append(d)
        return d

    def close(self, executeScriptBeforeClose=""):
        if DEBUG:
            print("CLOSE WAS CALLED")
        d = self.notifyOnClose()
        self.call('nevow_closeLive', self.flt(executeScriptBeforeClose))
        return d

    # Here is some api your handlers can use to more easily manipulate the
    # live page
    def flt(self, what, quote=True):
        return flt(what, quote=quote, client=self)

    def set(self, what, to):
        """Set the contents of the node with the id 'what' to the stan 'to'
        """
        if not isinstance(to, _js):
            to = "'%s'" % (self.flt(to), )
        self.sendScript("nevow_setNode('%s', %s);" % (self.flt(what), to))

    def alert(self, what):
        """Show the user an alert 'what'
        """
        if not isinstance(what, _js):
            what = "'%s'" % (self.flt(what), )
        self.sendScript("alert(%s);" % (what, ))

    def append(self, where, what):
        """Append the stan 'what' to the node with the id 'where'
        """
        # client.append('foo', js("document.getNodeByID('bar')"))
        if not isinstance(what, _js):
            what = "'%s'" % (self.flt(what), )
        self.sendScript(
            "nevow_appendNode('%s', %s);" % (self.flt(where), what))

    def call(self, func, *args):
        """Call the javascript function named 'func' with the arguments given.
        """
        self.sendScript(callJS(func, *args) + ';')


class _js(object):
    """Marker indicating JavaScript should be included in a handler argument.
    No escaping will be performed.

    Normally arguments are embedded as strings in the javascript
    nevow_clientToServerEvent function call, and are evaluated in the
    context of this call. This puts the js variable 'node' in scope. When
    the js object is used, the unquoted string is inserted at that point
    in the argument list and will be evaluated by the JS interpreter
    before the nevow_clientToServerEvent call. The result will then be
    passed to nevow_clientToServerEvent and forwarded to the server.

    For example, the following:

    input(onchange=handler(foo, 'this.value'))

    Will be output as:

    nevow_clientToServerEvent('foo-identifier', 'this.value')

    Which will cause foo to be invoked on the server with the string
    'this.value', which is probably not what you want:

    foo(client, 'this.value')

    However, the following:

    input(onchange=handler(foo, js('this.value')))

    Will be output as:

    nevow_clientToServerEvent('foo-identifier', this.value)

    Which will cause foo to be invoked on the server with
    whatever the value of the input field was at the time the
    event handler fired:

    foo(client, 'fred flintstone')

    As a string. All handler arguments are always passed as strings.
    """

    def __init__(self, name=''):
        self._name = name

    def __getattr__(self, name):
        if self._name:
            return self.__class__(self._name + '.' + name)
        return self.__class__(name)

    def __call__(self, *args):
        if not self._name:
            name, = args
            return self.__class__(name)
        return self.__class__(callJS(self._name, *args))

    def __getitem__(self, args):
        if not isinstance(args, tuple):
            args = (args,)
        return self.__class__(
            self._name + '[' + ','.join(map(str, _quoteJSArguments(args))) + ']')

    def __str__(self):
        return self._name


js = _js()
flat.registerFlattener(lambda original, ctx: str(original), _js)


document = _js('document')
window = _js('window')
this = _js('this')
self = _js('self')


class DefaultClientHandleFactory(object):
    clientHandleClass = ClientHandle

    def __init__(self):
        self.clientHandles = {}
        self.handleCounter = itertools.count()

    def next_handle(self):
        return next(self.handleCounter)

    def newClientHandle(self, ctx, refreshInterval, targetTimeoutCount):
        handleid = inevow.ISession(ctx).uid + '-' + str(self.handleCounter())
        handle = self.clientHandleClass(handleid,
                                        refreshInterval, targetTimeoutCount)
        self.clientHandles[handleid] = handle
        handle.notifyOnClose().addCallback(self.deleteHandle, handleid=handleid)
        return handle

    def deleteHandle(self, _=None, handleid=None):
        del self.clientHandles[handleid]

    def getHandleForId(self, handleId):
        """Override this to restore old handles on demand."""
        if not self.clientHandles.has_key(handleId):
            log.msg("No handle for ID %s" % handleId)
        return self.clientHandles[handleId]


clientHandleFactory = DefaultClientHandleFactory()


def allClients(client1, client2):
    return True


def otherClients(client1, client2):
    return client1.handleId != client2.handleId


def allSessionClients(client1, client2):
    return client1.handleId[:32] == client2.handleId[:32]


def otherSessionClients(client1, client2):
    return otherClients(
        client1,
        client2) and allSessionClients(
        client1,
        client2)


def allSessionPackageClients(client1, client2):
    return client1.packageName == client2.packageName and allSessionClients(
        client1, client2)


def otherSessionPackageClients(client1, client2):
    return otherClients(
        client1,
        client2) and allSessionPackageClients(
        client1,
        client2)


class eXeClientHandle(ClientHandle):
    __implements__ = IClientHandle

    def sendScript(self, script, filter_func=None):
        if filter_func:
            for client in list(
                    nevow.livepage.clientHandleFactory.clientHandles.values()):
                if filter_func(client, self):
                    ClientHandle.sendScript(client, script)
        else:
            ClientHandle.sendScript(self, script)

    def alert(self, what, onDone=None, filter_func=False, title=''):
        """Show the user an alert 'what'
        """
        if not isinstance(what, _js):
            what = "'%s'" % (self.flt(what), )
        if onDone:
            script = "Ext.Msg.alert('%s',%s, function() { %s });" % (
                title, what, onDone)
        else:
            script = "Ext.Msg.alert('%s',%s);" % (title, what)
        if filter_func and onDone:
            for client in list(
                    nevow.livepage.clientHandleFactory.clientHandles.values()):
                if filter_func(client, self):
                    client.sendScript(onDone)
        self.sendScript(script)

    def notifyStatus(self, title, msg):
        self.sendScript(
            "eXe.controller.eXeViewport.prototype.eXeNotificationStatus('%s', '%s');" %
            (jquote(title), jquote(msg)), filter_func=allSessionClients)

    def hideStatus(self):
        self.sendScript(
            'Ext.ComponentQuery.query("#eXeNotification")[0].hide();',
            filter_func=allSessionClients)

    def notifyNotice(self, title, msg, type):
        self.sendScript(
            "eXe.controller.eXeViewport.prototype.eXeNotificationNotice('%s','%s', '%s');" %
            (jquote(title), jquote(msg), jquote(type)), filter_func=allSessionClients)


class eXeClientHandleFactory(DefaultClientHandleFactory):
    clientHandleClass = eXeClientHandle

    def newClientHandle(self, ctx, refreshInterval, targetTimeoutCount):
        handle = DefaultClientHandleFactory.newClientHandle(
            self, ctx, refreshInterval, targetTimeoutCount)
        handle.currentNodeId = ctx.tag.package.currentNode.id
        handle.packageName = ctx.tag.package.name
        handle.session = inevow.ISession(ctx)
        log.debug('New client handle %s. Handles %s' %
                  (handle.handleId, self.clientHandles))
        return handle


LivePage.clientHandleFactory = eXeClientHandleFactory()


class RenderableLivePage(_RenderablePage, LivePage):
    """
    This class is both a renderable and a LivePage/Resource
    """

    def __init__(self, parent, package=None, config=None):
        """
        Same as Renderable.__init__ but
        """
        LivePage.__init__(self)
        _RenderablePage.__init__(self, parent, package, config)
        self.clientHandleFactory = nevow.livepage.clientHandleFactory

    def renderHTTP(self, ctx):
        request = inevow.IRequest(ctx)
        request.setHeader('Expires', 'Fri, 25 Nov 1966 08:22:00 EST')
        request.setHeader(
            "Cache-Control",
            "no-store, no-cache, must-revalidate")
        request.setHeader("Pragma", "no-cache")
        return LivePage.renderHTTP(self, ctx)

    def render_liveglue(self, ctx, data):
        return tags.script(src='/jsui/nevow_glue.js')
