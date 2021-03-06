WidgetList.explore = function() {

	function ready() {
		var self = this;
		
		$.get('/api/u/1/photos/')
			.done(function(data) {
				var el = document.getElementById('explore_container');
				ko.applyBindings(data, el);
			});
	}
	
	return {
		name: 'Explore',
		template: 'explore.html',
		size: {
			minWidth: 300,
			minHeight: 100,
			maxHeight: 500,
			maxWidth: 400
		},
		ready: ready
	};
};
