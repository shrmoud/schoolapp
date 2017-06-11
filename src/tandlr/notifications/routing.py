# -*- coding: utf-8 -*-

from channels.staticfiles import StaticFilesConsumer

from tandlr.notifications import consumers

channel_routing = {
    'http.request': StaticFilesConsumer(),

    # Wire up websocket channels to our consumers:
    'websocket.connect': consumers.ws_connect,
    'websocket.receive': consumers.ws_receive,
    'websocket.disconnect': consumers.ws_disconnect,
}
