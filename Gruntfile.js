module.exports = function (grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        concat: {
            app_js: {
                src: [
                    'languagemonster/languagemonster/static/js/interface.js',
                    'languagemonster/languagemonster/static/js/modal-fix.js',
                ],
                dest: 'languagemonster/languagemonster/static/js/out/app.js'
            },
            games_js: {
                src: [
                    'languagemonster/languagemonster/static/js/game/base.js',
                    'languagemonster/languagemonster/static/js/game/utility.js',
                    'languagemonster/languagemonster/static/js/game/common.js',
                    'languagemonster/languagemonster/static/js/game/easing.js',
                    'languagemonster/languagemonster/static/js/game/tween.js',
                    'languagemonster/languagemonster/static/js/game/key.js',
                    'languagemonster/languagemonster/static/js/game/data_loader.js',
                    'languagemonster/languagemonster/static/js/game/abstract_screen.js',
                    'languagemonster/languagemonster/static/js/game/simple_game.js',

                    'languagemonster/languagemonster/static/js/game/space/main.js',
                    'languagemonster/languagemonster/static/js/game/space/ship.js',
                    'languagemonster/languagemonster/static/js/game/space/interface.js',

                    'languagemonster/languagemonster/static/js/game/plane/main.js',
                    'languagemonster/languagemonster/static/js/game/plane/ship.js',
                    'languagemonster/languagemonster/static/js/game/plane/interface.js',

                    'languagemonster/languagemonster/static/js/game/runner/main.js',
                    'languagemonster/languagemonster/static/js/game/runner/ship.js',
                    'languagemonster/languagemonster/static/js/game/runner/interface.js',

                    'languagemonster/languagemonster/static/js/game/shooter/main.js',
                    'languagemonster/languagemonster/static/js/game/shooter/ship.js',
                    'languagemonster/languagemonster/static/js/game/shooter/interface.js',

                    'languagemonster/languagemonster/static/js/game/loader.js',
                    'languagemonster/languagemonster/static/js/game/game.js'
                ],
                dest: 'languagemonster/languagemonster/static/js/out/games.js'
            },
            landing_js: {
                src: [
                    'languagemonster/languagemonster/static/js/init.js',
                    'languagemonster/languagemonster/static/js/parallax.js',
                    'languagemonster/languagemonster/static/js/modal-fix.js'
                ],
                dest: 'languagemonster/languagemonster/static/js/out/landing.js'
            }
        },
        cssmin: {
            app: {
                src: 'languagemonster/languagemonster/static/css/app/css.css',
                dest: 'languagemonster/languagemonster/static/css/app/css.min.css'
            },
            landing: {
                src: 'languagemonster/languagemonster/static/css/landing/css.css',
                dest: 'languagemonster/languagemonster/static/css/landing/css.min.css'
            }
        },
        uglify: {
            js: {
                files: {
                    'languagemonster/languagemonster/static/js/out/app.js':
                    ['languagemonster/languagemonster/static/js/out/app.js'],
                    'languagemonster/languagemonster/static/js/out/landing.js':
                    ['languagemonster/languagemonster/static/js/out/landing.js'],
                    'languagemonster/languagemonster/static/js/out/games.js':
                    ['languagemonster/languagemonster/static/js/out/games.js']
                }
            }
        },
        watch: {
            files: ['languagemonster/languagemonster/static/**'],
            tasks: ['concat', 'cssmin', 'uglify']
        }
    });
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.registerTask('default', [
        'cssmin:app',
        'cssmin:landing',
        'concat:app_js',
        'concat:games_js',
        'concat:landing_js',
        'uglify:js'
    ]);
};
