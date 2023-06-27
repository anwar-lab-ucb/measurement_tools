"""
Alec Vercruysse
2023-06
"""


def confirm(question, default=True):
    """
    default: boolean for yes or no, or None if no default
    Returns boolean corresponding to yes/no
    """
    prompt = '> '
    if default is not None:
        prompt += '[y/N]' if default is False else '[Y/n]'
    print(question)
    answer = input(prompt).lower()
    if answer == '':
        if default is not None:
            return default
    elif answer == 'yes' or answer == 'y':
        return True
    elif answer == 'no' or answer == 'n':
        return False
    else:
        print(f'Invalid Input: \'{answer}\'. Type any of y,yes,n,no')


def get_pyvisa_instr_ID(rm):
    """
    Given a pyvisa RM object, guide the user to figure out which /dev/tty
    port the instrument is connected to.

    TODO check how this works on Mac and Windows and adapt.
    """
    never_skip = False  # for debug
    instrs = list(rm.list_resources())
    if len(instrs) > 1 or never_skip:
        instr_idx = option_list(instrs,
                                'Choose Instrument Port ' +
                                '(press <enter> if you don\'t know):',
                                default='')
        if instr_idx == '':
            print('Determining ID automatically. ' +
                  'Unplug Instrument and press <enter>:')
            input('> ')
            diff = set(instrs) - set(rm.list_resources())
            print(f'These ports were disconnected: {list(diff)}')
            print('Plug Instrument back in and press <enter>:')
            input('> ')
            return get_pyvisa_instr_ID(rm)
    elif len(instrs) == 1:
        print(f'Only one VISA instrument found: {instrs[0]}.')
        instr_idx = 0
    else:
        raise Exception('No (VISA) instrument found :(')
    return instrs[instr_idx]


def option_list(options, prompt='Choose an option:', default=None):
    """
    Parameters:
    ----------
    options: list, options to choose.
    prompt: str, prompt.
    default: default value to return. Can be None.
    allow_none: boolean, whether to retry until a valid option is chosen.
      The alternative is to return None.

    Returns:
    -------
    Index of option, or `default`.
    """
    print(prompt)
    print('\n'.join([f'{i}) {option}' for i, option in enumerate(options)]))
    reply = input('> ' if default is None else f'(default \'{default}\') > ')
    if len(reply) == 0 and default is not None:
        return default
    try:
        idx = int(reply)
        assert idx >= 0
        assert idx < len(options)
        return idx
    except (ValueError, AssertionError):
        print(f'Invalid answer: {reply}. ' +
              f'Choose a value from 0-{len(options)-1}.')
        return option_list(options, prompt=prompt, default=default)
