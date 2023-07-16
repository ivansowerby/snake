# Snake

> [insert python joke]

- [Snake](#snake)
  - [Brief Introduction](#brief-introduction)
  - [Process Overview](#process-overview)
    - [Command-line (CLI)](#command-line-cli)
    - [Browser (BUI)](#browser-bui)
  - [Customisation](#customisation)
    - [Command-line (CLI)](#command-line-cli-1)
      - [Glyphs (characters)](#glyphs-characters)
      - [Resolution (width \& height)](#resolution-width--height)
    - [Browser (BUI)](#browser-bui-1)
      - [Colours](#colours)
      - [Resolution (width \& height)](#resolution-width--height-1)
  - [Installation](#installation)
    - [Powershell](#powershell)
    - [Bourne shell](#bourne-shell)
  - [Execution](#execution)
    - [Windows](#windows)
    - [Unix-like](#unix-like)

## Brief Introduction
---

An implementation of Snake (game), managing **objects**, **groups**, and (their) **attributes** with [Ludus](https://github.com/ivanl-exe/ludus). Along with **users** and their **personalities** (high score), by JSON. Manually playable by either a **CLI** (Command-Line Interface) using unicode **glyph** **attributes** - customisable by TOML, or by a **BUI** (Browser-User Interface) using the [Eel](https://github.com/python-eel/Eel) (python) package to host a webpage on [localhost:8000](http://localhost:8000). Whereby an **API** (Application Program Interface) allows the front-end Java-Script to access the backend Python, managing the game. To then display on the front-end, and take any browser inputs - using (minismised) jQuery and HTML5 canvas element(s) - customisable by JSON

## Process Overview
---

### Command-line (CLI)

1. Initiate the `Snake` class
2. `while` the the game is not over (`Snake.is_game_over`) continue
   1. Render (`Snake.render`) a frame of the game to the console, taking the `glyph` attribute of each, or the codepoint of the `blank` glyph if not an object coordinate
   2. `sleep`, as to delay the next instructions (giving time between frames, to be at a sensible speed) 
   3. Update (`Snake.update`) the game to the next frame, as by moving the snake in the direction of `velocity` of the head, shifting all velocities, and enforcing (`Snake.__enforce__`) the rules. For example:
      * If the snake were to collide with itself or the wall, killing the snake, and so ending the game
      * If the snake head were to collide/intercept with the coordinate of food, then removing the food (consumed), to then extend the length (by 1) of the snake

### Browser (BUI)

1. Initiate (`eel.init`) [Eel](https://github.com/python-eel/Eel), hooking it to the [web](src/web) directory/folder
2. Start (`eel.start`) by hosting a webpage on [localhost](http://localhost:8000), port 8000, opening the (Chrome) browser (in application mode) 
3. Get the `#snake-game-canvas`, and assign a variable (`ctx`) to the `2d` context of this canvas
4. `window.begin`
   1. Copy the width of `snake-game-canvas` by loading in [canvas.json](src/web/json/canvas.json) (with `loadJSON`) to the global width variable (`window.width`)
      1. Send an API request to begin (`eel.snakeBegin`) the snake game
         1. Hook a `keypress` event `.on` the body of the HTML document/page, such as to set the snake's direction (`eel.snakeSetDirection`) by an API request - only after having translating (`translateKey`) the key to a valid direction (as to active the relative on-screen button)
         2. Copy the attributes by loading [attributes.json](src/web/json/attributes.json) (with `loadJSON`) to the global attributes variable (`window.attributes`) 
            1. `render` immediately as to not halt the user from seeing the game prior to the first `update`
            2. `initiateInterval` of `update`, at an interval of `100`ms
5. Call `update`, as to continually animate the game
   1. Update (`eel.snakeUpdate`) the snake game instance - calling `Snake.update`, and passing an string argument of the current username (`window.username`), to be passed to the `Snake.scoreboard` function. As to store a high score for that user (if applicable) as a dump to [users.json](src/snake/json/users.json)
   2. Check if the game is over (`eel.snakeIsGameOver`) with an API request, if so `clearInterval` as to prevent updating the finished game (resulting in an error raised of a missing snake body), otherwise update the current score (`editCurrentScore`) from the snake length (`eel.snakeLength`) and update the high score (`editHighScore`) if applicable`
1. Call `render`, as to draw and display the objects (including the grid) onto the `#snake-game-canvas`
   1. Get the objects (`eel.getObjects`) of the game by an API request, copy to the internal object of `_objects`
   2. Get the groups' attributes (`eel.getAttributes`) of the game by an API request, copy to the internal object of `_attributes`
      1. Sort the objects into `layers` of their body coordinates, by `priorityLevel`, in ascending order
      2. `draw` each object in ascending `priorityLevel` onto `#snake-game-canvas` by filling a rectangle, using the respective colour found in [attributes.json](src/web/json/attributes.json) for each group
   3. Draw a grid (`drawGrid`) using the respective colour found in [attributes.json](src/web/json/attributes.json), to easily differentiate coordinates

## Customisation
---

Both styles of play, whether that be **command-line** (CLI) or **browser** (BUI) have customisable interfaces, using JSON and TOML files (whichever I found most appropriate, i.e. for JS exclusively JSON)

### Command-line (CLI)

#### Glyphs (characters)

To customise how `Snake.render` prints (a frame of) the game, edit [snake/attributes/toml/attributes.toml](src/snake/toml/attributes.toml). By default the given codepoints of the glyphs of `wall`, `snake`, `food`, and `track` are shown as the unicode character commented after. To change, simply change the codepoint to another unicode character

*there **MUST** be a `U+` prefix before the unicode codepoint, otherwise no character will be printed for that group*

#### Resolution (width & height)

To customise the resolution, the `width` and `height` can be passed as integer arguments when initiating the `Snake` class instance. Where the default value for both is `20`

### Browser (BUI)

#### Colours

To customise the colour of **groups** displayed on the HTML5 canvas in the browser, edit [web/json/attributes.json](src/web/json/attributes.json). These can be changed, and do not necessarily need to be hex(adecimal) codes (for example `rgb(255, 0, 0)` would be the same as `#FF0000`, and even the colour keyword `red`)

*for my ease, I have used British English spellings throughout the application, **UNLESS** necessary - such as in CSS - however may update with workarounds later (for example postcss)*

#### Resolution (width & height)

To customise the resolution, the width (passed to the `Snake` class) can be changed by editing the integer value to key `width` of `snake-game-canvas` in [web/json/canvas.json](src/web/json/canvas.json), whereas the height is determined by the `aspect-ratio` of the `#snake-game-canvas` canvas (set in [style.css](src/web/css/style.css)), this is to keep the 

*for example, by default the `#snake-game-canvas` has a `aspect-ratio: 4/3`*

## Installation
---

For execution python`>=3` needs to be installed, with the [standard library](https://docs.python.org/3/library/), with the additional packages found in [requirements.txt](src/requirements.txt). These can be installed using `pip` `install` with the `-r` flag - or simply by executing either:

### Powershell

``` shell
./install.ps1
```

### Bourne shell

(Linux, macOS)

``` shell
./install.sh
```

## Execution
---

### Windows

``` shell
python main.py
```

### Unix-like

(Linux, macOS)

``` shell
python3 main.py
```