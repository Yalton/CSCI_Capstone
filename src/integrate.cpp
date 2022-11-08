#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <omp.h>

int main()
{
    std::ifstream file("file.csv");
    std::string line;
    std::vector<std::vector<std::vector<double>>> matrix;
    long double integral; 
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


    for (int k = 0; k < nz; k++)
    {
        for (int i = 0; i < nx; i++)
        {
            for (int j = 0; j < ny; j++)
            {
                integral += 0.5 * (matrix[i][j][k] + matrix[i + 1][j][k]) * (matrix[i + 1][j][k] - matrix[i][j][k]);
            }
        }

        for (int j = 0; j < ny; j++)
        {
            for (int i = 0; i < nx; i++)
            {
                integral += 0.5 * (matrix[i][j][k] + matrix[i][j + 1][k]) * (matrix[0][j + 1][k]  - matrix[0][j][k]);
            }
        }
    }

    std::cout << integral << std::endl;
    return 0;
}