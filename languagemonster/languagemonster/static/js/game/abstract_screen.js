MONSTER.AbstractScreen = function(game)
{
    this.game = game;
};

MONSTER.AbstractScreen.prototype.constructor = MONSTER.AbstractScreen;


MONSTER.AbstractScreen.prototype.update = function()
{
    if (this.game.DEBUG) {
        var fps = Math.round(1000 / this.game.timeSinceLastFrame);

        var debug = this.game.debug;

        debug['fps_ticks']++;
        debug['fps_timer'] += this.game.timeSinceLastFrame;

        if (debug['fps_timer'] >= 1000) {
            debug['fps_avg_per_second']
                = Math.round(debug['fps_timer'] / debug['fps_ticks']);
            debug['fps_timer'] = 0;
            debug['fps_ticks'] = 1;
        }

        debug['fps'].text = debug['fps_avg_per_second'] + " / " + fps;
    }
};
