import sys, os, pickle
from django.conf import settings
import Python
import glob

class GameFileManager():

    def __init__(self):
        self.current_filename = settings.SAVE_FILE

    def getFileName(self, nb):
        return "{}{}".format(self.current_filename, nb)

    def getCurrent(self):
        current = self.load_from_file(self.current_filename)
        if current is None:
            return Python.Game().load_default_settings()
        else:
            return current

    def persist_to_file(self, game, fn):
        try:
            with open(fn, "wb") as f:
                print(pickle.dump(game.dump(), f))
        except:
            pass

    def persist(self, game):
        self.persist_to_file(game, self.current_filename)

    def load_from_file(self, fn):
        try:
            with open(fn, "rb") as f:
                return Python.Game().load(pickle.load(f))
        except:
            return None

    def load_save(self, ltr):
        fn = glob.glob("saved_game/slot"+ltr+"_*_*.mmg")
        print("saved_game/slot"+ltr+"_*_*.mmg")
        print(fn)
        try:
            with open(fn[0], "rb") as f:
                return Python.Game().load(pickle.load(f))
        except:
            return None

    def get_saves(self):
        return ({
            "A":self.load_save("a"),
            "B":self.load_save("b"),
            "C":self.load_save("c"),
            })

    def persist_save(self, ltr):
        fns = glob.glob("saved_game/slot"+ltr+"_*_*.mmg")
        print(fns)
        try:
            os.mkdir("saved_game")
        except:
            pass
        try:
            for fn in fns:
                os.unlink(fn)
            game = self.getCurrent()
            fn = "saved_game/slot"+ltr+"_"+str(len(game.caugh))+"_"+str(len(game.moviemons_ids))+".mmg"
            self.persist_to_file(game, fn)
        except Exception as e:
            print (e)
