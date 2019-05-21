class PidSyntaxException(Exception):
    """
    Raises when Handle syntax not correct.
    """

    def __init__(self, **args):

        self.msg = 'PID syntax not correct'
        self.correct_syntax = args['correct_syntax']
        self.concrete_msg = args['msg']
        self.pid = args['pid']

        if self.pid is not None:
            self.msg = self.msg.replace('andle', 'andle'+self.pid)

        if self.concrete_msg is not None:
            self.msg += ': '+self.concrete_msg

        if self.correct_syntax is not None:
           self.msg += '\n\tExpected: ' + self.correct_syntax

        self.msg += '.'

        super(self.__class__, self).__init__(self.msg)

class MetadataException(Exception):
    """
    Raises when metadata json file not correct.
    """

    def __init__(self, **args):

        self.msg = "Mandatory metadata item missing"

        self.concrete_msg = args['msg']

        if self.concrete_msg is not None:
            self.msg += ':'+self.concrete_msg
        self.msg += '.'

        super(self.__class__, self).__init__(self.msg)

class MetadataKeyMissingException(Exception):
    """
    Raises when key not created for record
    """

    def __init__(self, **args):

        self.msg = "Metadata key not created yet"

        self.concrete_msg = args['msg']

        if self.concrete_msg is not None:
            self.msg += ':'+self.concrete_msg
        self.msg += '.'

        super(self.__class__, self).__init__(self.msg)