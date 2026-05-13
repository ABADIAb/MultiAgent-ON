#include <assert.h>
#include <chrono>
#include <fstream>
#include <iostream>
#include <random>
#include <time.h>

#include "Network.h"

using namespace NS_NBGA;
using namespace std;


int main (int argc, char **argv)
{
    // check the number of input arguments
    if (argc < 7)
    {
        cerr << "Number of the entered arguments is less than expected! Please make sure to give all the information." << endl; 
        cerr << "Arguments: [TOPOLOGY] [OBJECTIVE_FUNCTION] [NUMBER_WAVELENGTHS] [STOPPING_CONDITION] [NUMBER_YEARS] [OUTPUT_FILE]";
        cerr << endl << "For more details please refer to README file." << endl;
        return -1;
    }

    if (argc > 7)
    {
        cerr << "Number of the entered arguments is more than expected!" << endl; 
        cerr << "Arguments: [TOPOLOGY] [OBJECTIVE_FUNCTION] [NUMBER_WAVELENGTHS] [STOPPING_CONDITION] [NUMBER_YEARS] [OUTPUT_FILE]";
        cerr << endl << "For more details please refer to README file." << endl;
        return -1;
    }

    // for cost only: 0 - for power only: 1 - for costified power model: 2 
    int objective = atoi(argv[2]);
    if (objective > 2 || objective < 0)
    {
        cerr << "Entered value for objective function is wrong! Please make sure to enter it correctly." << endl;
        cerr << "[0 for cost minimization] [1 for power minimization] [2 for costification of energy consumption]" << endl;
        cerr << "For more details please refer to README file." << endl;
        return -1;
    }

    // maximum number of wavelength 
    int number_lambdas = atoi(argv[3]);
    if (number_lambdas < 1)
    {
        cerr << "Entered value for number of wavelengths is wrong! Please make sure to enter it correctly." << endl;
        cerr << "It should be greater than 0." << endl;
        cerr << "For more details please refer to README file." << endl;
        return -1;
    }

    // number of generations that we want GA to explore
    int max_number_generation = atoi(argv[4]);
    if (max_number_generation < 0)
    {
        cerr << "Entered value for maximum number of generations is wrong! Please make sure to enter it correctly." << endl;
        cerr << "It should be either 0 or a positive number." << endl;
        cerr << "For more details please refer to README file." << endl;
        return -1;
    }

    // number of years that we plan the network for
    // it is used for calculating the electricity cost in costified model
    float years = atof(argv[5]);
    if (years < 0)
    {
        cerr << "Entered value for number of years is wrong! Please make sure to enter it correctly." << endl;
        cerr << "It should be a positive number." << endl;
        cerr << "For more details please refer to README file." << endl;
        return -1;
    }

    // current date/time based on current system
 	time_t now = time(0);

    // initialize the output file and write a banner into it
    ofstream result_file(argv[6], std::ios_base::app | std::ios_base::out);
    result_file << endl << endl << "***************************" << endl;
	result_file << ctime(&now) << "***************************" << endl;
    result_file.close();
    
    // set the random seed
    srand(32);

    // start time
    auto begin = std::chrono::high_resolution_clock::now();

    // create an instance of class Network and initialize it with the parameters
    Network hNetwork;
    if (!hNetwork.initialize(argv[1], objective, number_lambdas, max_number_generation, years, argv[6]))
        return -1;

    // run the Genetic Algorithm
    hNetwork.runExternalGA();

    // end time
    auto end = std::chrono::high_resolution_clock::now();

    // calculate run time
    auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);

    cout << endl << "Finished!" << endl;
    printf("Time measured: %.3f seconds.\n", elapsed.count() * 1e-9);

    result_file.open(argv[6], std::ios_base::app | std::ios_base::out);
    result_file << endl << "-------------------------- Finished --------------------------" << endl;
    result_file.precision(3);
    result_file << "Time measured: " << elapsed.count() * 1e-9 << " seconds." << endl;
    result_file << endl << "-------------------------- ******** --------------------------" << endl << endl;
    result_file.close();

    return 0;
}