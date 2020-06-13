#include <string>
#include <vector>

#define DIM 200             //numero di coppie
#define maxseq 204800        //dimensione array seq
#define maxstring 1638400     //dimensione array string
#define PI maxseq+DIM  

#include <iostream>
extern "C"
{
	void kmp(int *occ, int *stringdim, int *seqdim, char *seq, char *string, int *pi)
	{

#pragma HLS INTERFACE m_axi port = occ offset = slave bundle = gmem0
#pragma HLS INTERFACE m_axi port = stringdim offset = slave bundle = gmem1
#pragma HLS INTERFACE m_axi port = seqdim offset = slave bundle = gmem2
#pragma HLS INTERFACE m_axi port = seq offset = slave bundle = gmem3
#pragma HLS INTERFACE m_axi port = string offset = slave bundle = gmem4
#pragma HLS INTERFACE m_axi port = pi offset = slave bundle = gmem5

#pragma HLS INTERFACE s_axilite port = occ bundle = control
#pragma HLS INTERFACE s_axilite port = stringdim bundle = control
#pragma HLS INTERFACE s_axilite port = seqdim bundle = control
#pragma HLS INTERFACE s_axilite port = seq bundle = control
#pragma HLS INTERFACE s_axilite port = string bundle = control
#pragma HLS INTERFACE s_axilite port = pi bundle = control

#pragma HLS INTERFACE s_axilite port = return bundle = control

#pragma HLS dataflow

		int occ_local[DIM];
		char string_local[maxstring];
		char seq_local[maxseq];

		int seqdim_local[DIM];
		int stringdim_local[DIM];
		int pi_local[PI];

		std::cout << "SOURCE KMP" << std::endl;

		for (int i = 0; i < PI; i++)
		{
#pragma HLS pipeline
			pi_local[i] = pi[i];
		}

		for (int i = 0; i < DIM; i++)
		{
#pragma HLS pipeline
			occ_local[i] = occ[i];
			stringdim_local[i] = stringdim[i];
			seqdim_local[i] = seqdim[i];
		}

		for (int i = 0; i < maxstring; i++)
		{
#pragma HLS pipeline
			string_local[i] = string[i];
		}

		for (int i = 0; i < maxseq; i++)
		{
#pragma HLS pipeline
			seq_local[i] = seq[i];
		}

		unsigned int i = 0;
		unsigned int j = 0;
		unsigned int a = 0;
		unsigned int b = 0;
		int pi_count = 0;
		int n;
		int k;

	kmp:
		for (n = 0; n < DIM; n++)
		{

		matching:
			for (k = 0; k < (maxstring + maxseq); k++)
			{

#pragma HLS pipeline

				if (j <= seqdim_local[n])
				{

					if (i >= (stringdim_local[n] ))
					{

						a = a + seqdim_local[n];
						b = b + stringdim_local[n];
						pi_count = pi_count + 1 + seqdim_local[n];
						i = 0;
						j = 0;

						break;
					}

					if (string_local[b + i + j] == seq_local[a + j])
					{
						j++;

						if (j == seqdim_local[n])
						{

							occ_local[n] = i;
							a = a + seqdim_local[n];
							b = b + stringdim_local[n];
							pi_count = pi_count + 1 + seqdim_local[n];
							i = 0;
							j = 0;

							break;
						}
					}
					else
					{

						if (i >= (stringdim_local[n] ))
						{

							a = a + seqdim_local[n];
							b = b + stringdim_local[n];
							pi_count = pi_count + 1 + seqdim_local[n];
							i = 0;
							j = 0;

							break;
						}
						else
						{

							if (j == 0)
								i++;
							else
							{

								i = i + j - pi_local[j + pi_count];
								j = 0;
							}
						}
					}
				}
				else
				{

					a = a + seqdim_local[n];
					b = b + stringdim_local[n];
					pi_count = pi_count + 1 + seqdim_local[n];
					i = 0;
					j = 0;

					break;
				}
			}
		}

		for (int i = 0; i < DIM; i++)
		{
#pragma HLS pipeline
			occ[i] = occ_local[i];
		}

/*
		std::cout << "OCC FINAL" << std::endl;
		for (int i = 0; i < DIM; i++)
		{
			std::cout << i << " " << occ_local[i] << std::endl;
		}

*/

	}
}

