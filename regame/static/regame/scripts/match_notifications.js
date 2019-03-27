(function () {
    var webSocketAvailable = 'WebSocket' in window
    if (!webSocketAvailable) {
        return
    }
    var refreshElem = document.querySelector('meta[http-equiv="refresh"]')
    if (!refreshElem) {
        return
    }
    var refreshSecs = parseInt(refreshElem.content, 10)
    var stopTime = refreshSecs * 1000 / 2
    var delayedReload = function() {
        setTimeout(function(){location.reload(true)}, stopTime)
    }
    var connectWithSocket = function() {
        window.stop()
        var socket = new WebSocket('wss://' + location.host + '/ws' + location.pathname)
        socket.onmessage = function(ev) {
            var data = JSON.parse(ev.data)
            if (data.event === 'move') {
                location.reload(true)
            }
        }
        socket.onclose = delayedReload
        socket.onerror = delayedReload
    }
    setTimeout(connectWithSocket, stopTime)
})()
