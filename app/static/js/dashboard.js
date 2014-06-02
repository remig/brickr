/*global ko: false, $: false, WidgetList: false, WidgetViewModel: false, DashboardViewModel: false, $SCRIPT_ROOT: false */
(function() {

WidgetList = {};  // Global list used by each widget to register itself

var available_widget_names = [  // Official list of all available widgets
	'explore',
	'photo_stream',
	'group_list'
];

var snapSize = 0;
var dashboard_width, dashboard_height;

// data-bind="stopBinding: true" 
ko.bindingHandlers.stopBinding = {
	init: function() {
		return { controlsDescendantBindings: true };
	}
};

function minMax(min, max, v) {
	return Math.min(max, Math.max(min, v));
}
	
function pct(frac, value) {
	return (frac / value * 100).toFixed(4) + '%'
}

function px(pct, value) {
	return Math.round(parseFloat(pct) * value / 100);
}

function intersectDashboardRect(r1, r2) {
	return !(r2.l > (dashboard_width - r1.r) || (dashboard_width - r2.r) < r1.l || r2.t > (dashboard_height - r1.b) || (dashboard_height - r2.b) < r1.t);
}

function intersectRect(r1, r2) {
	return !(r2.x1 > r1.x2 || r2.x2 < r1.x1 || r2.y1 > r1.y2 || r2.y2 < r1.y1);
}

// pt is {x,y}, rect is {x1,y1,x2,y2}
function ptInRect(pt, rect) {
	return pt.x > rect.x1 && pt.x < rect.x2 && pt.y > rect.y1 && pt.y < rect.y2;
}

// a & b are {x1, y1, x2, y2} rectangles.  
// Return array of rectangles made up of a minus b.
function splitRect(a, b) {

	var new_rects = [];  // TODO: Get rid of duplicate splits
	var tl = {x: a.x1, y: a.y1};
	var tr = {x: a.x2, y: a.y1};
	var br = {x: a.x2, y: a.y2};
	var bl = {x: a.x1, y: a.y2};
	
	if (!ptInRect(tl, b)) {
		if (b.y1 < a.y1) {
			new_rects.push({x1: a.x1, x2: b.x1, y1: a.y1, y2: a.y2});
		} else {
			new_rects.push({x1: a.x1, x2: a.x2, y1: a.y1, y2: b.y1});
		}
	}
	if (!ptInRect(tr, b)) {
		if (b.x2 > a.x2) {
			new_rects.push({x1: a.x1, x2: a.x2, y1: a.y1, y2: b.y1});
		} else {
			new_rects.push({x1: b.x2, x2: a.x2, y1: a.y1, y2: a.y2});
		}
	}
	if (!ptInRect(br, b)) {
		if (b.y2 > a.y2) {
			new_rects.push({x1: b.x2, x2: a.x2, y1: a.y1, y2: a.y2});
		} else {
			new_rects.push({x1: a.x1, x2: a.x2, y1: b.y2, y2: a.y2});
		}
	}
	if (!ptInRect(bl, b)) {
		if (b.x1 < a.x1) {
			new_rects.push({x1: a.x1, x2: a.x2, y1: b.y2, y2: a.y2});
		} else {
			new_rects.push({x1: a.x1, x2: b.x1, y1: a.y1, y2: a.y2});
		}
	}
	return new_rects;
}

// Convert a widget config object (as defined by widget author) into an observable array	
function configToArray(config) {
	var newConfig = [];
	for (var k in config) {
		if (config.hasOwnProperty(k)) {
			if (typeof config[k] === 'function') {
				newConfig.push({name: k, callback: config[k].bind(self)});
			} else {
				newConfig.push({
					name: k, 
					callback: function(){},  // Necessary to keep window.click from hiding menu
					children: configToArray(config[k])
				});
			}
		}
	}
	return newConfig;
}

WidgetViewModel = function(widget, id, html) {  // Global

	var self = this;
	$.extend(self, widget);
	self.id = id;
	self.htmlTemplate = html;
	
	self.deltas = {x: 0, y: 0, w: 0, h: 0};  // Track distance between user mouse drag & nearest gridline
	self.pos = {l: 0, t: 0, r: 0, b: 0};

	self.isConfiguring = ko.observable(false);  // Track if user has clicked config button
	self.isConfigurable = widget.hasOwnProperty('configMenu');  // Track if widget is configurable
	if (self.isConfigurable) {
		self.configMenu = ko.observable(configToArray(widget.configMenu));
	}
	
	self.config_click = function() {
		self.isConfiguring(!self.isConfiguring());
	};

	self.l = ko.observable();  // observed by CSS styles
	self.t = ko.observable();
	self.r = ko.observable();
	self.b = ko.observable();

	self.updateCSS = function() {  // Push internally stored pixel position out to CSS values as percentages
		self.l(pct(self.pos.l, dashboard_width));
		self.t(pct(self.pos.t, dashboard_height));
		self.r(pct(self.pos.r, dashboard_width));
		self.b(pct(self.pos.b, dashboard_height));
	};
	
	self.updatePosOnResize = function() {  // Recalculate internal pixel position after a resize event
		self.pos = {
			l : px(self.l(), dashboard_width),
			t: px(self.t(), dashboard_height),
			r: px(self.r(), dashboard_width),
			b: px(self.b(), dashboard_height)
		};
	}
	
	// Ensure widget does not overlap any other widget
	self.overlapCheck = function(new_pos, widget_list) {
		for (var i = 0; i < widget_list.length; i++) {
			if (widget_list[i] !== self && intersectDashboardRect(new_pos, widget_list[i].pos)) {
				return true;
			}
		}
		return false;
	}
	
	// Ensure widget remains entirely inside the page and respects its min & max sizing
	self.outOfBoundCheck = function(new_pos) {
		
		if (new_pos.l < 0 || new_pos.t < 0 || new_pos.r < 0 || new_pos.b < 0) {
			return true;
		}
		
		if (self.size) {
			var r = self.size;
			var w = (dashboard_width - new_pos.r) - new_pos.l;
			var h = (dashboard_height - new_pos.b) - new_pos.t;
			if ((w < (r.minWidth || 0)) || (w > (r.maxWidth || Infinity))) {
				return true;
			}
			if ((h < (r.minHeight || 0)) || (h > (r.maxHeight || Infinity))) {
				return true;
			}
		}
		return false;
	}

	// Change the position of widget's edge by dx pixels.
	// 'edge' is one of 'l', 't', 'r', 'b', 'move'.
	// returns true if move is acceptable, false otherwise
	self.moveEdge = function(widget_list, edge, dx, dy) {

		if (dx === 0 && dy === 0) {
			return true;
		}

		var new_pos;
		if (edge === 'move') {
			new_pos = {l: self.pos.l + dx, t: self.pos.t + dy, r: self.pos.r - dx, b: self.pos.b - dy};
		} else {
			new_pos = {l: self.pos.l, t: self.pos.t, r: self.pos.r, b: self.pos.b};
			new_pos[edge] += dx;
		}
		
		if (self.overlapCheck(new_pos, widget_list)) {
			return false;  // This move overlaps something - ignore it
		}
		
		if (self.outOfBoundCheck(new_pos)) {
			return false;  // Move is out of bounds, or exceeds widget min/max size - ignore it.
		}
				
		var need_update = false;
		var v = self.pos[edge];

		if (snapSize !== 0) {  // TODO: snap is broken
			self.deltas[edge] += dx;
			if (self.deltas[edge] >= snapSize) {
				need_update = true;
				self.pos[edge] = v + snapSize;
				self.deltas[edge] -= snapSize;
			} else if (self.deltas[edge] <= -1 * snapSize) {
				need_update = true;
				self.pos[edge] = v - snapSize;
				self.deltas[edge] += snapSize;
			}
		} else {
			need_update = true;
			self.pos = new_pos;
		}

		if (need_update) {
			self.updateCSS();
		}
		return true;
	};
	
	self.addToDashboard = function(layout) {
	
		if (layout.hasOwnProperty('config')) {
			self.config = layout.config;
		}
		
		if (typeof layout.l === 'string') {
			self.pos = {
				l : px(layout.l, dashboard_width),
				t: px(layout.t, dashboard_height),
				r: px(layout.r, dashboard_width),
				b: px(layout.b, dashboard_height)
			};
		} else {
			self.pos = layout;
		}
		
		if (self.outOfBoundCheck(self.pos)) {
			self.pos.r = Math.max(self.pos.r, (dashboard_width - self.pos.l - (self.size.maxWidth || 200)));
			self.pos.b = Math.max(self.pos.b, (dashboard_height - self.pos.t - (self.size.maxHeight || 100)));
		}

		self.updateCSS();
	};
};

DashboardViewModel = function(user_widget_settings) {  // Global

	if (user_widget_settings == null) {  // If user has not initialized their dashboard yet, use these as defaults.
		user_widget_settings = {
			photo_stream: {l: 10, t: 10, r: 50, b: 50},
			group_list: {l: 60, t: 10, r: 30, b: 20}
		}
	}

	var self = this;
	self.configureEnabled = ko.observable(false);
	self.user_widget_list = ko.observableArray();
	self.all_widget_list = ko.observableArray();
	self.unused_widget_list = ko.computed(function() {
		return ko.utils.arrayFilter(self.all_widget_list(), function(el){
			return self.user_widget_list.indexOf(el) < 0;
		})
	});

	var dashboard_div = document.getElementById('dashboard_container');
	function on_resize() {
		dashboard_width = dashboard_div.clientWidth;
		dashboard_height = dashboard_div.clientHeight;
		ko.utils.arrayForEach(self.user_widget_list(), function(el) {
			el.updatePosOnResize();
		});
	}
	$(window).ready(on_resize);
	$(window).resize(on_resize);
	
	self.configure = function() {
		var enable = !self.configureEnabled();
		self.configureEnabled(enable);
		dashboard_div.style.backgroundImage = enable ? "url('/static/img/dashboard_grid_50.png')" : "";
		if (!enable) {
			save_widgets();
		}
	};
	
	function save_widgets() {
		var new_layout = {};
		ko.utils.arrayForEach(self.user_widget_list(), function(el) {
			new_layout[el.id] = {l: el.l(), t: el.t(), r: el.r(), b: el.b()};
			if (el.hasOwnProperty('config')) {
				new_layout[el.id].config = el.config;
			}
		});
		$.post($SCRIPT_ROOT + '/users/updateDashboard',
			{dashboard: JSON.stringify(new_layout)},
			function(data) {
				if (data.result) {
					console.log('success');
				}
			}
		);
	}
	
	self.delete_click = function() {
		self.user_widget_list.remove(this);
	};

	self.findEmptyPosition = function(w, h) {
	
		var rect_list = [{x1: 0, y1: 0, x2: dashboard_width, y2: dashboard_height}];
		var secondary_list = [];
		var wl = self.user_widget_list();
		
		for (var i = 0; i < wl.length; i++) {
		
			var pos = wl[i].pos;
			var widget_rect = {x1: pos.l, y1: pos.t, x2: dashboard_width - pos.r, y2: dashboard_height - pos.b};
			
			for (var j = 0; j < rect_list.length; j++) {
			
				if (intersectRect(widget_rect, rect_list[j])) {
					var new_spaces = splitRect(rect_list[j], widget_rect);
					secondary_list = secondary_list.concat(new_spaces);					
				} else {
					secondary_list.push(rect_list[j]);
				}
			}
			
			rect_list = secondary_list;
			secondary_list = [];
		}
		
		// Find smallest rect that still fits widget
		var best;
		for (var i = 0; i < rect_list.length; i++) {
			var r = rect_list[i];
			var rw = r.x2 - r.x1, rh = r.y2 - r.y1;
			if (w < rw && h < rh) {
				if (best) {  // If we already have a nice fit, see if this rect fits better (compare by area)
					if (rw * rh < best.area) {
						best = r;
						best.area = rw * rh;
					}
				} else {
					best = r;
					best.area = rw * rh;
				}
			}
		}
		return best;
	};
	
	self.add_widget_to_dashboard_proxy = function(widget) {  // When called from a ko bind, passes extra bad arguments
		var w = (widget.size && widget.size.minWidth) ? widget.size.minWidth : 200;
		var h = (widget.size && widget.size.minHeight) ? widget.size.minHeight : 100;
		var l = self.findEmptyPosition(w, h);
		l = {l: l.x1 + 1, t: l.y1 + 1, r: dashboard_width - l.x2 + 1, b: dashboard_height - l.y2 + 1};
		self.add_widget_to_dashboard(widget, l);
	};
	
	self.add_widget_to_dashboard = function(widget, settings) {
		self.user_widget_list.push(widget);
		widget.addToDashboard(settings);
		widget.ready(widget.config);  // Trigger widget's initialization callback
	};
	
	function create_widget(widget, id, html) {
		var new_widget = new WidgetViewModel(widget, id, html);
		self.all_widget_list.push(new_widget);
		if (user_widget_settings[id] != null) {
			self.add_widget_to_dashboard(new_widget, user_widget_settings[id]);
		}
	}

	// Create each widget in user's dashboard
	var path = '/static/widgets/';
	for (var i = 0; i < available_widget_names.length; i++) {
	
		var widget_name = available_widget_names[i];

		$('<link/>', {
			rel: 'stylesheet/less',
			type: 'text/css',
			type: 'text/css',
			href: path + widget_name + '.less',
		}).prependTo('head');
		
		$.getScript(path + widget_name + '.js')  // Load each widget's JS
			.done((function() {
				var id = this;
				var widget = WidgetList[id]();
				$.get(path + widget.template, function(html) {  // Load each widget's HTML template
					create_widget(widget, id, html);
				});
			}).bind(widget_name))
			.fail((function(xhr, settings, e) {
				if (e instanceof SyntaxError) {
					console.log('  !! Syntax Error in JS code for Widget "{0}" ({1})'.format(this, e.message));
				}
			}).bind(widget_name));
			
		$.getScript('/static/js/less-1.7.0.js')
			.fail(function(xhr, settings, e) {
				if (e instanceof SyntaxError) {
					console.log('  !! Syntax Error in JS code for Widget "{0}" ({1})'.format(this, e.message));
				}
			});
	}
	
	// Build list of widget edges and widgets that the mouse is currently over
	function findEdge(evt) {
		evt.target.style.cursor = 'default';
		var mx = evt.offsetX, my = evt.offsetY;
		var edges = [];
		var wl = self.user_widget_list();
		for (var i = 0; i < wl.length; i++) {
			var widget = wl[i];
			var pos = widget.pos;
			var l = pos.l, t = pos.t;
			var r = dashboard_width - pos.r, b = dashboard_height - pos.b;
//			console.log('l: ' + l + ', r: ' + r + ', t: ' + t + ', b: ' + b + ', mx: ' + mx + ', my: ' + my);

			if (my >= t && my <= b) {
				if (Math.abs(mx - l) < 5) {  // left
					evt.target.style.cursor = 'e-resize';
					edges.push({side: 'l', widget: widget});
				} else if (Math.abs(mx - r) < 5) {  // right
					evt.target.style.cursor = 'e-resize';
					edges.push({side: 'r', widget: widget});
				} else if (mx >= l && mx <= r) {
					evt.target.style.cursor = 'move';
					return [{side: 'move', widget: widget}];  //  Can move only one widget at a time
				}
			}
			if (mx >= l && mx <= r) {
				if (Math.abs(my - t) < 5) {  // top
					evt.target.style.cursor = 'n-resize';
					edges.push({side: 't', widget: widget});
				} else if (Math.abs(my - b) < 5) {  // bottom
					evt.target.style.cursor = 'n-resize';
					edges.push({side: 'b', widget: widget});
				}
			}
		}
		return edges;
	}
	
	function drag(hoveredEdges, dx, dy) {
		var wl = self.user_widget_list();
		for (var i = 0; i < hoveredEdges.length; i++) {
			var widget = hoveredEdges[i].widget;
			switch (hoveredEdges[i].side) {
				case 'l':
					widget.moveEdge(wl, 'l', dx);
					break;
				case 'r':
					widget.moveEdge(wl, 'r', -dx);
					break;
				case 't':
					widget.moveEdge(wl, 't', dy);
					break;
				case 'b':
					widget.moveEdge(wl, 'b', -dy);
					break;
				case 'move':
					widget.moveEdge(wl, 'move', dx, dy);
					break;
			}
		}
	}
	
	var hoveredEdges, mouseDown = false;
	var lastMouseX = 0, lastMouseY = 0;
	var eventer = document.getElementById('dashboard_eventer');

	eventer.addEventListener('mousemove', function(evt) {
		evt.preventDefault();
		var mx = evt.offsetX, my = evt.offsetY;
		var dx = mx - lastMouseX;
		var dy = my - lastMouseY;

		lastMouseX = mx;
		lastMouseY = my;
		
		if (mouseDown && hoveredEdges) {
			drag(hoveredEdges, dx, dy);
		} else {
			hoveredEdges = findEdge(evt);
		}
	});
	
	eventer.addEventListener('mousedown', function(evt) {
		evt.preventDefault();
		mouseDown = true;
	});

	function endInteraction(evt) {
		evt.preventDefault();
		mouseDown = false;
		hoveredEdges = undefined;
		ko.utils.arrayForEach(self.user_widget_list(), function(el) {
			el.deltas = {x: 0, y: 0, w: 0, h: 0};
		});
	}

	eventer.addEventListener('mouseup', endInteraction);
	eventer.addEventListener('mouseout', endInteraction);
	
	function endWidgetConfig(evt) {
		console.log('click');
		ko.utils.arrayForEach(self.user_widget_list(), function(el) {
			el.isConfiguring(false);
		});
	}
	
	window.addEventListener('click', endWidgetConfig);
	
	$(window).on('beforeunload', function() {
		if (self.configureEnabled()) {
			return 'Do you want to leave with unsaved Dashboard changes?';
		}
	});
};

})();
