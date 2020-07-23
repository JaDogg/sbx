### 📚📦 StudyBox (SBX) - Terminal Flashcards

![screenshot](https://github.com/JaDogg/sbx/blob/master/images/screenshot1.png?raw=true "Screenshot")

### Credits 🙇‍♂️
* Sm2 - Algorithm by Super Memo
* prompt-toolkit - TUI library. 😎

### Why ? 🤔
* Wanted a flashcard solution that uses markdown.
* I wanted to memorise useful information.
* GitHub/Gitlab/etc,.. readable flashcards.

### Installation (Unix, Windows)

#### Install with pipx
```bash
git clone git@github.com:JaDogg/sbx.git
cd sbx
pipx install .
```

#### Install with setup.py
```bash
git clone git@github.com:JaDogg/sbx.git
cd sbx
python setup.py install
```

### Features
* It's markdown. (You can use your own editor, as long as you maintain comments in it)
* Syntax highlighting.
* List files. (leech, last one marked with lowest score, include all, etc.)
* Use your own folder structure. (Study at any level in your structure, recursive or not is up to you)
* Built in editor which shows front and back of the flashcards.
* Push your files to github and you can read them.

### TODO:
* [ ] Support tags.
* [ ] Plugin Support
* [ ] Configurable Keys
* [ ] Statistics?
* [ ] Support ASCII drawing
* [ ] Support for different algorithms.
* [x] Support for leech detection
* [x] Leech in info box
* [ ] Leech in different colour? 
* [x] Leech in list
* [x] Last quality zero in list
* [ ] Test with 100,000 cards (Performance)
* [ ] Auto Save Plugin?
* [ ] ASCII Plugin
* [x] Make the scratch pad editable always
* [x] No need to have 1-6 shortcuts
* [x] On show or when 1-6 is clicked focus on the text box
	* So you can practice
* [x] Keep the last sessions in a string (string stack) :)
* [ ] ~Create a new algorithm that can use a gradient descent based on past scores need minimum 5 items but if we have about 20 or more we can be more confident.~ - maybe later 
* [ ] Implement Sm2+ 
* [ ] Implement Sm4
* [x] Past stat graph 
```
-  |
q 6|             ** *
u 5|            *  * 
a 4|     ***** * 
l 3| *   *     *
i 2|* * *
t 1|   *
y 0|
-  ---------------------
    1       10        20
       -- reps --
```
