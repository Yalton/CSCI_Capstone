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

    // std::ifstream file("file.csv");
    // std::string line;
    // std::vector<std::vector<std::vector<double>>> matrix;

#ifdef DEBUG
    std::cout << "Loading "
              << "file.csv"
              << " into 3D matrix" << std::endl;
#endif


    // file.close();
    // Vectors to hold data from each column
    std::vector<double> x;
    std::vector<double> y;
    std::vector<double> z;

    // vector<vector<vector<int>>> vec = vector<vector<vector<int>>>();

    // Open the file
    std::ifstream file("file.csv");

    // Read the file line by line
    std::string line;
    while (std::getline(file, line))
    {

        // Create a stringstream to read the line
        std::stringstream line_stream(line);

        // Create a double to hold a value from the file
        double value;

        // Read x
        std::getline(line_stream, line, ',');
        std::stringstream(line) >> value;
        x.push_back(value);

        // Read y
        std::getline(line_stream, line, ',');
        std::stringstream(line) >> value;
        y.push_back(value);

        // Read z
        std::getline(line_stream, line, ',');
        std::stringstream(line) >> value;
        z.push_back(value);
    }

    // Close the file
    file.close();

#ifdef DEBUG
    std::cout << "Number of items in x vec " << x.size() << " Number of items in y vec " << y.size()
              << " Number of items in z vec " << z.size() << std::endl;
#endif

    return 0;
}


// void printcsv(std::ostream &out, const std::vector<std::vector<std::vector<double>>> &v)
// {
//     for (auto &m : v)
//     {
//         for (auto &n : m)
//         {
//             for (auto &k : n)
//             {
//                 out << k << ",";
//             }
//             out << std::endl;
//         }
//         out << std::endl;
//     }
// }

// vector<vector<vector<int> > > vec (5,vector<vector<int> >(3,vector <int>(2,4)));
// std::vector<std::vector<std::vector<double>>> matrix;
// matrix.push_back(x);
// matrix.push_back(y);
// matrix.push_back(z);

//     int nx = matrix.size();
//     int ny = matrix[0].size();
//     int nz = matrix[0][0].size();

// #ifdef DEBUG
//     std::cout << "Number of items in x " << nx << " Number of items in y " << ny
//               << " Number of items in z " << nz << std::endl;
//     std::ofstream ofile("out.csv");
//     printcsv(ofile, matrix);
// #endif
// long double integral;
//     int i, j, k = 0;

// #pragma omp parallel for num_threads(thread_count) private(k, i, j) \
//     shared(nx, ny, nz)
//     for (k = 0; k < nz; k++)
//     {
//         for (i = 0; i < nx; i++)
//         {
//             for (j = 0; j < ny; j++)
//             {
//                 integral += 0.5 * (matrix[i][j][k] + matrix[i + 1][j][k]) *
//                             (matrix[i + 1][j][k] - matrix[i][j][k]);
//             }
//         }

//         for (j = 0; j < ny; j++)
//         {
//             for (i = 0; i < nx; i++)
//             {
//                 integral += 0.5 * (matrix[i][j][k] + matrix[i][j + 1][k]) *
//                             (matrix[0][j + 1][k] - matrix[0][j][k]);
//             }
//         }
//     }

//     std::cout << integral << std::endl;
    // while (std::getline(file, line))
// {
//     std::vector<std::vector<double>> layer;
//     std::istringstream iss(line);
//     std::string token;
//     while (std::getline(iss, token, ','))
//     {
//         std::vector<double> row;
//         std::istringstream iss2(token);
//         std::string token2;
//         while (std::getline(iss2, token2, ';'))
//         {
//             row.push_back(std::stod(token2));
//         }
//         layer.push_back(row);
//     }
//     matrix.push_back(layer);
// }
// while (getline(file, line))
// {
//     std::stringstream ss(line);
//     std::string token;

//     int i = 0;
//     int j = 0;
//     int k = 0;

//     if (matrix.empty())
//     {
//         matrix.emplace_back();
//         matrix.back().emplace_back();
//     }

//     while (getline(ss, token, ','))
//     {
//         // Read CSV
//         if (i == 0)
//         {
//             matrix[k][j].push_back(std::stoi(token));
//             i++;
//         }
//         if (i == 1)
//         {
//             matrix[k].emplace_back();
//             matrix[k].back().push_back(std::stoi(token));
//             j++;
//             i++;
//         }
//         if (i == 2)
//         {
//             k++;
//             matrix.emplace_back();
//             matrix.back().emplace_back();
//             matrix.back().back().push_back(std::stoi(token));
//             i = 0;
//             j = 0;
//         }
//     }
// }