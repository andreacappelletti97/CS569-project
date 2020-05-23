#include "xcl2.hpp"
#include <algorithm>
#include <iostream>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <fstream>





  int main(int argc, char **argv)
  {
    char data;

    ifstream inputFile("proteine.txt");
    while (!inputFile.eof())
    {
      inputFile >> data;
      std::cout << data;
    }

    inputFile.close();
  }