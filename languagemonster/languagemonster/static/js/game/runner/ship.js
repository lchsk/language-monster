MONSTER.RunnerGame.prototype.moveShip = function()
{
    var t = this.game.timeSinceLastFrame;

    if (this.state === this.State.RUNNING) {
        if (MONSTER.Key.isUp(MONSTER.Key.UP)) {
            this.state = this.State.JUMPING;
            this.ship.textures = this.textures_jump;
            this.ship.start_y = this.ship.position.y;
            this.ship.stop_y = this.ship.start_y - 200;
        }
    }

    if (this.state === this.State.RUNNING) {
         if (MONSTER.Key.isDown(MONSTER.Key.DOWN)) {
            this.state = this.State.SLIDING;
            this.ship.rotation = 0.75 * 2.0 * MONSTER.Const.PI;
            this.ship.gotoAndStop(1);
            this.ship.position.y = this.slide_y;
         }
    }

    if (this.state === this.State.SLIDING) {
        if (!MONSTER.Key.isDown(MONSTER.Key.DOWN)) {
            // Stand up after sliding

            this.state = this.State.RUNNING;
            this.ship.rotation = 0;
            this.ship.play();
            this.ship.position.y = this.original_y;
        }
    } else if (this.state === this.State.JUMPING) {
        this.ship.v_time += t;

        var pct = MONSTER.Easing.easeOutQuart(this.ship.v_time / this.JUMP_TIME);

        // Move upwards
        this.ship.position.y = Math.round(
            pct * (this.ship.stop_y - this.ship.start_y))
            + this.ship.start_y;

        if (this.ship.v_time > this.JUMP_TIME) {
            // Falling now

            this.ship.v_time = 0.0;
            this.state = this.State.FALLING;
            this.ship.position.y = this.ship.stop_y;
        }
    }

    if (this.state === this.State.FALLING
        && this.ship.position.y < this.original_y) {
        // Move downwards

        this.ship.position.y += t * 0.3;
    }

    if (this.state === this.State.FALLING
        && this.ship.position.y >= this.original_y) {
        // Back on the ground

        this.state = this.State.RUNNING;
        this.ship.textures = this.textures;
    }
};

MONSTER.RunnerGame.prototype.checkCollisions = function()
{
    if (this.ship && ! this.hit)
    {
        var left = 0;

        for (var i = 0; i < this.answers.length; i++)
        {
            var obj = this.answers[i];
            var collision = false;

            if (this.ship.v_down)
            {
                if (obj.text.position.x >= this.ship.position.x - this.ship.width / 2 &&
                    obj.text.position.x <= this.ship.position.x + this.ship.width / 2 &&
                    obj.text.position.y >= this.ship.position.y - this.ship.height / 2.5 &&
                    obj.text.position.y <= this.ship.position.y + this.ship.height / 2.5
                )
                    collision = true;
            }
            else
            {
                if (obj.text.position.x >= this.ship.position.x - this.ship.width / 2 &&
                    obj.text.position.x <= this.ship.position.x + this.ship.width / 2 &&
                    obj.text.position.y >= this.ship.position.y - this.ship.height / 2 &&
                    obj.text.position.y <= this.ship.position.y + this.ship.height / 2
                )
                    collision = true;
            }

            if (collision)
            {
                this.hit = true;
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
            this.moveOutOfScreen();
            MONSTER.Common.negative(this);
        }
    }
};
