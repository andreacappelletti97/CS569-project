//
//  fsm.cpp
//  kmp_fsm
//
//  Created by Andrea Cappelletti on 26/03/2020.
//  Copyright © 2020 Andrea Cappelletti. All rights reserved.
//

#include <stdio.h>
#include <iostream>

void printPi(int patSize, int pi[])
{
    for (int j = 0; j < patSize + 1; j++)
    {
        std::cout << pi[j] << " ";
    }
    std::cout << std::endl;
}

void computePrefix(std::string pat)
{

    int pi[pat.size()];
    pi[0] = -1;
    pi[1] = 0;
    int a = 0;

    for (int i = 1; i < pat.size(); i++)
    {
        if (pi[i] == 0)
        {
            if (pat[a + i] == pat[a])
                pi[i + 1] = 1;
            else
                pi[i + 1] = 0;
        }
        else
        {
            if (pat[a + i] == pat[a + pi[i]])
                pi[i + 1] = pi[i] + 1;
            else
                pi[i + 1] = 0;
        }
    }
    printPi(pat.size(), pi);
}

int main(int argc, const char *argv[])
{

    std::string pat = "aagt";
    int state = 0;
    int pi[pat.size()];
    pi[0] = -1;
    pi[1] = 0;
    int i = 0; //index

    while (i <= pat.size())
    {
        switch (state)
        {
        case 0:
            std::cout << "State 0" << std::endl;
            if (pi[i] == 0)
            {
                state = 1;
                break;
            }
            else
            {
                state = 2;
                break;
            }
        case 1:
            std::cout << "State 1" << std::endl;
            if (pat[i] == pat[0])
            {
                state = 3;
                break;
            }
            else
            {
                state = 4;
                break;
            }
        case 2:
            std::cout << "State 2" << std::endl;
            if (pat[i] == pat[pi[i]])
            {
                state = 5;
                break;
            }
            else
            {
                state = 6;
                break;
            }

        case 3:
            std::cout << "State 3" << std::endl;
            pi[i + 1] = 1;
            ++i;
            state = 2;
            break;

        case 4:
            std::cout << "State 4" << std::endl;
            pi[i + 1] = 0;
            ++i;
            state = 1;
            break;

        case 5:
            std::cout << "State 5" << std::endl;
            pi[i + 1] = pi[i] + 1;
            ++i;
            state = 2;
            break;

        case 6:
            std::cout << "State 6" << std::endl;
            pi[i + 1] = 0;
            ++i;
            state = 1;
            break;
        }
    }

    computePrefix(pat);
    printPi(pat.size(), pi);
}
