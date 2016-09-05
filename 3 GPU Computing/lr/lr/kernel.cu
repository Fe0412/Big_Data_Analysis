
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <math.h>
#include <cuda_runtime.h>
#include <cublas_v2.h>

#define A 6
#define B 2
#define C 1

__global__ void transpose(float *odata, float* idata, int ny, int nx)
{
	int ix = blockDim.x * blockIdx.x + threadIdx.x;
	int iy = blockDim.y * blockIdx.y + threadIdx.y;

	if (ix < nx && iy < ny)
	{
		odata[ix * ny + iy] = idata[iy * nx + ix];
	}
}

__global__ void product(float *a, float *b, float *c, int aa, int bb, int cc)
{
	int ix = blockIdx.x * blockDim.x + threadIdx.x;
	int iy = blockIdx.y * blockDim.y + threadIdx.y;
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

#define PERR(call) \
if (call) {\
	fprintf(stderr, "%s:%d Error [%s] on "#call"\n", __FILE__, __LINE__, \
	cudaGetErrorString(cudaGetLastError())); \
	exit(1); \
}
#define ERRCHECK \
if (cudaPeekAtLastError()) {\
	fprintf(stderr, "%s:%d Error [%s]\n", __FILE__, __LINE__, \
	cudaGetErrorString(cudaGetLastError())); \
	exit(1); \
}

__global__ void inv_kernel(float *a_i, float *c_o, int n)
{
	int *p = (int *)malloc(3 * sizeof(int));
	int *info = (int *)malloc(sizeof(int));
	int batch;
	cublasHandle_t hdl;
	cublasStatus_t status = cublasCreate_v2(&hdl);

	info[0] = 0;
	batch = 1;
	float **a = (float **)malloc(sizeof(float *));
	*a = a_i;
	const float **aconst = (const float **)a;
	float **c = (float **)malloc(sizeof(float *));
	*c = c_o;
	status = cublasSgetrfBatched(hdl, n, a, n, p, info, batch);
	__syncthreads();
	status = cublasSgetriBatched(hdl, n, aconst, n, p,
		c, n, info, batch);
	__syncthreads();
	cublasDestroy_v2(hdl);
}

static void run_inv(float *in, float *out, int n)
{
	float *a_d, *c_d;

	PERR(cudaMalloc(&a_d, n*n*sizeof(float)));
	PERR(cudaMalloc(&c_d, n*n*sizeof(float)));
	PERR(cudaMemcpy(a_d, in, n*n*sizeof(float), cudaMemcpyHostToDevice));

	inv_kernel << <1, 1 >> >(a_d, c_d, n);

	cudaDeviceSynchronize();
	ERRCHECK;

	PERR(cudaMemcpy(out, c_d, n*n*sizeof(float), cudaMemcpyDeviceToHost));
	PERR(cudaFree(a_d));
	PERR(cudaFree(c_d));
}


int main(int argc, char **argv)
{
	//-------------------- matrix transpose X' --------------------
	float X[12] = { 1, 0, 1, 1, 1, 2, 1, 3, 1, 4, 1, 5 };
	printf("X:\n");
	for (int i = 0; i < 6; i++)
	{
		for (int j = 0; j < 2; j++)
			printf("%.4f\t", X[i * 2 + j]);
		printf("\n");
	}
	float y[6] = { 0, 20, 60, 68, 77, 110 };
	printf("\n");
	printf("y:\n");
	for (int i = 0; i < 6; i++)
	{
		printf("%.4f\t", y[i]);
	}
	printf("\n");
	printf("\n");

	float *b;
	//b is transpose of x
	b = (float *)malloc(B * A*sizeof(float));

	for (int i = 0; i < B * A; ++i)
		b[i] = 0;

	//-------------------- matrx initialization for transpose --------------------
	float *d_a, *d_b;

	cudaMalloc(&d_a, A * B*sizeof(float));
	cudaMalloc(&d_b, B * A*sizeof(float));

	cudaMemcpy(d_a, X, A * B*sizeof(float), cudaMemcpyHostToDevice);
	cudaMemcpy(d_b, b, B * A*sizeof(float), cudaMemcpyHostToDevice);

	int dimx = 32;
	int dimy = 32;
	dim3 block(dimx, dimy);
	dim3 grid((B + block.x - 1) / block.x, (A + block.y - 1) / block.y);

	transpose << <grid, block >> >(d_b, d_a, A, B);

	cudaMemcpy(b, d_b, B * A*sizeof(float), cudaMemcpyDeviceToHost);

	printf("X':\n");
	for (int i = 0; i < B; i++)
	{
		for (int j = 0; j < A; j++)
			printf("%.4f\t", b[i * A + j]);
		printf("\n");
	}

	//-------------------- matrx initialization for multiplication X'*X--------------------
	float *c;
	c = (float *)malloc(B * B*sizeof(float));	
	float *d_c;

	//start using GPU to multiply matrix
	cudaMalloc(&d_c, B * B*sizeof(float));
	cudaMemcpy(d_c, c, B * B*sizeof(float), cudaMemcpyHostToDevice);

	dim3 grid2((B + block.x - 1) / block.x, (B + block.y - 1) / block.y);

	product << <grid2, block >> >(d_b, d_a, d_c, B, A, B);

	cudaMemcpy(c, d_c, B * B*sizeof(float), cudaMemcpyDeviceToHost);

	printf("\n");
	printf("X'*X:\n");
	for (int i = 0; i < B; i++)
	{
		for (int j = 0; j < B; j++)
			printf("%.4f\t", c[i * B + j]);
		printf("\n");
	}

	//-------------------- pinv(X'*X) --------------------
	float *invmatrix;
	invmatrix = (float *)malloc(B * B*sizeof(float));
	run_inv(c, invmatrix, B);
	printf("\n");
	printf("pinv(X'*X):\n");
	for (int i = 0; i < B; i++){
		for (int j = 0; j < B; j++) printf("%.4f, ", invmatrix[(B * i) + j]);
		printf("\n");
	}

	//-------------------- pinv(X'*X)*X' --------------------
	float *invma;
	cudaMalloc(&invma, B * B*sizeof(float));
	cudaMemcpy(invma, invmatrix, B * B*sizeof(float), cudaMemcpyHostToDevice);

	float *e;
	e = (float *)malloc(B * A*sizeof(float));
	float *d_e;
	cudaMalloc(&d_e, B * A*sizeof(float));
	cudaMemcpy(d_e, e, B * A*sizeof(float), cudaMemcpyHostToDevice);

	dim3 grid3((B + block.x - 1) / block.x, (A + block.y - 1) / block.y);
	product << <grid3, block >> >(invma, d_b, d_e, B, B, A);
	cudaMemcpy(e, d_e, B * A*sizeof(float), cudaMemcpyDeviceToHost);

	printf("\n");
	printf("pinv(X'*X)*X:\n");
	for (int i = 0; i < B; i++)
	{
		for (int j = 0; j < A; j++)
			printf("%.4f\t", e[i * A + j]);
		printf("\n");
	}

	//-------------------- pinv(X'*X)*X'*y' --------------------
	float *res;
	res = (float *)malloc(B * C*sizeof(float));
	float *d_res;
	cudaMalloc(&d_res, B * C*sizeof(float));
	cudaMemcpy(d_res, res, B * C*sizeof(float), cudaMemcpyHostToDevice);

	float *d_y;
	cudaMalloc(&d_y, A * C*sizeof(float));
	cudaMemcpy(d_y, y, A * C*sizeof(float), cudaMemcpyHostToDevice);

	dim3 grid4((B + block.x - 1) / block.x, (C + block.y - 1) / block.y);
	product << <grid4, block >> >(d_e, d_y, d_res, B, A, C);
	cudaMemcpy(res, d_res, B * C*sizeof(float), cudaMemcpyDeviceToHost);

	printf("\n");
	printf("the result is:\n");
	for (int i = 0; i < B; i++)
	{
		for (int j = 0; j < C; j++)
			printf("%.4f\t", res[i * C + j]);
		printf("\n");
	}

	printf("\n");
	printf("------------------------------------------\n");
	printf("The regression model is:");
	printf("y = %.4f * x + %.4f\n", res[1],res[0]);
	printf("------------------------------------------\n");

	free(b);
	free(c);
	free(invmatrix);
	free(e);
	free(res);

	cudaFree(d_a);
	cudaFree(d_b);
	cudaFree(d_c);
	cudaFree(invma);
	cudaFree(d_e);
	cudaFree(d_res);

	return 0;
}