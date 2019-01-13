from django.shortcuts import render, HttpResponse
from GameFile import GameFileManager
import Python
import random
from django.http import Http404
import operator
import pygame

# This is a global needed to battle sound instance
battleStart = False

def index(request):
    usr = ''
    return render(request, "index.html", {'commands':{
        'btn_a':'/worldmap?new_game',
        'btn_b':'/options/load_game',
        'btn_start':'#',
        'btn_select':'#',
        'btn_up':'#',
        'btn_lft':'#',
        'btn_rgt':'#',
        'btn_dwn':'#',
        },
        'usr':usr
        })


def butn_from_pos(pos):
    if pos is None:
        return "#"
    else:
        return "/worldmap?x={}&y={}".format(pos[0], pos[1])


def worldmap(request):
    gfm = GameFileManager()
    message= None
    btn_a = "#"

    pygame.mixer.init()
    pygame.mixer.music.stop()
    global battleStart
    battleStart = False

    if request.method =='GET' and 'new_game' in request.GET:
        game = Python.Game().load_default_settings()
    else:
        game = gfm.getCurrent()

    if request.method == 'GET' and 'x' in request.GET and 'y' in request.GET:
        try:
            x = int(request.GET.get('x', 0))
            y = int(request.GET.get('y', 0))

            pos_adjasc =[(x, y + 1), (x, y - 1 ), (x - 1, y), (x + 1, y)]

            game.go_to_position((x, y))

            print ("Ball_indicator:  {}".format(game.ball_indicator))
            if game.ball_indicator:
                game.balls += 1
                game.ball_indicator = False

            event = random.randint(0,5)

            if event == 0:
                game.ball_indicator = True
                while 42:
                    test = pos_adjasc[random.randint(0,3)]
                    res = game.get_ball_map(test)
                    if res != -1:
                        break
                message = "You found a ball, youpee!"
            if event == 1:
                movid = game.get_random_movie()
                if movid is not None:
                    while 42:
                        test = pos_adjasc[random.randint(0,3)]
                        res = game.get_moviemon_map(test)
                        if res != -1:
                            break
                    message = "You found a Moviemon, press A to capture!"
                    btn_a = "/battle/"+movid
        except:
            pass
    #print(game.dump())
    game.get_movie("tt0365748")
    gfm.persist(game)
    return render(request, "Worldmap.html", {'commands':{
        'btn_a':btn_a,
        'btn_b':'#',
        'btn_start':'/options',
        'btn_select':'/moviedex',
        'btn_up':butn_from_pos(game.get_up_pos()),
        'btn_lft':butn_from_pos(game.get_lft_pos()),
        'btn_rgt':butn_from_pos(game.get_rgt_pos()),
        'btn_dwn':butn_from_pos(game.get_dwn_pos()),
        },
        'grid_size':(range(0, game.grid_size[1]), range(0, game.grid_size[0])),
        'ply_position':game.ply_position,
        'movid_position': game.movid_position,
        'ball_position': game.ball_position,
        'balls':game.balls,
        'message':message,
        })


def load(request):
    gfm = GameFileManager()
    game = gfm.getCurrent()
    msg = None

    if request.method =='GET' and 'load_from' in request.GET and request.GET['load_from'] in ("a", "b", "c"):
        selected = request.GET['load_from']
    else:
        selected = "a"
    btn_a = '/options/load_game?load_from='+selected+"&load"
    if request.method =='GET' and 'load' in request.GET:
        game = gfm.load_save(request.GET['load_from'])
        if game is not None:
            msg = "File loaded from slot "+request.GET['load_from']
            gfm.persist(game)
            btn_a = "/worldmap"
        saves = gfm.get_saves()
    caugh ={'A':None, 'B':None, 'C':None}
    for key,save in saves.items():
        if save is not None:
            caugh[key]=str(len(save.caugh))+"/"+str(len(save.moviemons_ids))
    if selected == "a":
        lft = "/options/load_game?load_from=c"
        rgt = "/options/load_game?load_from=b"
    if selected == "b":
        lft = "/options/load_game?load_from=a"
        rgt = "/options/load_game?load_from=c"
    if selected == "c":
        lft = "/options/load_game?load_from=b"
        rgt = "/options/load_game?load_from=a"
    return render(request, "Option/load.html", {'commands':{
        'btn_a':btn_a,
        'btn_b':'',
        'btn_start':'/worldmap',
        'btn_select':'#',
        'btn_up':lft,
        'btn_lft':lft,
        'btn_rgt':rgt,
        'btn_dwn':rgt,
        },
        'savefile':saves,
        'message':msg,
        'caugh':caugh,
        'selected':selected.upper()
        })

def battle(request, match):
    gfm = GameFileManager()
    game = gfm.getCurrent()
    if match not in game.get_free_movies():
        raise Http404("You can't capture that Moviemon")
    details = game.get_movie(match)

    pygame.mixer.init()
    global battleStart
    if battleStart == False:
        pygame.mixer.music.load('app/static/sound/battle.mp3')
        pygame.mixer.music.play(100)
        battleStart = True
    catchFailed = False

    msg = "Battle!!!"
    cmd_a = "Press A to try and get it"
    disable_a = None
    movieball_lnch = '/battle/'+match+"?launch"
    rate = int(50 - (float(details['imdbRating']) * 10) + (game.get_strength() * 5))
    strength_movie = int(float(details['imdbRating']))
    if rate < 1:
        rate = 1
    if rate > 90:
        rate = 90
    if request.method =='GET' and 'launch' in request.GET:
        if game.balls > 0:
            game.balls -= 1
            tentative = random.randint(0, 100)
            if tentative <= rate:
                #captured
                msg = "The Movie Has been captured!"
                pygame.mixer.music.load('app/static/sound/victory.mp3')
                pygame.mixer.music.play()
                game.caugh.append(match)
                cmd_a = None
                movieball_lnch = "#"
                disable_a = True
            else:
                catchFailed = True
                msg = "You failed, you big failure!"

    gfm.persist(game)
    return render(request, "battle.html", {'commands':{
        'btn_a':movieball_lnch,
        'btn_b':'/worldmap',
        'btn_start':'#',
        'btn_select':'#',
        'btn_up':'#',
        'btn_lft':'#',
        'btn_rgt':'#',
        'btn_dwn':'#',
        },
        'strength':game.get_strength(),
        'balls': game.balls,
        'rate' : rate,
        'strength_movie' : strength_movie,
        'cmd_a': cmd_a,
        'message':msg,
        'catchFailed': catchFailed,
        'img': details['Poster'],
        'disable_a': disable_a,
        'title':details['Title'],
        })


def moviedex(request):
    gfm = GameFileManager()
    game = gfm.getCurrent()
    x = None
    x = { row : game.get_movie(row)['Poster'] for row in game.caugh }
    if request.method == 'GET' and 'selected' in request.GET:
        try:
            selected = int(request.GET.get('selected', 0))
        except:
            selected = 0
    else:
        selected=0
    btn_lft = "#"
    btn_rgt = "#"
    moviedex_dtl = "#"
    select_id = None
    sort = sorted(x.items(), key=operator.itemgetter(0))
    # print('test')
    # print(sort)
    if len(game.caugh) > 0:
        empty = False
        selected = selected % len(game.caugh)
        select_id = sort[selected][0]
        btn_lft = "/moviedex?selected="+str(game.get_left_select(selected))
        btn_rgt = "/moviedex?selected="+str(game.get_right_select(selected))
        moviedex_dtl = 'moviedex/'+select_id
        btn_a = '/moviedex/'+select_id
    else:
        empty = True
        btn_a = '#'

    return render(request, "moviedex.html", {'commands':{
        # 'btn_a':,
        'btn_a': btn_a,
        'btn_b':'#',
        'btn_start':'#',
        'btn_select':'/worldmap',
        'btn_up':'#',
        'btn_lft':btn_lft,
        'btn_rgt':btn_rgt,
        'btn_dwn':'#',
        },'movies': x,
        'selected': select_id,
        'movies2': sort,
        'empty': empty,
        'len':len(sort)
        })

def detail(request, match):
    gfm = GameFileManager()
    game = gfm.getCurrent()

    if match not in game.caugh:
        raise Http404("You can't capture that Moviemon")

    x = game.get_movie(match)
    # print(len(x));
    # print(x)

    usr = ''
    movie_name = "movie"
    moviedex_dtl = 'moviedex/'+movie_name

    # Send eleme`nts to the template
    return render(request, "detail.html", {
        'commands':{
            'btn_a':'#',
            'btn_b':'/moviedex',
            'btn_start':'#',
            'btn_select':'/worldmap',
            'btn_up':'#',
            'btn_lft':'#',
            'btn_rgt':'#',
            'btn_dwn':'#',
        },'movie': x,
    })

# /**
#  * Handle the save view
#  */
def option(request):
    # Send eleme`nts to the template
    return render(request, "option.html", {
        'commands':{
            'btn_a':'/options/save_game',
            'btn_b':'/',
            'btn_start':'/worldmap',
            'btn_select':'#',
            'btn_up':'#',
            'btn_lft':'#',
            'btn_rgt':'#',
            'btn_dwn':'#',
        },
    })

# /**
#  * Handle the save view
#  */
def save(request):
    gfm = GameFileManager()
    game = gfm.getCurrent()
    msg = None

    if request.method =='GET' and 'save_to' in request.GET and request.GET['save_to'] in ("a", "b", "c"):
        selected = request.GET['save_to']
    else:
        selected = "a"

    if request.method =='GET' and 'save' in request.GET:
        gfm.persist_save(request.GET['save_to'])
        msg = "File saved to slot "+request.GET['save_to']

    # Default svae slot configuration
    caugh ={'A':None, 'B':None, 'C':None}

    # Get save files
    saves = gfm.get_saves()

    # Fill party slot if there is a saved party
    for key,save in saves.items():
        if save is not None:
            caugh[key]=str(len(save.caugh))+"/"+str(len(save.moviemons_ids))

    # Save in slot A
    if selected == "a":
        lft = "/options/save_game?save_to=c"
        rgt = "/options/save_game?save_to=b"

    # Save in slot B
    if selected == "b":
        lft = "/options/save_game?save_to=a"
        rgt = "/options/save_game?save_to=c"

    # Save in slot C
    if selected == "c":
        lft = "/options/save_game?save_to=b"
        rgt = "/options/save_game?save_to=a"

    # Send eleme`nts to the template
    return render(request, "save.html", {
        'commands':{
            'btn_a':'/options/save_game?save_to='+selected+"&save",
            'btn_b':'/options',
            'btn_start':'/worldmap',
            'btn_select':'#',
            'btn_up':lft,
            'btn_lft':lft,
            'btn_rgt':rgt,
            'btn_dwn':rgt,
        },
        'savefile':saves,
        'message':msg,
        'caugh':caugh,
        'selected':selected.upper()
    })

# /**
#  * Handle the load view
#  */
def load(request):
    gfm = GameFileManager()
    game = gfm.getCurrent()
    msg = None
    isLoad = "A - load game"

    if request.method =='GET' and 'load_from' in request.GET and request.GET['load_from'] in ("a", "b", "c"):
        selected = request.GET['load_from']
    else:
        selected = "a"

    btn_a = '/load?load_from='+selected+"&load"

    if request.method =='GET' and 'load' in request.GET:
        game = gfm.load_save(request.GET['load_from'])
        if game is not None:
            isLoad = "A - start game"
            msg = "File loaded from slot "+request.GET['load_from']
            gfm.persist(game)
            btn_a = "/worldmap"

    # Default svae slot configuration
    caugh ={'A':None, 'B':None, 'C':None}

    # Get save files
    saves = gfm.get_saves()

    # Fill party slot if there is a saved party
    for key,save in saves.items():
        if save is not None:
            caugh[key]=str(len(save.caugh))+"/"+str(len(save.moviemons_ids))

    # Load slot A
    if selected == "a":
        lft = "/load?load_from=c"
        rgt = "/load?load_from=b"

    # Load slot B
    if selected == "b":
        lft = "/load?load_from=a"
        rgt = "/load?load_from=c"

    # Load slot C
    if selected == "c":
        lft = "/load?load_from=b"
        rgt = "/load?load_from=a"

    # Send elements to the template
    return render(request, "load.html", {
        'commands': {
            'btn_a':btn_a,
            'btn_b':'/',
            'btn_start':'#',
            'btn_select':'#',
            'btn_up':lft,
            'btn_lft':lft,
            'btn_rgt':rgt,
            'btn_dwn':rgt,
        },
        'isLoad': isLoad,
        'savefile':saves,
        'message':msg,
        'caugh':caugh,
        'selected':selected.upper()
    })
