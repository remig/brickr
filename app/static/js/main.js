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
