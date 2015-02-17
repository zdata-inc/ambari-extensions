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

var movingPNG = function (source_url, timeline, canvasEl, delayFactor, endHangLength) {
    delayFactor = delayFactor || 0.7;
    endHangLength = 4000;

    var context = null;
    var image = new Image();

    var totalRuntime = 0;
    var currentRuntime = 0;
    var lastRun = 0;

    var drawImage = null;

    var init = function() {
        context = canvasEl.getContext('2d');
        image.onload = function() {
            drawImage = create_partial(context.drawImage, image);
            window.requestAnimationFrame(animationLoop);
        }.bind(this);

        image.src = source_url;

        totalRuntime = computeRuntime();
        lastRun = currentTime();
    };

    var currentTime = function() {
        return new Date().getTime();
    };

    var computeRuntime = function() {
        var runtime = 0;
        for (var j = 0; j < timeline.length - 1; ++j)
            runtime += timeline[j].delay;
        return runtime + endHangLength;
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

    var animationLoop = function(elapsedTime) {
        var elapsedTime = currentTime() - lastRun;
        currentRuntime = (currentRuntime + elapsedTime) % totalRuntime;

        var frame = getFrame(currentRuntime);
        var delay = timeline[frame].delay * delayFactor;
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

        window.requestAnimationFrame(animationLoop);
    };

    animationLoop = animationLoop.bind(this);

    init();
};