/*global $: false, ko: false, $SCRIPT_ROOT: false, PhotoViewModel: true, NoteViewModel: false */
(function() {


// TODO: outer most, permanent, comment add box has a 'Cancel' button

function makeCommentObservable(comment) {
	comment.children = ko.observableArray();
	comment.isEditing = ko.observable(false);
	comment.isExpanded = ko.observable(true);
	return comment;
}

// Comments come back from the server in a flat array.  Each comment has an id
// and an optional parentID.  If parentID is not null, this is a child comment.
// Remove children comments from the flat list and insert them into the
// 'children' list of the correct parent.
function nestChildComments(comment_list) {
	for (var i = 0; i < comment_list.length; i++) {
		var comment = makeCommentObservable(comment_list[i]);
		if (comment.parentID != null) {
			var parent = comment_list.find(function(el){return el.id === comment.parentID;});
			if (parent) {
				parent.children.push(comment);
			}
		}
	}

	return comment_list.filter(function(el){return el.parentID == null ? el : null});
}

function insertComment(comment, comment_list) {  // Insert the comment under the right parent
	if (!comment.parentID) {
		return comment_list.push(comment);
	}

	ko.utils.arrayForEach(comment_list(), function(item) {
		if (item.id === comment.parentID) {
			item.children.push(comment);
		} else {
			insertComment(comment, item.children);
		}
	});
}

function removeComment(comment, comment_list) {
	if (comment_list.indexOf(comment) >= 0) {
		comment_list.remove(comment);
		return;
	}
	ko.utils.arrayForEach(comment_list(), function(item) {
		return removeComment(comment, item.children);
	});
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
						self.tags.push(data.tags[i]);
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

	self.toggleEditMetaInfo = function() {
		self.isEditing(!self.isEditing());
	};

	self.saveMetaInfoEdit = function() {
		var title = self.title(), desc = self.description();
		if (title !== self.photo.title || desc !== self.photo.description) {
			$.post(self.baseURL + '_updatePhoto/',
				{photoID: self.photo.id, title: title, desc: desc},
				function(data) {
					if (data.result) {
						self.photo.title = self.title();
						self.photo.description = self.description();
					}
				}
			);
		}
		self.toggleEditMetaInfo();
	};

	self.cancelMetaInfoEdit = function() {
		self.title(self.photo.title);
		self.description(self.photo.description);
		self.toggleEditMetaInfo();
	};

	$('#photo-comments').on('click', '.comment-reply', function() {
		ko.contextFor(this).$data.isEditing(true);
		return false;
	});
	
	$('#photo-comments').on('click', '.comment-delete', function() {
		var comment = ko.contextFor(this).$data;
		$.post(self.baseURL + 'removeComment',
			{photoID: self.photo.id, commentID: comment.id},
			function(data) {
				if (data.result) {
					removeComment(comment, self.comments);
				}
			}
		);
		return false;
	});
	
	$('#photo-comments').on('click', '.comments-expand', function() {
		var comment = ko.contextFor(this).$data;
		comment.isExpanded(!comment.isExpanded());
	});

	$('#single-photo-info').on('click', '.comment-save', function() {
		var comment_text = self.newComment();
		comment_text = comment_text.replace(/\n/g, '<br />');  // replace raw newlines with HTML breaks, to preserve paragraph structure
		var parentID, context = ko.contextFor(this);
		if (context.$data !== self) {
			parentID = context.$data.id;
			context.$data.isEditing(false);
		}
		$.post(self.baseURL + 'addComment',
			{photoID: self.photo.id, comment: comment_text, parentID: parentID},
			function(data) {
				if (data.result && data.comment) {
					var newComment = makeCommentObservable(JSON.parse(data.comment));
					insertComment(newComment, self.comments);
					self.newComment('');
				}
			}
		);
	});
	
	$('#single-photo-info').on('click', '.comment-cancel', function() {
		ko.contextFor(this).$data.isEditing(false);
		return false;
	});
};

})();
