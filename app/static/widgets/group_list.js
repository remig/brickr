WidgetList.group_list = function() {

	var viewModel = {bar: "SCORE!!!"};

	function ready() {
		var self = this;

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
			minWidth: 200,
			minHeight: 50
		}
	};
};
