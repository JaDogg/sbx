# Usage Guide

* `sbx` is a command line application.
* `sbx` is also a python library.
	* This means you can write your own scripts using `sbx.core` features.

## Help

```bash
# To get help for sbx try running
sbx --help
```

## Q & A

### How do I create a new card file?

```bash
sbx create python-for-loop.md
```
* You can now edit it using any editor.

### How do I edit a card file using built in editor?

```bash
sbx edit python-for-loop.md
```

### How do I list files I need to study today with recursive scanning?

```bash
cd my-flash-cards-location
sbx list -rn .
```

### I want to reset the state of a flash card, How do I do it?

```bash
sbx reset java-iterable.md
```

### How do I reset all cards in a directory (ex: 'coding')

```bash
sbx list -irn coding | tr '\n' '\0' | xargs -0 -L1 sbx reset
```

* Parameter `-i` include all files.
* Parameter `-r` searches recursively.
* Parameter `-n` lists only names.
* `tr` command converts new lines to zero terminated.
* `xargs` splits by zero (`-0`), uses only 1 input (`-L1`) and call `sbx reset FILENAME`
* (This assumes bash like shell in unix environment with `tr` and `xargs` present).

### I want to list cards that I don't remember properly?

```bash
cd my-flash-cards-location
sbx list -rnil .
```

* Parameter `-r` searches recursively.
* Parameter `-n` lists only names.
* Parameter `-i` include all files.
* Parameter `-l` filter by leech cards.

### I marked some cards as zero last time, how do I find them?

```bash
cd my-flash-cards-location
sbx list -rniz .
```

* Parameter `-r` searches recursively.
* Parameter `-n` lists only names.
* Parameter `-i` include all files.
* Parameter `-z` only list cards that were last marked as zero.

### How do I start a study session for content in current directory (non-recursive)?

```bash
cd exam-cards
sbx study .
```

Or 

```bash
sbx study exam-cards
```

* In this mode you get to first guess the answer.
* You can type it in scratch pad area.
* Scratch pad area get reset when you go to next card.
* After selecting a show back, you can then select how much you remember.
* Press `F1` for help. (Note: Some terminal emulators might associate it with something else)


### How do I exit a study session or editing?

* Press `Ctrl+E` to exit. (This is the default shortcut)


### How do I write a file after editing it?

* Press `Ctrl+W to write`.

### How do I navigate in edit session or study session?

* Press `Ctrl + arrow keys`.
