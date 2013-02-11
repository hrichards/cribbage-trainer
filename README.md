cribbage-trainer
================

A quick, metrics-friendly, command-line centered training program for scoring
cribbage hands.

Usage
-----

Of course, the "cards" are colorized on terminals that can read the appropriate
ANSI escape sequences!

```
[hunter@hunter:~/cribbage-trainer]$python cribbage_trainer.py 
Welcome to 'Cribbage Trainer'! ('?' for help, 'Ctrl-C' to quit)
J♣ | J♠ 9♦ 8♥ 8♦: 4
Correct!
T♦ | 6♠ 5♦ 7♠ 9♣: 0

Actual score: 7

Pairs       : 0
Fifteens    : 4
Runs        : 3
Flushes     : 0
Nobs        : 0

8♣ | 9♦ 5♣ Q♦ 6♦: ^C
Goodbye!
```
