from pynput.mouse import Controller as MouseController

def get_screen_size():
    """Utility function to get screen resolution"""

    mouse = MouseController()

    width = height = 0

    def _reset_mouse_position():
        # Move the mouse to the top left of 
        # the screen
        mouse.position = (0, 0)

    # Reset mouse position
    _reset_mouse_position()

    count = 0
    while 1:
        count += 1
        mouse.move(count, 0)
        
        # Get the current position of the mouse
        left = mouse.position[0]

        # If the left doesn't change anymore, then
        # that's the screen resolution's width
        if width == left:
            # Add the last pixel
            width += 1

            # Reset count for use for height
            count = 0
            break

        # On each iteration, assign the left to 
        # the width
        width = left
    
    # Reset mouse position
    _reset_mouse_position()

    while 1:
        count += 1
        mouse.move(0, count)

        # Get the current position of the mouse
        right = mouse.position[1]

        # If the right doesn't change anymore, then
        # that's the screen resolution's height
        if height == right:
            # Add the last pixel
            height += 1
            break

        # On each iteration, assign the left to 
        # the width
        height = right

    return width, height