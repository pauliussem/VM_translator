## VM language translator to assembly language instructions

This is the project from course "Nand2tetris (part 2)". 

The main part of this project was to understand how stack logic works and how to translate it to assembly language instructions.

Python language was picked to translate VM language to assembly language instructions for "hack computer".


### **"Hack computer"** is 16-bit virtual computer implemented in this course.

ALU can compute very few arithmetic / logical commands like subtract, add, negate, less-than, greater than, equal, and, not and or.


**Assigned memory segments:**

![Image](https://github.com/user-attachments/assets/c31837fb-2efe-4a9b-b63f-776f164cb1c7)

**Memory access commands:**

* push;
* pop.

**Branching commands:**

* label label_name;
* goto label_name;
* if-goto label_name.

**Function commands:**

* function function_name nVars;
* call function_name nArgs;
* return.
