import os
import yaml

def load_bagcheck_file() -> dict:
    global disable_global
    global disable_local

    home_dir = os.path.expanduser('~')

    bagcheck_config = {
        'disable': {
            'global': [],
            'local': []
        }
    }

    global_bagcheck_config = {}
    if os.path.exists(f'{home_dir}/.bagcheck'):
        with open(f'{home_dir}/.bagcheck') as bagcheck_file:
            global_bagcheck_config = yaml.safe_load(bagcheck_file)
        
    local_bagcheck_config = {}
    if os.path.exists(f'.bagcheck'):
        with open(f'.bagcheck') as bagcheck_file:
            local_bagcheck_config = yaml.safe_load(bagcheck_file)

    if 'disable' in global_bagcheck_config:
        if 'global' in global_bagcheck_config['disable']:
            bagcheck_config['disable']['global'] = global_bagcheck_config['disable']['global']
        if 'local' in global_bagcheck_config['disable']:
            bagcheck_config['disable']['local'] = global_bagcheck_config['disable']['local']

    if 'disable' in local_bagcheck_config:
        if 'global' in local_bagcheck_config['disable']:
            bagcheck_config['disable']['global'] += local_bagcheck_config['disable']['global']
            bagcheck_config['disable']['global'] = list(set(bagcheck_config['disable']['global']))
        if 'local' in local_bagcheck_config['disable']:
            for local_ignore in local_bagcheck_config['disable']['local']:
                path_exists = False
                for idx, current_local_ignore in enumerate(bagcheck_config['disable']['local']):
                    if local_ignore['path'] == current_local_ignore['path']:
                        bagcheck_config['disable']['local'][idx]['tests'] += local_ignore['test']
                        bagcheck_config['disable']['local'][idx]['tests'] = list(set(bagcheck_config['disable']['local'][idx]['tests']))
                        path_exists = True
                        break
                if not path_exists:
                    bagcheck_config['disable']['local'].append(local_ignore)

    return bagcheck_config
