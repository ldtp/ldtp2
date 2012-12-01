#!perl

use strict;
use warnings;

use LDTP;
use LDTP::Service;
use Test::More tests => 4;

{
    my $service = LDTP::Service->new;
    isa_ok( $service, 'LDTP::Service' );
    can_ok( $service, qw<isalive start stop> );
}

my $ldtp = LDTP->new();
isa_ok( $ldtp, 'LDTP' );

my $service = $ldtp->service;
isa_ok( $service, 'LDTP::Service' );
