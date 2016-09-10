#!python
import os.path as path
import json
import cherrypy
from ws4py.websocket import WebSocket
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

delimeter = '\t'
world = {}
clients = set({})

class ServerWebSocket(WebSocket):
    def opened(self):
        clients.add(self)
        
    def closed(self, code, reason=None):
        clients.remove(self)
        
    def received_message(self, message):
        print 'received_message:\t' + str(message)
        toks = str(message).split(delimeter)
        
        if toks[0] == 'get':
            request = json.loads(toks[1])
            startX = int(request['startX'])
            startY = int(request['startY'])
            endX = int(request['endX'])
            endY = int(request['endY'])
            
            data = {}
            
            for x in range(startX, endX):
                for y in range(startY, endY):
                    if (x, y) in world:
                        if x not in data:
                            data[x] = {}
                        #if y not in data[x]:
                        #    data[x][y] = {}
                            
                        data[x][y] = world[(x, y)]
                    
            self.send('set' + delimeter + json.dumps(data))
            print 'sent:\t' + 'set' + delimeter + json.dumps(data)
        
        elif toks[0] == 'set':
            data = json.loads(toks[1])
            x = int(data['x'])
            y = int(data['y'])
            color = data['color']
            
            if (x,y) not in world:
                world[(x,y)] = {}
                
            world[(x,y)]['color'] = color
            
            newData = {}
            newData[x] = {}
            newData[x][y] = {}
            newData[x][y]['color'] = color
            
            for client in clients:
                if client != self:
                    client.send('set' + delimeter + json.dumps(newData))
            print 'sent:\t' + 'set'
        

class Root:
    @cherrypy.expose
    def index(self):
        return """<html>
<head>
    <title>Test bed</title>
    <style>
    html, body {
      width: 100%;
      height: 100%;
      margin: 0px;
      border: 0;
      overflow: hidden; /*  Disable scrollbars */
      display: block;  /* No floating content on sides */
    }
    </style>
    <script type="text/javascript">
        
        function initialize() {
           var cnv = document.getElementById("cnv");
           
           var gridOptions = {
                   lines: {
                       separation: 25,
                       color: '#BBBBBB',
                       min: 15,
                       max: 200
                   },
                   width: cnv.width,
                   height: cnv.height,
                   canvas: cnv,
                   cells: {},
                   startX: 0,
                   startY: 0
               };
               
           gridOptions.ws = new WebSocket("ws://localhost:8080/ws");
           gridOptions.ws.onmessage = function(e){onMessage(e, gridOptions)};
           //gridOptions.ws.onopen = function(e){console.log('Socket Opened')};
           //gridOptions.ws.onclose = function(e){console.log('Socket Closed')};
           //gridOptions.ws.onmessage = function(e){console.log('recieved:\t' + e.data)};
           
           
               
           // Register an event listener to call the resizeCanvas() function 
           // each time the window is resized.
           window.addEventListener('resize', function(){resizeCanvas(gridOptions)}, false);
           window.addEventListener("keypress", function(e){onKeypress(e, gridOptions)}, false);
           window.addEventListener("keydown", function(e){onKeydown(e, gridOptions)}, false);
           window.addEventListener("click", function(e){onClick(e, gridOptions)}, false);
           //window.addEventListener("message", function(e){onMessage(e, gridOptions)}, false);
           
           window.setInterval(function(){requestData({'startX':gridOptions.startX-5, 'startY':gridOptions.startY-5, 'endX':gridOptions.endX + 5, 'endY':gridOptions.endY + 5}, gridOptions)}, 1000);
           
           
           
           // Draw canvas border for the first time.
           resizeCanvas(gridOptions);
        }
        
        function onKeypress(e, gridOptions) {
           console.log('onKeypress')
           if(e.keyCode == 43 && gridOptions.lines.separation < gridOptions.lines.max) {
              // +
              gridOptions.lines.separation += 1;
              redraw(gridOptions);
           }
           else if(e.keyCode == 45 && gridOptions.lines.separation > gridOptions.lines.min) {
              // -
              gridOptions.lines.separation -= 1;
              redraw(gridOptions);
           }
           
        }
        
        function onKeydown(e, gridOptions) {
            console.log('onKeydown')
            if(e.keyCode == 37) {
                //Left
                gridOptions.startX -= 1;
                redraw(gridOptions);
            }
            else if(e.keyCode == 39) {
                //Right
                gridOptions.startX += 1;
                redraw(gridOptions);
            }
            else if(e.keyCode == 38) {
                //Up
                gridOptions.startY -= 1;
                redraw(gridOptions);
            }
            else if(e.keyCode == 40) {
                //Down
                gridOptions.startY += 1;
                redraw(gridOptions);
            }
        }
        
        function onClick(e, gridOptions) {
            console.log('onClick')
            var x = e.clientX;
            var y = e.clientY;
            
            var cell = getCellAt(x, y, gridOptions);
            
            if(cell.color == '#FF0000') {
                cell.color = '#FFFFFF';
                submitData(cell.x, cell.y, gridOptions);
                redraw(gridOptions);
            }
            else{
                cell.color = '#FF0000';
                submitData(cell.x, cell.y, gridOptions);
                redraw(gridOptions);
            }
            
            
        }
        
        function getCellAt(x, y, gridOptions) {
            var sep = gridOptions.lines.separation;
            
            var cellX = Math.floor(x / sep) + gridOptions.startX;
            var cellY = Math.floor(y / sep) + gridOptions.startY;
            
            if(gridOptions.cells[cellX] == undefined) {
                gridOptions.cells[cellX] = {}
            }
            
            if(gridOptions.cells[cellX][cellY] == undefined) {
                gridOptions.cells[cellX][cellY] = {};
            }
            gridOptions.cells[cellX][cellY].x = cellX;
            gridOptions.cells[cellX][cellY].y = cellY;
            
            return gridOptions.cells[cellX][cellY];
        }
        
        function resizeCanvas(gridOptions) {
            console.log('resizeCanvas')
            var cnv = gridOptions.canvas;
            cnv.width = window.innerWidth;
            cnv.height = window.innerHeight;
            gridOptions.width = cnv.width;
            gridOptions.height = cnv.height;
            
            redraw(gridOptions);
        }
        
        function redraw(gridOptions) {
            var cnv = gridOptions.canvas;
            cnv.getContext('2d').clearRect(0, 0, cnv.width, cnv.height);
            
            drawCells(gridOptions);
            drawGridLines(gridOptions);
            
        }
        
        function drawGridLines(gridOptions) {
            var cnv = gridOptions.canvas;
            var ctx = cnv.getContext('2d');

            var iWidth = cnv.width;
            var iHeight = cnv.height;
            var sep = gridOptions.lines.separation;

            ctx.strokeStyle = gridOptions.lines.color;
            ctx.strokeWidth = 1;

            ctx.beginPath();

            var iCount = null;
            var i = null;
            var x = null;
            var y = null;

            iCount = Math.floor(iWidth / sep);

            for (i = 1; i <= iCount; i++) {
                x = (i * sep);
                ctx.moveTo(x, 0);
                ctx.lineTo(x, iHeight);
                ctx.stroke();
            }


            iCount = Math.floor(iHeight / sep);

            for (i = 1; i <= iCount; i++) {
                y = (i * sep);
                ctx.moveTo(0, y);
                ctx.lineTo(iWidth, y);
                ctx.stroke();
            }

            ctx.closePath();

            return;
        }
        
        function drawCells(gridOptions) {
            var cnv = gridOptions.canvas;
            var ctx = cnv.getContext('2d');
            
            var sep = gridOptions.lines.separation;
            var iWidth = cnv.width;
            var iHeight = cnv.height;
            var startX = gridOptions.startX;
            var startY = gridOptions.startY;
            var numCellsX = Math.floor(iWidth / sep);
            var numCellsY = Math.floor(iHeight / sep);
            
            gridOptions.endX = startX + numCellsX;
            gridOptions.endY = startY + numCellsY;
            
            //requestData({'startX':startX, 'startY':startY, 'endX':startX + numCellsX, 'endY':startY + numCellsY}, gridOptions);
            
            for(var x = 0; x < numCellsX; x++) {
                for(var y = 0; y < numCellsX; y++) {
                    if(gridOptions.cells[x+startX] == undefined) continue;
                    if(gridOptions.cells[x+startX][y+startY] == undefined) continue;
                    
                    var cell = gridOptions.cells[x+startX][y+startY];
                    
                    if(cell.color != undefined) ctx.fillStyle = cell.color;
                    
                    ctx.fillRect(x*sep,y*sep,sep,sep);
                }
            }
            return;
        }
        
        function onMessage(e, gridOptions) {
            console.log('recieved:\t' + e.data)
            var toks = e.data.split('\t');
            
            if(toks[0] == 'set') {
                var cells = JSON.parse(toks[1]);
                for(x in cells) {
                    for(y in cells[x]) {
                        if(gridOptions.cells[x] == undefined) {
                            gridOptions.cells[x] = {}
                        }
                        gridOptions.cells[x][y] = cells[x][y];
                    }
                }
                redraw(gridOptions);
            }
        }
        
        function requestData(range, gridOptions) {
            var ws = gridOptions.ws;
            
            if(ws.readyState) {
                ws.send('get\t' + JSON.stringify(range))
            }
            
        }
        
        function submitData(x, y, gridOptions) {
            var ws = gridOptions.ws;
            
            var data = gridOptions.cells[x][y];
            data.x = x;
            data.y = y;
            
            if(ws.readyState) {
                ws.send('set\t' + JSON.stringify(data))
            }
        }
    </script>
</head>
<body onload="initialize()">
    <canvas id="cnv" style='position:absolute; left:0px; top:0px;'></canvas>
</body>
</html>
"""
    @cherrypy.expose
    def ws(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler    

if __name__ == '__main__':

    current_dir = path.dirname(path.abspath(__file__))
    
    cherrypy.config.update({'server.socket_port': 8080})
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()    

    # Set up site-wide config first so we get a log if errors occur.
    cherrypy.config.update({'environment': 'production',
                            'log.error_file': 'site.log',
                            'log.screen': True})

    conf = {'/': {'tools.staticdir.on': True,
                  'tools.staticdir.dir': path.join(current_dir, 'datafiles')},
            '/ws': {'tools.websocket.on': True,
                    'tools.websocket.handler_cls': ServerWebSocket}}

    cherrypy.quickstart(Root(), '/', config=conf)

