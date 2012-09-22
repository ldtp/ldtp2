package LDTP::Role::RPCHandler;
# ABSTRACT: All the RPC handling code for LDTP

use Moo::Role;
use MooX::Types::MooseLike::Base qw<Int Str Object>;
use RPC::XML;
use RPC::XML::Client;
use Safe::Isa;

has host => (
    is      => 'ro',
    isa     => Str,
    default => sub {'localhost'},
);

has port => (
    is      => 'ro',
    isa     => Int,
    default => sub {4118},
);

has client => (
    is      => 'ro',
    isa     => Object,
    lazy    => 1,
    builder => 1,
    handles => { call => 'send_request' },
);

sub _build_client {
    my $self = shift;
    my $url  = sprintf 'http://%s:%s/RPC2', $self->host, $self->port;
    return RPC::XML::Client->new($url);
}

sub _try {
    my $self     = shift;
    my $action   = shift;
    my @args     = @_;
    my $response = $self->call( $action, @args );

    $response->$_isa('RPC::XML::fault')
        and die "Error in '$action': %s\n", $response->string;

    return $response->value;
}

1;

