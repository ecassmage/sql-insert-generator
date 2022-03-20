# sql-insert-generator
Generates some sql inserts based on specifications

there are three ways to define possible values for each attribute
  1. write an array -> [optiona, optionb, optionc]
  2. write in file  -> {filename}
  3. write in r_gex -> r_gex is short for random_gex. I am not sure if there is an official library which deals with this so I ended up making a set grammar of 
grammar which given a string can generate an output pertaining to the specifications of this string. Currently it is uses a very primitive version of regex 
specifications. those supported are:
<br>
  1. [] -> allows for all characters stored in here to be used at this location. Does not support ^
  2. {} -> allows for the previous section to be repeated for however many times is specified in these braces. Only supports {number} for now. Plan on adding {number, number} in the future
  3. () -> everything enclosed in here will be considered its own set like in regex (abc){2} will be abcabc vs abc{2} will be abcc
---
<br>
<br>
<br>
to run this program, you must run the parser.py program and give it the file you wish it to read. This file needs to be .sqpy (.txt file), no other file will be accepted
because I thought it would be funny to reject any other types of files including other .txt files.

example would be:
```txt
python parser.py TestFile.sqpy
```
If you want 
