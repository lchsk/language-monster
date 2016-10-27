MONSTER.PlaneGame.prototype.moveShip = function()
{
    var delta = this.game.timeSinceLastFrame;

    var rotation = 0;
    var v_up = false;

    if (MONSTER.Key.isDown(MONSTER.Key.UP)) {
        v_up = true;
        rotation = MONSTER.Utils.to_radians(-10);
    }

    if (this.ship.position.y <= 70) {
        // Ship is near the top edge - we will keep it there as long
        // the user wants it to fly upwards

        if (v_up) {
            this.ship.position.y = 70;
            this.ship.rotation = 0;

            return;
        }
    }

    this.ship.rotation = rotation;
    this.ship.v_up = v_up;

    if (this.ship) {
        if (this.ship.v_up) {
            // Flying upwards

            this.ship.start_y = this.ship.position.y;
            this.ship.v_time = 0.0;

            var y_movement = delta * 0.11; // Speed of going up
            this.ship.position.y -= y_movement;
        } else {
            // Falling down

            var T = 2000.0;

            this.ship.v_time += delta;
            this.ship.rotation = 0;

            var pct = MONSTER.Easing.easeInOutQuart(this.ship.v_time / T);

            this.ship.position.y = Math.round(
                pct * (this.ship.stop_y - this.ship.start_y)
            ) + this.ship.start_y;

            if (this.ship.v_time > T)
                this.ship.position.y = this.ship.stop_y;
        }
    }
};

MONSTER.PlaneGame.prototype.checkCollisions = function()
{
    if (this.ship && ! this.hit)
    {
        var left = 0;

        for (var i = 0; i < this.answers.length; i++)
        {
            var obj = this.answers[i];

            if (Math.abs(obj.text.position.x - this.ship.position.x) < this.ship.width / 2 &&
                Math.abs(obj.text.position.y - this.ship.position.y) < this.ship.height / 2
            )
            {
                this.hit = true;
                this.shipActive = false;
                this.ship.alpha = 0.5;
                this.moveOutOfScreen();

                if (obj.word == this.answer)
                    MONSTER.Common.correct(this);
                else
                    MONSTER.Common.negative(this);
            }
            else if (obj.text.position.x < obj.text.width / 2)
            {
                left++;
            }
        }

        if (left == this.answers.length)
        {
            this.constant_answer_speed = true;
            this.hit = true;
            this.shipActive = false;
            this.ship.alpha = 0.5;
            this.moveOutOfScreen();
            MONSTER.Common.negative(this);
        }
    }
};
