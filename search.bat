@echo off
REM Lets the marker run:  search <filename> <method>
REM It simply forwards both arguments to search.py in this folder.
python "%~dp0search.py" %*
