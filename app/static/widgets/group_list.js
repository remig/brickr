WidgetList.group_list = function() {

	function ready(config) {
	
		if (config && config.size) {
			setSize(config.size, this);
		}

		$.get('/api/u/-1/groups/')
			.done(function(data) {
				var el = document.getElementById('group_list');
				ko.applyBindings(data, el);
			});
	}
	
	function setSize(size, widget) {
		widget.config.size = size;
		$('#group_list').removeClass().addClass('group_list_container_' + size);
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
			size: 'large'
		},
		configMenu: {
			'Thumb Size': {
				'Small': function() {setSize('small', this);},
				'Large': function() {setSize('large', this);}
			}
		}
	};
};
