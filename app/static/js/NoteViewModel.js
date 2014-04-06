/*global $: false, ko: false, $SCRIPT_ROOT: false, NoteViewModel: true */

// TODO: create a new note then try moving it.  It resizes instead.
// TOOD: resize existing notes
// TODO: bounds check on note creation, move & resize

(function() {

var current_user;   // user currently viewing the page with these notes
var photo_id;  // ID of the photo being viewed
var img_w, img_h;
var edit_note, hovered_note;
var is_creating_note = false;

// Bind this to an {x, y, w, h} style object
// Converts between 0..100% relative coordinate space into absolute image coordinate space
ko.bindingHandlers.cssPosition = {
	update: function(element, valueAccessor) {
		var pos = ko.unwrap(valueAccessor());  // This is required outside the 'if' for updates to occur
		if (img_w != null && img_h != null && pos != null) {
			element.style.left = (img_w * pos.x / 100) + 'px';
			element.style.top = (img_h * pos.y / 100) + 'px';
			element.style.width = (img_w * pos.w / 100) + 'px';
			element.style.height = (img_h * pos.h / 100) + 'px';
		}
	}
};

var SingleNoteViewModel = function(note) {
	var self = this;
	
	// Track this note's current position
	self.pos = {x : note.x, y: note.y, w: note.w, h: note.h};
	self.original_pos = {x : note.x, y: note.y, w: note.w, h: note.h};  // Needed to cancel a move
	self.css_pos = ko.observable();  // Observed by the view to set element's position & size via CSS
	
	self.id = note.id;
	self.element_id = 'note_' + note.id;
	self.comment = ko.observable(note.comment);
	self.original_comment = note.comment;  // Needed to cancel a text edit
	self.user = note.user;
	
	self.contentTop = ko.observable();  // Track where the top of note text & UI should be positioned
	self.is_hovered = ko.observable(false);  // Track if user has hovered above this note
	self.is_editing = ko.observable(false);  // Track if user has begun editing this note
	
	self.resize = function() {  // Update the position of any bound elements
		self.css_pos(self.pos);
		self.contentTop((img_h * self.pos.h / 100) + 'px');
	};
	
    self.mouseOver = function() {  // Mouse moved into a note box
		if (edit_note && edit_note !== self) {
			return;  // If we're already editing some note, do not change hover state of other notes
		}
		hovered_note = self;
		self.is_hovered(true);
		if (self.user.id === current_user.id) {
			$('#' + self.element_id).addClass('moveable');
		}
    };
    
    self.mouseOut = function() {  // Mouse moved out of a note box
		if (edit_note) {
			return;  // If we're already editing some note, do not change hover state of other notes
		}
		hovered_note = null;
		self.is_hovered(false);
		if (self.user.id === current_user.id) {
			$('#' + self.element_id).removeClass('moveable');
		}
    };

    self.beginEdit = function() {
		self.mouseOver();
		self.is_editing(true);
        edit_note = self;
    };
	
	self.endEdit = function(doSave, doDelete) {
        if (doSave) {
			$.extend(self.original_pos, self.pos);
			self.original_comment = self.comment();
        } else {
			$.extend(self.pos, self.original_pos);
			self.resize();
			self.comment(self.original_comment);
		}
		if (doSave || doDelete) {
			self.pushNoteToServer(doDelete);
		}

		self.is_editing(false);
		is_creating_note = false;
        edit_note = hovered_note = null;
    };
	
	self.move = function(dx, dy) {
		self.pos.x += dx / img_w * 100;
		self.pos.y += dy / img_h * 100;
		self.resize();
	};
	
	self.drag_resize = function(dx, dy) {
		dx = dx / img_w * 100;
		dy = dy / img_h * 100;
		if (dx < 0) {
			self.pos.x = self.original_pos.x + dx;
			self.pos.w = self.original_pos.w - dx;
		} else {
			self.pos.w = self.original_pos.w + dx;
		}
		if (dy < 0) {
			self.pos.y = self.original_pos.y + dy;
			self.pos.h = self.original_pos.h - dy;
		} else {
			self.pos.h = self.original_pos.h + dy;
		}
		self.resize();
	};
	
	self.pushNoteToServer = function(doDelete) {

		$.post($SCRIPT_ROOT + '/photos/_updateNote/',
			{
				photoID: photo_id,
				noteID: self.id,
				note_text: self.comment(),
				doDelete: doDelete,
				x: self.pos.x, y: self.pos.y, w: self.pos.w, h: self.pos.h
			},
			function(data) {
				if (data.result) {
					self.id = data.noteID;  // Received a valid noteID from the server - store it.
				} else {
					alert('Add note failed because I suck');
				}
			}
		);
	};
};

NoteViewModel = function(note_list, pid, c_user) {

	var self = this;
    var mouse_pos;
	self.notes = ko.observableArray(note_list.map(function(el){return new SingleNoteViewModel(el);}));
	current_user = c_user;
	photo_id = pid;
    
    function mousePos(e, target) {
        return {
            x: e.pageX - target.offsetParent.offsetLeft,
            y: e.pageY - target.offsetParent.offsetTop
        };
    }
    
    function createNewNote(pos) {
		var note = {
			id: null,
			x: pos.x / img_w * 100,
			y: pos.y / img_h * 100,
			w: 0,
			h: 0,
			comment: 'New Note',
			user: current_user,
		};
		is_creating_note = true;
		edit_note = new SingleNoteViewModel(note);
		self.notes.push(edit_note);
    }
    
    function mouseDown(e) {
        if (e.target.nodeName === 'A' || e.which !== 1) {  // Ignore clicks on links & non-left button clicks
            return;
        }
        if (!edit_note || e.target.id === edit_note.element_id) {
            mouse_pos = mousePos(e, this);
        }
        if (!edit_note) {
			if (hovered_note && e.target.id === hovered_note.element_id && hovered_note.user.id === current_user.id) {  // edit existing note
				hovered_note.beginEdit();
			} else {  // create a new note
				createNewNote(mouse_pos);
			}
        }
    }

    function mouseMove(e) {
        if (mouse_pos == null || e.which !== 1 || edit_note == null) {  // Ignore mouse movements if mouse button is not down
            return;
        }

        e.preventDefault();
        var cur_pos = mousePos(e, this);
        var dx = cur_pos.x - mouse_pos.x;
        var dy = cur_pos.y - mouse_pos.y;
		
		if (is_creating_note && !edit_note.is_editing()) {  // Change size of a note that's being created now
			edit_note.drag_resize(dx, dy);
        } else if (edit_note) {
			mouse_pos.x = cur_pos.x;
			mouse_pos.y = cur_pos.y;
            edit_note.move(dx, dy);
        } 
    }
    
    function mouseUp() {
        mouse_pos = null;
        if (is_creating_note && edit_note) {
            if (edit_note.pos.w > 1000 / img_w && edit_note.pos.h > 1000 / img_h) {
                edit_note.beginEdit();
            } else {
				self.notes.remove(edit_note);  // Ignore really small notes
                edit_note = null;
            }
        }
    }
    
    function isDescendant(node, parentID) {  // Return true if node is a descendent of parent
        return $(node).parents('#' + parentID).length === 1;
    }
    
    function hoverOut(e) {
        if (isDescendant(e.relatedTarget, this.id) || this === e.relatedTarget) {
            return;  // Ignore mouse out if we moved over something still inside the event panel
        }
		e.preventDefault();
        if (is_creating_note) {
			mouseUp();
        }
    }
    
    // Set the position, width & height of each note.
    function recalcNotes() {
        var d = $('#the-actual-photo');
        img_w = d.width();
        img_h = d.height();
		self.notes().forEach(function(el){el.resize();});
		
        $('#note-eventer').css('width', img_w + 'px').css('height', img_h + 'px');  // TODO: this should *not* be here
        $('#photo-nav-holder').css('width', (img_w - 1) + 'px');
        $('#single-photo-img').css('width', (img_w + 88) + 'px');
    }
    
    $(window).resize(recalcNotes);
    $(window).load(recalcNotes);
	
	self.save_click = function() {
		if (edit_note) {
			edit_note.endEdit(true, false);
		}
	};
	
	self.cancel_click = function() {
		if (is_creating_note) {
			self.notes.remove(edit_note);
		} else if (edit_note) {
			edit_note.endEdit(false);
		}
		is_creating_note = false;
		edit_note = hovered_note = null;
	};
	
	self.delete_click = function() {
		if (is_creating_note) {
			self.cancel_click();
		} else if (edit_note && confirm('Do you really want to delete this note?')) {
			self.notes.remove(edit_note);
			edit_note.endEdit(true, true);
		}
	};

	if (current_user && current_user.id >= 0) {  // If user is logged in, enable note editing
		$(function() {
			$('#note-eventer')
				.mouseout(hoverOut)
				.mousedown(mouseDown)
				.mousemove(mouseMove)
				.mouseup(mouseUp);
		});
	}
};

}());
