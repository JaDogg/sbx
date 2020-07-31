# SBX File Format
* Study box uses markdown files with HTML comments.

## Structure

```
1|<!-- | {"a": 0, "b": 1, "c": 1.3, "reps": 7, "last": 1591825714, 
  	"next": 1591912114, "pastq": "2105302", "algo": "sm2", "sbx": "v1"} | -->
2|<!-- [[FRONT]] -->
3|# Front of the card goes here
4|
5|<!-- [[BACK]] -->
6|* This is the back of the card
7|
```
* Files without headers are ignored. So it's safer to have files such as `README.md`.

### Header
* In every card file **first line** need to contain an HTML comment with an embedded JSON content.
	* In addition to this JSON should be surrounded by PIPEs. (PIPE is not expected to be present in JSON strings)
* Why are all headers in first line?
	* Only need to load first line to see if it's scheduled & other meta data.
	* We can load rest of the file if required.

### Registers
* JSON header will have following registers.

```
{
# ----- Optional ----
"a"           # number
"b"           # number
"c"           # number
"d"           # number
"e"           # number
"f"           # bool
"g"           # bool
"h"           # string
# ---- Required ----
"reps"        # number
"last"        # number
"next"        # number
"pastq"       # string
"algo": "sm2" # string
"sbx": "v1",  # string
}
```

* Why registers?
	* Support different algorithms using a same structure.
	* Only used for optional registers that are used by an algorithm.
	* Algorithm oblivious create & reset commands.
* `"sbx"` key should be present and it should contain version of studybox which created card.
	* Future versions of studybox should be able to convert older formats. (Maybe with some issues such as resetting card)
* `"algo"` key should contain algorithm used to store information.
	* If a different algorithm is later used it may reset the data or use them if compatible.
* `"pastq"` key contains past qualities (will only keep 20).

### Body
* Body will immediately follow the header.
* `[[FRONT]]` denotes front of the card. (This goes on until `[[BACK]]` is encountered)
* `[[BACK]]` this denotes back of the card. (This goes until end of the file)
* You should have an empty newline after both FRONT and BACK sections.

