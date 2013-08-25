#!/usr/bin/env bash

find . -iname coverage.dat | xargs python bf_cov.py
