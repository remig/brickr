/*global ko: false, $: false, WidgetList: false, WidgetViewModel: false, DashboardViewModel: false, $SCRIPT_ROOT: false */
(function() {

WidgetList = {};  // Global list used by each widget to register itself

var available_widget_names = [  // Official list of all avaialble widgets
	'explore',
	'photo_stream',
	'group_list'
];

var snapSize = 50;
var dashboard_width, dashboard_height;

// data-bind="stopBinding: true" 
ko.bindingHandlers.stopBinding = {
	init: function() {
		return { controlsDescendantBindings: true };
	}
};

WidgetViewModel = function(widget, id, layout, html) {  // Global

	var self = this;
	$.extend(self, widget);
	self.id = id;
	self.htmlTemplate = html;
	self.isConfigurable = widget.hasOwnProperty('config');
	
	self.config_click = function() {
		var widget = this;
		console.log('Configuring this widget is NYI: ' + widget);
	};
	
	function minMax(min, max, v) {
		return Math.min(max, Math.max(min, v));
	}
	
	// Ensure widget remains entirely inside the page, and respects its min & max sizing
	self.boundCheck = function() {
		var pos = self.pos;
		var w = dashboard_width - pos.w;
		var h = dashboard_height - pos.h;
		var max_w = w - ((w % snapSize) || 0);
		var max_h = h - ((h % snapSize) || 0);
		pos.x = minMax(0, max_w, pos.x);
		pos.y = minMax(0, max_h, pos.y);
		if (self.size) {
			var r = self.size;
			pos.w = minMax(r.minWidth || 0, r.maxWidth || Infinity, pos.w);
			pos.h = minMax(r.minHeight || 0, r.maxHeight || Infinity, pos.h);
		}
	};
	
	self.updateCSS = function() {
		self.x(self.pos.x + 'px');
		self.y(self.pos.y + 'px');
		self.w(self.pos.w + 'px');
		self.h(self.pos.h + 'px');
	};
	
	// Change the position of the widget's edge by dt pixels.
	// 'edge' is one of 'x', 'y', 'w', 'h'.
	self.moveEdge = function(edge, dt) {

		if (dt === 0) {
			return;
		}

		var need_update = false;
		var v = self.pos[edge];

		if (snapSize !== 0) {
			self.deltas[edge] += dt;
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
			self.pos[edge] = v + dt;
		}

		if (need_update) {
			self.boundCheck();
			self.updateCSS();
		}
	};
	
	layout = layout || {x: 0, y: 0, w: 100, h: 100};
	self.pos = {x : layout.x, y: layout.y, w: layout.w, h: layout.h};
	self.deltas = {x: 0, y: 0, w: 0, h: 0};  // Track distance between user mouse drag & nearest gridline
	self.boundCheck();

	self.x = ko.observable(self.pos.x + 'px');  // observed by CSS styles
	self.y = ko.observable(self.pos.y + 'px');
	self.w = ko.observable(self.pos.w + 'px');
	self.h = ko.observable(self.pos.h + 'px');
};

DashboardViewModel = function (user_widgets) {  // Global

	if (user_widgets == null) {  // If user has not initialized their dashboard yet, use these as defaults.
		user_widgets = {
			photo_stream: {x: 50, y: 50, w: 300, h: 500},
			group_list: {x: 400, y: 50, w: 350, h: 200}
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
			new_layout[el.id] = el.pos;
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

	self.add_widget_to_dashboard = function(widget) {
		self.user_widget_list.push(widget);
		widget.ready();  // Trigger widget's initialization callback
	};
	
	function create_widget(widget, id, html) {
		var new_widget = new WidgetViewModel(widget, id, user_widgets[id], html);
		self.all_widget_list.push(new_widget);
		if (user_widgets[id] != null) {
			self.add_widget_to_dashboard(new_widget);
		}
	}

	// Create each widget in user's dashboard
	var path = '/static/widgets/';
	for (var i = 0; i < available_widget_names.length; i++) {
	
		var widget_name = available_widget_names[i];

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
	}
	
	// Build list of widget edges and widgets that the mouse is currently over
	function findEdge(evt) {
		evt.target.style.cursor = 'default';
		var mx = evt.offsetX, my = evt.offsetY;
		var edges = [];
		for (var i = 0; i < self.user_widget_list().length; i++) {
			var widget = self.user_widget_list()[i];
			var pos = widget.pos;
			var x = pos.x, y = pos.y;
			var w = pos.w, h = pos.h;

			if (my >= y && my <= y + h) {
				if (Math.abs(mx - x) < 5) {  // left
					evt.target.style.cursor = 'e-resize';
					edges.push({side: 'left', widget: widget});
				} else if (Math.abs(mx - x - w) < 5) {  // right
					evt.target.style.cursor = 'e-resize';
					edges.push({side: 'right', widget: widget});
				} else if (mx >= x && mx <= x + w) {
					evt.target.style.cursor = 'move';
					return [{side: 'move', widget: widget}];  //  Can move only one widget at a time
				}
			}
			if (mx >= x && mx <= x + w) {
				if (Math.abs(my - y) < 5) {  // top
					evt.target.style.cursor = 'n-resize';
					edges.push({side: 'top', widget: widget});
				} else if (Math.abs(my - y - h) < 5) {  // bottom
					evt.target.style.cursor = 'n-resize';
					edges.push({side: 'bottom', widget: widget});
				}
			}
		}
		return edges;
	}
	
	function drag(hoveredEdges, dx, dy) {
		for (var i = 0; i < hoveredEdges.length; i++) {
			var widget = hoveredEdges[i].widget;
			switch (hoveredEdges[i].side) {
				case 'left':
					widget.moveEdge('x', dx);
					widget.moveEdge('w', -dx);
					break;
				case 'right':
					widget.moveEdge('w', dx);
					break;
				case 'top':
					widget.moveEdge('y', dy);
					widget.moveEdge('h', -dy);
					break;
				case 'bottom':
					widget.moveEdge('h', dy);
					break;
				case 'move':
					widget.moveEdge('x', dx);
					widget.moveEdge('y', dy);
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
};

})();
