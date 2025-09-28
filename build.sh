#!/usr/bin/env bash
set -e
python3 render.py
# Prefer XeLaTeX; fall back to LuaLaTeX if needed
if latexmk -silent -f -xelatex -interaction=nonstopmode -halt-on-error Pranay_Kiran_Resume.tex; then
  echo "PDF built with XeLaTeX"
else
  echo "XeLaTeX failed, trying LuaLaTeX..."
  latexmk -silent -f -lualatex -interaction=nonstopmode -halt-on-error Pranay_Kiran_Resume.tex
fi
