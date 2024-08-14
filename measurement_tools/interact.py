"""
Alec Vercruysse
2023-06
"""
import json
import os
import pprint


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
        return confirm(question, default=default)


def get_pyvisa_instr_ID(rm, mytype=None, skip_confirm=True):
    """
    Given a pyvisa RM object, guide the user to figure out which /dev/tty
    port the instrument is connected to. This creates a .measurement-tools
    file in the current directory that caches which pyvisa ID corresponds
    to which calling class. When a class (e.g. LaserDriver calls this function
    to get an ID, it provides a 'mytype' value to store as an ID. Next time
    a script is run, the ID is remembered.

    Arguments:
    ---------
    mytype: any, optional, default None.
    identifier to associate the pyvisa ID with in the .measurement_tools cache.

    TODO check how this works on Mac and Windows and adapt.
    """
    if os.path.exists('.measurement_tools'):
        with open('.measurement_tools', 'r') as f:
            cache = json.load(f)
        if mytype is not None and mytype in cache:
            print(f'Found previous assignment of {mytype}->{cache[mytype]}')
            if skip_confirm or confirm("Use this VISA ID?"):
                return cache[mytype]
    else:
        cache = None
    instrs = sorted(list(rm.list_resources()))
    names_in_use = [n.resource_name for n in rm.list_opened_resources()]
    if len(names_in_use) > 0:
        print(f"Note: ingoring {names_in_use} since already in use.")
    instrs = sorted(list(set(instrs) - set(names_in_use)))
    instr_options = instrs.copy()
    if cache is not None:
        for idx, instr in enumerate(instr_options):
            if instr in cache.values():
                hint = list(cache.keys())[list(cache.values()).index(instr)]
                instr_options[idx] = f'{instr} (cached: <- {hint} )'
    if len(instrs) > 1:
        instr_idx = option_list(instr_options,
                                'Choose Instrument VISA ID ' +
                                '(press <enter> if you don\'t know):',
                                default='')
        if instr_idx == '':
            print('Determining ID automatically. ' +
                  'Unplug Instrument and press <enter>:')
            input('> ')
            diff = set(instrs) - set(rm.list_resources())
            print(f'These IDs were disconnected: {list(diff)}')
            if cache is not None:
                print('The following assignments were found in the cache:')
                pprint.pprint(cache)
            print('Plug Instrument back in and press <enter>:')
            input('> ')
            return get_pyvisa_instr_ID(rm)
    elif len(instrs) == 1:
        print(f'Only one unopened VISA instrument found: {instrs[0]}.')
        instr_idx = 0
    else:
        raise Exception('No unopened (VISA) instrument found :(')

    if os.path.exists('.measurement_tools'):
        if mytype is not None and confirm(
                f'Remember {mytype}->{instrs[instr_idx]} in the future?'):
            cache[mytype] = instrs[instr_idx]
            with open('.measurement_tools', 'w') as f:
                json.dump(cache, f)
    elif mytype is not None and confirm(
            'Create cache file .measurement_tools to ' +
            'remember device ID in the future?'):
        cache = {mytype: instrs[instr_idx]}
        with open('.measurement_tools', 'w') as f:
            json.dump(cache, f)
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
