(function() {

    var img_w, img_h, note_list, latest_note, mouse_pos;
    
    function mousePos(e, target) {
        return {
            x: e.pageX - target.offsetLeft,
            y: e.pageY - target.offsetTop
        }
    }
    
    function mouseDown(e) {
        e.preventDefault();
        mouse_pos = mousePos(e, this);
        latest_note = $('<div/>', {
            class: 'note-box',
            css: {
                left: mouse_pos.x + 'px',
                top: mouse_pos.y + 'px'
            }
        }).appendTo(note_list);
    }

    function mouseMove(e) {
        if (mouse_pos == null || latest_note == null) {
            return;
        }
        e.preventDefault();
        cur_pos = mousePos(e, this);
        var dx = cur_pos.x - mouse_pos.x;
        var dy = cur_pos.y - mouse_pos.y;
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
    
    function cssProp(p, s) {
        return Math.round(parseInt(latest_note.css(p)) / s * 100);
    }

    function mouseUp(e) {
        e.preventDefault();
        mouse_pos = null;
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
    
    function pushNoteToServer(x, y, w, h) {
        $.post($SCRIPT_ROOT + '/photos/_addNote/', 
            {
                photoID: window.__photoID,  // TODO: Need a clean way to pass template state into JS files without running all JS through template engine
                x: x, y: y, w: w, h: h
            },
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
    }

    function hoverIn(e) {
        note_list.show();
    }

    function hoverOut(e) {
        note_list.hide();
    }
    
    function noteIn(e) {
        //console.log('set up some kind of tooltip here...');
    }
    
    function noteOut(e) {
        //console.log('... and hide tooltip here');
    }

    function recalcNotes() {
        var d = $('#the-actual-photo');
        img_w = d.width();
        img_h = d.height();
        $('#note-eventer').css('width', img_w + 'px').css('height', img_h + 'px');
        $('.note-box').each(function(i, v) {
            var coords = v.id.split('_').slice(1).map(function(el){return parseInt(el) / 100;});
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
        note_list = $('#note-list');
        $('#note-eventer')
            .mouseover(hoverIn)
            .mouseout(hoverOut)
            .mousedown(mouseDown)
            .mousemove(mouseMove)
            .mouseup(mouseUp);
        $('.note-box').mouseover(noteIn).mouseout(noteOut);
    });
}());
