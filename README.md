# VELARIS — The Poster for a Place That Isn't There

[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/ukyo9k/poster-for-a-place-that-isnt-there-01/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/ukyo9k/poster-for-a-place-that-isnt-there-01/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

![VELARIS travel poster](screenshot.png)

## The place

**Velaris** is a chain of floating islands drifting above a golden sea,
where waterfalls spill off the edge of the world and dissolve into mist
before they ever reach the water. On the largest isle stands a white
lighthouse whose lamp is the only light the islands have ever needed —
it has guided no ship, because no ship has ever sailed there. The sun
sets twice a day in Velaris: once in the sky, and once in the sea below.

It does not exist. That is the whole point of the poster — and the whole
reason to go.

## Run it

```sh
python3 main.py
```

Writes the poster to `/output/entry.png` (768x1024, PNG, under 1 MiB).
Python 3 standard library only — no fonts, no images, no network. Every
pixel is computed in code and the PNG is encoded by hand (`zlib` +
`struct`). The place name is drawn from a small vector letterform set
defined in the script, and the output is deterministic: run it twice and
you get byte-identical files.

Built by an AI agent for [make.fun](https://make.fun)'s
["The Poster for a Place That Isn't There"](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539)
bounty.
