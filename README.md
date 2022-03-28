# SQL INSERT GENERATOR

This program will take a .sqpy file as an input and generate, based on specifications written in file; and will output a file containing all the inserts 
specified by the user.
<br>The following is documentation for how to utilize this parser.

## **_THIS IS NOT A FINISHED PROJECT_**

<hr>

##random_gex
#### Uses ascii.

There are three ways to define possible values for each attribute
  1. write an array -> [optiona, optionb, optionc]
  2. write in file  -> {filename}
     - You can alternatively place the file in the folder Defined_Files. This will automatically collect the name
     of the file ex: ``filename.txt`` and name the set of data filename. this would be equivalent to ``filename = {filename.txt}``
  3. write in r_gex -> r_gex is short for random_gex. 
     - I am not sure if there is an official library which deals with this, so I ended up making a set grammar of 
     grammar which given a string can generate an output pertaining to the specifications of this string. 
     - Currently, it uses a very primitive version of regex 
     specifications.

> [] -> allows for all characters stored in here to be used at this location. Does not support ^. <br>
> {} -> allows for the previous section to be repeated for however many times is specified in these braces. <br>
> &emsp;&emsp; Only supports {number} for now, I plan on adding {number, number} in the future. <br>
> () -> everything enclosed in here will be considered its own set like in regex (abc){2} will be abcabc vs abc{2} will be abcc. `` <br>

<hr>

## Writing a .sqpy file

&emsp; There are **4** sections that must be added, each section is separated by %%

### &emsp;&emsp; Section 1

&emsp;&emsp;&emsp;&emsp; This Section contains rules for the program with which apply primarily to the program itself. <br>
&emsp;&emsp;&emsp;&emsp; These rules will control certain areas such as the maximum failsafe of recursive iterations to try and <br>
&emsp;&emsp;&emsp;&emsp; find a suitable primary_key. You can also disable and enable foreign keys if you don't wish for them to be <br>
&emsp;&emsp;&emsp;&emsp; written. Currently, while some have been implemented, I have not implemented them all nor have they been implemented <br>
&emsp;&emsp;&emsp;&emsp; to the degree I wish them to be, so it would be advised to leave this section blank for the time being.

<hr style="width:90%; margin: auto; margin-left:40px">

### &emsp;&emsp; Section 2

&emsp;&emsp;&emsp;&emsp; This is where you define sets of data to be used inside the third section. <br>
&emsp;&emsp;&emsp;&emsp; These are for the moment static sets of data which can not be modified due to influence from other<br>
&emsp;&emsp;&emsp;&emsp; sets of data. <br>
&emsp;&emsp;&emsp;&emsp; This section currently supports 3 kinds of data enclosed in their own unique characters ([], {}, ' ').<br>
&emsp;&emsp;&emsp;&emsp; ' ' are single quotes<br>
<br>
&emsp;&emsp;&emsp;&emsp; Note: While all data will be stored and chosen as strings, the final data type will be chosen<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; &ensp; based on type given in attribute. <br>
&emsp;&emsp;&emsp;&emsp;&emsp; [] stores arrays of data such as ``data = [data1, data2, data3]`` <- will choose from these 3 strings <br>
&emsp;&emsp;&emsp;&emsp;&emsp; {} stores files of data such as ``data = {filename.txt}`` <- will choose from data located in this file <br>
&emsp;&emsp;&emsp;&emsp;&emsp; '' stores r_gex specifications such as ``data = '[0-9]{3}'``<- will generate strings from 000-999 <br>

&emsp;&emsp;&emsp;&emsp; A goal which I have is to utilize <> or some other character encasing identifier to allow for<br>
&emsp;&emsp;&emsp;&emsp; the 'importation' of data into some other data <br>
&emsp;&emsp;&emsp;&emsp; An example of what I mean is<br>
&emsp;&emsp;&emsp;&emsp;``department = [science, math, chemistry]`` becomes <br>
&emsp;&emsp;&emsp;&emsp;``data_r_gex = 'Dept of. <department>' -> 'Dept of. (science|math|chemistry)'``<br>
&emsp;&emsp;&emsp;&emsp; Note: | is not a supported character however I do want this to be a thing in the future <br>

<hr style="width:90%; margin: auto; margin-left:40px">

### &emsp;&emsp; Section 3

&emsp;&emsp;&emsp;&emsp; This section contains the sql schema that is wanted to be generated.<br>
&emsp;&emsp;&emsp;&emsp; As an example let us use the table below.

```sql
CREATE TABLE table_demo(
    id INT PRIMARY KEY,
    name VARCHAR(15) NOT NULL,
    num1 INT NOT NULL,
    num2 INT,
    FOREIGN KEY(num2) REFERENCES table_demo2(id)  -- Assume that table_demo2 exists
);
```

To generate randomness we will modify this schema like so: 
```sql
CREATE TABLE table_demo(
    id INT PRIMARY KEY AUTOINCREMENT,   -- Will increment by 1 every time.
    name VARCHAR(15) NOT NULL <fname>,  -- fname is defined in the source code, as long as it is downloaded it should work.
    num1 INT NOT NULL '[0-9]{5}',       -- will generate a number from 0-99999.
    num2 INT,                    -- Does not need anything as it is a foreign key and will gain its value from table_demo2.
    FOREIGN KEY(num2) REFERENCES table_demo2(id)  -- Assume that table_demo2 exists.
);
```
> id takes on an incremental approach where every subsequent entity will go up by 1, similar to AUTO_INCREMENT Does not have the same limitations where it can only be used once.

> name takes on a string from the file fname which assuming the Defined_files folder is located, will have a large set of possible names to choose from.<br>
> Note: fname may have names larger than 15 characters and this program currently does not discriminate against size of string.

> num1 will choose a string between '00000' and '99999' then will convert to INT which will turn the number into a number between 0 and 99999

> num2 will not choose anything until closer to the end of the program where it will then choose an entity for which it is referring to.






<hr style="width:90%; margin: auto; margin-left:40px">

### &emsp;&emsp; Section 4

> NOTE: (-> and =) are interchangeable so Hospital = 5; is the same as Hospital -> 5; 
> however, it can be a good way to sort meanings
> 
&emsp;&emsp;&emsp;&emsp; Section 4 refers to rules between entities.<br>
&emsp;&emsp;&emsp;&emsp; This has been the most modified of the sections in this update.<br>
&emsp;&emsp;&emsp;&emsp; There are now 2 main functions of this section, <br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; 1. Tell the parser how many entities are desired<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; 2. Tell the parser limits between entities (only for foreign keys)<br> 
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp; ex: Only 3 doctors can work at 1 hospital<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp; Modeled as ``Hospital.id -> Doctor(3);`` <br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&ensp;.id refers to what doctor is referring to <br>
<br>
&emsp;&emsp;&emsp;&emsp; 1. Tells the parser how many entities are desired <br>
&emsp;&emsp;&emsp; &emsp; &emsp; This is written as such ``Hospital = 5;`` and this will create 5 instances of the Hospital entity.<br>
&emsp;&emsp;&emsp; &emsp; &emsp; You can also write these specifications right into the sql. Ex. in CREATE TABLE demo(); <br>
&emsp;&emsp;&emsp; &emsp; &emsp; you can write CREATE TABLE demo() * 10;  to indicate you want 10 demo entities generated. <br>

&emsp;&emsp;&emsp;&emsp; 2. Tells the parser limits between entities (only for foreign keys) <br> 
&emsp;&emsp;&emsp; &emsp; &emsp; This is written in a few ways: <br>
&emsp; &emsp; &emsp; &emsp; &emsp; ``Hospital -> Doctor(5);`` <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; Creates a relational limit where a Hospital entity can only be <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; related to 5 Doctor entities via any foreign keys. <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; **Note**: This will create a pool for all Doctor foreign keys referring to this <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp;&emsp;&ensp; specific Hospital for any of its keys. <br>

&emsp; &emsp; &emsp; &emsp; &emsp; ``Hospital -> Doctor(0, 5);`` <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; Creates a relational limit where a Hospital entity can only be <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; related to between 0 and 5 Doctor entities via all foreign keys. <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; **Note**: This will create a pool for all Doctor foreign keys referring to this <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp;&emsp;&ensp; specific Hospital for any of its keys. <br>

&emsp; &emsp; &emsp; &emsp; &emsp; ``Hospital.id -> Doctor(5);`` <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; Creates a relational limit where a Hospital entity can only be <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; related to 5 Doctor entities via the Hospital key id. <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; **Note**: This will create a pool for any Doctor foreign key referring to this <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp;&emsp;&ensp; specific Hospital id key. <br>

&emsp; &emsp; &emsp; &emsp; &emsp; ``Hospital.id -> Doctor(1, 5);`` <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; Creates a relational limit where a Hospital entity can only be <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; related to between 1 and 5 Doctor entities via the Hospital key id. <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; **Note**: This will create a pool for any Doctor foreign key referring to this <br>
&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp;&emsp;&ensp; specific Hospital id key. <br>

> The Full structure for 2 is <br>
> \<Referenced Entity>(.\<Any key in Referenced Entity>)? (->|=) \<Foreign Entity>((<lower bound>,)?\<upper bound>); <br>
> ? means optional, | or \<> means replace with something valid

<hr>

## Running the Program
### This was written in pycharm with python 3.10 using matches, so it is not compatible with any version of python less than 3.10

to run this program, you must run the SQ.py program and give it the file you wish it to read. This file needs to be .sqpy (.txt file), no other file will be accepted
because I thought it would be funny to reject any other types of files including other .txt files.

example would be:
```
python parser.py sqpy_filename.sqpy
```

This will generate a file (assuming no errors occur) called output.sql
<br>
If you want a custom output file name you can always specify when running parser.py after the input what you want the
custom name to be.
```txt
python parser.py sqpy_filename.sqpy output_filename.sql
```
Output file is not restricted by file name, as long as it can have python write to it in I assume unicode everything should work fine.

