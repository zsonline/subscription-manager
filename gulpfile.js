'use strict';

// Import node packages
const gulp = require('gulp');
const sass = require('gulp-sass');
const shell = require('gulp-shell');
const sourcemaps = require('gulp-sourcemaps');

/*
Default task. Starts watching for style changes.
 */
gulp.task('default', ['styles:watch']);

/*
Compiles the .scss files in static/styles/scss/ into
.css files in static/styles/. It also generates source
maps for the stylesheets and stores them in the same
directory.
 */
gulp.task('styles', function () {
    gulp.src('./subscription_manager/static/styles/scss/**/*.scss')
        .pipe(sourcemaps.init())
        .pipe(sass().on('error', sass.logError))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest('./subscription_manager/static/styles'));
});

/*
Watches in static/styles/scss/ for changes in .scss
files. If changes occur, the styles task is executed.
 */
gulp.task('styles:watch', ['styles'], function () {
    gulp.watch('./subscription_manager/static/styles/scss/**/*.scss', ['styles']);
});

/*
Resets the database by deleting all migration
files as well as the sqlite database. Afterwards,
it generates the new migrations and applies them.
 */
gulp.task('db:reset', shell.task([
    'find . -path *migrations* -name "*.py" -not -path "*__init__*" -not -path "*venv*" -exec rm {} \\;',
    'find . -path "*.sqlite3" -exec rm {} \\;',
    'python manage.py makemigrations',
    'python manage.py migrate',
    'python manage.py loaddata users subscription_types'
]));
