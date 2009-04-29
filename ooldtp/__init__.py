from _context import Context, Component

def context(window_name):
    return Context(window_name)

def component(window_name, object_name):
    return Component(window_name, object_name)
