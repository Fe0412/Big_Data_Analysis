#include <stdio.h>
#include <time.h>

#define A 2
#define B 3
#define C 4

__global__ void product(float *a, float *b, float *c, int aa, int bb, int cc)
{
	int ix = threadIdx.x + blockIdx.x * blockDim.x;
	int iy = threadIdx.y + blockIdx.y * blockDim.y;
	if (ix < aa && iy < cc)
	{
		float sum = 0;
		for (int index = 0; index < bb; index++)
		{
			sum += a[ix * bb + index] * b[index * cc + iy];
		}
		c[ix * cc + iy] = sum;
	}
}

int main()
{
	//********** CPU, matrix initialization **********
	float *a, *b, *c;

	a = (float *)malloc(A * B*sizeof(float));
	b = (float *)malloc(B * C*sizeof(float));
	c = (float *)malloc(A * C*sizeof(float));

	for (int i = 0; i < A * B; ++i)
		a[i] = 2;
	for (int i = 0; i < B * C; ++i)
		b[i] = 2;
	for (int i = 0; i < A * C; ++i)
		c[i] = 0;
	
	printf("input matrix 1:\n");
	for (int i = 0; i < A; i++)
	{
		for (int j = 0; j < B; j++)
			printf("%.2f\t", a[i * B + j]);
		printf("\n");
	}
	printf("\n");
	printf("input matrix 2:\n");
	for (int i = 0; i < B; i++)
	{
		for (int j = 0; j < C; j++)
			printf("%.2f\t", b[i * C + j]);
		printf("\n");
	}
	
	clock_t startc, finishc;

	//start using CPU to multiply matrix
	startc = clock();
	for (int i = 0; i < A; i++){
		for (int j = 0; j < C; j++)
		{
			float sum = 0;
			for (int k = 0; k < B; k++)
			{
				sum += a[i * B + k] * b[k * C + j];
			}
			c[i * C + j] = sum;
		}
	}
	finishc = clock();

	printf("\n");
	printf("output matrix (CPU):\n");
	//printf("number in matrix: %.2f\n", c[10]);
	
	for (int i = 0; i < A; i++)
	{
		for (int j = 0; j < C; j++)
			printf("%.2f\t", c[i * B + j]);
		printf("\n");
	}

	printf("***********************************************\n");
	printf("The total time using CPU: %f seconds\n", ((float)finishc - startc) / 1000);
	printf("***********************************************\n");

	//********** GPU, matrx initialization **********
	clock_t start, finish;
	float *d_a, *d_b, *d_c;

	//start using GPU to multiply matrix
	start = clock();

	cudaMalloc(&d_a, A * B*sizeof(float));
	cudaMalloc(&d_b, B * C*sizeof(float));
	cudaMalloc(&d_c, A * C*sizeof(float));

	cudaMemcpy(d_a, a, A * B*sizeof(float), cudaMemcpyHostToDevice);
	cudaMemcpy(d_b, b, B * C*sizeof(float), cudaMemcpyHostToDevice);
	cudaMemcpy(d_c, c, A * C*sizeof(float), cudaMemcpyHostToDevice);

	int dimx = 32;
	int dimy = 32;
	dim3 block(dimx, dimy);
	dim3 grid((A + block.x - 1) / block.x, (C + block.y - 1) / block.y);

	product << <grid, block >> >(d_a, d_b, d_c, A, B, C);

	cudaMemcpy(c, d_c, A * C*sizeof(float), cudaMemcpyDeviceToHost);
	/*
	printf("\n");
	printf("output matrix (using GPU):\n");
	for (int i = 0; i < A; i++)
	{
		for (int j = 0; j < C; j++)
			printf("%.2f\t", c[i * C + j]);
		printf("\n");
	}
	*/
	free(a);
	free(b);
	free(c);

	cudaFree(d_a);
	cudaFree(d_b);
	cudaFree(d_c);
	finish = clock();
	//printf("number in matrix (GPU): %d\n", f[1]);
	printf("***********************************************\n");
	printf("The total time using GPU: %f seconds\n", ((float)finish - start) / 1000);
	printf("***********************************************\n");

	return 0;
}