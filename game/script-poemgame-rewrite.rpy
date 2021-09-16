define POEM_DISLIKE_THRESHOLD = 29
define POEM_LIKE_THRESHOLD = 45

init -1 python:
    import random, json, os

    class PoemWord(object):
        wordlist = [ ]

        def __init__(self, word, **fields):
            self.word = word
            self.glitch = fields.pop("glitch", None)
            self.fields = fields

            self.wordlist.append(self)

        def get_field(self, name, default=None):
            return self.fields.get(name, default)


        # Constructors

        @classmethod
        def load_from_txt(cls, txt):
            with renpy.file(txt) as wordfile:
                for line in wordfile:
                    # Ignore lines beginning with '#' and empty lines
                    line = line.strip()

                    if line == '' or line[0] == '#': continue

                    # File format: word,sPoint,nPoint,yPoint
                    x = line.split(',')
                    cls(
                        word=x[0],
                        sPoint=float(x[1]),
                        nPoint=float(x[2]),
                        yPoint=float(x[3])
                    )

        @classmethod
        def load_from_json(cls, json_path):
            with renpy.file(json_path) as wordfile:
                json_contents = json.load(wordfile)

                for k, v in json_contents.items():
                    cls(
                        k, **v
                    )

        # Export

        @classmethod
        def write_to_json(cls, json_path):
            json_contents = { }

            for word in cls.wordlist:
                json_contents[word.word] = word.fields

            with open(os.path.join(config.gamedir, json_path), "wb+") as wordfile:
                wordfile.write(json.dumps(json_contents, indent=4, sort_keys=False))

    PoemWord.load_from_json("poemwords.json")

init python:
    import random

    class PoemGame(object):
        def __init__(self, callbacks, max_words=20):
            self.callbacks = callbacks
            self.words = PoemWord.wordlist.copy()
            self.current_words = [ ]

            self.word_progress = 0
            self.max_words = 20

            self.points = { 
                "sayori": 0.0,
                "monika": 0.0,
                "natsuki": 0.0,
                "yuri": 0.0,
            }

        def background(self):
            return "bg notebook"

        def iterate_words(self, n=10):
            if not self.current_words:
                self.current_words = [ self.words.pop() for i in random.sample(range(len(self.words)), n) ]
                self.words = [ i for i in self.words if i not in self.current_words ]

            return self.current_words

        def progress(self):
            return "{progress}/{count}".format(progress=self.word_progress + 1, count=self.max_words)

        def process_word(self, word):
            self.points["sayori"] += word.get_field("sPoint", 0.0)
            self.points["yuri"] += word.get_field("yPoint", 0.0)
            self.points["natsuki"] += word.get_field("nPoint", 0.0)
            self.points["monika"] += word.get_field("mPoint", 0.0)
            
            cb = self.callbacks.get("word_callback", None)

            if cb is not None:
                cb(word)

        def _select_word(self, word):
            self.word_progress += 1
            self.current_words = [ ]

            self.process_word(word)

            if self.word_progress >= self.max_words:
                return self.points

        def SelectWord(self, word):
            return Function(self._select_word, word)

init:
    python:
        class ChibiTransform(object):
            def __init__(self):
                self.pos = renpy.random.randint(-1,1)
                self.xzoom = 1
                self.xoffset = 0
                self.time = renpy.random.random() * 4 + 4

            def pause(self, trans, st, at):
                if st > self.time:
                    self.time = renpy.random.random() * 4 + 4
                    return None

                return 0.0

            def move(self, trans, st, at):
                if st > .16:
                    if self.pos > 0:
                        self.pos = renpy.random.randint(-1,0)
                    elif self.pos < 0:
                        self.pos = renpy.random.randint(0,1)
                    else:
                        self.pos = renpy.random.randint(-1,1)

                    if trans.xoffset * self.pos > 5:
                        self.pos *= -1

                    return None

                if self.pos > 0:
                    trans.xzoom = -1
                elif self.pos < 0:
                    trans.xzoom = 1

                trans.xoffset += .16 * 10 * self.pos
                self.xoffset = trans.xoffset
                self.xzoom = trans.xzoom
                return 0.0

        def sticker_pos_xcenter(r):
            start = 100
            d = 120

            return start + d * (r - 1)

        def sticker_pos_yalign(c):
            return 0.5 if c == 1 else 0.9

        class Sticker(object):
            def __init__(self, idle, hop, **kwargs):
                super(Sticker, self).__init__(**kwargs)

                self.transform_animation = ChibiTransform()

                self.idle = renpy.displayable(idle)
                self.hop = renpy.displayable(hop)
                self.in_hop = False

            def set_hop(self):
                self.in_hop = True

            def clear_hop(self):
                self.in_hop = False

            def __call__(self):
                if not self.in_hop:
                    return At(self.idle, sticker_animation(self.transform_animation))

                return At(self.hop, sticker_hop)

    transform sticker_animation(trans_object):
        # function trans_object.pause
        pause 1.0
        parallel:
            sticker_move_n
        parallel:
            function trans_object.move
        repeat

    transform sticker_move_n:
        easein_quad .08 yoffset -15
        easeout_quad .08 yoffset 0

    transform sticker_hop:
        easein_quad .18 yoffset -80
        easeout_quad .18 yoffset 0
        easein_quad .18 yoffset -80
        easeout_quad .18 yoffset 0

    transform sticker_pos(r=1, c=1):
        subpixel True
        xcenter sticker_pos_xcenter(r)
        yalign sticker_pos_yalign(c)

    image m_sticker:
        "gui/poemgame/m_sticker_1.png"

    image m_sticker hop:
        "gui/poemgame/m_sticker_2.png"

    image n_sticker:
        "gui/poemgame/n_sticker_1.png"

    image n_sticker hop:
        "gui/poemgame/n_sticker_2.png"

    image s_sticker:
        "gui/poemgame/s_sticker_1.png"

    image s_sticker hop:
        "gui/poemgame/s_sticker_2.png"

    image y_sticker:
        "gui/poemgame/y_sticker_1.png"

    image y_sticker hop:
        "gui/poemgame/y_sticker_2.png"

    python:
        yuri_sticker = Sticker("y_sticker", "y_sticker hop")
        monika_sticker = Sticker("m_sticker", "m_sticker hop")
        sayori_sticker = Sticker("s_sticker", "s_sticker hop")
        natsuki_sticker = Sticker("n_sticker", "n_sticker hop")

        def callback(word):
            if word.get_field("sPoint", 0.0) >= 3.0:
                sayori_sticker.set_hop()

            if word.get_field("yPoint", 0.0) >= 3.0:
                yuri_sticker.set_hop()

            if word.get_field("nPoint", 0.0) >= 3.0:
                natsuki_sticker.set_hop()

            if word.get_field("mPoint", 0.0) >= 3.0:
                monika_sticker.set_hop()


label poem(transition=True):
    call screen poem_interface()
    $ print(_return)

screen poem_interface():
    style_prefix "poem_interface"

    default poem_game = PoemGame(
        callbacks={
            "word_callback": callback
        }
    )

    add poem_game.background()
    use poem_game_stickers()

    grid 2 5:
        for word in poem_game.iterate_words():
            use poem_word(poem_game, word)

    text _(poem_game.progress())

screen poem_game_stickers():
    for i, sticker in enumerate([ natsuki_sticker, sayori_sticker, monika_sticker, yuri_sticker ]):
        add sticker() at sticker_pos((i % 3) + 1, (i) // 3)

        if sticker.in_hop:
            timer 0.18 * 4.0 action Function(sticker.clear_hop)

style poem_interface_grid:
    xpos 440 ypos 160
    yspacing 56

style poem_interface_text is poemgame_text:
    color "#000"
    xanchor 1.0
    xpos 885 ypos 80

screen poem_word(poem_game, word):
    style_prefix "poem_word"
    fixed:
        textbutton _(word.word) action poem_game.SelectWord(word)

style poem_word_fixed:
    yfit True
    xsize 240

style poem_word_button_text is poemgame_text:
    yalign 0.5