import sys, random, requests
from django.conf import settings


class Game():

    def __init__(self):
        self.ply_str = 10
        self.moviemons_ids = ()
        self.movid_position = ((),)
        self.ball_position = ((),)
        self.ball_indicator = False
        self.catchFaile = False
        self.caugh = []
        self.ply_position = (0, 0)
        self.grid_size = (10, 10)
        self.balls = 0

    """Charge les données de jeu passés en paramètres dans l’instance de classe.
    Retourne l’instance courante."""
    def load(self, param_dict):
        self.ply_str = param_dict['ply_str']
        self.movid_position = ((),)
        self.ball_position = ((),)
        self.ball_indicator = param_dict['ball_indicator']
        self.moviemons_ids = param_dict['moviemons_ids']
        self.caugh = param_dict['caugh']
        self.ply_position = param_dict['ply_position']
        self.grid_size = param_dict['grid_size']
        self.balls = param_dict['balls']
        return self

    """Retourne les données de jeu."""
    def dump(self):
        return {'ply_str':self.ply_str,
                'moviemons_ids':self.moviemons_ids,
                'movid_position': self.movid_position,
                'ball_position': self.ball_position,
                'ball_indicator': self.ball_indicator,
                'caugh':self.caugh,
                'ply_position':self.ply_position,
                'grid_size':self.grid_size,
                'balls':self.balls
                }

    def get_free_movies(self):
        return [item for item in self.moviemons_ids if item not in self.caugh]


    """Retourne un Moviemon au hasard parmis les Moviemonsnon capturés."""
    def get_random_movie(self):
        return random.choice([item for item in self.moviemons_ids if item not in self.caugh])

    """Charge les données de jeu dans l’instance de classe depuis
    les settings. Requête et stocke les détails de tous les Moviemons sur IMDB. Retourne
    l’instance courante."""
    def load_default_settings(self):
        self.moviemons_ids = settings.MOVIES
        self.ply_position = settings.START_POSITION
        self.grid_size = settings.GRID_SIZE
        self.balls = settings.BALLS
        self.movid_position = ((),)
        self.ball_position = ((),)
        # self.ball_indicator = False
        return self

    """Retourne la force du joueur"""
    def get_strength(self):
        return self.ply_str

    """ Retourne un dictionnaire Python contenant tous les détails depuis
    le nom du Moviemon passé en paramètre et nécessaires à la page Detail."""
    def get_movie(self, id):
        url = 'http://www.omdbapi.com/'
        param = {'apikey':settings.TOKEN_OMDB, 'i':id}
        try:
            r = requests.get(url,params=param)
        except:
            return {}
        return r.json()


    def go_to_position(self, pos):
        if (pos[0] < 0 or pos[0] >= self.grid_size[0] or pos[1] < 0 or pos[1] >= self.grid_size[1]):
            return self
        move_x = self.ply_position[0] - pos[0]
        move_y = self.ply_position[1] - pos[1]
        if ((move_x == 1 or move_x == -1) and move_y == 0):
            self.ply_position = pos
            return self
        elif ((move_y == 1 or move_y == -1) and move_x == 0):
            self.ply_position = pos
            return self
        else:
            return self

    def get_moviemon_map(self, pos):
        if (pos[0] < 0 or pos[0] >= self.grid_size[0] or pos[1] < 0 or pos[1] >= self.grid_size[1]):
                return -1
        self.movid_position = pos
        return self

    def get_ball_map(self, pos):
        if (pos[0] < 0 or pos[0] >= self.grid_size[0] or pos[1] < 0 or pos[1] >= self.grid_size[1]):
                return -1
        self.ball_position = pos
        return self

    def get_right_select(self, pos):
        size = len(self.caugh)
        pos += 1
        while pos < 0:
            pos += size
        return pos % size

    def get_left_select(self, pos):
        size = len(self.caugh)
        pos -= 1
        while pos < 0:
            pos += size
        return pos % size

    def get_up_pos(self):
        if self.ply_position[1] == 0:
            return None
        else:
            return (self.ply_position[0], self.ply_position[1] - 1)

    def get_dwn_pos(self):
        if self.ply_position[1] >= self.grid_size[1] - 1:
            return None
        else:
            return (self.ply_position[0], self.ply_position[1] + 1)

    def get_lft_pos(self):
        if self.ply_position[0] == 0:
            return None
        else:
            return (self.ply_position[0] - 1, self.ply_position[1])

    def get_rgt_pos(self):
        if self.ply_position[0] >= self.grid_size[0] - 1:
            return None
        else:
            return (self.ply_position[0] + 1, self.ply_position[1])
