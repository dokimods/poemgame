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

init python:
    import random

    class PoemGame(object):
        def __init__(self, max_words=20):
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
            
            if word.get_field("sPoint", 0.0) >= 3:
                renpy.show("s_sticker hop", layer="screens")
            if word.get_field("nPoint", 0.0) >= 3:
                renpy.show("n_sticker hop", layer="screens")
            if word.get_field("yPoint", 0.0) >= 3:
                renpy.show("y_sticker hop", layer="screens")
            if word.get_field("mPoint", 0.0) >= 3:
                renpy.show("m_sticker hop", layer="screens")

        def _select_word(self, word):
            self.word_progress += 1
            self.current_words = [ ]

            self.process_word(word)

            if self.word_progress >= self.max_words:
                return self.points

        def SelectWord(self, word):
            return Function(self._select_word, word)

label poem(transition=True):
    show m_sticker at sticker_mid onlayer screens zorder 10:
        yalign 0.45
    show s_sticker at sticker_left onlayer screens zorder 10
    show n_sticker at sticker_mid onlayer screens zorder 10
    show y_sticker at sticker_right onlayer screens zorder 10

    call screen poem_interface()
    $ print(_return)

screen poem_interface():
    style_prefix "poem_interface"

    default poem_game = PoemGame()

    add poem_game.background()

    grid 2 5:
        for word in poem_game.iterate_words():
            use poem_word(poem_game, word)

    text _(poem_game.progress())

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