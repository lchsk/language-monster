
// Adapted from:
// http://nokarma.org/2011/02/27/javascript-game-development-keyboard-input/

MONSTER.Key = function()
{
};

MONSTER.Key._pressed = {};

MONSTER.Key.P = 80;
MONSTER.Key.SPACE = 32;
MONSTER.Key.ENTER = 13;
MONSTER.Key.LEFT = 37;
MONSTER.Key.UP = 38;
MONSTER.Key.RIGHT = 39;
MONSTER.Key.DOWN = 40;

MONSTER.Key.isDown = function(keyCode)
{
    return MONSTER.Key._pressed[keyCode];
};

MONSTER.Key.isUp = function(keyCode)
{
    if (MONSTER.Key._pressed[keyCode]) {
        delete MONSTER.Key._pressed[keyCode];

        return true;
    }

    return false;
};

MONSTER.Key.onKeydown = function(event)
{
    MONSTER.Key._pressed[event.keyCode] = true;
};

MONSTER.Key.onKeyup = function(event)
{
    delete MONSTER.Key._pressed[event.keyCode];
};

window.addEventListener('keyup', function(event) {
    MONSTER.Key.onKeyup(event);
}, false);
window.addEventListener('keydown', function(event) {
    MONSTER.Key.onKeydown(event);
}, false);

MONSTER.Key.blockScrolling = function()
{
    window.addEventListener("keydown", function(e){
        if([
            MONSTER.Key.SPACE,
            MONSTER.Key.LEFT,
            MONSTER.Key.RIGHT,
            MONSTER.Key.DOWN,
            MONSTER.Key.UP
        ].indexOf(e.keyCode) > -1) {
            e.preventDefault();
        }
    }, false);
};
