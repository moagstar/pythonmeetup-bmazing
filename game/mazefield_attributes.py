


class Path(object):
    def __str__(self):
        return ' '


class Wall(object):
    def __str__(self):
        return '#'


class Finish(object):
    def __str__(self):
        return '='


class Start(Path):
    def __str__(self):
        return '0'
