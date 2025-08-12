// This C program takes two command line arguments:
// 1. An integer 'n' specifying the size of a symmetric matrix.
// 2. A filename containing n*(n-1)/2 float values to populate the upper triangle of the matrix.

#include <stdio.h>
#include <malloc.h>
#include <math.h>

int main(int argc, char *argv[]) {
    // Initialize variables and allocate memory for arrays.
    int i, j, k;
    int n;
    int *subunit;
    FILE *fp;
    float *q_list, **q_matrix;

    // Parse the first argument as the size of the matrix.
    n = atoi(argv[1]);

    // Allocate memory for q_list (upper triangle elements) and q_matrix.
    q_list = (float *)malloc(n * (n - 1) / 2 * sizeof(float));
    q_matrix = (float **)malloc(n * sizeof(float *));
    for(i = 0; i < n; i++){
        q_matrix[i] = (float *)malloc(n * sizeof(float));
    }

    // Read the upper triangle elements from the file specified in argv[2].
    fp = fopen(argv[2], "r");
    if(fp == NULL){
        printf("Failed to open input file.\n");
        return 1;
    }

    float value;
    int count = 0;
    while(fscanf(fp, "%f", &value) == 1 && count < n * (n - 1) / 2){
        q_list[count++] = value;
    }
    fclose(fp); // Close the input file after reading.

    if(count != n * (n - 1) / 2){
        printf("Input file is empty or doesn't contain enough data.\n");
        return 1;
    } else {
        // Populate the symmetric matrix.
        for(i = 0, k = 0; i < n; i++){
            for(j = i + 1; j < n; j++, k++){
                q_matrix[i][j] = q_list[k];
            }
            // Symmetrically copy the upper triangle to the lower triangle.
            for(j = 0; j < i; j++){
                q_matrix[i][j] = q_matrix[j][i];
            }
        }

        // Set diagonal elements to zero.
        for(i = 0; i < n; i++){
            q_matrix[i][i] = 0.0;
        }

        // Determine if elements near the diagonal are close to zero, storing results in subunit array.
        subunit = (int *)malloc(n * sizeof(int));
        for(i = 0; i < n; i++){
            subunit[i] = 1;
            for(j = 0; j < n; j++){
                if(fabs(q_matrix[i][j]) >= 1e-5){
                    subunit[i] = 0;
                    break;
                }
            }
        }

        // Write the contents of subunit array into a file named "subunit.txt".
        fp = fopen("subunit.txt", "w");
        if(fp == NULL){
            printf("Failed to create output file.\n");
            return 1;
        }
        for(i = 0; i < n; i++){
            fprintf(fp, "%d\n", subunit[i]);
        }
        fclose(fp); // Close the output file after writing.
    }

    // Free allocated memory here (omitted for brevity).

    return 0;
}


// To use this program:
// Compile it using a C compiler (e.g., gcc yourfile.c -o yourprogram).
// Run with two arguments: the matrix size and the input file name,
// e.g., ./yourprogram 5 data.txt