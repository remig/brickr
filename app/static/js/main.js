function PhotoViewModel(photo) {

	var self = this;
	self.baseURL = $SCRIPT_ROOT + '/photos/';
	self.photo = photo;
	self.favorite = ko.observable(photo.favorite);
	
	self.tags = ko.observableArray(photo.tagList.map(function(el){return {desc: el};}));
	
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

function addContact(userID, username) {
	$.ajax($SCRIPT_ROOT + '/users/_addContact/', {
		data: {userID: userID},
		type: 'POST',
		success: function(data) {
			if (data.result) {
				$('span#add_contact').css('visibility', 'hidden');
				$('span#remove_contact').css('visibility', '');
			}
		}
	});
	return false;
}

function removeContact(userID, username) {
	$.ajax($SCRIPT_ROOT + '/users/_removeContact/', {
		data: {userID: userID},
		type: 'POST',
		success: function(data) {
			if (data.result) {
				$('span#add_contact').css('visibility', '');
				$('span#remove_contact').css('visibility', 'hidden');
			}
		}
	});
	return false;
}

function leaveOrJoinGroup(action, groupName, groupID, userID) {
	if (confirm('Do you really want to ' + action + ' the group "' + groupName + '"?')) {
		$.post($SCRIPT_ROOT + '/groups/_leaveOrJoinGroup/', 
			{userID: userID, groupID: groupID, action: action},
			function(data) {
				if (data.result) {
					window.location.reload();  // fuck me that's nasty; need better way to refresh member list and 'join / abandon' link
				} else {
					alert('Something went terribly wrong in the group ' + action + ' process...')
				}
			}
		);
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

function importFromFlickr() {
	$('.activity-indicator').show();
    var photoID = $('#flickr-photo-id').val();
    $.post($SCRIPT_ROOT + '/photos/_importFromFlickr/',
        {photoID: photoID},
        function(data) {
			$('.activity-indicator').hide();
            if (data.result) {
				document.location = data.url;
			} else {
                alert(data.error || 'Failed to Import Flickr photo.  Gremlins in the tubes.');
            }
        }
    );
}
