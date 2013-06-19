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
				$('div#contact-form').html(username + ' is a Contact. <input type="submit" value="Remove" onclick="removeContact(' + userID + ', \'' + username + '\');" id="remove-contact"></input>');
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
				$('div#contact-form').html('<input type="submit" onclick="addContact(' + userID + ', \'' + username + '\');" id="add-contact" value="Add ' + username + ' as a Contact"></input>');
			}
		}
	});
	return false;
}