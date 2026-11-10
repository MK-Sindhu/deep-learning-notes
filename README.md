# CS6910 Deep Learning: lecture notes

Notes for **CS6910/CS7015 Deep Learning** at IIT Madras (Prof. Mitesh M. Khapra), lectures 2–14 of the [course schedule](https://www.cse.iitm.ac.in/~miteshk/CS6910.html). One page per lecture, built from the official slides and the module videos: diagrams, the maths written out, timestamp links into the videos, and self-test questions.

Not an official IIT Madras resource.

## Structure

| Path | What it is |
| --- | --- |
| `index.html` | Hub page with the lecture list, slides links and status |
| `lecture-02.html` … `lecture-14.html` | One page per lecture |
| `notes.css`, `notes.js` | Styles and behaviour shared by every page |
| `scripts/sync_nav.py` | Regenerates the lecture list and prev/next links |
| `scripts/check_page.py` | Sanity-checks a page (tags, scripts, ids, colours, MathJax, timestamps) |

A plain static site: no build step, no dependencies. Maths is rendered by MathJax from a CDN.

## View locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploy on Vercel

Import the repository, choose the **Other** framework preset, and leave the build command and output directory empty.

## Adding or editing a lecture

After adding a `lecture-NN.html` file, run:

```bash
python3 scripts/sync_nav.py
```
