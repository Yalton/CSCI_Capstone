#define DEBUG

#include <fstream>
#include <iostream>
#include <omp.h>
#include <sstream>
#include <string>
#include <vector>

int main(int argc, char *argv[])
{

    std::string infile;
    int thread_count;
    if (argc > 2)
    {
        printf("Using custom input file & custom thread count of %s %s: argc=%d, "
               "argv[0]=%s, argv[1]=%s, argv[2]=%s\n",
               argv[2], argv[0], argc, argv[0], argv[1], argv[2]);
        infile = argv[1];
        thread_count = atoi(argv[2]);
    }
    else
    {
        printf("Using default input file & default thread count of 4 %s: argc=%d, "
               "argv[0]=%s, argv[1]=%s\n",
               argv[0], argc, argv[0], argv[1]);
        infile = "file.csv";
        thread_count = 4;
    }

    std::ifstream file("file.csv");
    std::string line;
    std::vector<std::vector<std::vector<double>>> matrix;
    long double integral;

#ifdef DEBUG
    std::cout << "Loading "
              << "file.csv"
              << " into 3D matrix" << std::endl;
#endif

    while (std::getline(file, line))
    {
        std::vector<std::vector<double>> layer;
        std::istringstream iss(line);
        std::string token;
        while (std::getline(iss, token, ','))
        {
            std::vector<double> row;
            std::istringstream iss2(token);
            std::string token2;
            while (std::getline(iss2, token2, ';'))
            {
                row.push_back(std::stod(token2));
            }
            layer.push_back(row);
        }
        matrix.push_back(layer);
    }

    int nx = matrix.size();
    int ny = matrix[0].size();
    int nz = matrix[0][0].size();

#ifdef DEBUG
    std::cout << "Number of items in x " << nx << " Number of items in y " << ny
              << " Number of items in y " << nz << std::endl;
#endif

    int i, j, k = 0;

#pragma omp parallel for num_threads(thread_count) private(k, i, j) \
    shared(nx, ny, nz)
    for (k = 0; k < nz; k++)
    {
        for (i = 0; i < nx; i++)
        {
            for (j = 0; j < ny; j++)
            {
                integral += 0.5 * (matrix[i][j][k] + matrix[i + 1][j][k]) *
                            (matrix[i + 1][j][k] - matrix[i][j][k]);
            }
        }

        for (j = 0; j < ny; j++)
        {
            for (i = 0; i < nx; i++)
            {
                integral += 0.5 * (matrix[i][j][k] + matrix[i][j + 1][k]) *
                            (matrix[0][j + 1][k] - matrix[0][j][k]);
            }
        }
    }

    std::cout << integral << std::endl;
    return 0;
}