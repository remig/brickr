/*global $: false, ko: false, $SCRIPT_ROOT: false, PhotoViewModel: true, NoteViewModel: false */
(function() {

// Comments come back from the server in a flat array.  Each comment has an id
// and an optional parentID.  If parentID is not null, this is a child comment.
// Remove children comments from the flat list and insert them into the
// 'children' list of the correct parent.
function nestChildComments(comment_list) {
	for (var i = 0; i < comment_list.length; i++) {
		var comment = comment_list[i];
		if (comment.parentID != null) {
			var parent = comment_list.find(function(el){return el.id === comment.parentID;});
			if (parent) {
				parent.children = parent.children || [];
				parent.children.push(comment);
			}
		}
	}

	return comment_list.filter(function(el){return el.parentID == null ? el : null});
}

PhotoViewModel = function (photo, current_user) {  // Global

	var self = this;
	self.baseURL = $SCRIPT_ROOT + '/photos/';
	photo.prev_photo_url = photo.prev_photo_id == null ? null : self.baseURL + photo.user.url + '/' + photo.prev_photo_id;
	photo.next_photo_url = photo.next_photo_id == null ? null : self.baseURL + photo.user.url + '/' + photo.next_photo_id;

	self.photo = photo;
	self.title = ko.observable(photo.title);
	self.description = ko.observable(photo.description);
	self.favorite = ko.observable(photo.favorite);
	self.favorites = ko.observableArray(photo.favorites);
	self.comments = ko.observableArray(nestChildComments(photo.comments));
	self.newComment = ko.observable('');
	self.tags = ko.observableArray(photo.tags);
	self.groups = ko.observableArray(photo.groups);
	self.noteModel = new NoteViewModel(photo.notes, photo.id, current_user);
	self.isEditing = ko.observable(false);

	self.favoriteNameList = function(markup) {
		var maxNames = 4;  // Display up to this many user names before appending 'and x others'
		var lineEnd = ' favorited this photo.';
		var favCount = self.favorites().length;
		var favNames = self.favorites().slice(0, maxNames).map(function(el){
			return markup.replace('user_url', '"' + el.user_url + '"')
				.replace('user_name', el.user_name);
		});

		if (favCount === maxNames + 1) {
			favNames.push('1 other' + lineEnd);
		} else if (favCount > maxNames) {
			favNames.push((favCount - maxNames) + ' others' + lineEnd);
		}
		
		var res = favNames.join(', ').replace(/,([^,]*)$/, ' and$1');
		
		if (favCount <= maxNames) {
			res += lineEnd;
		}

		return res;
	};

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
	};
	
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
	};
	
	self.changeFavorite = function() {
		var isFavorited = self.favorite();
		$.post(self.baseURL + (isFavorited ? 'removeFavorite' : 'addFavorite'),
			{photoID: self.photo.id},
			function(data) {
				if (data.result) {
					var fav = JSON.parse(data.favorite);
					self.favorite(!isFavorited);
					if (!isFavorited) {
						self.favorites.push(fav);
					} else {
						self.favorites.remove(self.favorites().find(function(el){return el.id === fav.id;}));
					}
				}
			}
		);
		return false;
	};

	self.addComment = function() {
		var comment = self.newComment();
		comment = comment.replace(/\n/g, '<br />');  // replace raw newlines with HTML breaks, to preserve paragraph structure
		$.post(self.baseURL + 'addComment',
			{photoID: self.photo.id, comment: comment},
			function(data) {
				if (data.result && data.comment) {
					self.comments.push(JSON.parse(data.comment));
					self.newComment('');
				}
			}
		);
	};

	self.deleteComment = function() {
		var comment = this;
		$.post(self.baseURL + 'removeComment',
			{photoID: self.photo.id, commentID: comment.id},
			function(data) {
				if (data.result) {
					self.comments.remove(comment);
				}
			}
		);
	};
	
	self.replyComment = function(args) {
		console.log(this);
	};

	self.edit = function() {
		self.isEditing(!self.isEditing());
	};

	self.saveEdit = function() {
		var title = self.title(), desc = self.description();
		if (title !== self.photo.title || desc !== self.photo.description) {
			$.post(self.baseURL + '_updatePhoto/',
				{photoID: self.photo.id, title: title, desc: desc},
				function(data) {
					if (!data.result) {
						alert('Failed to update photo title & description because of random fluctuations in the space time continuum.  Or something.');
					}
				}
			);
		}
		self.edit();
	};

	self.cancelEdit = function() {
		self.title(self.photo.title);
		self.description(self.photo.description);
		self.edit();
	};
};

})();
