/*
 *
 * GPLv3
 * 2011-2012 by anonymous
 *
 */

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

function nodeSelect(prop) {
    console.log(prop);
}

function main() {

    /*
    addEvent(get('btn-timeline'), 'click', function(e) {
        toggleClass(get('timeline'), 'active');
    });
    */
    var options = {
      stabilize: false,
      smoothCurves: false,
      nodes: {
        shape: 'dot',
        radius: 24,
        fontSize: 24
      },
      edges: { width: 2 },
      clustering: { enabled: false }
    };
    graph = new vis.Graph(get('graph'), data, options);

    addEvent(window, 'resize', graph.redraw);

    graph.on('select', nodeSelect);

}

document.addEventListener('DOMContentLoaded', main);

