/**
 * Polyfill requestAnimationFrame
 */

(function() {
    var lastTime = 0;
    var vendors = ['webkit', 'moz'];
    for(var x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {
        window.requestAnimationFrame = window[vendors[x]+'RequestAnimationFrame'];
        window.cancelAnimationFrame =
          window[vendors[x]+'CancelAnimationFrame'] || window[vendors[x]+'CancelRequestAnimationFrame'];
    }

    if (!window.requestAnimationFrame)
        window.requestAnimationFrame = function(callback, element) {
            var currTime = new Date().getTime();
            var timeToCall = Math.max(0, 16 - (currTime - lastTime));
            var id = window.setTimeout(function() { callback(currTime + timeToCall); },
              timeToCall);
            lastTime = currTime + timeToCall;
            return id;
        };

    if (!window.cancelAnimationFrame)
        window.cancelAnimationFrame = function(id) {
            clearTimeout(id);
        };
}());

/**
 * Use underscore's partial method.
 * http://underscorejs.org/#partial
 */
var create_partial = function(func) {
    var boundArgs = Array.prototype.slice.call(arguments, 1);
    return function() {
        var position = 0;
        var args = boundArgs.slice();
        while (position < arguments.length) args.push(arguments[position++]);
        return func.apply(this, args);
    };
};

/**
 * Options:
 *  - sourceUrl - (required) Url for the packed png.
 *  - timeline - (required) Object which holds the blips information.
 *  - canvasEl - (required) Canvas element to paint image onto.
 *  - delayFactor - Offset timing by a multiplier.  Default 1.0.
 *  - loop - Should the movingPNG automatically loop?  Default true.
 *  - endHangLength - Length of time to wait at the end before looping.  Default 4000ms.
 *  - autostart - Should the movingPNG start on page load?  Default true
 */
var movingPNG = function (options) {
    options.delayFactor = options.hasOwnProperty('delayFactor') ? options.delayFactor : 0.7;
    options.endHangLength = options.hasOwnProperty('endHangTime') ? options.endHangTime : 4000;
    options.autostart = options.hasOwnProperty('autostart') ? options.autostart : true;
    options.loop = options.hasOwnProperty('loop') ? options.loop : true;

    if (!options.hasOwnProperty('sourceUrl') || !options.hasOwnProperty('timeline') || !options.hasOwnProperty('canvasEl'))
        throw new Error('Missing one or more required settings for movingPNG.');

    var context = null;
    var image = new Image();
    var timeline = options.timeline;

    var running = false;
    var totalRuntime = 0;
    var currentRuntime = 0;
    var lastRun = 0;

    var drawImage = null;

    var init = function() {
        context = options.canvasEl.getContext('2d');
        image.onload = function() {
            drawImage = create_partial(context.drawImage, image);

            // Always let it run once so the initial image is displayed
            start();
            if (!options.autostart)
                stop();
        }.bind(this);

        image.src = options.sourceUrl;

        totalRuntime = computeRuntime();
        lastRun = currentTime();
    };

    var start = function() {
        lastRun = currentTime();
        running = true;
        window.requestAnimationFrame(animationLoop);
    };

    var pause = function() {
        running = false;
    };

    var stop = function() {
        running = false;
        currentRuntime = 0;
        lastRun = 0;
    };

    var isRunning = function() {
        return running;
    };

    var currentTime = function() {
        return new Date().getTime();
    };

    var computeRuntime = function() {
        var runtime = 0;
        for (var j = 0; j < timeline.length - 1; ++j)
            runtime += timeline[j].delay;
        return runtime + options.endHangLength;
    };

    var getFrame = function(currentTime) {
        var run_time = 0;
        for (var j = 0; j < timeline.length - 1; ++j) {
            run_time += timeline[j].delay;
            if (currentTime < run_time)
                return j;
        }

        return j;
    };

    var animationLoop = function(timestamp) {
        var elapsedTime = currentTime() - lastRun;

        currentRuntime = currentRuntime + elapsedTime;
        if (!options.loop && currentRuntime > totalRuntime)
            stop();

        currentRuntime = currentRuntime % totalRuntime;

        var frame = getFrame(currentRuntime);
        var delay = timeline[frame].delay * options.delayFactor;
        var blits = timeline[frame].blit;

        for (j = 0; j < blits.length; ++j) {
            var blit = blits[j],
                sx = blit[0],
                sy = blit[1],
                w = blit[2],
                h = blit[3],
                dx = blit[4],
                dy = blit[5];

            context.drawImage(image, sx, sy, w, h, dx, dy, w, h);
        }

        lastRun = currentTime();

        if (running)
            window.requestAnimationFrame(animationLoop);
    };

    animationLoop = animationLoop.bind(this);
    this.start = start.bind(this);
    this.stop = stop.bind(this);
    this.pause = pause.bind(this);
    this.isRunning = isRunning.bind(this);

    init();
};