# High Performance Processors and Systems

## Politecnico di Milano - UIC 569

## Course Project Report

## Maeve

## An ad-hoc implementation of

## the Knuth Morris Pratt algorithm on FPGA

## Andrea Cappelletti

## 24th June 2020


## Contents

- 1 Introduction
   - 1.1 Context
   - 1.2 Problem
- 2 Knuth Morris Pratt Algorithm
   - 2.1 String matching
   - 2.2 The algorithm
   - 2.3 Failure Function
      - 2.3.1 Failure function as a Finite State Automata
   - 2.4 State of Art
      - 2.4.1 Parallelization of the KMP on a SIMD architecture
      - 2.4.2 L-I-KMP
         - Genome Sequencing 2.4.3 GenSeq+: A Scalable High-Performance Accelerator for
      - 2.4.4 Hardware based String Matching Algorithms: A Survey
   - 2.5 Implementation
      - 2.5.1 Key performance indicators
      - 2.5.2 Why FPGAs
   - 2.6 Implementation
      - 2.6.1 Kernel
      - 2.6.2 Host code
- 3 Repeat Analyzer
   - 3.1 Scope
   - 3.2 Strain identification
   - 3.3 Integration
   - 3.4 Performance
   - 3.5 Code
- 4 Future work
- 5 References


## 1 Introduction

### 1.1 Context

Looking from the outside we are all the same, we are all human with more or
less similar habits. But when it comes to health everyone of us is different and
what makes us deeply different is our DNA, a kind of biomolecules that stores
and encode generic instruction of each organism and also many types of viruses.

During last years data collecting has become very important, especially in the
genomics field. From the data it is possible to extract useful information that
can lead to the prevention of human diseases and the production of personalized
medicine.

The genomics pipeline underlines different steps of the sequencing analysis and
one of the most important is the exact pattern matching, in other words being
able to find the occurrences of a pattern (i.e. amino-acid, protein, ...) in a
sequence most of the times of DNA.

### 1.2 Problem

Exact pattern matching represents a challenge computationally speaking be-
cause just a sequence of DNA is composed by over three billion base pair.
The size of the data not only affects the cost of the computation, but also the
resources used.

Moreover the process itself is very time consuming and dealing with a patient
who is fighting between life and death time is everything.
The real challenge is to transform the vast amount of data into valuable knowl-
edge within a considerable small amount of time.

In this context hardware acceleration comes to help, exploiting the parallelism
in order to achieve improved performance.
Hardware acceleration combined with a linear time complexity algorithm will
definitely shorten the execution time and achieve improved performances.


## 2 Knuth Morris Pratt Algorithm

String matching is a classical problem in Computer Science, not only used for
genomics but also widely spread in frequently used tool (e.g. looking for a pre-
cise string in all the directory trough grep).
The use of pattern matching is very broad and efficient parallel pattern matching
algorithms can improve system performance in various problems of computer
science. The focus of this project is the Knuth Morris Pratt algorithm.
The algorithm was conceived by James Morris and then independently discov-
ered by Donald Knuth a few weeks later. Morris and Vaughan Pratt published
a technical report in 1970. The three published then a paper with the algorithm
in 1977 jointly. This is the first linear time algorithm for string matching in-
vented. Indeed the KMP algorithm performs string matching with a complexity
in the worst case scenario of O(n), where n is the length of the string.

### 2.1 String matching

A string matching problem consists in finding the occurrences of a pattern p
into a string s.
The general and simplest approach used to solve this problem is the brute force
algorithm, but its time complexity is not really efficient: O(nm), where n is the
length of the string and m the length of the pattern.
Several algorithms has been developed through the years, for instance Boyer-
Moore, which average time complexity is O(n/m), Karp-Rabin, which the best
time complexity is O(m+n) and so on.
All these algorithms differs from the brute force approach for a pre-processing
phase executed on the pattern, but they also present a time complexity of O(nm)
in the worst case scenario, depending on how the alphabet of the string and the
pattern is composed.
In the following section a more technical overview of the Knuth Morris Pratt
algorithm is presented.

### 2.2 The algorithm

The algorithm is characterized by two phases, at first it computes the prefix
table through the failure function for the pattern to search and then it performs
the matching with the string.
When it comes to matching, it compares character by character from left to
right the string with the pattern, but, differently from the brute force approach,
when a mismatch occurs it takes advantage from the prefix table to skip unnec-
essary comparisons.
More in detail when a mismatch occurs, after a partial match, instead of start-
ing to compare from the next sequential position (as the brute force), it skips
all the characters that were previously matched according to the prefix table.


The bottleneck of the algorithm, as discussed also in the implementation sec-
tion, is the matching function. In fact it turns out that it is very time consuming
with respect to the failure function and this for this reason lead several imple-
mentation choices has been discussed and some preferred over others.
The pseudo-code of the matching function is represented in the figure below.

### 2.3 Failure Function

The computation of the prefix table, also known as LPS (Longest proper prefix
which is also suffix), is done through the failure function. The function computes
the table for all the patterns. The prefix table is used to decide how many
characters skip whenever a mismatch occurs.


#### 2.3.1 Failure function as a Finite State Automata

The failure function computation can be implemented as a finite state machine.
To exploit this possibility, consider the picture below representing the finite
state machine for the pattern ”abacad”.

The logic can be easily integrated into an FPGA.
In 1999 the first implementation of a finite state machine to compute the failure
function was integrated with an FPGA through a pre-configured template. In
case of a mismatch the finite state machine was able to execute two comparisons
in one clock cycle.

### 2.4 State of Art

This section presents and discusses the state of art related to the Knuth Morris
Pratt algorithm implementations on different architectures.

#### 2.4.1 Parallelization of the KMP on a SIMD architecture

This implementation of the KMP algorithm is designed to run on a SIMD
architecture. In order to exploit the parallelism the input data has to be divided.
This requires a pre-processing phase to find the more suitable division point
to grand a complete and consistent search. The pre-processing phase takes
into consideration how many processors are available. Once the most suitable
division point has been found, it searches for the pattern in different parts of
the input string. The search has to be performed also between the connection
points of different substrings. As we already know the KMP reduce the number
of comparison and combining it with a SIMD architecture will improve the time
efficiency. The result achieved are reported in the picture below.


#### 2.4.2 L-I-KMP

L-I-KMP algorithm combines KMP algorithm and Sunday algorithm to obtain
an improvement in performance.
It introduces a new data structure as output of the failure function computation.
This structure is called last-identical array and its aim is deciding the length of
the move to perform in some matching occasions.
L-I-KMP performs well when the distinct characters in the pattern are only a
few.
Knuth Morris Pratt and L-I-KMP are almost equal in terms of efficiency, assum-
ing a small data set. L-I-KMP performs better with respect to original version
of the Knuth Morris Pratt when the dataset is large and the alfabeth concerning
the patterns is very large. For our computation we refer to a limited alphabet
containing the four DNA basis: adenine, guanine, cytosine and thymine. The
performance obtained are summarized in the picture below.

2.4.3 GenSeq+: A Scalable High-Performance Accelerator for Genome
Sequencing

GenSeq+ underlines that the difficulties in nowadays hardware implementations
are how to design a scalable accelerator and that the programming model has
seriously limited the applicability of the accelerator based on design paradigms.
To solve the underlined weaknesses, they propose an implementation of the


KMP algorithm on FPGA. This aims to speed up performances through the
partitioning of the algorithm. The hardware platform used for this purpose is
Xilinx Zynq FPGA board and the dataset are strings from MatLab. In order
to perform the KMP, they create a Direct Acyclic Word Graph (DAWG). The
KMP aligner keep the genomic sequence in a prefix tree. For each read it builds
a DAWG. This process is executed in order to analyze the trade-off between the
execution speed and the aligner sensitivity. The result achieved are:

- 5x speedup with respect to an ARM Cortex-A9 processor
- 2x speedup with respect to an Intel Core-Duo processor
- Low energy consumption and admissible hardware cost

#### 2.4.4 Hardware based String Matching Algorithms: A Survey

The paper analyses pros and cons between different pattern matching algo-
rithms.

```
Algorithm Advantages Disadvantages
Brute Force No preprocessing phase Time complexity O(N*M)
KMP Prefix function as FSM Data transfer rate
FM - Index Very fast Memory lack
Aho-Corasicks Algorithm Build the AC-Trie Low length pattern
```

### 2.5 Implementation

The aim of this section is to describe more in detail the implementation method-
ologies followed in order to obtain the current work status.
The overall aim of the project is to obtain a scalable, high performance and
energy efficient implementation of the Knuth Morris Pratt algorithm.

#### 2.5.1 Key performance indicators

The key performance indicators for this project have the aim to underline the
best trade off between human effort and hardware capability. Moreover the solu-
tion has to be economical convenient. Performance is the most important KPI,
because our algorithm has to be able to produce the result in a discreet amount
of time and using a relatively small amount of resources. High performance is
achievable by a lot of hardware architecture nowadays, in order to discriminate
among them it is worth considering the cost and the power consumption.

#### 2.5.2 Why FPGAs

The aim of this project is to suit the latest needs achieving an optimized, low
power consuming, high speed and low cost solution.
Behind all the possibilities, a reasonable choice is between these four hardware
platforms: CPU, GPU, FPGA, ASIC.

In order to understand the advantages and disadvantages of each platform,
the analysis will be carried out with respect to the key performance indicators
defined in the previous section.

When it comes to performance, FPGAs and ASICs achieve the best result in
comparison with GPUs and CPUs. For the reasons mentioned before, the need
to achieve peak performances is high, especially when the time of diagnosing is
limited. This brings to discard CPUs as a possible implementation choice.

FPGAs and ASICs will also result the best choice in terms of power consump-
tion. On the other hand GPUs are very high power demanding and in order to
achieve the best trade off they are not a suitable choice for our solution.

Both FPGAs and ASICs lack in flexibility and design time, especially ASICs,
with respect to CPUs and GPUs, but for our purpose the dominant key perfor-
mance indicators are performance and power consumption.

They are relevant so, despite the flexibility and design time, FPGAs and ASICs
are preferred. Among these two possible hardware architectures FPGAs are to
prefer on ASICs because of the restricted design time.

The best trade off among the key performance indicators is given by the choice
of FPGAs as the hardware architecture on which implement the project.


The board used to develop the entire project is Xilinx Alveo U200.

### 2.6 Implementation

This section describes technically how the Knuth Morris Pratt algorithm has
been implemented and the rationality behind the choices. The development has
been carried out with Vitis HLS using the programming language C++.

#### 2.6.1 Kernel

The aim of the kernel is to perform the matching function, that as we as seen
so far represents the bottleneck of the algorithm. The failure function, since
performs very efficiently, is computed in the host code and sent to the kernel
as a parameter. The function kmp, present in the kernel, takes as input six
different parameters listed below:

- occ: array of integer representing the position of the occurence found
- stringdim: array of integer, each element represent the different lengths of
    the input string
- string: array of char that contains the input string
- seqdim: array of integer, each element represent the length of the different
    patterns in seq
- seq: array of char that contains the patterns
- pi: array of integer that contains the prefix table computed for all the
    patterns

The idea behind this implementation is to make the matching function compute
multiple sequences in parallel, in order to gain in performance.

To achieve this aim, different strings can be saved into an array of char, having
a respectively array of integer containing the dimensions of each string.
To better underline this concept, consider two strings ’ABC’ and ’DEFGH’, the
size of the first string is 3 and the size of the second string is 5.

The string array of char will save all the chars of both the string and will
look like: ’A’, ’B’, ’C’, ’D’, ’E’. ’F’, ’G’, ’H’, then in order to know in which
position a string start and in which position it ends we save the respectively
size into an array of integer, stringdim that will look like: ’3’, ’5’.

In this case we know that the first string starts at position ’0’ and ends at
position ’2’, for the second string we know that it starts at position ’3’ and ends
at position ’7’.


In this way, in a genomics context, we can scan multiple fragment of the same
DNA sequence with a pattern at once or on the other side of the medal, we can
scan multiple patterns with the same fragment of DNA at once.

The matching function is implemented as two nested for loop, the outer loop
is cycling on all the couple of sequences to match and the inner performs the
matching itself.

Between consecutive loop iterations there are no data dependency, therefore it
is convenient implement a loop pipeline through the HLS PIPELINE PRAGMA
in the inner loop, which will flatten the outer loop.

In the table below it is reported the resources utilization.

```
Name BRAM18K DSP FF LUT URAM
DSP - - - - -
Expression - - 0 18 -
FIFO 0 - 495 335 -
Instance 915 - 4935 5953 -
Memory 366 - 0 0 -
Multiplexer - - - 36 -
Register - - 6 - -
Total 1281 0 5436 6342 0
Available 4320 6840 2364480 1182240 960
Available SLR 1440 2280 788160 394080 320
Utilization (%) 29 0 0 0 0
Utilization SLR (%) 88 0 0 1 0
```
The SLR utilization, which is the Super Logic Region and it is contained into
the Stacked Silicon Interconnect (SSI) Technology, sets the boundaries to the
size of the array we can transfer.

In order to not exceed the limits, the current implementation supports 200
input string of length 8192 chars and 200 patterns of length 1024 chars.

Those parameters are defined in the code as:

- DIM = 200 (number of couples)
- maxstring = 200*8192 (length of the string array)
- maxseq = 200*1024 (length of the seq array)


#### 2.6.2 Host code

The host code is developed in OpenCL. At first it select the accelerator device
on which run the kernel, in our case the board Alveo U-200. Then it reads the
input files containing the string and the patterns to match.

The input files format is FASTA, which is a well known text-based format
to represent either nucleotide sequences or amino acid (protein) sequences in
bioinformatics. Once it has read the input, it computes the prefix table running
the failure function on the patterns.
Then it is ready to run the kernel, in order to do that it prepares the buffer
containing the input parameters of the kmp function and calls the kernel to
execute the matching.

The kernel will return the array of occurrences populated with the positions
of the string in which the pattern at position i has been found. For example, if
we are matching the fifth pattern with the string and we find an occurrence at
position ’954’, the array of occurrences at position five (because of the pattern)
will be updated with the index of the occurrence found into the string, in this
case ’954’.


## 3 Repeat Analyzer

Repeat Analyzer is a tool for analysing and managing short-sequence repeat
data. In order to have a real scenario of application for the bitstream devel-
oped, I built a framework with Repeat Analyzer.

More information about Repeat Analyzer are available here:
https://bmcgenomics.biomedcentral.com/articles/10.1186/s12864-016-2686-

The official repository is public on BitBucket at this url:
https://bitbucket.org/repeatgroup/repeatanalyzer

### 3.1 Scope

The software is born from the need to catalog and track different repeats found
by different groups of researchers. The model specie by default is Anaplasma
Marginale, but the tool is able to manage different species at once and it can
be used to manage any set of short-sequence repeats regardless of the specie.

### 3.2 Strain identification

The main function of the tool is the strain identification. Given in input a se-
quence of DNA or amino-acids it is able to find the occurrences of short-sequence
repeats of the selected specie present into the sequence.

In order to do this, the software runs an implementation of the Knuth Mor-
ris Pratt algorithm and display the results.

More in detail the implementation of the Knuth Morris Pratt algorithm has
been written by David Eppstein and it is available at the following link:
https://www.ics.uci.edu/ eppstein/161/python/kmp.py

### 3.3 Integration

In order to develop a framework, integrating to Repeat Analyzer the computa-
tion of the Knuth Morris Pratt algorithm on an FPGA, several considerations
have to be taken into account.

First, the input files of Repeat Analyzer have a proprietary format. They have
been design according to the software, which stores information not only about
the strain and the short sequence repeats (patterns), but also about the re-
searcher who discovered the strain, the geographical zone and the attributed
name. If more than one short sequence repeats with the same pattern, but
different name is present, the software distinguishes between them according to
the geographical zone of the finding.


For the identification function, the input format implemented is FASTA, be-
cause it is a bioinformatics standard and does not limit the input pattern we
can submit to Repeat Analyzer.

Only the DNA matching, which is based on an alphabet of four letters ’A’,
’C’, ’G’, ’T’, has been integrated, but it will be immediate to integrate also the
amino-acid and protein matching because the input sequence will be converted
into a DNA sequence using an hash-table.

In order to search for the patterns, the host first reads the fasta files in in-
put and populate string, stringdim, seq and seqdim. Based on the limitations
discussed before, the input string is divided in 200 strings with length 8192 and
one sequence at a time populates the buffer seq.

The buffers are both sent to the kernel for the computation and the process
goes on iterativly until all the input string has been parsed.

### 3.4 Performance

The software has been developed using Python 2.7.
The performance reported below are evaluated using Nimbix, a online Virtual
Machine running Ubuntu with the board Alveo U-200 integrated.
For more informations: https://www.nimbix.net.

The VM environment is running with the following characteristics:

- Processor: 16x Intel(R) Xeon(R) CPU E5-2640 v3 @ 2.60 GHz
- OS: Ubuntu 16.04.4 LTS
- Memory: 131922 MB

The bottleneck of the strain identification feature is given by the computation
of the matching function of the Knuth Morris Pratt algorithm.
With respect to this, the time taken to compute the failure function is consid-
ered negligible.

In order to analyse Repeat Analyzer performance, several use cases are taken
into consideration. The user interface of the software has been disabled, because
it crashes when it comes to handle a huge amount of data.

The following data have been analysed.
The source of the sequences is the website GenBank.

- RAD23A: human RAD23A homolog [Homo sapiens]


- Bgt-09: Blumeria graminis f. sp. tritici genome assembly, chromosome
- Anaplasma Marginale
- Anaplasma Centrale

The results are reported in the table below.

More in detail, input represents the input sequence of chromosomes with the
respectively size measured in chars.

Exe time (matching) represents the execution time of the matching function
in Repeat Analyzer (python code).

Pattern represents the input pattern.

For this benchmark two input patterns has been considered: Anaplasma Marginale,
which contains 47 sequences and in total 2350 chars and Anaplasma Centrale,


which contains 178 sequences and in total 10.680 chars.

Exe time (failure func) represents the execution time of the failure function
in Repeat Analyzer.

Last but not least, Exe time (FPGA) represents the execution time of the
matching function of the Knuth Morris Pratt algorithm on the board Alveo
U-200 through FPGA.

As we can notice the time taken from the failure function to be executed is
very low with respect to the matching function. For this reason we can consider
it negligible. Moreover we can observe that in applying the same input string
as pattern the computation results very efficient, this underlines the importance
of the prefix table in the Knuth Morris Pratt algorithm.

In order to better understand the performance, a test with a single input string
has been executed: Bgt-09, with several input patterns.

As we can notice from the chart reported below, for small pattern sequences
the difference between software and hardware computation is almost irrelevant,
but increasing the size of the patterns the FPGA implementation execution time
is definitely outperforming the software implementation of the KMP matching
function.

The overall speedup achieved, considering the pre-processing phase, is up to
4.86x.


### 3.5 Code

The code of the project is available on GitHub at the link:

https://github.com/andreacappelletti97/HPPSproject

The repository is organized as follow:

- ./HW contains all the files related to the hw implementation
    ./Makefiles contains all the makefile versions
    ./Origin contains the original code implemented in Vitis HLS
    ./build contains the different bitstream build with version
    ./fsm contains an implementation of the failure function as FSM
    ./src contains the source code developed to build the bitstream
- ./RA software contains the framework with Repeat Analyzer and the host
    file
- ./tutorial contains the PDF user manual of Repeat Analyzer
- install.sh is a script that installs all the dependecies needed to make the
    tool run


## 4 Future work

The work done so far can be optimized in several ways in order to achieve better
performance, low power consumption and more flexibility.

The algorithm can be run in a multi-core mode in order to speed up the execu-
tion. Moreover the patterns can be transferred just one time on the accelerator
to reduce the overall latency.

Repeat Analyzer can be configured to analyse different repeats.
The graphic user interface can be improved to work with different short sequence
repeats at the same time and store the results obtain by the identification func-
tion.

The tool can be configured to detect Covid-19 patterns, for example:
https://www.ncbi.nlm.nih.gov/genbank/sars-cov-2-seqs/ and plot the result ob-
tained. It can also underline the body part affected by the disease.

Moreover the hash table to convert amino-acid fragments to DNA fragments
is easily implementable.


## 5 References

1. Unusual Pattern Detection in DNA Database Using KMP Algorithm
2. Programming by Expression Refinement: the KMP Algorithm
3. Parallized Knuth-Morris Pratt
4. ACM/SIGDA 12th international symposium on Field programmable gate
    arrays
5. Prefix function. Knuth–Morris–Pratt algorithm
6. Computing Prefix Function - Knuth–Morris–Pratt Algorithm
7. Knuth-Morris-Pratt algorithm
8. KMP prefix table
9. Simpler KMP prefix table building. What would be wrong with this im-
    plementation
10. Introduction to Algorithms for Biologists


