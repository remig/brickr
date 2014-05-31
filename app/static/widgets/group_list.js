WidgetList.group_list = function() {

	function ready() {
		var self = this;

		$.get('/api/u/-1/groups/')
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
		},
		config: {
			'Thumb Size': {
				'Small': function() {console.log('small');},
				'Medium': function() {console.log('med');},
				'Large': function() {console.log('large');}
			}
		}
	};
};
