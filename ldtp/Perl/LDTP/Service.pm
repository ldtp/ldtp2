package LDTP::Service;
# ABSTRACT: Handling the LDTP service

use Moo;
use MooX::Types::MooseLike::Base qw<Bool Int Str>;
use Carp;

with 'LDTP::Role::RPCHandler';

has windows_env => (
    is      => 'ro',
    isa     => Bool,
    lazy    => 1,
    builder => 1,
);

has bin => (
    is      => 'ro',
    isa     => Str,
    lazy    => 1,
    builder => 1,
);

has app => (
    is => 'rw',
);

has pid => (
    is => 'rw',
);

sub _build_windows_env {
    my $self = shift;

    # first check %ENV
    $ENV{'LDTP_WINDOWS'} and return 1;
    $ENV{'LDTP_LINUX'}   and return 0;

    # now check the the host OS
    $^O =~ /win|mingw/i and return 1;

    # when all else fails, we assume we're not on Windows
    return 0;
}

sub _build_bin {
    my $self = shift;
    return $self->windows_env ? 'CobraWinLDTP.exe' : 'ldtp';
}

sub start {
    my $self = shift;
    my $bin  = $self->bin;
    my $pid  = open my $app, '-|', $bin;

    defined $pid or croak "Error starting LDTP app ($bin): $!";

    # close the child
    $pid == 0 and exit;

    $self->app($app);
    $self->pid($pid);

    return 1;
}

sub stop {
    my $self = shift;
    my $pid  = $self->pid or return 0;
    my $app  = $self->app or return 0;

    # we gots to kill the app and close the socket
    kill 'KILL', $pid;
    close $app;

    # return an indication of whether it worked or not
    return kill 0, $pid ? 0 : 1;
}

sub isalive {
    my $self = shift;
    return $self->_try('isalive');
}

1;

