#include "xcl2.hpp"
#include <algorithm>
#include <iostream>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <fstream>



#define DIM 1         //numero di coppie
#define maxseq 4    //dimensione array seq
#define maxstring 12 //dimensione array string
#define piDIM 5



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
                                 sizeof(int) * piDIM * DIM,
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

  OCL_CHECK(err, err = kernel.setArg(0, buffer_occ));
  OCL_CHECK(err, err = (kernel).setArg(1, buffer_stringdim));
  OCL_CHECK(err, err = (kernel).setArg(2, buffer_seqdim));
  OCL_CHECK(err, err = (kernel).setArg(3, buffer_seq));
  OCL_CHECK(err, err = (kernel).setArg(4, buffer_string));

  OCL_CHECK(err, err = (kernel).setArg(5, buffer_pi));

  std::cout << "ARG SETUP DONE" << std::endl;

  // Copy input data to Device Global Memory from HOST to board
  OCL_CHECK(err,
            err = q.enqueueMigrateMemObjects({buffer_occ, buffer_stringdim, buffer_seqdim, buffer_string, buffer_seq, buffer_pi},
                                             0  /*0 means from host*/));

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



//Function to read input string and pattern
void getInputString(std::vector<char, aligned_allocator<char>> &string, int type)
{
  std::ifstream inputFile;
  if (type == 0)
  {

    inputFile.open("proteine.txt");
  }
  else
  {

    inputFile.open("pattern.txt");
  }

  while (!inputFile.eof())
  {
    char c;
    inputFile >> c;
    string.push_back(c);
  }
  string.pop_back();
}

//Function to print vector content
void printVectorContent(std::vector<char, aligned_allocator<char>> &repeat)
{
  for (unsigned int i = 0; i < repeat.size(); i++)
  {
    std::cout << i << " " << repeat[i] << std::endl;
  }
}


void failure_function(std::vector<char, aligned_allocator<char>> &seq, std::vector<int, aligned_allocator<int>> &seqdim, int *pi)
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

  std::vector<char, aligned_allocator<char>> string;
  std::vector<char, aligned_allocator<char>> pattern;
  std::vector<int, aligned_allocator<int>> vStringdim(DIM);
  std::vector<int, aligned_allocator<int>> vSeqdim(DIM);
  std::vector<int, aligned_allocator<int>> vOcc(50);
  std::vector<int, aligned_allocator<int>> vPi(piDIM * DIM);
  int pi[piDIM * DIM];

  //Set static dimension to try
  vSeqdim.push_back(4);
  vStringdim.push_back(12);


  //Read input string
  getInputString(string, 0);
  printVectorContent(string);
  //Read pattern to search into the string
  getInputString(pattern, 1);
  printVectorContent(pattern);
//Compute failure function
failure_function(pattern, vSeqdim, pi); 

for (int i = 0; i < piDIM * DIM; i++)
  {
    vPi[i] = pi[i];
  }

 //Call run kernel function
  double kernel_time_in_sec = 0;

  kernel_time_in_sec = run_krnl(context,
                                q,
                                kernel,
                                vStringdim,
                                vSeqdim,
                                string,
                                pattern,
                                vPi,
                                vOcc);

  std::cout << "Total time in seconds: " << kernel_time_in_sec << std::endl;


for (unsigned int i = 0; i < vOcc.size(); i++)
  {
    std::cout << i << " " << vOcc[i] << std::endl;
  }

}