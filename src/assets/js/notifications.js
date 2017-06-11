$(function() {
    // Let the library know where WebSocketMain.swf is:
    WEB_SOCKET_SWF_LOCATION = "https://tandlr.pythonballz.com/static/WebSocketMain.swf";

    // Write your code in the same way as for native WebSocket:
    var ws = new WebSocket("wss://ws.tandlr.pythonballz.com/notifications");
    var token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImphdmllcnRlc3QyQGdtYWlsLmNvbSIsIm9yaWdfaWF0IjoxNDY5MDMzOTI2LCJ1c2VyX2lkIjozNCwiZW1haWwiOiJqYXZpZXJ0ZXN0MkBnbWFpbC5jb20iLCJleHAiOjE0NzE2MjU5MjZ9.__xazcN_xKNg6c1z8QaUBDiKSpLXdncy9i3vQnMWkvM"

    // Connection Opened
    ws.onopen = function() {
        // We do login
        var message = {
            "login": true,
            "jwt": token
        }
        ws.send(JSON.stringify(message));
        console.info("conected");
    };

    // Connection Closed
    ws.onclose = function() {
        console.info("closed");
    };

    // When the client receive a message(notification)
    ws.onmessage = function(e) {
        var data = $.parseJSON(e.data);

        // Execute the script when the user has a new notification
        if (e.data.search('target_action:mass_notification') >= 0) {
            alert('New mass-notification \n' + data.message);
        }else{
            alert(data.target_type + ' has been ' + data.target_action);
        }

        $("#notifications").val(parseInt($("#notifications").val()) + 1);
    };

    // Create a new notification when user click on button
    $("#new").on("click", function(event) {
        var message = {
            "jwt": token
        }
        ws.send(JSON.stringify(message));
    });
});
