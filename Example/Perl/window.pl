#!perl

use strict;
use warnings;

use LDTP;
use LDTP::Window;
use Test::More tests => 5;

my $ldtp = LDTP->new();
isa_ok( $ldtp, 'LDTP' );

my $window = $ldtp->window('XX');
isa_ok( $window, 'LDTP::Window' );
is( $window->name, 'XX', 'Correct name' );

my $new_win = LDTP::Window->new( name => 'YY' );
isa_ok( $new_win, 'LDTP::Window' );
is( $new_win->name, 'YY', 'Correct name' );
