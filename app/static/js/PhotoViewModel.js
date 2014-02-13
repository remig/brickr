function PhotoViewModel(photo) {

	var self = this;
	self.baseURL = $SCRIPT_ROOT + '/photos/';
	self.photo = photo;
	self.favorite = ko.observable(photo.favorite);
	
	self.tags = ko.observableArray(photo.tags);
	
	self.addTag = function(model, event) {
		if (event.charCode !== 13 || !event.target.value) {
			return true;
		}
		$.post(self.baseURL + 'addTags',
			{photoID: self.photo.id, tag: event.target.value},
			function(data) {
				if (data.result && data.tags) {
					for (var i = 0; i < data.tags.length; i++) {
						self.tags.push({desc: data.tags[i]});
					}
					event.target.value = '';
				}
			}
		);
		return false;
	}
	
	self.removeTag = function() {
		var tag = this;
		$.post(self.baseURL + 'removeTag',
			{photoID: self.photo.id, tag: tag.desc},
			function(data) {
				if (data.result) {
					self.tags.remove(tag);
				}
			}
		);
		return false;
	}
	
	self.changeFavorite = function() {
		
		var isFavorited = self.favorite();
		$.post(self.baseURL + (isFavorited ? 'removeFavorite' : 'addFavorite'),
			{photoID: self.photo.id},
			function(data) {
				if (data.result) {
					self.favorite(!isFavorited);
				}
			}
		);
		return false;
	}
}

function editPhotoInfo(showUI, photoID) {

    function toggleUI(show) {
        if (show) {
            $('.single-photo-title-edit').val($('.single-photo-title').text());
            $('.single-photo-desc-edit').val($('.single-photo-desc').text());
            $('.photo-display-info').hide();
            $('.photo-edit-info').show();
        } else {
            $('.photo-display-info').show();
            $('.photo-edit-info').hide();
        }
    }
    
    function pushToServer(title, desc, photoID) {
        $.post($SCRIPT_ROOT + '/photos/_updatePhoto/',
            {
                photoID: photoID,
                title: title,
                desc: desc
            },
            function(data) {
                if (!data.result) {
                    alert('Failed to update photo title & description because of random fluctuations in the space time continuum.  Or something.');
                }
            }
        );
    }
    
    if (showUI) {
        toggleUI(true);
    } else {  // User clicked 'Save' or 'Cancel'
        if (photoID > 0) {
            var title = $('.single-photo-title-edit').val() || $('.single-photo-title').text();
            var desc = $('.single-photo-desc-edit').val() || $('.single-photo-desc').text();
            pushToServer(title, desc, photoID);
            $('.single-photo-title').text(title);
            $('.single-photo-desc').text(desc);
        }
        toggleUI(false);
    }
}
