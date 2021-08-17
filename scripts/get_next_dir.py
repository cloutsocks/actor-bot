import os

def make_next_dir(path, allow_empty=False, separator='_'):
    n = 0
    target_path = path
    while True:
        if os.path.exists(target_path):
            if allow_empty and not any(os.scandir(target_path)):
                return target_path
        else:
            os.makedirs(target_path)
            return target_path
        n += 1
        target_path = f'{path}{separator}{n}'
