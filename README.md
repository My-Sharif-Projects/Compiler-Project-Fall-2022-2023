# Compiler-Project-Fall-2022-2023
A compiler for C-minus language as a project at Sharif University of Technology in the Fall semester of 2022-2023 coded by Parham Bateni and Pooya EsmaeilAkhoondi
## Phase1: writing the code of the scanner
Scanner DFA:
![Scanner DFA](https://user-images.githubusercontent.com/79264909/203630026-4798ca58-201e-4d32-a032-1a9cb84b4dda.png)
## Phase2: writing the code of LR(1) parser
Grammar:
![image](https://user-images.githubusercontent.com/79264909/210583402-acf0028a-f790-4433-9fca-25f8870ae42a.png)
## Phase3: writing the code of Intermediate code generator
In this phase we changed the previous phase's grammar and we added the required action symbols in the grammar so the intermediate code generator could generate three address codes. The final output of the three address codes were tested using an available interpreter. The three address codes are as following:
![image](https://user-images.githubusercontent.com/79264909/216455407-bcddf79c-0c40-40ad-b9c6-3eff7b4d335a.png)
