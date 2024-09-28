
var testFrameNode = document.getElementById('testframe');
testFrameNode.addEventListener('load', loadNotify, true);

var sendSubmitEvent = function(theTarget, callWhenDone) {
    var theEvent = testFrameNode.contentDocument.createEvent("HTMLEvents");
    theEvent.initEvent("submit",
        true,
        true);
    theTarget.dispatchEvent(theEvent);
    callWhenDone()
}

var sendClickEvent = function(targetId, callWhenDone) {
    var theTarget = testFrameNode.contentDocument.getElementById(targetId);
    var doEventOfType = function(eventType) {
    var theEvent = testFrameNode.contentDocument.createEvent("MouseEvents");
    var evt = document.createEvent("MouseEvents")
    theTarget.dispatchEvent(evt);
    }
    doEventOfType('mousedown');
    doEventOfType('mouseup');
    doEventOfType('click');
    callWhenDone();
}
