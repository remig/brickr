function addFavorite(photoID) {
	$.ajax($SCRIPT_ROOT + '/photos/_addFavorite/', {
		data: {photoID: photoID},
		type: 'POST',
		success: function(data) {
			alert(data.result);
		}
	});
	return false;
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

function tagKeyPress(el, e, photoID) {
	if (e.charCode !== 13) {
		return;
	}
	$.post($SCRIPT_ROOT + '/photos/_addTag/', 
		{photoID: photoID, tag: el.value},
		function(data) {
			if (data.result && data.tags) {
				for (var i = 0; i < data.tags.length; i++) {
					$('ul#tagList').append('<li><a href="">' + data.tags[i] + '</a></li>');
				}
				el.value = '';
			} else {
				console.log('Add tag failed because I suck');
			}
		}
	);
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
    
    function pushToServer(title, desc) {
        $.post($SCRIPT_ROOT + '/photos/_updatePhoto/',
            {
                photoID: window.__photoID,
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
            pushToServer(title, desc);
            $('.single-photo-title').text(title);
            $('.single-photo-desc').text(desc);
        }
        toggleUI(false);
    }
}
