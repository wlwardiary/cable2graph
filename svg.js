/*
 * GPLv3
 */

var zlevel = 10;

function get(el) {
    return document.getElementById(el);
}

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

function setSize(w, h) {
    var svg = get('svg');
    if (svg) {
        svg.setAttribute('width', w);
        svg.setAttribute('height', h);
        svg.style.width = w + 'px';
        svg.style.height = h + 'px';
    }
}

function main() {
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
        get('zoom-circle').setAttribute('class', 'level' + zlevel);
        get('graph').setAttribute('class', 'level' + zlevel);
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
        get('zoom-circle').setAttribute('class', 'level' + zlevel);
        get('graph').setAttribute('class', 'level' + zlevel);
    });
}

document.addEventListener('DOMContentLoaded',main);

