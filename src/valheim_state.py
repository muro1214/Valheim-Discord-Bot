from transitions import Machine
from logger import Logger

class ValheimState(object):
    states = ['stopping', 'running']

    def __init__(self, name):
        self.name = name
        self.machine = Machine(model=self, states=ValheimState.states, initial='stopping', auto_transitions=False)
        self.machine.add_transition(trigger='startup', source='stopping', dest='running', before='to_running')
        self.machine.add_transition(trigger='running_continue', source='running', dest='=')
        self.machine.add_transition(trigger='shutdown', source='running', dest='stopping', before='to_stopping')
        self.machine.add_transition(trigger='stopping_continue', source='stopping', dest='=')


    def to_running(self):
        Logger.log('transition to running.')


    def to_stopping(self):
        Logger.log('transition to stopping.')

