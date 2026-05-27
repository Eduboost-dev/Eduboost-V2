# Import-Linter Contract Run

Generated at: `2026-05-26T18:25:30Z`

**Status:** pass

```text

╔══╗─────────▶╔╗ ╔╗      ╔╗◀───┐
╚╣╠╝◀─────┐  ╔╝╚╗║║────▶╔╝╚╗   │
 ║║   ╔══╦══╦╩╗╔╝║║  ╔╦═╩╗╔╝╔═╦══╗
 ║║╔══╣╔╗║╔╗║╔╣║ ║║ ╔╬╣╔╗║║ ║│║╔═╝
╔╣╠╣║║║╚╝║╚╝║║║╚╗║╚═╝║║║║║╚╗║═╣║
╚══╩╩╩╣╔═╩══╩╝╚═╝╚═══╩╩╝╚╩═╩╩═╩╝
  └──▶║║                    ▲ 
      ╚╝────────────────────┘


---------
Contracts
---------

Analyzed 381 files, 1849 dependencies.
--------------------------------------

FastAPI v2 routers should not import repositories directly KEPT
POPIA router uses dependency layer rather than repository construction KEPT
Lessons router uses authorization service layer rather than repositories KEPT

Contracts: 3 kept, 0 broken.
```
