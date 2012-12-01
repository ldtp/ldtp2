package LDTP::Window;
# ABSTRACT: Window-related functions for LDTP

use Moo;
use MooX::Types::MooseLike::Base qw<Str>;

with 'LDTP::Role::RPCHandler';

has name => (
    is       => 'ro',
    isa      => Str,
    required => 1,
);

sub waittillguiexists {
    my $self        = shift;
    my $object_name = shift;
    my $gui_timeout = shift;
    my $state       = shift;

    # this is for compatibility with 5.8.x
    # i'd rather use "shift // ..." or "//= ..."
    defined $object_name or $object_name = '';
    defined $gui_timeout or $gui_timeout = 30;
    defined $state       or $state       = '';

    $self->_try(
        'waittillguiexist',
        $self->name,
        $object_name,
        $gui_timeout,
        $state,
    );
}

sub waittillguinotexist {
    my $self        = shift;
    my $object_name = shift;
    my $gui_timeout = shift;
    my $state       = shift;

    # this is for compatibility with 5.8.x
    # i'd rather use "shift // ..." or "//= ..."
    defined $object_name or $object_name = '';
    defined $gui_timeout or $gui_timeout = 30;
    defined $state       or $state       = '';

    $self->_try(
        'waittillguinotexist',
        $self->window_name,
        $object_name,
        $gui_timeout,
        $state,
    );
}

sub guiexists {
    my $self        = shift;
    my $object_name = shift;

    defined $object_name or $object_name = '';

    $self->_try( 'guiexist', $self->window_name, $object_name );
}

sub hasstate {
    my $self = shift;
    my ( $object_name, $state, $gui_timeout ) = @_;

    defined $gui_timeout or $gui_timeout = 0;

    $self->_try(
        'hasstate',
        $self->window_name,
        $object_name,
        $state,
        $gui_timeout,
    );
}

sub selectrow {
    my $self = shift;
    my ( $object_name, $row_text ) = @_;

    $self->_try(
        'selectrow',
        $self->window_name,
        $object_name,
        $row_text,
        XML::RPC::boolean->new(0), # false
    );
}

sub getchild {
    my $self = shift;
    my ( $child_name, $role, $parent ) = @_;

    defined $child_name or $child_name = '';
    defined $role       or $role       = '';
    defined $parent     or $parent     = '';

    $self->_try(
        'getchild',
        $self->window_name,
        $child_name,
        $role,
        $parent,
    );
}

sub enterstring {
    my $self                = shift;
    my ( $param1, $param2 ) = @_;

    if ( ( not defined $param2 ) || ( $param2 eq '' ) ) {
        $self->_try( 'enterstring', $param1, '', '' );
    } else {
        $self->_try( 'enterstring', $self->window_name, $param1, $param2 );
    }
}

sub setvalue {
    my $self                   = shift;
    my ( $object_name, $data ) = @_;

    $self->_try( 'setvalue', $self->window_name, $object_name, $data );
}

sub grabfocus {
    my $self        = shift;
    my $object_name = shift;

    defined $object_name or $object_name = '';

    # On Linux just with window name, grab focus doesn't work
    # So, we can't make this call generic
    $self->_try( 'grabfocus', $self->window_name, $object_name );
}

sub copytext {
    my $self = shift;
    my ( $object_name, $start, $end_index ) = @_;

    defined $end_index or $end_index = -1;
    
    $self->_try(
        'copytext',
        $self->window_name,
        $object_name,
        $start,
        $end_index,
    );
}

sub cuttext {
    my $self = shift;
    my ( $object_name, $start, $end_index ) = @_;

    defined $end_index or $end_index = -1;
    
    $self->_try(
        'cuttext',
        $self->window_name,
        $object_name,
        $start,
        $end_index,
    );
}

sub deletetext {
    my $self = shift;
    my ( $object_name, $start, $end_index ) = @_;

    defined $end_index or $end_index = -1;
    
    $self->_try(
        'deletetext',
        $self->window_name,
        $object_name,
        $start,
        $end_index,
    );
}

sub gettextvalue {
    my $self = shift;
    my ( $object_name, $start_pos, $end_pos ) = @_;

    defined $start_pos or $start_pos = 0;
    defined $end_pos   or $end_pos   = 0;

    $self->_try(
        'gettextvalue',
        $self->window_name,
        $object_name,
        $start_pos,
        $end_pos,
    );
}

sub getcellvalue {
    my $self = shift;
    my ( $object_name, $row, $column ) = @_;

    defined $column   or $column   = 0;

    $self->_try(
        'getcellvalue',
        $self->window_name,
        $object_name,
        $row,
        $column,
    );
}

sub getcellsize {
    my $self = shift;
    my ( $object_name, $row, $column ) = @_;

    defined $column   or $column   = 0;

    $self->_try(
        'getcellsize',
        $self->window_name,
        $object_name,
        $row,
        $column,
    );
}

sub close {
    my $self = shift;
    $self->_try( 'closewindow', $self->name );
}

sub maximizewindow {
    my $self = shift;
    $self->_try( 'maximizewindow', $self->name );
}

sub minimizewindow {
    my $self = shift;
    $self->_try( 'minimizewindow', $self->name );
}

1;

