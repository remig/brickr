WidgetList.group_list = function() {

	var viewModel = {bar: "SCORE!!!"};

	function ready() {
		var self = this;
		console.log('Successfully Initialized Group List Widget');

		$.get('/api/u/1/groups/')
			.done(function(data) {
				var el = document.getElementById('group_list');
				ko.applyBindings(data, el);
			});
	}
	
	return {
		name: 'Group List',
		template: 'group_list.html',
		ready: ready,
		size: {
			minWidth: 100,
			minHeight: 50,
			maxHeight: 150,
			maxWidth: 300
		},
		config: {
		}
	};
};
