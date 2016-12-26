var gulp = require('gulp');

var sass = require('gulp-sass');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var cssmin = require('gulp-cssmin');
var rename = require('gulp-rename');
var eslint = require('gulp-eslint');

var static_dir = 'languagemonster/languagemonster/static/';

var js_dir = static_dir + 'js/';
var js_build_dir = static_dir + 'js_build/';
var js_games_dir = static_dir + 'js/game/';
var css_dir = static_dir + 'css/';
var scss_dir = static_dir + 'scss/';

gulp.task('lint', function() {
    return gulp.src([js_dir + '**/*.js', '!' + js_dir + 'build/**/*.js'])
        .pipe(eslint())
        .pipe(eslint.format());
});

gulp.task('scss_app', function() {
    return gulp.src(scss_dir + 'app/*.scss')
        .pipe(sass())
        .pipe(rename('css.css'))
        .pipe(cssmin())
        .pipe(rename({suffix: '.min'}))
        .pipe(gulp.dest(css_dir + 'app/'));
});

gulp.task('scss_landing', function() {
    return gulp.src(scss_dir + 'landing/*.scss')
        .pipe(sass())
        .pipe(rename('css.css'))
        .pipe(cssmin())
        .pipe(rename({suffix: '.min'}))
        .pipe(gulp.dest(css_dir + 'landing/'));
});

gulp.task('js_games', function() {
    return gulp.src([
        js_games_dir + 'base.js',
        js_games_dir + 'utility.js',
        js_games_dir + 'common.js',
        js_games_dir + 'easing.js',
        js_games_dir + 'tween.js',
        js_games_dir + 'key.js',
        js_games_dir + 'data_loader.js',
        js_games_dir + 'abstract_screen.js',
        js_games_dir + 'loading_screen.js',
        js_games_dir + 'simple_game.js',

        js_games_dir + 'space/main.js',
        js_games_dir + 'space/ship.js',
        js_games_dir + 'space/interface.js',

        js_games_dir + 'plane/main.js',
        js_games_dir + 'plane/ship.js',
        js_games_dir + 'plane/interface.js',

        js_games_dir + 'runner/main.js',
        js_games_dir + 'runner/ship.js',
        js_games_dir + 'runner/interface.js',

        js_games_dir + 'shooter/main.js',
        js_games_dir + 'shooter/ship.js',
        js_games_dir + 'shooter/interface.js',

        js_games_dir + 'game.js'
    ], {base: js_dir})
        .pipe(concat('games.js'))
        .pipe(gulp.dest(js_build_dir))
        .pipe(rename('games.js'))
        .pipe(uglify())
        .pipe(rename('games.min.js'))
        .pipe(gulp.dest(js_build_dir));
});

gulp.task('js_app', function() {
    return gulp.src([
        js_dir + 'app/interface.js',
        js_dir + 'app/admin.js'
    ], {base: js_dir})
    .pipe(concat('app.js'))
    .pipe(gulp.dest(js_build_dir))
    .pipe(rename('app.js'))
    .pipe(uglify())
    .pipe(rename('app.min.js'))
    .pipe(gulp.dest(js_build_dir));
});

gulp.task('js_landing', function() {
    return gulp.src([
        js_dir + 'util.js',
        js_dir + 'landing/home.js'

    ], {base: js_dir})
    .pipe(concat('landing.js'))
    .pipe(gulp.dest(js_build_dir))
    .pipe(rename('landing.js'))
    .pipe(uglify())
    .pipe(rename('landing.min.js'))
    .pipe(gulp.dest(js_build_dir));
});

gulp.task('js', ['js_landing', 'js_app', 'js_games']);
gulp.task('scss', ['scss_landing', 'scss_app']);

gulp.task('watch', function() {
    gulp.watch(js_dir + '**/*.js', ['lint', 'js']);
    gulp.watch(scss_dir + '**/*.scss', ['scss']);
});

gulp.task('default', ['lint', 'js', 'scss']);
