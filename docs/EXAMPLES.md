# Example Scripts

## Create a file

```python
from sbx.core.card import Card

# Create a card with given path (doesn't need to exist)
card = Card("jit.md")
card.front = "What does JIT stands for in JIT compiler?"
card.back = "Just in time"
card.save()
```

* This will create a card file `jit.md`

## Export a card to `.json`

```python
import json
from sbx.core.card import Card

# This card need to exist
card = Card("./tests/box/test-card-2.md")

data = {"front": card.front, "back": card.back, "meta": card.meta.to_dict()}
# Accessing '.front' will automatically load the full card details from file
print(json.dumps(data, indent="  "))
```

* This prints

```json
{
  "front": "How do I display `\"World World\"` in Python?",
  "back": "```python\nprint(\"World World\")\n```",
  "meta": {
    "a": 4,
    "b": 9.744000000000002,
    "c": 1.4000000000000001,
    "next": 1592667591,
    "last": 1591825710,
    "pastq": "2104335",
    "reps": 7,
    "algo": "sm2",
    "sbx": "v1"
  }
}
```

## Get a list of cards

```python
import pprint
from sbx.core.study import CardStack

cards = CardStack("./tests/box", recursive=True, include_unscheduled=True)
pprint.pprint([x.path for x in cards.iter()])
```

* This prints

```python
['tests/box/test-card-3.md',
 'tests/box/test-card-zero.md',
 'tests/box/test-card-2.md',
 'tests/box/test-card.md',
 'tests/box/test-card-leech-zero.md',
 'tests/box/test-card-ok.md',
 'tests/box/test-card-leech.md']
```

