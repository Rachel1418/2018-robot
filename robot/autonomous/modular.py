from magicbot.state_machine import state, timed_state, AutonomousStateMachine
from components import drive, crane
from magicbot import tunable
from networktables.util import ntproperty


class Modular(AutonomousStateMachine):
    """
    Modular autonomous.

    Should not be executed on its own.
    """
    DEFAULT = False

    drive = drive.Drive
    crane = crane.Crane

    position = ntproperty('/autonomous/position', '')
    plates = ntproperty('/robot/plates', '')

    advance = tunable(True)
    switch = tunable(True)
    scale = tunable(False)

    def direction(self):
        """
        Return directional multiplier based on position (or owned plate if in middle position).
        """
        if self.position == 'left':
            return -1
        elif self.postiion == 'right':
            return 1
        else:
            if self.position[0] == 'L':
                return -1
            if self.position[0] == 'R':
                return 1

    @state(first=True)
    def start(self):
        """
        Decide how to begin the autonomous.
        """
        self.crane.grip()
        # If we are only advancing to cross the auto line,
        # make the charge sequence longer. Only charge if on the left or right,
        # so that the robot will not crash into the switch.
        if self.switch or self.scale:
            self.next_state('switch_initial')
        elif self.advance and (self.position == 'left' or self.position == 'right'):
            self.next_state('cross_auto_line')

    @timed_state(duration=1.5)
    def cross_auto_line(self):
        """
        If we ONLY want to cross the auto line, run this method.
        """
        self.drive.move(0.8, 0)

    # Duration needs to be short so that the robot does not crash into the cube stack if it is in the middle
    @timed_state(duration=1.7, next_state='switch_rotate_side')
    def switch_initial(self):
        """
        Give the robot some distance from the starting point.
        """
        self.crane.move(0.4)
        self.drive.move(0.7, 0)

    @timed_state(duration=0.6, next_state='switch_drop_side')
    def switch_rotate_side(self):
        """
        Rotate robot to face the switch.
        """
        self.crane.move(0.4)
        # Numbers are approximate
        if self.position == 'left':
            self.drive.move(0.2, 1)
        elif self.position == 'right':
            self.drive.move(0.2, -1)
        else:
            if self.plates[0] == 'L':
                self.drive.move(0.2, -1)
            elif self.plates[0] == 'R':
                self.drive.move(0.2, 1)
        # The robot will now have the opportunity to pursue different paths
        # It can either try to score on the switch, the switch and the scale,
        # just the scale, or neither, depending on what is selected in the UI
        if self.switch:
            # TODO: Make this do things
            # self.next_state('switch_curve')
            pass

    @timed_state(duration=0.5)
    def switch_drop_side(self):
        """
        Drop preloaded cube in switch.
        """
        if self.switch():
            self.crane.release()
