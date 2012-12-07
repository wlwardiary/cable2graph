/*
 *
 * GPLv3
 * 2011-2012 by anonymous
 *
 */

/* zoom level */
var zlevel = 10;

/* get element */
function get(el) {
    return document.getElementById(el);
}

/* add event to object */
var addEvent = function() {
    if (window.addEventListener) {
        return function(el, type, fn) {
            el.addEventListener(type, fn, false);
        };
    } else if (window.attachEvent) {
        return function(el, type, fn) {
            var f = function() {
                fn.call(el, window.event);
            };
        el.attachEvent('on' + type, f);
        };
    }
}();

/* set the SVG transform attribute */
function setTransform(w, h, s) {
    var frame = get('frame');
    if (frame) {
        frame.setAttribute(
            'transform', 
            'translate(' + w + ',' + h + ') ' + 
            'scale(' + s + ')'
        );
    }
}

/* set the SVG size attributes */
function setSize(w, h) {
    var svg = get('svg');
    if (svg) {
        svg.setAttribute('width', w);
        svg.setAttribute('height', h);
        svg.style.width = w + 'px';
        svg.style.height = h + 'px';
    }
}

/* toggle any class attribute */
function toggleClass(e, v) {
    if (e.className == null) {
        var a = Array()
    } else {
        var a = e.className.split(/\s+/);
    }
    if (a.indexOf(v) > - 1) {
        a[a.indexOf(v)] = "";
    } else {
        a.push(v);
    }
    e.className = a.join(" ");
}

function main() {
    
    /* 
     * The last 4 zoom levels hide all labels.
     * Zoom is using the #page class attribute. 
     */

    addEvent(get('zoom-out'), 'click', function(e) {
        scale = scale - .1;
        zlevel = zlevel - 1;
        if (scale < 0.1) {
            scale = 0.1;
            zlevel = 1;
        } else if (scale > 1.2) {
            scale = 1.2;
            zlevel = 12;
        }
        setTransform(xw * scale, xh * scale, scale);
        setSize(width * scale, height * scale);
        get('page').className = 'level' + zlevel;
    });

    addEvent(get('zoom-in'), 'click', function(e) {
        scale = scale + .1;
        zlevel = zlevel + 1;
        if (scale < 0.1) {
            scale = 0.1;
            zlevel = 1;
        } else if (scale > 1.2) {
            scale = 1.2;
            zlevel = 12;
        }
        setTransform(xw * scale, xh * scale, scale);
        setSize(width * scale, height * scale);
        get('page').className = 'level' + zlevel;
    });

    /* 
     * Labels and Properties can be switched on and off via CSS.
     * This is using the #graph class attribute 
     */

    addEvent(get('mrn-switch'), 'click', function(e) {
        toggleClass(get('mrn-switch'), 'active');
        toggleClass(get('graph'), 'hide-mrn');
    });

    addEvent(get('date-switch'), 'click', function(e) {
        toggleClass(get('date-switch'), 'active');
        toggleClass(get('graph'), 'hide-date');
    });

    addEvent(get('classification-switch'), 'click', function(e) {
        toggleClass(get('classification-switch'), 'active');
        toggleClass(get('graph'), 'hide-classification');
    });

    addEvent(get('betweenness-switch'), 'click', function(e) {
        toggleClass(get('betweenness-switch'), 'active');
        toggleClass(get('graph'), 'hide-betweenness');
    });

    addEvent(get('authority-switch'), 'click', function(e) {
        toggleClass(get('authority-switch'), 'active');
        toggleClass(get('graph'), 'hide-authority');
    });

    addEvent(get('missing-switch'), 'click', function(e) {
        toggleClass(get('missing-switch'), 'active');
        toggleClass(get('graph'), 'hide-missing');
    });
}

document.addEventListener('DOMContentLoaded',main);

