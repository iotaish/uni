#!/usr/bin/perl
$latex = 'uplatex -synctex=1 -halt-on-error';
$bibtex = 'upbibtex';
$dvipdf = 'dvipdfmx %O -o %D %S';
$makeindex = 'mendex %O -o %D %S';
$pdf_mode = 3;