#!/usr/bin/env python3
"""Regenerate navigation for the CS6910 Deep Learning notes site.

Rewrites the marked regions in:
  - index.html        <!-- COURSE-MAP:START --> ... <!-- COURSE-MAP:END -->
  - lecture-NN.html   <!-- PARTNAV:START --> ... <!-- PARTNAV:END -->
                      <!-- PAGER:START --> ... <!-- PAGER:END -->

A lecture counts as "ready" when its lecture-NN.html exists (or, with
--ready 2,3,5, only the listed lectures do).
Run from anywhere:  python3 scripts/sync_nav.py [--ready 2,3]
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIRST, LAST = 2, 14
SLIDES = "https://iitm-pod.slides.com/arunprakash_ai"
PDFS = "https://www.cse.iitm.ac.in/~miteshk/CS7015/Slides/Teaching/pdf"

# (lecture, short title, schedule "Contents", group, slide links)
LECTURES = [
    (2, "McCulloch–Pitts neurons, perceptrons and MLPs", "McCulloch Pitts Neuron, Thresholding Logic, Perceptrons, Perceptron Learning Algorithm and Convergence, Multilayer Perceptrons (MLPs), Representation Power of MLPs", "Foundations", [f"{SLIDES}/cs6910-lecture-2/fullscreen"]),
    (3, "Sigmoid neurons, gradient descent, feedforward networks", "Sigmoid Neurons, Gradient Descent, Feedforward Neural Networks, Representation Power of Feedforward Neural Networks", "Foundations", [f"{SLIDES}/cs6910-lecture-3-44073c/fullscreen"]),
    (4, "Feedforward networks and backpropagation", "Feedforward Neural Networks, Backpropagation", "Foundations", [f"{SLIDES}/cs6910-lecture-4/fullscreen"]),
    (5, "Optimization: from gradient descent to Adam", "Gradient Descent (GD), Momentum Based GD, Nesterov Accelerated GD, Stochastic GD, AdaGrad, RMSProp, Adam", "Training deep networks", [f"{SLIDES}/cs6910-lecture-5/fullscreen", f"{SLIDES}/cs6910-lecture-52/fullscreen"]),
    (6, "Regularization", "Bias Variance Tradeoff, L2 regularization, Early stopping, Dataset augmentation, Parameter sharing and tying, Injecting noise at input, Ensemble methods, Dropout", "Training deep networks", [f"{SLIDES}/cs6910-lecture-8/fullscreen"]),
    (7, "Pre-training, activations, initialization, batch norm", "Greedy Layerwise Pre-training, Better activation functions, Better weight initialization methods, Batch Normalization", "Training deep networks", [f"{SLIDES}/cs6910-lecture-6/fullscreen"]),
    (8, "Convolutional neural networks", "Convolutional Neural Networks, LeNet, AlexNet, ZF-Net, VGGNet, GoogLeNet, ResNet", "Convolutional networks", [f"{PDFS}/Lecture11.pdf"]),
    (9, "Visualizing and fooling CNNs", "Visualizing Convolutional Neural Networks, Guided Backpropagation, Deep Dream, Deep Art, Fooling Convolutional Neural Networks", "Convolutional networks", [f"{PDFS}/Lecture13.pdf"]),
    (10, "Word representations", "Learning Vectorial Representations Of Words", "Sequences and language", [f"{PDFS}/Lecture10.pdf"]),
    (11, "Recurrent neural networks and BPTT", "Recurrent Neural Networks, Backpropagation Through Time (BPTT), Vanishing and Exploding Gradients, Truncated BPTT", "Sequences and language", [f"{PDFS}/Lecture14.pdf"]),
    (12, "GRUs and LSTMs", "Gated Recurrent Units (GRUs), Long Short Term Memory (LSTM) Cells, Solving the vanishing gradient problem with LSTMs", "Sequences and language", [f"{PDFS}/Lecture15.pdf"]),
    (13, "Encoder–decoder models and attention", "Encoder Decoder Models, Attention Mechanism, Attention over images, Hierarchical Attention", "Sequences and language", [f"{PDFS}/Lecture16.pdf"]),
    (14, "Transformers", "Transformers: Multi-headed Self Attention, Cross Attention", "Sequences and language", [f"{SLIDES}/lecture-17-transformers-ce11cb/fullscreen"]),
]
BY_N = {x[0]: x for x in LECTURES}
ONLY: set[int] | None = None


def fname(n: int) -> str:
    return f"lecture-{n:02d}.html"


def ready(n: int) -> bool:
    if ONLY is not None and n not in ONLY:
        return False
    return (ROOT / fname(n)).exists()


def write_if_changed(path: Path, text: str) -> None:
    if path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def replace_region(text: str, name: str, content: str) -> str:
    pat = re.compile(rf"(<!-- {name}:START -->)(.*?)(<!-- {name}:END -->)", re.S)
    return pat.sub(lambda m: m.group(1) + content + m.group(3), text) if pat.search(text) else text


def course_map() -> str:
    rows, group = [], None
    for n, title, contents, grp, slides in LECTURES:
        if grp != group:
            rows.append(f'<tr class="group"><td colspan="4">{html.escape(grp)}</td></tr>')
            group = grp
        t = html.escape(title)
        cell = f'<a href="{fname(n)}">{t}</a>' if ready(n) else t
        cell += f'<span class="sub">{html.escape(contents)}</span>'
        sl = " · ".join(f'<a href="{u}" target="_blank" rel="noopener">{"Slides" if len(slides) == 1 else f"Slides {i + 1}"}</a>' for i, u in enumerate(slides))
        chip = '<span class="chip ready">Ready</span>' if ready(n) else '<span class="chip planned">Coming</span>'
        rows.append(f"<tr><td>{n:02d}</td><td>{cell}</td><td>{sl}</td><td>{chip}</td></tr>")
    return "\n" + "\n".join(rows) + "\n"


def neighbours(n: int):
    prev = next((m for m in range(n - 1, FIRST - 1, -1) if ready(m)), None)
    nxt = next((m for m in range(n + 1, LAST + 1) if ready(m)), None)
    return prev, nxt


def partnav(n: int) -> str:
    prev, nxt = neighbours(n)
    bits = ['<a href="index.html">DL Notes</a>', '<span class="sep">/</span>', f"<span>Lecture {n}</span>"]
    if prev:
        bits += ['<span class="sep">·</span>', f'<a href="{fname(prev)}">← Lecture {prev}</a>']
    if nxt:
        bits += ['<span class="sep">·</span>', f'<a href="{fname(nxt)}">Lecture {nxt} →</a>']
    return '<nav class="partnav" aria-label="Lectures">' + "".join(bits) + "</nav>"


def pager(n: int) -> str:
    prev, nxt = neighbours(n)
    out = ['<nav class="pager" aria-label="Previous and next lecture">']
    if prev:
        out.append(f'<a href="{fname(prev)}"><span class="dir">← Lecture {prev}</span><span class="nm">{html.escape(BY_N[prev][1])}</span></a>')
    else:
        out.append('<a href="index.html"><span class="dir">← All lectures</span><span class="nm">Course map</span></a>')
    if nxt:
        out.append(f'<a class="next" href="{fname(nxt)}"><span class="dir">Lecture {nxt} →</span><span class="nm">{html.escape(BY_N[nxt][1])}</span></a>')
    elif n < LAST:
        out.append(f'<a class="next" href="index.html"><span class="dir">Lecture {n + 1} · coming</span><span class="nm">{html.escape(BY_N[n + 1][1])}</span></a>')
    else:
        out.append('<a class="next" href="index.html"><span class="dir">Finished →</span><span class="nm">Back to all lectures</span></a>')
    out.append("</nav>")
    return "".join(out)


def main() -> None:
    global ONLY
    args = sys.argv[1:]
    if args[:1] == ["--ready"] and len(args) > 1:
        ONLY = {int(x) for x in args[1].split(",") if x.strip()}
    idx = ROOT / "index.html"
    if idx.exists():
        write_if_changed(idx, replace_region(idx.read_text(encoding="utf-8"), "COURSE-MAP", course_map()))
    done = []
    for n, *_ in LECTURES:
        f = ROOT / fname(n)
        if not f.exists() or (ONLY is not None and n not in ONLY):
            continue
        t = f.read_text(encoding="utf-8")
        t = replace_region(replace_region(t, "PARTNAV", partnav(n)), "PAGER", pager(n))
        write_if_changed(f, t)
        done.append(n)
    print("ready lectures:", done)


if __name__ == "__main__":
    main()
