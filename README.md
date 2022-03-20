# sql-insert-generator
Generates some sql inserts based on specifications

**_THIS IS NOT A FINISHED PROJECT_**

## random_gex
there are three ways to define possible values for each attribute
  1. write an array -> [optiona, optionb, optionc]
  2. write in file  -> {filename}
  3. write in r_gex -> r_gex is short for random_gex. 
     - I am not sure if there is an official library which deals with this, so I ended up making a set grammar of 
     grammar which given a string can generate an output pertaining to the specifications of this string. 
     - Currently, it uses a very primitive version of regex 
     specifications.
     
Those regex specifications supported are:
  ```
  [] -> allows for all characters stored in here to be used at this location. Does not support ^.
  {} -> allows for the previous section to be repeated for however many times is specified in these braces.
     Only supports {number} for now. Plan on adding {number, number} in the future.
  () -> everything enclosed in here will be considered its own set like in regex (abc){2} will be abcabc vs abc{2} will be abcc.
  ```

## Writing a .sqpy File
There are **4** sections that must be added, each section is separated by %%

### Section 1
This section contains booleans for telling the parser to do things differently.
<br>
Currently Supports:
- foreign
  > foreign controls whether the or not the parser will ignore foreign keys. Should the parser be told to ignore them<br>
  then it will replace all occurrences of foreign keys with null


%%

### Section 2

Can store arrays, files or random_gex strings here to be used in the third section
format needs to be:

```
<define name> = <list of stuff>
example for array: define_array_name = [arr_element1, arr_element2, arr_element3]
example for file: define_file_name = {filename.txt}
example for random_gex: define_reg_name = '[abc]{3}'
```

these can be called in by the third section using <define name> enclosed in the angle brackets.


%%

### Section 3
The third section contains the sql code. 
For this we only need to copy and paste the code into this section before then modifying each attribute slightly.<br>
At the end of each attribute for which you would like the parser to assign a value for, you must add a segment of code
to either look for the defined set of choices from section 2 via angled brackets and the defined sets name or define it in
this location.

As an example: 

```sql
CREATE TABLE table_name (
    id INT,
    name VARCHAR(25) NOT NULL,
    string VARCHAR(25) NOT NULL,
    PRIMARY KEY(id)
);
```
If we take this table schema and place it in the thirst section, we then modify the code like this:
```txt
CREATE TABLE table_name (
    id INT AUTOINCREMENT, 
    name VARCHAR(25) [name1, name2, name3, name4, ...],
    string VARCHAR(25) <define_array_name>,
    PRIMARY KEY(id)
);
```
```txt
CREATE TABLE table_name (
    id INT AUTOINCREMENT,  <- AUTOINCREMENT will tell the parser that this needs to be incremented by 1 for every new entity
    
    name VARCHAR(25) [name1, name2, name3, name4, ...], <- this will create a new defined set of information 
                                                        inside of section 2, then it will assign the new define
                                                        to this attribute.
                                                        
    string VARCHAR(25) <define_array_name>,  <- this will assign the defined set of choices found at define_array_name
                                             to this attribute.
                                             
    PRIMARY KEY(id) <- This will signify this attribute is primary key. You can also write this all on a single line
                    Example: id INT PRIMARY KEY AUTOINCREMENT
);
```
A little trick to circumvent section 4 is to add a *number between the closing parenthesis of the table and the semicolon
as the * 10 will tell the parser to create 10 instances of this entity.
```txt
CREATE TABLE table_name (
    id INT AUTOINCREMENT, 
    name VARCHAR(25) [name1, name2, name3, name4, ...],
    string VARCHAR(25) <define_array_name>,
    PRIMARY KEY(id)
) * 10;
```

%%

### Section 4

This is where you define the number of entities you want for each table.
```
<table_name> = <number_of_entities>
Example: 
%%
table_name = 10
```

## Running the Program
to run this program, you must run the parser.py program and give it the file you wish it to read. This file needs to be .sqpy (.txt file), no other file will be accepted
because I thought it would be funny to reject any other types of files including other .txt files.

example would be:
```
python parser.py TestFile.sqpy
```

This will generate a file (assuming no errors occur) called output.sql
<br>
If you want a custom output file name you can always specify when running parser.py after the input what you want the
custom name to be.
```txt
python parser.py TestFile.sqpy new_output_file_name.sql
```
Output file is not restricted by file name, as long as it can have python write to it in I assume unicode.
