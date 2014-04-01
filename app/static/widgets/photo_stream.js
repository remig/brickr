WidgetList.photo_stream = function() {

	function ready() {
		var self = this;
		
		$.get('/api/u/1/photos/?from_contacts&count=20')
			.done(function(data) {
				var el = document.getElementById('photo_stream');
				ko.applyBindings(data, el);
				
				$('.stream_container-photo').mouseover(
					function() {$('.stream_container-user-info', this).show();}
				).mouseout(
					function() {$('.stream_container-user-info', this).hide();}
				);
			});
	}
	
	return {
		name: 'Photo Stream',
		template: 'photo_stream.html',
		ready: ready,
		config: {
		}
	};
};
