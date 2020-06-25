#include <iostream>
#include <cstdlib>
#include <ctime>
#include "kmp_test.hpp"
#define DIM 1000             //numero di coppie
#define maxseq 512000        //dimensione array seq
#define maxstring 4096000    //dimensione array string
#define PI maxseq+DIM        //dimensione array pi

#include <string>
#include <vector>

void kmp(int *occ, int *stringdim, int *seqdim, char *seq, char *string, int *pi);

char random_char()
{
    char alphabet[4] = {'A', 'C', 'G', 'T'};
    return alphabet[rand() % 4];
}

void failure_function(char *seq, int *seqdim, int *pi)
{

    int seq_count = 0; //scorre le sequenze
    int pi_count = 0;  //scorre pi

    for (int n = 0; n < DIM; n++)
    {
        pi[pi_count] = -1;    //first element always equal to -1
        pi[pi_count + 1] = 0; //second element always equal to 0

        for (int i = 1; i < seqdim[n]; i++)
        {
            if (seq[seq_count + i] == seq[seq_count + pi[pi_count + i]])
                pi[pi_count + i + 1] = pi[pi_count + i] + 1;
            else
            {
                if (seq[seq_count + i] == seq[seq_count])
                    pi[pi_count + i + 1] = pi[pi_count + i];
                else
                    pi[pi_count + i + 1] = 0;
            }

        }

        pi_count = pi_count + seqdim[n] + 1;
        seq_count = seq_count + seqdim[n];
    }
}

//numero random per definire la lunghezza della sequenza casualmente
int random_intsm()
{
    int number[7] = {3, 4, 5, 6, 7, 8, 9};
    return number[rand() % 7];
}

//numero random per definire la lunghezza della stringa casualmente
int random_intlg()
{
    int number[7] = {29, 35, 28, 30, 31, 33, 34};
    return number[rand() % 7];
}

int main(int argc, char *argv[])
{

    char string[maxstring];
    char seq[maxseq];

    int seqdim[DIM];
    int stringdim[DIM];

    int pi[PI];

    srand((unsigned)time(NULL));

    for (unsigned long long int i = 0; i < maxstring; i++)
        string[i] = random_char();


    std::cout<<"inizio seq\n";
    for (unsigned long long int i = 0; i < maxseq; i++)
        seq[i] = random_char();
    std::cout<<"caratteri assegnati\n";

    //assegno ai due array di dimensione dei numeri casuali
    for (unsigned long long int i = 0; i < DIM; i++)
        //seqdim[i] = random_intsm();
        seqdim[i] = 512;

    for (unsigned long long int i = 0; i < DIM; i++)
        //stringdim[i] = random_intlg();
        stringdim[i] = 4096;

    std::cout<<"dimensione assegnata\n";

    int occ[DIM];
    for (unsigned long long int i = 0; i < DIM; i++)
        occ[i] = -1;

    failure_function(seq, seqdim, pi);
/*
    int s=10;
    for (int i = 0; i < DIM; i++) s=s+seqdim[i];
    for (int i =0; i<s; i++) std::cout<<pi[i]<<"";
    std::cout<<std::endl;
*/
    kmp(occ, stringdim, seqdim, seq, string, pi);

    std::string str;
    std::string sq;
    int a = 0;
    int b = 0;
    bool test = true;
    for (unsigned int i = 0; i < DIM; i++)
    {

        for (int j = 0; j < stringdim[i]; j++)
            str.push_back(string[b + j]);
        for (int j = 0; j < seqdim[i]; j++)
            sq.push_back(seq[a + j]);
/*
        std::cout << std::endl;
        std::cout << str << std::endl;
        std::cout << sq << std::endl;
        std::cout << occ[i];

        std::cout << std::endl;
*/
        std::string v1 = std::string(str);
        std::string v2 = std::string(sq);

        test &= check(v1, v2, occ[i]);

        str.clear();
        sq.clear();

        a = a + seqdim[i];
        b = b + stringdim[i];
    }

    if (test)
        std::cout << "ALL RESULTS CORRECT" << std::endl;
    else
        std::cout << "TEST FAILED" << std::endl;

    return 0;
}
