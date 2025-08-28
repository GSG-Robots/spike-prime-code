# Packets

## Format

` `:I]` `

` `:I10asdfghjklö` `

## Host to Hub

| ID | Task | Args |
| -- | ---- | ---- |
| Y | Start SYNC | |
| F | Sync a file | Absolute File Path inside /src, Hash of that file |
| D | Sync a directory | Absolute File Path inside /src |
| N | Stop SYNC | |
| W | Open File (write) | Absolute File Path inside /src |
| C | Transfer File Chunk | chunk (base64) |
| E | End of File | |
| R | Remove File or Folder | Absolute File Path inside /src |
| A | Create Folder | Absolute File Path inside /src |
| P | Restart `main.py` |  |
| X | Stop `main.py` |  |
| > | Return to REPL |  |
| & | ` `machine.reset()` ` |  |
| $ | Reset connection |  |

## Hub to Host

| ID | Task | Args |
| -- | ---- | ---- |
| K | OK |  |
| U | Hash mismatch |  |
| ! | Error | Error Message (base64) |
| $ | Reset connection |  |
