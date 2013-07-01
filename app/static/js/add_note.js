/*global $: false, $SCRIPT_ROOT: false */

(function() {

    var img_w, img_h, note_list, mouse_pos;
    var hovered_note, edit_note, newest_note;
    var is_editing = false;
    
    function mousePos(e, target) {
        return {
            x: e.pageX - target.offsetLeft,
            y: e.pageY - target.offsetTop
        };
    }
    
    function cssProp(note, p, s) {
        return Math.round(parseInt(note.css(p), 10) / s * 100);
    }
    
    function getNoteCoords(note) {
        return [
            cssProp(note, 'left', img_w),
            cssProp(note, 'top', img_h),
            cssProp(note, 'width', img_w),
            cssProp(note, 'height', img_h)
        ];
    }

    function beginNoteEdit(note_box) {
        is_editing = true;
        var n = note_box[0];
        n.dataset.originalLeft = n.dataset.currentLeft = n.style.left;  // cache current coords so we can restore them if edit is aborted
        n.dataset.originalTop = n.dataset.currentTop = n.style.top;
        edit_note = note_box;
        edit_note.find('.note-text').show();
        edit_note.find('.note-buttons').show();
        positionNoteContent(edit_note);
    }
    
    function endNoteEdit(doSave, doDelete) {
        if (edit_note == null) {
            return;  // Can't end an edit that doesn't exist
        }
        if (doSave || doDelete) {
            pushNoteToServer(edit_note, doDelete);
        }
        edit_note.find('.note-text').hide();
        edit_note.find('.note-buttons').hide();
        positionNoteContent(edit_note);

        edit_note[0].dataset.brickrCoords = getNoteCoords(edit_note).join('_');

        is_editing = false;
        edit_note = newest_note = hovered_note = null;
    }
    
    function pushNoteToServer(note, doDelete) {

        var coords = getNoteCoords(note);

        $.post($SCRIPT_ROOT + '/photos/_updateNote/',
            {
                photoID: window.__photoID,  // TODO: Need a clean way to pass template state into JS files without running JS through template engine
                noteID: note.attr('id') || 0,
                note_text: note.find('.note-text').text(),
                doDelete: doDelete,
                x: coords[0], y: coords[1], w: coords[2], h: coords[3]
            },
            function(data) {
                if (!data.result) {
                    alert('Add note failed because I suck');
                }
            }
        );
    }

    function moveNote(note_box, dx, dy) {
        var h = note_box.height();
        var newX = bound(parseInt(note_box[0].dataset.currentLeft, 10) + dx, 0, img_w - note_box.width());
        var newY = bound(parseInt(note_box[0].dataset.currentTop, 10) + dy, 0, img_h - h);
        note_box.css('left', newX + 'px');
        note_box.css('top', newY + 'px');
        
        positionNoteContent(note_box, h, newY);
    }

    function createNewNote() {
        var last_note = note_list.children().last();
        newest_note = last_note.clone(true, true);
        newest_note.attr('id', '0')
            .css('left', mouse_pos.x + 'px')
            .css('top', mouse_pos.y + 'px')
            .css('width', '0px')
            .css('height', '0px')
            .appendTo(note_list);  // TODO: insert this into list ordered by area
                        
        newest_note.find('.note-text').text('Your new note!');
        newest_note[0].dataset.brickrUserid = window.__userID;
        newest_note[0].dataset.brickrCoords = null;
    }
    
    function mouseDown(e) {
        e.preventDefault();
        mouse_pos = mousePos(e, this);
        if (is_editing) {
            return;  // Only trigger either existing note edit or new note creation if we haven't already
        }
        if (hovered_note && hovered_note.dataset.brickrUserid === window.__userID) {  // edit existing note
            beginNoteEdit($(hovered_note));
        } else {  // create a new note
            if (hovered_note) {
                noteOut.call(hovered_note);
            }
            createNewNote();
        }
    }

    function bound(t, min, max) {
        return Math.min(max, Math.max(min, t));
    }
    
    function mouseMove(e) {
        if (mouse_pos == null || e.which !== 1) {  // Ignore mouse movements if mouse button is not down
            return;
        }

        e.preventDefault();
        var cur_pos = mousePos(e, this);
        var dx = cur_pos.x - mouse_pos.x;
        var dy = cur_pos.y - mouse_pos.y;

        if (is_editing && hovered_note != null && edit_note != null && edit_note[0] === hovered_note) {

            moveNote(edit_note, dx, dy);

        } else if (!is_editing) {  // Change size of a note that's being created now
            if (dx < 0) {
                newest_note.css('left', cur_pos.x + 'px').css('width', (-dx) + 'px');
            } else {
                newest_note.css('width', dx + 'px');
            }
            if (dy < 0) {
                newest_note.css('top', cur_pos.y + 'px').css('height', (-dy) + 'px');
            } else {
                newest_note.css('height', dy + 'px');
            }
        }
    }
    
    function mouseUp(e) {
        e.preventDefault();
        mouse_pos = null;
        if (!is_editing && newest_note) {
            if (newest_note.width() > 10 && newest_note.height() > 10) {
                beginNoteEdit(newest_note);
            } else {
                newest_note.remove();  // Ignore really small notes
                newest_note = null;
            }
        } else if (is_editing && edit_note) {  // End existing note move
            var n = edit_note[0];
            n.dataset.currentLeft = n.style.left;
            n.dataset.currentTop = n.style.top;
        }
    }
    
    function isDescendant(node, parentID) {  // Return true if node is a descendent of parent
        return $(node).parents('#' + parentID).length === 1;
    }
    
    function hoverIn() {  // Mouse moved over image - show notes
        note_list.show();
    }

    function hoverOut(e) {  // Mouse moved off image - hide notes
        if (isDescendant(e.target, this.id) || isDescendant(e.relatedTarget, this.id)) {
            return;  // Ignore mouse out if we moved over something still inside the event panel
        }
        if (!is_editing) {  // Don't hide anything if we're in edit mode
            note_list.hide();
            mouse_pos = null;
        }
    }

    function noteIn() {  // Mouse moved into a note box.  If we're not in note edit mode, highlight hovered note box and show its note text
        if (newest_note != null) {
            return;  // Only trigger note hover if we're not busy creating a new note
        }
        hovered_note = this;
        if (!is_editing) {
            $(this).css('border', '2px solid white');
            $(this).find('.note-text').show();
            if (this.dataset.brickrUserid === window.__userID) {
                $(this).css('cursor', 'move');
            }
        }
    }
    
    function noteOut() {  // Mouse moved out of a note box
        if (!is_editing && hovered_note != null) {
            $(this).css('border', '1px dashed white');
            $(this).find('.note-text').hide();
        }
        hovered_note = null;
    }
    
    // Position note content (text & edit buttons) below note box.
    // If note content doesn't fit below note, put it above
    function positionNoteContent(note_box, note_box_height, note_box_top) {
    
        var note_content = note_box.children('.note-content');
        note_box_height = note_box_height || note_box.height();
        note_box_top = note_box_top || parseInt(note_box.css('top'), 10);
        
        if (img_h - note_box_top - note_box_height < note_content.height()) {
            note_content.css('top', (0 - note_content.height()) + 'px');
        } else {
            note_content.css('top', note_box_height + 'px');
        }
    }
    
    // Set the position, width & height of each note, based on its brickrCoord attribute (an 'x_y_w_h' style string).
    function recalcNotes() {
        var d = $('#the-actual-photo');
        img_w = d.width();
        img_h = d.height();
        $('#note-eventer').css('width', img_w + 'px').css('height', img_h + 'px');
        $('.note-box').each(function(i, v) {
            var coords = v.dataset.brickrCoords.split('_').map(function(el){return parseInt(el, 10) / 100;});
            var l = img_w * coords[0];
            var t = img_h * coords[1];
            var w = img_w * coords[2];
            var h = img_h * coords[3];

            v = $(v);
            v.css('left', l + 'px').css('top', t + 'px')
                .css('width', w + 'px').css('height', h + 'px');
            
            positionNoteContent(v, h, t);
        });
    }
    
    $(window).resize(recalcNotes);

    $(window).load(function() {  // Need this show / hide trickery because everything starts out invisible, which means a lot of height=0 problems
        var notes = $('.note-text');
        note_list.show();
        notes.show();
        recalcNotes();
        notes.hide();
        note_list.hide();
    });
    
    $(function() {

        note_list = $('#note-list').data('userID', 7);

        $('#note-eventer')
            .mouseover(hoverIn)
            .mouseout(hoverOut)
            .mousedown(mouseDown)
            .mousemove(mouseMove)
            .mouseup(mouseUp);

        $('.note-box').mouseover(noteIn).mouseout(noteOut);
        
        $('.save-button').click(function() {
            endNoteEdit(true);  // TODO: need to populate note ID, so that create -> save -> move -> save works
        });
        
        $('.cancel-button').click(function() {
            if (newest_note) {
                newest_note.remove();  // Cancel new note creation
                endNoteEdit(false);
            } else {
                var d = edit_note[0].dataset;  // Move note back to its original spot
                edit_note.css('left', d.originalLeft);
                edit_note.css('top', d.originalTop);
                endNoteEdit(false);
            }
        });
        
        $('.delete-button').click(function() {
            if (newest_note) {
                newest_note.remove();  // Cancel new note creation
                endNoteEdit(false);
            } else if (confirm('Do you really want to delete this note?')) {
                endNoteEdit(true, true);
                $(this).parents('.note-box').remove();
            }
        });
    });
}());
