(function() {

    var img_w, img_h, note_list, latest_note, mouse_pos, over_owner_note = false;
    
    function mousePos(e, target) {
        return {
            x: e.pageX - target.offsetLeft,
            y: e.pageY - target.offsetTop
        }
    }
    
    function mouseDown(e) {
        e.preventDefault();
        mouse_pos = mousePos(e, this);
        if (over_owner_note) {
            e.target.originalLeft = parseInt(e.target.style.left);
            e.target.originalTop = parseInt(e.target.style.top);
            latest_note = $(e.target);
        } else {
            latest_note = $('<div/>', {
                class: 'note-box',
                css: {
                    left: mouse_pos.x + 'px',
                    top: mouse_pos.y + 'px'
                }
            }).appendTo(note_list);
        }
    }

    function bound(t, min, max) {
        return Math.min(max, Math.max(min, t));
    }

    function mouseMove(e) {
        if (mouse_pos == null || latest_note == null) {
            return;
        }
        e.preventDefault();
        cur_pos = mousePos(e, this);
        var dx = cur_pos.x - mouse_pos.x;
        var dy = cur_pos.y - mouse_pos.y;
        if (over_owner_note) {  // Move an existing note
            var newX = bound(latest_note[0].originalLeft + dx, 0, img_w - latest_note.width());
            var newY = bound(latest_note[0].originalTop + dy, 0, img_h - latest_note.height());
            latest_note.css('left', newX + 'px');
            latest_note.css('top', newY + 'px');
        } else {  // Change size of a note that's being created now
            if (dx < 0) {
                latest_note.css('left', cur_pos.x + 'px').css('width', (-dx) + 'px');
            } else {
                latest_note.css('width', dx + 'px')
            }
            if (dy < 0) {
                latest_note.css('top', cur_pos.y + 'px').css('height', (-dy) + 'px');
            } else {
                latest_note.css('height', dy + 'px');
            }
        }
    }
    
    function cssProp(p, s) {
        return Math.round(parseInt(latest_note.css(p)) / s * 100);
    }

    function mouseUp(e) {
        e.preventDefault();
        mouse_pos = null;
        if (over_owner_note) {
        } else {
            var x = cssProp('left', img_w);
            var y = cssProp('top', img_h);
            var w = cssProp('width', img_w);
            var h = cssProp('height', img_h);
            if (w > 3 && h > 3) {
                latest_note[0].id = ['note', x, y, w, h].join('_');
                latest_note[0].title = latest_note[0].id;
                pushNoteToServer(x, y, w, h);
            } else {
                latest_note.remove();  // Ignore really small notes
            }
        }
    }
    
    function pushNoteToServer(x, y, w, h) {
        $.post($SCRIPT_ROOT + '/photos/_addNote/', 
            {
                photoID: window.__photoID,  // TODO: Need a clean way to pass template state into JS files without running all JS through template engine
                x: x, y: y, w: w, h: h
            },
            function(data) {
                if (data.result) {
                } else {
                    console.log('Add note failed because I suck');
                }
            }
        );
    }

    function isDescendant(node, parentID) {  // Return true if node is a descendent of parent
        return $(node).parents('#' + parentID).length == 1;
    }
    
    function hoverIn(e) {
        if (isDescendant(e.target, this.id) || isDescendant(e.relatedTarget, this.id)) {
            return;
        }

        note_list.show();
    }

    function hoverOut(e) {
        if (isDescendant(e.target, this.id) || isDescendant(e.relatedTarget, this.id)) {
            return;
        }

        note_list.hide();
        mouse_pos = null;
    }

    function noteIn(e) {
        if (mouse_pos == null && this.dataset.brickrUserid === window.__userID) {
            this.style.cursor = 'move';
            over_owner_note = true;
        } else {
            //console.log('set up some kind of tooltip here...');
        }
    }
    
    function noteOut(e) {
        over_owner_note = false;
        //console.log('... and hide tooltip here');
    }

    function recalcNotes() {
        var d = $('#the-actual-photo');
        img_w = d.width();
        img_h = d.height();
        $('#note-eventer').css('width', img_w + 'px').css('height', img_h + 'px');
        $('.note-box').each(function(i, v) {
            var coords = v.dataset.brickrCoords.split('_').map(function(el){return parseInt(el) / 100;});
            v = $(v);
            v.css('left',   (img_w * coords[0]) + 'px');
            v.css('top',    (img_h * coords[1]) + 'px');
            v.css('width',  (img_w * coords[2]) + 'px');
            v.css('height', (img_h * coords[3]) + 'px');
        })
    }
    
    $(window).load(recalcNotes);
    $(window).resize(recalcNotes);
    
    $(function() {
        note_list = $('#note-list').data('userID', 7);
        $('#note-eventer')
            .mouseover(hoverIn)
            .mouseout(hoverOut)
            .mousedown(mouseDown)
            .mousemove(mouseMove)
            .mouseup(mouseUp);
        $('.note-box').mouseover(noteIn).mouseout(noteOut);
    });
}());
