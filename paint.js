
function initialize() {
	var cnv = document.getElementById("cnv");

	var gridOptions = {
		lines : {
			separation : 25,
			color : '#D0D0D0',
			min : 10,
			max : 200
		},
		width : cnv.width,
		height : cnv.height,
		canvas : cnv,
		cells : {},
		startX : 0,
		startY : 0,
		power : {
			current : 1.0,
			max : 1.0,
			min : 0.01,
			delta : 8.0
		},
	};

	gridOptions.ws = new WebSocket("ws://cloudvm.mine.nu/ws");
	gridOptions.ws.onmessage = function (e) {
		onMessage(e, gridOptions)
	};
	gridOptions.ws.onopen = function (e) {
		requestData({
			'startX' : gridOptions.startX - 5,
			'startY' : gridOptions.startY - 5,
			'endX' : gridOptions.endX + 5,
			'endY' : gridOptions.endY + 5
		}, gridOptions)
	};
	//gridOptions.ws.onclose = function(e){console.log('Socket Closed')};
	//gridOptions.ws.onmessage = function(e){console.log('recieved:\t' + e.data)};


	// Register an event listener to call the resizeCanvas() function
	// each time the window is resized.
	window.addEventListener('resize', function () {
		resizeCanvas(gridOptions)
	}, false);
	window.addEventListener("keypress", function (e) {
		onKeypress(e, gridOptions)
	}, false);
	window.addEventListener("keydown", function (e) {
		onKeydown(e, gridOptions)
	}, false);
	window.addEventListener("click", function (e) {
		onClick(e, gridOptions)
	}, false);
	//window.addEventListener("click", function(e){onClick(e, gridOptions)}, false);
	window.addEventListener("mousemove", function (e) {
		gridOptions.mouseX = e.clientX;
		gridOptions.mouseY = e.clientY;
	}, false);
	window.addEventListener("mousewheel", function (e) {
		MouseWheelHandler(e, gridOptions)
	}, false);
	window.addEventListener("DOMMouseScroll", function (e) {
		MouseWheelHandler(e, gridOptions)
	}, false);

	window.setInterval(function () {
		requestData({
			'startX' : gridOptions.startX - 5,
			'startY' : gridOptions.startY - 5,
			'endX' : gridOptions.endX + 5,
			'endY' : gridOptions.endY + 5
		}, gridOptions)
	}, 5000);

	// Draw canvas border for the first time.
	resizeCanvas(gridOptions);
}

function zoom(amount, gridOptions) {
	gridOptions.lines.separation += amount;
	if (gridOptions.lines.separation > gridOptions.lines.max)
		gridOptions.lines.separation = gridOptions.lines.max;
	else if (gridOptions.lines.separation < gridOptions.lines.min)
		gridOptions.lines.separation = gridOptions.lines.min;
	redraw(gridOptions);
}

function MouseWheelHandler(e, gridOptions) {

	// cross-browser wheel delta
	var e = window.event || e; // old IE support
	var delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail)));
	zoom(delta, gridOptions)
}

function onKeypress(e, gridOptions) {
	console.log('onKeypress')
	if (e.keyCode == 43 || e.keyCode == 61) {
		// + or =
		zoom(1, gridOptions);
	} else if (e.keyCode == 45) {
		// -
		zoom(-1, gridOptions);
	} else if (e.keyCode == 32) {
		// Space
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			toggleCell(cell, gridOptions);
		}
	} else if (e.keyCode == 122) {
		// Z
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			setCellColor(cell, '', gridOptions);
		}
	} else if (e.keyCode == 120) {
		// X
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			setCellColor(cell, '#000000', gridOptions);
		}
	} else if (e.keyCode == 99) {
		// C
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			setCellColor(cell, '#FF0000', gridOptions);
		}
	} else if (e.keyCode == 118) {
		// V
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			setCellColor(cell, '#00FF00', gridOptions);
		}
	} else if (e.keyCode == 98) {
		// B
		var cell = getCellAtMouse(gridOptions);

		if (cell != gridOptions.lastCell) {
			gridOptions.lastCell = cell;
			setCellColor(cell, '#0000FF', gridOptions);
		}
	} else if (e.keyCode == 113) {
		//Q
		gridOptions.power.current += 1.0 / gridOptions.power.delta;
		if (gridOptions.power.current > gridOptions.power.max)
			gridOptions.power.current = 1;
	} else if (e.keyCode == 97) {
		//A
		gridOptions.power.current -= 1.0 / gridOptions.power.delta;
		if (gridOptions.power.current < gridOptions.power.min)
			gridOptions.power.current = gridOptions.power.min;
	} else if (e.keyCode == 119) {
		//W
		gridOptions.power.delta /= 2;
		if (gridOptions.power.delta < 2)
			gridOptions.power.delta = 2;
	} else if (e.keyCode == 115) {
		//S
		gridOptions.power.delta *= 2;
		if (gridOptions.power.delta > 128)
			gridOptions.power.delta = 128;
	}

}

function onKeydown(e, gridOptions) {
	if (e.keyCode == 37) {
		//Left
		gridOptions.startX -= 1;
		redraw(gridOptions);
	} else if (e.keyCode == 39) {
		//Right
		gridOptions.startX += 1;
		redraw(gridOptions);
	} else if (e.keyCode == 38) {
		//Up
		gridOptions.startY -= 1;
		redraw(gridOptions);
	} else if (e.keyCode == 40) {
		//Down
		gridOptions.startY += 1;
		redraw(gridOptions);
	}
}

function onClick(e, gridOptions) {
	var x = e.clientX;
	var y = e.clientY;

	var cell = getCellAt(x, y, gridOptions);

	toggleCell(cell, gridOptions)
}

function blendRGBColors(p, c0, c1) {
	c0 = c0 || '#FFFFFF'
		c1 = c1 || '#FFFFFF'
		if (c1 == '')
			c1 = '#FFFFFF'

				var color0 = {};
		var color1 = {};
	color0.r = parseInt(c0[1] + c0[2], 16);
	color0.g = parseInt(c0[3] + c0[4], 16);
	color0.b = parseInt(c0[5] + c0[6], 16);
	color1.r = parseInt(c1[1] + c1[2], 16);
	color1.g = parseInt(c1[3] + c1[4], 16);
	color1.b = parseInt(c1[5] + c1[6], 16);

	var newColor = {}
	for (var c in color0) {
		newColor[c] = Math.ceil(color0[c] * p + color1[c] * (1 - p));
		if (newColor[c] < 0x10)
			newColor[c] = 0;
		if (newColor[c] > 0xF0)
			newColor[c] = 0xFF;
		var hex = newColor[c].toString(16);
		if (hex.length < 2) {
			hex = '0' + hex;
		}
		newColor[c] = hex;
		if (newColor[c].length > 2)
			newColor[c] = 'FF';
	}

	return ('#' + newColor.r + newColor.g + newColor.b).toUpperCase();
}

function setCellColor(cell, color, gridOptions) {
	cell.color = blendRGBColors(gridOptions.power.current, color, cell.color);
	if (cell.color == '#FFFFFF')
		cell.color = '';
	submitData(cell.x, cell.y, gridOptions);
	redraw(gridOptions);
}

function toggleCell(cell, gridOptions) {

	if (cell.color == '#000000') {
		setCellColor(cell, '#FF0000', gridOptions);
	} else if (cell.color == '#FF0000') {
		setCellColor(cell, '#00FF00', gridOptions);
	} else if (cell.color == '#00FF00') {
		setCellColor(cell, '#0000FF', gridOptions);
	} else if (cell.color == '#0000FF') {
		setCellColor(cell, '', gridOptions);
	} else if (cell.color == '#FFFFFF' || cell.color == undefined || cell.color == '') {
		setCellColor(cell, '#000000', gridOptions);
	}

}

function getCellAtMouse(gridOptions) {
	return getCellAt(gridOptions.mouseX, gridOptions.mouseY, gridOptions)
}

function getCellAt(x, y, gridOptions) {
	var sep = gridOptions.lines.separation;

	var cellX = Math.floor(x / sep) + gridOptions.startX;
	var cellY = Math.floor(y / sep) + gridOptions.startY;

	if (gridOptions.cells[cellX] == undefined) {
		gridOptions.cells[cellX] = {}
	}

	if (gridOptions.cells[cellX][cellY] == undefined) {
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

	for (var x = 0; x <= numCellsX; x++) {
		for (var y = 0; y <= numCellsX; y++) {
			if (gridOptions.cells[x + startX] == undefined)
				continue;
			if (gridOptions.cells[x + startX][y + startY] == undefined)
				continue;

			var cell = gridOptions.cells[x + startX][y + startY];

			if (cell.color == undefined || cell.color == '')
				ctx.fillStyle = '#FFFFFF';
			else
				ctx.fillStyle = cell.color;

			ctx.fillRect(x * sep, y * sep, sep, sep);
		}
	}
	return;
}

function onMessage(e, gridOptions) {
	console.log('recieved:\t' + e.data)
	var toks = e.data.split('\t');

	if (toks[0] == 'set') {
		var cells = JSON.parse(toks[1]);
		for (x in cells) {
			for (y in cells[x]) {
				if (gridOptions.cells[x] == undefined) {
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

	if (ws.readyState == 1) {
		ws.send('get\t' + JSON.stringify(range))
	}

}

function submitData(x, y, gridOptions) {
	var ws = gridOptions.ws;

	var data = gridOptions.cells[x][y];
	data.x = x;
	data.y = y;

	if (ws.readyState == 1) {
		ws.send('set\t' + JSON.stringify(data))
	}
}

