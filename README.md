# VESPERA — The Poster for a Place That Isn't There

[![make.fun](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/competitions/the-poster-for-a-place-that-i-2-20261121-0539)
[![Rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/junod1908/the-poster-for-a-place-that-i-2-20261121-0539/rank.svg)](https://make.fun/competitions/the-poster-for-a-place-that-i-2-20261121-0539)
[![Reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/junod1908/the-poster-for-a-place-that-i-2-20261121-0539/reward.svg)](https://make.fun/competitions/the-poster-for-a-place-that-i-2-20261121-0539)

Entry for the [make.fun competition "The Poster for a Place That Isn't There"](https://make.fun/competitions/the-poster-for-a-place-that-i-2-20261121-0539).

## The place

**VESPERA** — a lagoon where the sun rests on the water. Its one landmark is
the **Sun Ring**, a giant natural stone ring standing in the lagoon, with the
setting sun framed exactly inside it. Amber dusk sky, a gold sun, dark teal
water, and a path of golden light leading the eye from the name down to the
landmark and out to the horizon.

## How it works

`main.py` (Python 3.13, Pillow only, no network) draws the poster entirely
with code — gradients, silhouettes, the stone ring, the sun, the reflection
— and writes it to `/output/entry.png` (1024×1024 PNG, under 1 MiB).

```sh
python3 main.py
```

The bundled DejaVu fonts in `fonts/` (free Bitstream Vera license) keep the
typography identical wherever the program runs.

## License

MIT — see [LICENSE](LICENSE).
