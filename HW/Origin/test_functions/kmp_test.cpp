#include "kmp_test.hpp"
#include <iostream>

bool check(std::string v1, std::string v2, int occ)
{

    std::vector<int> test_occ(v1.size(), 0);

    unsigned int idx = 0;

    test_occ[0] = -1; //AGGIUNTA

    for (unsigned int i = 0; i < v1.size(); i++)
    {
        bool tmp = true;
        for (unsigned int j = 0; j < v2.size(); j++)
        {
            if (v1[i + j] != v2[j] || (i + j) > v1.size())
            {
                tmp = false;
                break;
            }
        }
        if (tmp)
        {
            test_occ[idx] = i;
            idx++;
        }
    }

    bool test = true;

    if (test_occ[0] != occ)
        test = false;

    // std::cout<<test_occ[0]<<std::endl;

    // if (test_occ[0]==-1) //AGGIUNTA
    // 	std::cout<<"NO MATCH"<<std::endl;

    return test;
}
