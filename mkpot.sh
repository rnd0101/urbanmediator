#!/bin/sh

L=urbanmediator/locales/fi.po

extract_i18n.py urbanmediator py EN.pot $L
#extract_i18n.py urbanmediator py EN.pot ENG

cat EN.pot $L > ENGLISH1.pot
#cat EN.pot ENG > ENGLISH1.pot

extract_i18n.py urbanmediator html EN2.pot ENGLISH1.pot
#extract_i18n.py urbanmediator html EN2.pot ENGLISH1.pot

cat EN.pot EN2.pot > ENGLISH.pot

rm ENGLISH1.pot EN.pot EN2.pot
