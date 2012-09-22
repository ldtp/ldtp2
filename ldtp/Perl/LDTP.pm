package LDTP;
# ABSTRACT: Perl interface to LDTP (Linux Desktop Testing Project)

use Moo;
use MooX::Types::MooseLike::Base qw<HashRef Object>;
use Carp;
use File::Temp;
use MIME::Base64;

use LDTP::Window;
use LDTP::Service;

with 'LDTP::Role::RPCHandler';

has poll_events => (
    is      => 'ro',
    isa     => HashRef,
    default => sub { {} },
);

# we provide a single service and keep track of it
has service => (
    is      => 'ro',
    isa     => Object,
    lazy    => 1,
    builder => 1,
);

sub _build_service {
    my $self = shift;
    return LDTP::Service->new( client => $self->client );
}

sub window {
    my $self = shift;
    my $name = shift;
    return LDTP::Window->new( name => $name, client => $self->client );
}

sub wait {
    my $self    = shift;
    my $timeout = shift || 5;
    $self->_try( 'wait', $timeout );
}

sub generatemouseevent {
    my $self = shift;
    my ( $x, $y, $event_type ) = @_;

    defined $event_type or $event_type = 'b1c';

    $self->_try( 'generatemouseevent', $x, $y, $event_type );
}

sub getapplist {
    my $self = shift;
    $self->_try('getapplist');
}

sub getwindowlist {
    my $self = shift;
    $self->_try('getwindowlist');
}

sub registerevent {
    my $self = shift;
    my ( $event_name, $fnname, @args ) = @_;

    $self->poll_events->{$event_name} = [ $fnname, \@args ];
    $self->_try( 'registerevent', $event_name );
}

sub deregisterevent {
    my $self       = shift;
    my $event_name = shift;

    delete $self->poll_events->{$event_name};
    $self->_try( 'deregisterevent', $event_name );
}

sub registerkbevent {
    my $self = shift;
    my ( $keys, $modifiers, $fnname, @args ) = @_;

    my $event_name = "kbevent$keys$modifiers";
    $self->poll_events->{$event_name} = [ $fnname, \@args ];
    $self->_try( 'registerkbevent', $event_name );
}

sub deregisterkbevent {
    my $self = shift;
    my ( $keys, $modifiers ) = @_;

    my $event_name = "kbevent$keys$modifiers";
    delete $self->poll_events->{$event_name};
    $self->_try( 'deregisterkbevent', $event_name );
}

sub launchapp {
    my $self = shift;
    my ( $cmd, $args, $delay, $env, $lang ) = @_;

    defined $args  or $args = [];
    defined $delay or $delay = 0;
    defined $env   or $env   = 1;
    defined $lang  or $lang  = 'C';

    $self->_try( 'launchapp', $cmd, $args, $delay, $env, $lang );
}

sub getcpustat {
    my $self         = shift;
    my $process_name = shift;

    $self->_try( 'getcpustat', $process_name );
}

sub getmemorystat {
    my $self         = shift;
    my $process_name = shift;

    $self->_try( 'getmemorystat', $process_name );
}

sub getlastlog {
    my $self = shift;
    $self->_try('getlastlog');
}

sub getobjectnameatcoords {
    my $self      = shift;
    my $wait_time = shift;

    defined $wait_time or $wait_time = 0;

    $self->_try( 'getobjectnameatcoords', $wait_time );
}

sub startprocessmonitor {
    my $self = shift;
    my ( $process_name, $interval ) = @_;

    defined $interval or $interval = 2;

    $self->_try( 'startprocessmonitor', $process_name, $interval );
}

sub stopprocessmonitor {
    my $self         = shift;
    my $process_name = shift;
    $self->_try( 'stopprocessmonitor', $process_name );
}

sub keypress {
    my $self = shift;
    my $data = shift;
    $self->_try( 'keypress', $data );
}

sub keyrelease {
    my $self = shift;
    my $data = shift;
    $self->_try( 'keyrelease', $data );
}

sub closewindow {
    my $self        = shift;
    my $window_name = shift;

    defined $window_name or $window_name = '';

    $self->window($window_name)->close;
}

sub maximizewindow {
    my $self        = shift;
    my $window_name = shift;

    defined $window_name or $window_name = '';

    $self->window($window_name)->maximize;
}

sub minimizewindow {
    my $self        = shift;
    my $window_name = shift;

    defined $window_name or $window_name = '';

    $self->window($window_name)->minimize;
}

sub simulatemousemove {
    my $self = shift;
    my ( $src_x, $src_y, $dst_x, $dst_y, $delay ) = @_;

    defined $delay or $delay = 0.0;

    $self->_try(
        'simulatemousemove',
        $src_x, $src_y,
        $dst_x, $dst_y,
        $delay,
    );
}

sub delaycmdexec {
    my $self  = shift;
    my $delay = shift;
    $self->_try( 'delaycmdexec', $delay );
}

sub onwindowcreate {
    my $self = shift;
    my ( $window_name, $fnname, @args ) = @_;
    $self->poll_events->{$window_name} = [ $fnname, \@args ];
    # FIXME: implement
}

sub removecallback {
    my $self = shift;
    my ( $window_name, $fnname ) = @_;
    delete $self->poll_events->{$window_name};
    # FIXME: implement
}

sub method_missing {
    my $self = shift;
    my ( $window_name, $sym, $args, $block ) = @_;
    # FIXME: implement
}

sub imagecapture {
    my $self   = shift;
    my $params = shift;
    my %opts   = (
        window_name => '',
        out_file    => '',
        x           => 0,
        y           => 0,
        width       => -1,
        height      => -1,
        @_,
    );

    my $res = $self->_try(
        'imagecapture',
        $opts{'window_name'},
        $opts{'x'},     $opts{'y'},
        $opts{'width'}, $opts{'height'},
    );

    my ( $filename, $fh );

    if ( $opts{'out_file'} ne '' ) {
        $filename = $opts{'out_file'};
        open $fh, '>', $filename or croak "Can't open '$filename': $!";
    } else {
        ( $filename, $fh ) = tempfile();
    }

    print {$fh} decode_base64($res);
    close $fh or croak "Can't close '$filename': $!";
    return $filename;
}

1;

