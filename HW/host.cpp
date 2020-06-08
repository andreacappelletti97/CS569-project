#include "xcl2.hpp"
#include <algorithm>
#include <iostream>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <string>

#define DIM 200           //numero di coppie
#define maxseq 204800     //dimensione array seq
#define maxstring 1638400 //dimensione array string
#define PI maxseq + DIM

double run_krnl(cl::Context &context,
                cl::CommandQueue &q,
                cl::Kernel &kernel,
                std::vector<int, aligned_allocator<int>> &vStringdim,
                std::vector<int, aligned_allocator<int>> &vSeqdim,
                std::vector<char, aligned_allocator<char>> &vString,
                std::vector<char, aligned_allocator<char>> &vSeq,
                std::vector<int, aligned_allocator<int>> &vPi,
                std::vector<int, aligned_allocator<int>> &vOcc)
{
    cl_int err;

    // These commands will allocate memory on the FPGA. The cl::Buffer objects can
    // be used to reference the memory locations on the device.
    //Creating Buffers

    std::cout << "RUN KERNEL ENTER" << std::endl;

    OCL_CHECK(err,
              cl::Buffer buffer_stringdim(context,
                                          CL_MEM_USE_HOST_PTR |
                                              CL_MEM_READ_ONLY,
                                          sizeof(int) * DIM,
                                          vStringdim.data(),
                                          &err));
    OCL_CHECK(err,
              cl::Buffer buffer_seqdim(context,
                                       CL_MEM_USE_HOST_PTR |
                                           CL_MEM_READ_ONLY,
                                       sizeof(int) * DIM,
                                       vSeqdim.data(),
                                       &err));

    OCL_CHECK(err,
              cl::Buffer buffer_string(context,
                                       CL_MEM_USE_HOST_PTR |
                                           CL_MEM_READ_ONLY,
                                       sizeof(char) * maxstring,
                                       vString.data(),
                                       &err));

    OCL_CHECK(err,
              cl::Buffer buffer_seq(context,
                                    CL_MEM_USE_HOST_PTR |
                                        CL_MEM_READ_ONLY,
                                    sizeof(char) * maxseq,
                                    vSeq.data(),
                                    &err));
    OCL_CHECK(err,
              cl::Buffer buffer_pi(context,
                                   CL_MEM_USE_HOST_PTR |
                                       CL_MEM_READ_ONLY,
                                   sizeof(int) * PI,
                                   vPi.data(),
                                   &err));

    OCL_CHECK(err,
              cl::Buffer buffer_occ(context,
                                    CL_MEM_USE_HOST_PTR |
                                        CL_MEM_WRITE_ONLY,
                                    sizeof(int) * DIM,
                                    vOcc.data(),
                                    &err));

    //Setting the kernel Arguments

    OCL_CHECK(err, err = (kernel).setArg(0, buffer_occ));
    OCL_CHECK(err, err = (kernel).setArg(1, buffer_stringdim));
    OCL_CHECK(err, err = (kernel).setArg(2, buffer_seqdim));
    OCL_CHECK(err, err = (kernel).setArg(3, buffer_seq));
    OCL_CHECK(err, err = (kernel).setArg(4, buffer_string));
    OCL_CHECK(err, err = (kernel).setArg(5, buffer_pi));

    std::cout << "ARG SETUP DONE" << std::endl;

    // Copy input data to Device Global Memory from HOST to board
    OCL_CHECK(err,
              err = q.enqueueMigrateMemObjects({buffer_occ, buffer_stringdim, buffer_seqdim, buffer_string, buffer_seq, buffer_pi},
                                               0 /* 0 means from host*/));

    std::cout << "INPUT DATA COPIED" << std::endl;

    std::chrono::duration<double> kernel_time(0);

    auto kernel_start = std::chrono::high_resolution_clock::now();

    //Execution of the kernel KMP
    OCL_CHECK(err, err = q.enqueueTask(kernel));

    auto kernel_end = std::chrono::high_resolution_clock::now();

    kernel_time = std::chrono::duration<double>(kernel_end - kernel_start);

    std::cout << "KERNEL EXE COMPLETED" << std::endl;

    // Copy Result from Device Global Memory to Host Local Memory
    OCL_CHECK(err,
              err = q.enqueueMigrateMemObjects({buffer_occ},
                                               CL_MIGRATE_MEM_OBJECT_HOST));

    q.finish();

    return kernel_time.count();
}

//Function to compute the failure function of the KMP algorithm
void failure_function(std::vector<char, aligned_allocator<char>> &seq, std::vector<int, aligned_allocator<int>> &seqdim, std::vector<int, aligned_allocator<int>> &pi)
{

    int seq_count = 0; //scorre le sequenze
    int pi_count = 0;  //scorre pi

    //For each couple computer PI
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

//Utility Function to print vector content
void printVectorContent(std::vector<char, aligned_allocator<char>> &string)
{
    for (unsigned int i = 0; i < string.size(); i++)
    {
        std::cout << i << " " << string[i] << std::endl;
    }
}

//Function to read input seq and automatically set seq dimension for Repeat Analyzer
void getPattern(std::vector<char, aligned_allocator<char>> &seq, std::vector<int, aligned_allocator<int>> &seqdim, bool pattern)
{

    bool firstRead = true;
    std::string line;
    std::string pat;
    std::ifstream inputFile;
    //Input file for sequences
    if (pattern)
    {
        inputFile.open("pattern.txt");
    }
    else
    {
        inputFile.open("proteine.txt");
    }
    while (getline(inputFile, line))
    {
        //New sequence is starting
        if (line.substr(0, 2) == "SQ" && isdigit(line[2]) && line[3] == ':')
        {
            //First read
            if (firstRead)
            {
                pat = line;
                firstRead = false;
            }
            //If it's not the first read push the new sequence into the array
            else
            {
                for (unsigned int i = 4; i < pat.size(); i++)
                {
                    seq.push_back(pat[i]);
                }
                //Update the dimension with the size of the sequence in input
                seqdim.push_back(pat.size() - 4);
                pat = line;
            }
        } //End of the file
        else if (line.substr(0, 3) == "END")
        {

            for (unsigned int i = 4; i < pat.size(); i++)
            {
                seq.push_back(pat[i]);
            }
            seqdim.push_back(pat.size() - 4);
            break;
        }

        else
        {
            pat += line;
        }
    }
}

//Function to read fasta file format and automatically set dimension of seq and string
void readFastaInput(std::vector<char, aligned_allocator<char>> &seq, std::vector<int, aligned_allocator<int>> &seqdim, bool isString)
{
    std::ifstream input;
    if (isString)
    {
        input.open("string2.fasta");
    }
    else
    {
        input.open("pattern2.fasta");
    }

    std::string line, id, DNA_sequence;

    while (std::getline(input, line))
    {
        //std::cout << line << std::endl;

        // line may be empty so you *must* ignore blank lines
        // or you have a crash waiting to happen with line[0]
        if (line.empty())
            continue;

        if (line[0] == '>')
        {
            // output previous line before overwriting id
            // but ONLY if id actually contains something
            if (!id.empty())
            {
                for (int i = 0; i < DNA_sequence.size(); i++)
                {
                    seq.push_back(DNA_sequence[i]);
                }
                seqdim.push_back(DNA_sequence.size());
                //std::cout << "DNA SIZE: " << DNA_sequence.size() << std::endl;
            }

            //seqdim.push_back(DNA_sequence.size());
            id = line.substr(1);
            DNA_sequence.clear();
        }
        else
        { //  if (line[0] != '>'){ // not needed because implicit
            DNA_sequence += line;
        }
    }
    for (int i = 0; i < DNA_sequence.size(); i++)
    {
        seq.push_back(DNA_sequence[i]);
    }
    seqdim.push_back(DNA_sequence.size());
    /*
  std::cout << "PRINT SEQ " << std::endl;
  for (int i = 0; i < seq.size(); i++)
  {
    std::cout << seq[i];
  } 

  std::cout << std::endl;
  std::cout << "PRINT SEQDIM " << std::endl;
  for (int i = 0; i < seqdim.size(); i++)
  {
    std::cout << i << " " << seqdim[i] << std::endl;
  }
  */
}

int main(int argc, char **argv)
{
    //Define the platform = devices + context + queues
    cl_int err;
    cl::Context context;
    cl::CommandQueue q;
    cl::Kernel kernel;
    std::string binaryFile = argv[1];

    // The get_xil_devices will return vector of Xilinx Devices
    auto devices = xcl::get_devices("Xilinx");

    // read_binary_file() command will find the OpenCL binary file created using the
    // V++ compiler load into OpenCL Binary and return pointer to file buffer.

    auto fileBuf = xcl::read_binary_file(binaryFile);

    cl::Program::Binaries bins{{fileBuf.data(), fileBuf.size()}};
    int valid_device = 0;
    for (unsigned int i = 0; i < devices.size(); i++)
    {
        auto device = devices[i];
        // Creating Context and Command Queue for selected Device
        OCL_CHECK(err, context = cl::Context(device, NULL, NULL, NULL, &err));
        OCL_CHECK(err,
                  q = cl::CommandQueue(
                      context, device, CL_QUEUE_PROFILING_ENABLE, &err));

        std::cout << "Trying to program device[" << i
                  << "]: " << device.getInfo<CL_DEVICE_NAME>() << std::endl;
        cl::Program program(context, {device}, bins, NULL, &err);
        if (err != CL_SUCCESS)
        {
            std::cout << "Failed to program device[" << i
                      << "] with xclbin file!\n";
        }
        else
        {
            std::cout << "Device[" << i << "]: program successful!\n";
            OCL_CHECK(err,
                      kernel = cl::Kernel(program, "kmp", &err));
            valid_device++;
            break; // we break because we found a valid device
        }
    }
    if (valid_device == 0)
    {
        std::cout << "Failed to program any device found, exit!\n";
        exit(EXIT_FAILURE);
    }

    //Declare input vector
    std::vector<int, aligned_allocator<int>> occ(DIM);
    std::vector<int, aligned_allocator<int>> stringdim;
    std::vector<int, aligned_allocator<int>> seqdim;
    std::vector<char, aligned_allocator<char>> seq;
    std::vector<char, aligned_allocator<char>> string;
    std::vector<int, aligned_allocator<int>> pi;

    readFastaInput(string, stringdim, true);
    readFastaInput(seq, seqdim, false);

    double kernel_time_in_sec = 0;


    while (string.size() > 0 )
    {
        std::cout << "WHILE ENTER" << std::endl;
        std::vector<char, aligned_allocator<char>> stringDiv(maxstring);
        std::vector<int, aligned_allocator<int>> stringdimDiv(DIM);

        if (string.size() >= maxstring)
        {
            std::cout << "MX STRING GREATER" << std::endl;
            for (size_t i = 0; i < maxstring; i++)
            {
                stringDiv[i] = string[i];
            }
            //Set all the string dimension
            for (size_t m = 0; m < DIM; m++)
            {
                stringdimDiv[m] = maxstring / DIM;
            }
        }
        else
        {
            for (size_t i = 0; i < string.size(); i++)
            {
                stringDiv[i] = string[i];
            }
            stringdimDiv[0] = string.size();
        }

        std::cout << "STRING SIZE " << stringDiv.size() << std::endl;
        std::cout << "STRING DIM SIZE " << stringdimDiv.size() << std::endl;

        int sequence_index_seq = 0;
        int save_sequence_index_seq = 0;
        //For all the sequences
        for (size_t l = 0; l < seqdim.size(); l++)
        { 

            
            for (int i = 0; i < DIM; i++)
            {
                occ[i] = -1;
            }

            std::vector<char, aligned_allocator<char>> currentSeq(seqdim[l] * DIM);
            std::vector<int, aligned_allocator<int>> currentSeqDim(DIM);
            std::vector<int, aligned_allocator<int>> pi(seqdim[l] * DIM + DIM);
            int sequence_index = 0;
            
            save_sequence_index_seq = sequence_index_seq;
            //Fill the DIM couples for the comparisons
            for (size_t i = 0; i < DIM; i++)
            {
                for (size_t s = sequence_index; s < sequence_index + seqdim[l]; s++)
                {

                    currentSeq[s] = seq[sequence_index_seq++];
                }
                sequence_index += seqdim[l];
                currentSeqDim[i] = seqdim[l];
                sequence_index_seq = save_sequence_index_seq;
            }

            sequence_index_seq = save_sequence_index_seq + seqdim[l];

            std::cout << "SEQ" << std::endl;
            std::cout << currentSeq.size() << std::endl;
            std::cout << "SEQ DIM" << std::endl;
            std::cout << currentSeqDim.size() << std::endl;
            			for(int i = 0; i < currentSeq.size(); i++){
			std::cout << i <<" "<<currentSeq[i]<< std::endl;	
}


            failure_function(currentSeq, currentSeqDim, pi);

            kernel_time_in_sec += run_krnl(context,
                                           q,
                                           kernel,
                                           stringdimDiv,
                                           currentSeqDim,
                                           stringDiv,
                                           currentSeq,
                                           pi,
                                           occ);
        }

       string.erase(string.begin(), string.begin() + maxstring);
        std::cout << "STRING DIM" << std::endl;
        std::cout << string.size() << std::endl;
    }

    std::cout << "Total time in seconds: " << kernel_time_in_sec << std::endl;
}
