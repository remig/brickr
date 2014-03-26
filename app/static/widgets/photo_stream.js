WidgetList.photo_stream = function() {

	function ready() {
		var self = this;
		console.log('Successfully Initialized Photo Stream Widget');
		
		$.get('/api/u/1/photos/?from_contacts')
			.done(function(data) {
				var el = document.getElementById('photo_stream');
				ko.applyBindings(data, el);
			});
	}
	
	return {
		name: 'Photo Stream',
		template: 'photo_stream.html',
		ready: ready
	};
};
