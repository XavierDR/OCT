/***************************************************************************
*
* SaveImages.cpp
*
* This application acquires images in real time from a external camera.
* The images are combined and processed with the following formula:
* I = (I1-I2)^2 + (I3-I4)^2
* The resulting images are then saved into a binary file in this format:
* startfile/ rows columns img1 img2 img3 img4 .../endfile
*
* Only the processed images are saved, not the raw ones.
*
* @author Xavier Ducharme Rivard
* @version 1.0 28/09/2015
* 18/09/2015 created
***************************************************************************/


#include "stdafx.h"
#include <iostream>
#include <fstream>
#include "resource.h"
#include "SequenceInterface.h"
#include <string>

#include "opencv2/core/core.hpp"
#include "persistence.hpp"
#include "opencv2/imgproc/imgproc_c.h"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

int bitmapSize = 1024*1024;
int imgRows = 1024;
int imgCols = 1024;

void imgProc(PBFU32* bufArr, BFU32 bufs, char fileName[60]);

using namespace std;
using namespace cv;

int main(int argc, char* argv[])
{		
	BFU32	numBuffers = 100;	// Allocate 100 buffers
	BFU32	setupOptions = 0;	// Use default setup options.

	cout << "Input filename is: " << argv[1] << " and is "
		<< strlen(argv[1]) << " characters long" << endl;

	char	FileName[30] = "";
	for(unsigned int i = 0; i < strlen(argv[1]); i++){
		FileName[i] = argv[1][i];
	}

	int counter = 0, loops = 1;

	cout << "Creating instance of sequence interface." << endl;
	BufferAcquisition::SequenceInterface board(0, numBuffers, 0);
	PBFU32* pBufferArray= board.getBufferArrayPointers();
		
	bool keeplooping = true;
	cout << "Acquiring sequence..." << endl;

	// Acquisition loop
	while(!BFkbhit() && keeplooping && counter<loops)
	{
		board.seqControl(BISTART, BiWait);
		// Wait here until the sequence has been captured.
		board.seqWaitDone(10000);
		counter++;
	}

	// Binary file reading for verification purposes
	Mat orthoImg;
	Mat paraImg(1024, 1024, CV_8UC1);
	imgProc(pBufferArray, numBuffers, FileName);
	cout << "Reading file named : " << FileName << endl;
	ifstream ifs(FileName, fstream::binary | ios::in);
	ifs.seekg(ios::beg);
	int rows, cols;
	ifs.read((char *) &rows, sizeof(int));
	ifs.read((char *) &cols, sizeof(int));
	cout << "Rows: " << rows << " Cols: " << cols << endl;
	string fname = "C:\\Users\\OCT\\Desktop\\OCTImages\\Img00";
	string fNumber;
	char number[10];
	cout << "Saving images..." << endl;
	for(unsigned int i=0; i < numBuffers/4; i++){
		ifs.read((char*)paraImg.data, 1024*1024);
		//paraImg.convertTo(paraImg, CV_8UC3, 12.0);
		cv::imwrite(fname + fNumber + ".png", paraImg);
		_itoa_s((i+1), number, 10);
		if((i+1)< 10)
			fname[35] = *number;
		else{
			fname[34] = number[0];
			fname[35] = number[1];
		}

		imshow(FileName, paraImg);
		waitKey(210);
	}
}

void imgProc(PBFU32* bufArr, BFU32 bufs, char fileName[]){
	ofstream file(fileName, fstream::binary);
	cout << fileName << endl;;
	Mat endImg;
	cout << "Saving sequence to disk..." << endl;
	file.seekp(ios::beg);
	file.write((char*)&imgRows, sizeof(int));
	file.write((char*)&imgCols, sizeof(int));
	for(unsigned int i=0; i < bufs-4; i+=4){
		Mat temp1, temp2;
		Mat img1(Size(1024, 1024), CV_8UC1, (void *)bufArr[i], (size_t)1024);
		Mat img2(Size(1024, 1024), CV_8UC1, (void *)bufArr[i+1], (size_t)1024);
		Mat img3(Size(1024, 1024), CV_8UC1, (void *)bufArr[i+2], (size_t)1024);
		Mat img4(Size(1024, 1024), CV_8UC1, (void *)bufArr[i+3], (size_t)1024);

		subtract(img1, img2, temp1);
		subtract(img3, img4, temp2);
		temp1 = temp1.mul(temp1);
		temp2 = temp2.mul(temp2);
		cv::add(temp1, temp2, endImg);
		file.write((char*) endImg.data, bitmapSize); // Not the subtraction yet (Black image)
	}
	file.close();
}
