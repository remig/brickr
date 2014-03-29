function PhotoViewModel(photo) {

	var self = this;
	self.baseURL = $SCRIPT_ROOT + '/photos/';
	photo.prev_photo_url = photo.prev_photo_id == null ? null : self.baseURL + photo.user_url + '/' + photo.prev_photo_id;
	photo.next_photo_url = photo.next_photo_id == null ? null : self.baseURL + photo.user_url + '/' + photo.next_photo_id;

	self.photo = photo;
	self.title = ko.observable(photo.title);
	self.description = ko.observable(photo.description);
	self.favorite = ko.observable(photo.favorite);
	self.favorites = ko.observableArray(photo.favorites);
	self.comments = ko.observableArray(photo.comments);
	self.newComment = ko.observable('');
	self.tags = ko.observableArray(photo.tags);
	self.groups = ko.observableArray(photo.groups);
	self.isEditing = ko.observable(false);

	self.favoriteNameList = function(markup) {
		var maxNames = 4;  // Display up to this many user names before appending 'and x others'
		var lineEnd = ' favorited this photo.'
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

	self.addComment = function() {
		var comment = self.newComment();
		$.post(self.baseURL + 'addComment',
			{photoID: self.photo.id, comment: comment},
			function(data) {
				if (data.result && data.comment) {
					self.comments.push(JSON.parse(data.comment));
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

	self.edit = function() {
		self.isEditing(!self.isEditing());
	}

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
	}

	self.cancelEdit = function() {
		self.title(self.photo.title);
		self.description(self.photo.description);
		self.edit();
	}
}
