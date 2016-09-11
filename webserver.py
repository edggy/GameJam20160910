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
        try:
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
                
                if world[(x,y)]['color'] == '':
                    world[(x,y)].pop('color', None)
                    if len(world[(x,y)]) == 0:
                        del world[(x,y)]
                
                newData = {}
                newData[x] = {}
                newData[x][y] = {}
                newData[x][y]['color'] = color
                
                for client in clients:
                    if client != self:
                        client.send('set' + delimeter + json.dumps(newData))
                print 'sent:\t' + 'set'
        except ValueError:
            pass
        

class Root:
    @cherrypy.expose
    def index(self):
        
        with open('paint.html') as f:
            str = f.read()
        return str
    
    @cherrypy.expose
    def ws(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler    
        
    @cherrypy.expose
    def reset(self):
        world.clear()
        return self.index()

if __name__ == '__main__':

    current_dir = path.dirname(path.abspath(__file__))
    
    cherrypy.config.update({'server.socket_port': 80})
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()    

    # Set up site-wide config first so we get a log if errors occur.
    cherrypy.config.update({'environment': 'production',
                            'log.error_file': 'site.log',
                            'log.screen': True})

    conf = {'/': {'tools.staticdir.on': True,
                  'tools.staticdir.dir': path.join(current_dir, 'datafiles')},
            '/ws': {'tools.websocket.on': True,
                    'tools.websocket.handler_cls': ServerWebSocket},
            '/paint.js': {'tools.staticfile.on': True,
                          'tools.staticfile.filename': path.join(current_dir, 'paint.js')}}

    cherrypy.quickstart(Root(), '/', config=conf)

